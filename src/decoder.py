class Decoder:
    def __init__(self):
        """
        Initializes the Decoder class.
        """
        pass
        
    def read_rom(rom_file, start_address, size):
        """
        Reads a segment of the ROM file from the specified start address to the end address.

        Parameters:
            rom_file (str): The path to the ROM file.
            start_address (int): The starting position in the file to read from.
            size (int): The number of bytes to read.

        Returns:
            bytes: The data read from the ROM file.
        """
        try:
            with open(rom_file, "rb") as f:
                f.seek(start_address)
                data = f.read(size)
            return data
        except ValueError:
            return

    def read_tbl(tbl_file, bracket_index):
        """
        Reads a .tbl file to create a character mapping table (supports DTE/MTE).

        Parameters:
            tbl_file (str): The path to the .tbl file.
            bracket_index (int): Determines the bracket style to block his use.

        Returns:
            dict: A dictionary where keys are byte values (int) and values are strings (characters or sequences).
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
        with open(tbl_file, "r", encoding="UTF-8") as f:
            for line in f:
                if line.startswith(";") or line.startswith("/"):
                    continue  
                if "=" in line:
                    hex_value, chars = line.split("=", 1)
                    if any(c in restricted_chars for c in chars):
                        continue
                    try:
                        hex_value = int(hex_value, 16)
                        chars = chars.strip("\n")
                        char_table[hex_value] = chars 
                    except ValueError:
                        print(f"Warning: {hex_value} invalid number!, ignored.")
                        continue
        return char_table

    def process_pointers_2_bytes(data, base, endianness):
        """
        Processes the pointer data by converting it to pairs and transforming it to big-endian,
        then adding the header offset.

        Parameters:
            data (bytes): The raw pointer data read from the ROM.
            base (int): The offset to add to each pointer.
            endianness (int): Determines the byte order (0 for little-endian, 1 for big-endian).

        Returns:
            list: A list of processed pointers as integers.
        """
        result = []
        for i in range(0, len(data), 2):
            pair = data[i:i + 2]
            if endianness == 0:
                value = int.from_bytes(pair, byteorder='little') + base
            elif endianness == 1:
                value = int.from_bytes(pair, byteorder='big') + base   
            result.append(value)
        return result

    def process_pointers_split_2_bytes(lsb, msb, base):
        """
        Processes the pointer data by converting it to pairs and transforming it to little-endian,
        then adding the header offset.

        Parameters:
            lsb (list): List of least significant bytes of the pointers.
            msb (list): List of most significant bytes of the pointers.
            base (int): The offset to add to each pointer.

        Returns:
            list: A list of processed pointers as integers.
        """
        result = []
        for i in range(len(lsb)):
            pair = [lsb[i], msb[i]]
            value = int.from_bytes(pair, byteorder='little') + base
            result.append(value)
        return result

    def process_pointers_3_bytes(data, base, endianness):
        """
        Processes the pointer data by converting it to triplets of 3 bytes, 
        then reversing the last two bytes, and transforming to big-endian,
        and adding the header offset.

        Parameters:
            data (bytes): The raw pointer data read from the ROM.
            base (int): The offset to add to each pointer.
            endianness (int): Determines the byte order (0 for little-endian, 1 for big-endian).

        Returns:
            list: A list of processed pointers as integers.
        """
        result = []
        for i in range(0, len(data), 3):
            triplet = data[i:i + 3]       
            use_last_pair = triplet[1:]
            if endianness == 0:
                value = int.from_bytes(use_last_pair, byteorder='little') + base
            elif endianness == 1:
                value = int.from_bytes(use_last_pair, byteorder='big') + base
            result.append(value)    
        return result

    def process_pointers_4_bytes(data, base, endianness):
        """
        Processes the pointer data by converting it to quadruples of 4 bytes,
        then transforming to big-endian, and adding the header offset.

        Parameters:
            data (bytes): The raw pointer data read from the ROM.
            base (int): The offset to add to each pointer.
            endianness (int): Determines the byte order (0 for little-endian, 1 for big-endian).

        Returns:
            list: A list of processed pointers as integers.
        """
        result = []
        for i in range(0, len(data), 4):
            quartet = data[i:i + 4]
            use_last_pair = quartet[1:]
            if endianness == 0:
                value = int.from_bytes(use_last_pair, byteorder='little') + base
            elif endianness == 1:
                value = int.from_bytes(use_last_pair, byteorder='big') + base
            result.append(value)
        return result

    def decode_script(rom_data, addresses_list, end_line, char_table, ignore_end_line, bracket_index):
        """
        Extracts texts from the ROM data at specified addresses until a line breaker is encountered.

        Parameters:
            rom_data (bytes): The complete ROM data.
            addresses_list (list): A list of addresses to read the texts from.
            end_line (set): A set of byte values used as line breakers.
            char_table (dict): A dictionary mapping byte values to characters or sequences.
            decoded_valid_character (bool): Flag indicating if a valid character has been decoded.
            bracket_index (int): Specifies the bracket style to use around special characters.

        Returns:
            tuple: Containing:
                - texts (list): Extracted script text.
                - total_bytes_read (int): Total text block size.
                - lines_length (list): Length of each line in bytes.
        """             
        texts = []  
        lines_length = []
        bytes_line_counter = 0
        total = 0
        
        #formats
        bracket_formats = {
            0: "~{0}~",
            1: "[{0}]",  
            2: "{{{0}}}", 
            3: "<{0}>"  
        }

        bracket_format = bracket_formats.get(bracket_index)

        for addr in addresses_list:
            text = bytearray()
            decoded_valid_character = False
            
            while True:
                byte = rom_data[addr]  
                bytes_line_counter += 1

                # If the byte is a end_line, stop extracting
                if ignore_end_line: 
                    if byte in end_line and decoded_valid_character:
                        split_byte = byte
                        break
                else:
                    if byte in end_line:
                        split_byte = byte
                        break

                # Map the byte using char_table to get the character
                char = char_table.get(byte, None)  
                if char:
                    # If single character
                    if len(char) == 1:
                        text.append(ord(char))
                        decoded_valid_character = True
                    # If multiple characters (DTE/MTE)
                    else:  
                        for c in char:
                            text.append(ord(c))
                        decoded_valid_character = True
                # If byte is not in char_table use raw byte
                else:
                    hex_value = format(byte, '02X')
                    bracket = bracket_format.format(hex_value)
                    text.extend(bracket.encode('UTF-8'))
                addr += 1
                
            # Add the breaker byte to the text
            if split_byte is not None:
                char = char_table.get(split_byte, None)
                if char:
                    # if assigned to a single character
                    if len(char) == 1:
                        text.append(ord(char))
                    # if assigned to a chain characters
                    else:
                        for c in char:
                            text.append(ord(c))
                    # Use raw byte
                else:
                    hex_value = format(split_byte, '02X')
                    bracket = bracket_format.format(hex_value)
                    text.extend(bracket.encode('UTF-8'))
                                     
            # Convert byte array to string
            decoded_text = text.decode('UTF-8', errors='replace')

            # Append the decoded text to the list
            texts.append(decoded_text)
            lines_length.append(bytes_line_counter)
            total = total + bytes_line_counter
            bytes_line_counter = 0

        # Calculate total bytes read
        total_bytes_read = abs((addresses_list[-1] + lines_length[-1]) - addresses_list[0])

        return texts, total_bytes_read, lines_length

    def decode_script_no_end_line(rom_data, addresses_list, end_offset, char_table, bracket_index):
        """
        Extracts texts from the ROM data at specified addresses based on the lengths in lines_length.

        Parameters:
            rom_data (bytes): The complete ROM data.
            addresses_list (list): A list of addresses to read the texts from.
            end_offset (set): The final offset after the last address.
            char_table (dict): A dictionary mapping byte values to characters or sequences.

        Returns:
            tuple: Containing:
                - texts (list): Extracted script text.
                - total_bytes_read (int): Total text block size.
                - lines_length (list): Length of each line in bytes.
        """
        texts = []  
        lines_length = []
        total = 0

        #formats
        bracket_formats = {
            0: "~{0}~",
            1: "[{0}]",  
            2: "{{{0}}}", 
            3: "<{0}>"  
        }

        bracket_format = bracket_formats.get(bracket_index)

        # Add final offset to the addresses_list
        addresses_list.append(end_offset)

        # Calculate lines length of each segment is the difference between consecutive addresses
        for i in range(len(addresses_list) - 1):
            length = int(addresses_list[i + 1]) - int(addresses_list[i])
            lines_length.append(length)

        # Loop over each starting address in the list and use lines_length for determining byte ranges
        for i in range(len(addresses_list) - 1):
            start_addr = addresses_list[i]
            length = lines_length[i]
            end_addr = start_addr + length          
            text = bytearray()
            
            # Read bytes from the starting address to the end address (using the specified length)
            for addr in range(start_addr, end_addr):
                byte = rom_data[addr]

                # Map the byte using char_table to get the character
                char = char_table.get(byte, None)  
                if char:
                    # If single character
                    if len(char) == 1:
                        text.append(ord(char))
                    # If multiple characters (DTE/MTE)
                    else:  
                        for c in char:
                            text.append(ord(c))
                # If byte is not in char_table use raw byte
                else:
                    hex_value = format(byte, '02X')
                    bracket = bracket_format.format(hex_value)
                    text.extend(bracket.encode('UTF-8'))
            
            # Convert byte array to string
            decoded_text = text.decode('UTF-8', errors='replace')

            # Append the decoded text to the list
            texts.append(decoded_text)
            total += length

        # Calculate total bytes read (this will be the sum of all lengths in lines_length)
        total_bytes_read = total

        return texts, total_bytes_read, lines_length

    def parse_end_lines(string):
        """
        Parses a string of comma-separated hexadecimal values into a set of integers.

        Parameters:
            string (str): A string containing hexadecimal values separated by commas.

        Returns:
            set: A set of integers representing the line breakers.
        """      
        end_lines = set()
        for byte in string.split(','):
            byte = byte.strip() 
            end_lines.add(int(byte, 16))
        return end_lines

    @staticmethod
    def format_hex_string(hex_set):
        """
        Takes a string of hex values separated by commas and returns a formatted string separated by '~'.

        Parameters:
            hex_string (set): Set with end lines codes.

        Returns:
            str: The formatted string with - separating the hex values.
        """
        formatted_values = [f"-{val:02X}" for val in hex_set]
        formatted_string = ''.join(formatted_values)    
        return formatted_string

    def write_out_file(file, script_text, pointers_start_address, pointers_end_address, pointer_size, pointers_list, lines_length, end_line, no_comments):
        """
        Writes data to a file, formatting each line with a semicolon and newline.
        
        Parameters:
            file (str): The path to the output file.
            script_text (list): A list of strings representing the script content to write to the file.
            pointers_start_address (int): The starting address of the pointer table.
            pointer_table_size (int): The size of the pointer table.
            address_list (list): A list of addresses corresponding to each line in the script.
            lines_length (list): A list of the length of each line in the script.
            line_breaker (int): A value used to split lines.
            no_comments (bool): Flag indicating whether to include comments (default is False).
        """
        with open(file, "w", encoding='UTF-8') as f:
            if not end_line == None:
                formatted_string = Decoder.format_hex_string(end_line)
                f.write(f";{{{pointers_start_address:08X}-{(pointers_end_address):08X}-{pointer_size:08X}}}{formatted_string}\n")
            else:
                f.write(f";{{{pointers_start_address:08X}-{(pointers_end_address):08X}-{pointer_size:08X}}}\n")          
            i = 0
            for line in script_text:
                # Format the address as uppercase hex with leading zeros
                address_str = f"{pointers_list[i]:08X}"
                
                # Write the formatted address followed by the line content and length
                f.write(f"@{i+1}\n")
                
                # Write the comment section based on no_comments flag
                if no_comments:
                    f.write(f";{address_str}#{len(line)}#{lines_length[i]}\n")
                else:
                    f.write(f";{address_str}{{{line}}}#{len(line)}#{lines_length[i]}\n")
                
                f.write(f"{line}\n")
                f.write("|\n")
                i += 1
