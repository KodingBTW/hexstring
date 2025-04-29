import re

class Encoder:
    def __init__(self):
        """
        Initializes the Decoder class.
        """
        pass

    def read_script(file):
        """
        Reads a file containing the game's text and extracts pointer information from the first line. 
        It also handles multiple breaker lines or just one.
        
        Parameters:
            file (str): The path to the file to read.
        
        Returns:
            tuple: Contains:
                - text_data (list): A list of strings, each representing a line of text from the file.
                - pointers_start_address (int): The start address of the pointers.
                - pointers_end_address (int): The end address of the pointers.
                - pointer_table_size (int): The size of the pointer table.
                - end_lines (str): A string representing the line breakers used in the file.
        """
        hex_data = []
        end_lines=''
        with open(file, "r", encoding='UTF-8') as f:
            first_line = f.readline().strip()
            match = re.match(r";\{([0-9A-Fa-f\-]+)\}-(.*)", first_line)
            offsets = match.group(1)
            hex_data.extend([int(addr, 16) for addr in offsets.split('-')])
            byte = match.group(2)
            end_lines = ",".join([f"{val}" for val in byte.split('-')])
            
            script = [
                line.rstrip('\n') for line in f.readlines()
                if not (line.startswith(";") or line.startswith("@") or line.startswith("|"))
            ]
        return script, hex_data[0], hex_data[1], hex_data[2], end_lines

    def read_tbl(tbl_file, bracket_index):
        """
        Reads a .tbl file to create a character mapping table based on a given bracket index.
        
        Parameters:
            tbl_file (str): The path to the .tbl file.
            bracket_index (int): Index used to determine restricted characters.
        
        Returns:
            tuple: Contains:
                - char_table (dict): A dictionary where keys are character sequences and values are their corresponding byte values.
                - longest_char (int): The length of the longest character sequence in the table.
        """
        if bracket_index == 0:
            restricted_chars = {"~"}
        elif bracket_index == 1:
            restricted_chars = {"[", "]"}
        elif bracket_index == 2:
            restricted_chars = {"{", "}"}
        elif bracket_index == 3:
            restricted_chars = {"<", ">"}
        else:
            restricted_chars = set()
            
        char_table = {}
        longest_char = 0
        
        with open(tbl_file, "r", encoding="UTF-8") as f:
            for line in f:
                if line.startswith(";") or line.startswith("/"):
                    continue
                if "=" in line:
                    hex_value, chars = line.split("=",1)
                    if any(c in restricted_chars for c in chars):
                        continue
                    try:
                        hex_value = int(hex_value, 16)
                        chars = chars.strip("\n")
                        char_table[chars] = hex_value
                        longest_char = max(longest_char, len(chars))
                    except ValueError:
                        continue
        return char_table, longest_char

    def encode_script(text_script, end_lines, char_table, longest_char, not_use_end_lines, bracket_index):
        """
        Encodes the text into bytes using DTE/MTE encoding schemes, considering the provided character table.
        
        Parameters:
            text_script (list): List of text strings to encode.
            end_lines (set): A set the end lines used in the split pointers.
            char_table (dict): Dictionary that maps character sequences to byte values.
            longest_char (int): Maximum length of sequences to consider while encoding.
            ignore_end_lines (bool): Whether to ignore end lines or not.
            bracket_index (int): Determines which type of character bracket is used in the encoding process.
        
        Returns:
            tuple: A tuple containing:
                - encoded_data (bytearray): The encoded text data.
                - pointers (list): List of pointers (cumulative lengths).
        """
        if bracket_index == 0:
            raw_byte = r'(~[A-Za-z0-9]+~)'
            hex_code = r'~([0-9A-Fa-f]{2})~'
        elif bracket_index == 1:
            raw_byte = r'([[A-Za-z0-9]+])'
            hex_code = r'[([0-9A-Fa-f]{2})]'
        elif bracket_index == 2:
            raw_byte = r'({[A-Za-z0-9]+})'
            hex_code = r'{([0-9A-Fa-f]{2})}'
        elif bracket_index == 3:
            raw_byte = r'(<[A-Za-z0-9]+>)'
            hex_code = r'<([0-9A-Fa-f]{2})>'

        encoded_data = bytearray()
        total_bytes = 0
        cumulative_length = [0]

        for line in text_script:
            # Split lines if raw byte are encounter
            parts = []
            split_line = re.split(raw_byte, line)
            split_line = [part for part in split_line if part]
            parts.extend(split_line)
            
            # Process each sub-line
            processed_sub_lines = []
            for part in parts:
                # Search for repeat pointer function
                if part.startswith("&"):
                    cumulative_length.pop()
                    copy_length = total_bytes
                    total_bytes = cumulative_length[-1]
                    cumulative_length.append(total_bytes)
                    total_bytes = copy_length
                    continue
                
                # If is a raw byte
                elif re.match(hex_code, part):
                    processed_sub_lines.append(bytes([int(part[1:3], 16)])) 
                    total_bytes += 1
                else:
                    # If is a char
                    i = 0
                    encoded_sub_lines = bytearray()
                    while i < len(part):
                        # Searching for sequences based on the longest char (DTE/MTE Algorithm)
                        for length in range(min(longest_char, len(part) - i), 0, -1):
                            seq = part[i:i+length]
                            if seq in char_table:
                                encoded_sub_lines.append(char_table[seq])
                                total_bytes += 1
                                i += length
                                break
                        else:
                            # Protection: if not encounter anyone encode by ASCII form.
                            encoded_sub_lines.append(ord(part[i]))
                            total_bytes += 1
                            i += 1
                    
                    # Add the encoded
                    processed_sub_lines.append(encoded_sub_lines)

            # Add sub-lines to final line
            encoded_line = bytearray()
            for sub_line in processed_sub_lines:
                encoded_line.extend(sub_line)

            # Add the processed line to the final result
            encoded_data.extend(encoded_line)

            # Split pointer by line lenght in script
            if not_use_end_lines:
                cumulative_length.append(total_bytes)
            else:
            # Split pointer by end lines code
                for char in sub_line:
                    if char in end_lines:
                        cumulative_length.append(total_bytes)

        # Remove last pointer
        cumulative_length.pop()
        
        return encoded_data, len(encoded_data), cumulative_length

    def calculate_pointers_2_bytes(list_cumulative_length, first_pointer, base, endianness):
        """
        Calculates pointer data by adjusting each pointer with the header size 
        and encoding them in little-endian format.

        Parameters:
            list_cumulative_length (list): A list of cumulative pointer lengths to adjust.
            first_pointer (int): The first pointer to add to each cumulative length.
            base (int): The base address to subtract from each pointer.
            endianness (int): The endianness (0 for little-endian, 1 for big-endian).

        Returns:
            tuple: A tuple containing:
                - pointers_data (bytearray): The encoded pointer data in little-endian format.
                - data_length (int): The length of the encoded pointer data.
        """
        pointers_data = bytearray()
        pointers_list = [ptr + first_pointer for ptr in list_cumulative_length]
        pointers_list = [ptr - base for ptr in pointers_list]
        if endianness == 0:
            for ptr in pointers_list:
                pointers_data.append(ptr & 0xFF)                 
                pointers_data.append((ptr >> 8) & 0xFF)         
        elif endianness == 1:
            for ptr in pointers_list:
                pointers_data.append((ptr >> 8) & 0xFF)
                pointers_data.append(ptr & 0xFF)
        return pointers_data, len(pointers_data)

    def calculate_pointers_2_bytes_split(list_cumulative_length, first_pointer, base):
        """
        Similar to calculate_pointers_2_bytes, but encodes the pointers as two separate byte arrays (LSB, MSB).

        Parameters:
            list_cumulative_length (list): A list of cumulative pointer lengths to adjust.
            first_pointer (int): The first pointer to add to each cumulative length.
            base (int): The base address to subtract from each pointer.
            endianness (int): The endianness (0 for little-endian, 1 for big-endian).

        Returns:
            tuple: Contains:
                - lsb_ptr (bytearray): Least significant byte values.
                - msb_ptr (bytearray): Most significant byte values.
                - data_length (int): The length of the byte arrays.
        """
        lsb_ptr = bytearray()
        msb_ptr = bytearray()
        pointers_list = [ptr + first_pointer for ptr in list_cumulative_length]
        pointers_list = [ptr - base for ptr in pointers_list]

        for ptr in pointers_list:
            lsb_ptr.append(ptr & 0xFF)
            msb_ptr.append((ptr >> 8) & 0xFF)
        return lsb_ptr, msb_ptr, len(lsb_ptr)

    def calculate_pointers_3_bytes(list_cumulative_length, first_pointer, base, endianness):
        """
        Similar to calculate_pointers_2_bytes, but works with 3-byte pointers.

        Parameters:
            list_cumulative_length (list): A list of cumulative pointer lengths to adjust.
            first_pointer (int): The first pointer to add to each cumulative length.
            base (int): The base address to subtract from each pointer.
            endianness (int): The endianness (0 for little-endian, 1 for big-endian).

        Returns:
            tuple: A tuple containing:
                - pointers_data (bytearray): The encoded pointer data.
                - data_length (int): The length of the encoded pointer data.
        """
        pointers_data = bytearray()
        pointers_list = [ptr + first_pointer for ptr in list_cumulative_length]
        if endianness == 0:
            for ptr in pointers_list:
                pointers_data.append((ptr >> 16) & 0xFF)                 
                pointers_data.append(ptr & 0xFF)
                pointers_data.append((ptr >> 8) & 0xFF)
        elif endianness == 1:
            for ptr in pointers_list:
                pointers_data.append((ptr >> 16) & 0xFF)
                pointers_data.append((ptr >> 8) & 0xFF)
                pointers_data.append(ptr & 0xFF)
        return pointers_data, len(pointers_data)
        
    def calculate_pointers_4_bytes(list_cumulative_length, first_pointer, base, endianness):
        """
        Calculates and returns the pointer data after adjusting each pointer with the header size
        and encoding them in big-endian format.

        Parameters:
            pointersList (list): A list of pointers to adjust and encode.
            headerSize (int): The header size to subtract from each pointer.

        Returns:
            bytearray: The encoded pointer data in big-endian format.
        """
        pointers_data = bytearray()
        pointers_list = [ptr + first_pointer for ptr in list_cumulative_length]
        if endianness == 0:
            for ptr in pointers_list:
                pointers_data.append((ptr >> 24) & 0xFF)     
                pointers_data.append((ptr >> 16) & 0xFF)
                pointers_data.append(ptr & 0xFF)
                pointers_data.append((ptr >> 8) & 0xFF)
        elif endianness == 1:
            for ptr in pointers_list:
                pointers_data.append((ptr >> 24) & 0xFF)     
                pointers_data.append((ptr >> 16) & 0xFF)
                pointers_data.append((ptr >> 8) & 0xFF) 
                pointers_data.append(ptr & 0xFF)
        return pointers_data, len(pointers_data)


    def write_rom(rom_file, start_offset, original_size, data, fill_free_space, fill_free_space_byte):
        """
        Writes data to the ROM at the specified offset, filling any free space if requested.
        
        Parameters:
            rom_file (str): The path to the ROM file.
            start_offset (int): The offset in the ROM file where data should be written.
            original_size (int): The original size of the data to ensure there is enough space for the write operation.
            data (bytes or bytearray): The data to write to the ROM.
            fill_free_space (bool): Whether to fill the remaining space with a specific byte.
            fill_free_space_byte (byte): The byte used to fill the remaining space.
        
        Returns:
            int: The amount of free space left after writing the data.
        """
        free_space = int(original_size) - len(data)
        if fill_free_space:
            filled_data = data + fill_free_space_byte * free_space
        else:
            filled_data = data    
        with open(rom_file, "r+b") as f: 
            f.seek(start_offset)
            f.write(filled_data)
        return free_space
