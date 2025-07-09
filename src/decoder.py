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

    def read_tbl(tbl_file):
        """
        Reads a .tbl file to create a character mapping table (supports DTE/MTE, multibyte values).

        Parameters:
            tbl_file (str): The path to the .tbl file.

        Returns:
            char_table (dict): A dictionary where keys are byte sequences (as `bytes`) and values are strings (characters or sequences).
        """               
        char_table = {}
        
        with open(tbl_file, "r", encoding="UTF-8") as f:
            for line in f:
                if not line or line.startswith(";") or line.startswith("/"):
                    continue  
                if "=" in line:
                    hex_value, chars = line.split("=", 1)
                    try:
                        if len(hex_value) % 2 != 0:
                            print(f"Warning: '{hex_value}' is invalid! Skipped.")
                            continue
                        byte_key = bytes.fromhex(hex_value)
                        char_table[byte_key] = chars.strip("\n")
                    except ValueError:
                        print(f"Warning: '{hex_value}' is invalid! Skipped.")
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
            if value < 0:
                value = 0
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
            if value < 0:
                value = 0
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
            if len(triplet) < 3:
                continue
            low = triplet[0]
            high = triplet[1]
            bank = triplet[2]
            if endianness == 0:
                value = int.from_bytes([low, high, bank], byteorder='little') + base
            elif endianness == 1:
                value = int.from_bytes([low, high, bank], byteorder='big') + base
            elif endianness == 2:
                value = int.from_bytes([bank, high, low], byteorder='big') + base
            if value < 0:
                value = 0 
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
            #use_last_pair = quartet[2:]
            if endianness == 0:
                value = int.from_bytes(quartet, byteorder='little') + base
            elif endianness == 1:
                value = int.from_bytes(quartet, byteorder='big') + base
            if value < 0:
                value = 0
            result.append(value)
        print(result)
        return result

    def decode_script(rom_data, addresses_list, end_line, char_table, bracket_index):
        """
        Extracts texts from the ROM data at specified addresses until a end line
        Support multi-byte
.
        Parameters:
            rom_data (bytes): The complete ROM data.
            addresses_list (list): A list of addresses to read the texts from.
            end_line (set): A set of byte values used as end_lines
            char_table (dict): A dictionary mapping byte values or sequences to characters.
            bracket_index (int): Specifies the bracket style to use around unknown bytes.

        Returns:
            tuple: Containing:
                - texts (list): Extracted script text.
                - total_bytes_read (int): Total text block size.
                - lines_length (list): Length of each line in bytes.
        """             
        texts = []  
        lines_length = []
        total = 0

        # Bracket formats
        bracket_formats = {
            0: "~{0}~",
            1: "[{0}]",
            2: "{{{0}}}",
            3: "<{0}>"
        }

        bracket_format = bracket_formats.get(bracket_index)

        # Sort keys from .tbl
        key_lengths = sorted({len(k) for k in char_table.keys()}, reverse=True)

        for start_addr in addresses_list:
            addr = start_addr
            text = bytearray()
            bytes_line_counter = 0

            while addr < len(rom_data):
                matched = False

                for length in key_lengths:
                    if addr + length > len(rom_data):
                        continue

                    segment = rom_data[addr:addr + length]

                    if segment in char_table:
                        char = char_table[segment]
                        text.extend(char.encode('utf-8'))
                        addr += length
                        bytes_line_counter += length

                        # If end line
                        if length == 1 and segment[0] in end_line:
                            matched = True
                            break
                        matched = True
                        break

                if matched:
                    if length == 1 and segment[0] in end_line:
                        break 
                    continue

                # If raw byte
                byte = rom_data[addr]
                hex_value = format(byte, '02X')
                bracket = bracket_format.format(hex_value)
                text.extend(bracket.encode('utf-8'))
                addr += 1
                bytes_line_counter += 1

                if byte in end_line:
                    break

            decoded_text = text.decode('utf-8', errors='replace')
            texts.append(decoded_text)
            lines_length.append(bytes_line_counter)
            total += bytes_line_counter

        total_bytes_read = abs((addresses_list[-1] + lines_length[-1]) - addresses_list[0])
        return texts, total_bytes_read, lines_length

    def decode_script_no_end_line(rom_data, addresses_list, end_offset, char_table, bracket_index):
        """
        Extracts texts from the ROM data at specified addresses based on the lengths in lines_length.

        Parameters:
            rom_data (bytes): The complete ROM data.
            addresses_list (list): A list of addresses to read the texts from.
            end_offset (int): The final offset after the last address.
            char_table (dict): A dictionary mapping byte sequences (bytes) to characters or sequences.
            bracket_index (int): Specifies the bracket style to use around unknown bytes.

        Returns:
            tuple: Containing:
                - texts (list): Extracted script text.
                - total_bytes_read (int): Total text block size.
                - lines_length (list): Length of each line in bytes.
        """
        texts = []  
        lines_length = []
        total = 0

        # Bracket formats
        bracket_formats = {
            0: "~{0}~",
            1: "[{0}]",  
            2: "{{{0}}}", 
            3: "<{0}>"
        }

        bracket_format = bracket_formats.get(bracket_index)

        # Add final offset to the addresses list
        addresses_list.append(end_offset)

        # Calculate line lengths
        for i in range(len(addresses_list) - 1):
            length = int(addresses_list[i + 1]) - int(addresses_list[i])
            lines_length.append(length)

        # Prepare sorted multibyte keys for efficient matching
        sorted_keys = sorted(char_table.keys(), key=lambda k: len(k), reverse=True)

        for i in range(len(addresses_list) - 1):
            start_addr = addresses_list[i]
            length = lines_length[i]
            end_addr = start_addr + length          
            text = bytearray()
            addr = start_addr

            while addr < end_addr:
                matched = False
                for key in sorted_keys:
                    key_len = len(key)
                    if rom_data[addr:addr + key_len] == key:
                        text.extend(char_table[key].encode('utf-8'))
                        addr += key_len
                        matched = True
                        break
                if not matched:
                    # Unknown byte: wrap in bracket
                    byte = rom_data[addr]
                    hex_value = format(byte, '02X')
                    bracket = bracket_format.format(hex_value)
                    text.extend(bracket.encode('utf-8'))
                    addr += 1

            decoded_text = text.decode('utf-8', errors='replace')
            texts.append(decoded_text)
            total += length

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
