import bitstring

class Lempel_ziv:
    def __init__(self):
        pass

    def decompress_lz77(data, start_offset):
        """
        Decompress LZ77 algorithm from provided data using a flag-based format.

        Parameters:
            data (bytes): The binary data to decompress from.
            start_offset (int): The starting offset in the data to begin decompressing.

        Returns:
            tuple: Contains:
                - Full output: decompressed data + remaining ROM data (bytes).
                - The size of the decompressed script.
                - The final offset reached during decompression.
                - The size of the compressed data.
        """
        pos = start_offset
        decompressed_script = bytearray()

        while pos < len(data):
            flags = data[pos]
            pos += 1

            for i in range(8):
                if pos >= len(data):
                    break

                if flags & (0x80 >> i):
                    # Literal byte
                    decompressed_script.append(data[pos])
                    pos += 1
                else:
                    if pos + 1 >= len(data):
                        break

                    byte1 = data[pos]
                    byte2 = data[pos + 1]
                    pos += 2

                    # 12-bit offset, 4-bit length
                    offset = ((byte1 << 4) | (byte2 >> 4))
                    length = (byte2 & 0x0F) + 3

                    if offset == 0:
                        final_offset = pos - 1
                        compressed_size = final_offset - start_offset + 1
                        decompressed_script_size = len(decompressed_script)
                        remaining_data = data[final_offset + 1:]
                        full_output = bytes(decompressed_script) + remaining_data
                        return full_output, decompressed_script_size, final_offset, compressed_size

                    for _ in range(length):
                        decompressed_script.append(decompressed_script[-offset])

        final_offset = pos - 1
        compressed_size = final_offset - start_offset + 1
        decompressed_script_size = len(decompressed_script)
        remaining_data = data[final_offset + 1:]
        full_output = bytes(decompressed_script) + remaining_data

        return full_output, decompressed_script_size, final_offset, compressed_size
    
    def decompress_lzss(data, start_offset):
        """
        Decompress LZSS algorithm from provided data.

        Parameters:
            data (bytes): The binary data to decompress from.
            start_offset (int): The starting offset in the data to begin decompressing.

        Returns:
            tuple: Contains:
                - Decompressed data (bytes).
                - The size of the decompressed data
                - The final offset.
                - The size of the compressed data.
        """
        BIT_PASTCOPY = 0
        BIT_LITERAL = 1

        stream = bitstring.ConstBitStream(bytes=data)
        stream.bytepos = start_offset

        decompressed_script = bytearray()

        copy_source_size = stream.read('uint:4')
        copy_length_size = stream.read('uint:4')

        while True:
            if stream.pos >= stream.len:
                break

            next_command = stream.read('bool')

            if next_command == BIT_PASTCOPY:
                copy_source = stream.read(copy_source_size).uint
                copy_length = stream.read(copy_length_size).uint
                copy_length += 3

                if copy_source == 0:
                    break

                for _ in range(copy_length):
                    decompressed_script.append(decompressed_script[-copy_source])

            elif next_command == BIT_LITERAL:
                literal_byte = stream.read('uint:8')
                decompressed_script.append(literal_byte)

        stream.bytealign()
        script_end_offset = stream.bytepos - 1
        compressed_script_size = script_end_offset - start_offset + 1
        decompressed_script_size = len(decompressed_script)

        remaining_data = data[script_end_offset + 1:]
        full_output = bytes(decompressed_script) + remaining_data

        return full_output, decompressed_script_size, script_end_offset, compressed_script_size

    def decompress_lzw(data, start_offset, code_size=12):
        """
        Decompress LZW data with fixed-length codes (default 12 bits).

        Parameters:
            data (bytes): Full binary data stream.
            start_offset (int): Byte offset where the LZW data starts.
            code_size (int): Bit length per code (default: 12).

        Returns:
            tuple:
                - Full output: decompressed data + remaining ROM data (bytes).
                - Size of decompressed script (int).
                - Final offset in input (int).
                - Size of compressed data (int).
        """
        import bitstring

        # Convert input to bit stream and set starting position
        stream = bitstring.ConstBitStream(bytes=data)
        stream.bytepos = start_offset

        # Initialize dictionary with single-byte sequences
        dict_size = 256
        dictionary = {i: bytes([i]) for i in range(dict_size)}

        decompressed_script = bytearray()
        prev_code = None

        try:
            while True:
                code = stream.read(f"uint:{code_size}")
                if code in dictionary:
                    entry = dictionary[code]
                elif code == dict_size and prev_code is not None:
                    entry = dictionary[prev_code] + dictionary[prev_code][:1]
                else:
                    break  # Invalid code or premature end

                decompressed_script.extend(entry)

                if prev_code is not None:
                    dictionary[dict_size] = dictionary[prev_code] + entry[:1]
                    dict_size += 1

                prev_code = code

        except bitstring.ReadError:
            pass  # Reached end of stream

        stream.bytealign()
        script_end_offset = stream.bytepos - 1
        compressed_script_size = script_end_offset - start_offset + 1
        decompressed_script_size = len(decompressed_script)

        # Append remaining data from the ROM
        remaining_data = data[script_end_offset + 1:]
        full_output = bytes(decompressed_script) + remaining_data

        return full_output, decompressed_script_size, script_end_offset, compressed_script_size

    def compress_lz77(data):
        """
        Compress data using a simple LZ77 algorithm with 12-bit offset and 4-bit length format.

        Parameters:
            data (bytearray): The data to compress.

        Returns:
            tuple:
                - Compressed data (bytearray).
                - Compressed size (int).
                - Uncompressed size (int).
        """
        compressed = bytearray()
        i = 0
        data_len = len(data)
        decompressed_size = data_len

        WINDOW_SIZE = 0xFFF   # 12-bit offset max
        MIN_MATCH = 3
        MAX_MATCH = MIN_MATCH + 0xF  # 4-bit length: 0-15 -> actual 3–18

        while i < data_len:
            flags = 0
            flag_pos = len(compressed)
            compressed.append(0)  # Placeholder for flag byte

            flag_mask = 0x80  # Start at highest bit

            for _ in range(8):
                if i >= data_len:
                    break

                match_offset = 0
                match_length = 0

                # Search window
                start_index = max(0, i - WINDOW_SIZE)
                max_length = min(MAX_MATCH, data_len - i)

                for j in range(start_index, i):
                    length = 0
                    while length < max_length and data[j + length] == data[i + length]:
                        length += 1
                    if length >= MIN_MATCH and length > match_length:
                        match_offset = i - j
                        match_length = length

                if match_length >= MIN_MATCH:
                    # Write reference (2 bytes)
                    offset = match_offset
                    length = match_length - MIN_MATCH
                    byte1 = (offset >> 4) & 0xFF
                    byte2 = ((offset & 0xF) << 4) | (length & 0xF)
                    compressed.append(byte1)
                    compressed.append(byte2)
                    i += match_length
                else:
                    # Write literal
                    flags |= flag_mask
                    compressed.append(data[i])
                    i += 1

                flag_mask >>= 1

            compressed[flag_pos] = flags

        return compressed, len(compressed), decompressed_size

    def compress_lzss(data):
        """
        Compress LZSS algorithm from provided data.
        
        Parameters:
            data (bytearray): Script to compress.
        
        Returns:
            tuple:
                - A bytearray containing the compressed data.
                - The size of the compressed data.
                - The size of the original uncompressed data.
        """
        # Get decompressed size 
        decompressed_size = len(data)
        
        # Define some useful constants.
        BIT_PASTCOPY = 0
        BIT_LITERAL = 1

        # Initialize variables to store the best compressed data and its size
        best_compressed_data = None
        best_compressed_size = float('inf')
        best_source_arg_size = 0
        best_length_arg_size = 0

        for source_arg_size in range(10, 12):
            for length_arg_size in range(3, 6): 
                current_index = 0
                end_index = len(data)
                output = bitstring.BitArray()
                output.append(bitstring.pack('uint:4', source_arg_size))
                output.append(bitstring.pack('uint:4', length_arg_size))

                # Start compressing the input data
                while current_index < end_index:
                    best_source = 0
                    best_length = 0

                    # Limit the search for matching patterns based on the current source argument size
                    search_limit = min(current_index, (1 << source_arg_size) - 1)

                    # Search for the best match in the data
                    for i in range(1, search_limit + 1):
                        #Limit the length of the match based on the current length argument size
                        lookahead_limit = min((1 << length_arg_size) - 1 + 3, end_index - current_index)
                        current_length = 0
                        for j in range(lookahead_limit):
                            if data[current_index - i + j] == data[current_index + j]:
                                current_length += 1
                            else:
                                break

                        # Update the best match if the current match is longer
                        if current_length > best_length:
                            best_source = i
                            best_length = current_length

                    # If a match of at least 3 bytes is found, encode it as a past copy reference
                    if best_length >= 3:
                        output.append(bitstring.pack('uint:1', BIT_PASTCOPY))
                        output.append(bitstring.pack('uint:n=v', n=source_arg_size, v=best_source))
                        output.append(bitstring.pack('uint:n=v', n=length_arg_size, v=best_length - 3))
                        current_index += best_length
                    else:
                        output.append(bitstring.pack('uint:1', BIT_LITERAL))
                        output.append(bitstring.pack('uint:8', data[current_index]))
                        current_index += 1

                # End the compressed data with an additional past copy instruction
                output.append(bitstring.pack('uint:1', BIT_PASTCOPY))
                output.append(bitstring.pack('uint:n=v', n=source_arg_size, v=0))
                output.append(bitstring.pack('uint:n=v', n=length_arg_size, v=0))

                # Pad the output to make it byte-aligned if necessary
                if len(output) % 8 != 0:
                    output.append('0b' + '0' * (8 - len(output) % 8))
                

                # If the current compressed data is smaller than the best found so far, update the best data
                if len(output.bytes) < best_compressed_size:
                    best_compressed_data = output
                    best_compressed_size = len(output.bytes)
                    best_source_arg_size = source_arg_size
                    best_length_arg_size = length_arg_size
                    
        return bytearray(best_compressed_data.bytes), best_compressed_size, decompressed_size

    def compress_lzw(data, code_size=12):
        """
        Compress data using the LZW algorithm with fixed-length codes.

        Parameters:
            data (bytes or bytearray): Data to compress.
            code_size (int): Bit length of each code (default: 12).

        Returns:
            tuple:
                - Compressed data as a bytearray.
                - Size of compressed data.
                - Size of original uncompressed data.
        """
        max_dict_size = 1 << code_size
        dictionary = {bytes([i]): i for i in range(256)}
        dict_size = 256

        w = b""
        output_bits = bitstring.BitArray()

        for c in data:
            wc = w + bytes([c])
            if wc in dictionary:
                w = wc
            else:
                output_bits.append(f"uint:{code_size}={dictionary[w]}")
                if dict_size < max_dict_size:
                    dictionary[wc] = dict_size
                    dict_size += 1
                w = bytes([c])

        if w:
            output_bits.append(f"uint:{code_size}={dictionary[w]}")

        # Pad to byte alignment
        if output_bits.len % 8 != 0:
            output_bits.append(f"uint:{8 - (output_bits.len % 8)}=0")

        compressed_data = bytearray(output_bits.bytes)
        compressed_size = len(compressed_data)
        decompressed_size = len(data)

        return compressed_data, compressed_size, decompressed_size
