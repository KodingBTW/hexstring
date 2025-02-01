import re

def readScriptFile(file):
    """
    Reads a file with a game's text.
    Extracts pointer information from the first line and handles multiple breaker lines or just one.
    
    Parameters:
        file (str): The path to the file to read.
    
    Returns:
        tuple: Containing:
            - textData: A list of strings, each representing a line of text from the file.
            - hexData: A list of important data (pointersStartAddress,pointersEndAddress,PointerTableSize).
            - dataOut: A string of line breakers.
    """
    hexData = []
    lineBreakers=''
    # Open file
    with open(file, "r", encoding='UTF-8') as f:
        # Read first line
        firstLine = f.readline().strip()
        match = re.match(r";\{([0-9A-Fa-f\-]+)\}-(.*)", firstLine)
        # Extract addresses inside the braces
        address = match.group(1)
        hexData.extend([int(addr, 16) for addr in address.split('-')])
        # Extract and format breakerLines
        byte = match.group(2)
        lineBreakers = ",".join([f"0x{val}" for val in byte.split('-')])
        
    # Process text (excluding comments)
        textData = [
            line.rstrip('\n') for line in f.readlines()
            if not (line.startswith(";") or line.startswith("@") or line.startswith("|"))
        ]
    return textData, hexData[0], hexData[1], hexData[2], lineBreakers

def readTblFileInverted(tblFile):
    """
    Reads a .tbl file to create a character mapping table.
    
    Parameters:
        tblFile (str): The path to the .tbl file.
    
    Returns:
        dict: A dictionary where the keys are strings (characters or sequences) and the values are byte values (int).
        int: The length of the longest character sequence in the .tbl file.
    """
    charTable = {}
    maxSequence = 0
    
    with open(tblFile, "r", encoding="UTF-8") as f:
        for line in f:
            if line.startswith(";") or line.startswith("/"):
                continue
            if "=" in line:
                hexValue, chars = line.split("=",1)
                if "~" in chars:
                    continue
                try:
                    hexValue = int(hexValue, 16)
                    chars = chars.rstrip("\n")
                    charTable[chars] = hexValue
                    maxSequence = max(maxSequence, len(chars))
                except ValueError:
                    continue
    return charTable, maxSequence

def encodeText(textScript, lineBreakers, charTable, longestChar):
    """
    Encodes the text into bytes (supports DTE/MTE).
    
    Parameters:
        textScript (list): List of text strings to encode.
        charTable (dict): Dictionary that maps character sequences to byte values.
        longestChar (int): Maximum length of sequences to consider while encoding.
        
    Returns:
        tuple: A tuple containing:
            - bytearray: The encoded text data.
            - pointers: List of pointers (cumulative lengths).
    """
    encodedData = bytearray()
    totalBytes = 0
    cumulativeLength = [0]
    
    # Format to find hexadecimal sequences ~XX~
    hexCode = r'~([0-9A-Fa-f]{2})~'

    for line in textScript:
        # Break the line into substrings of normal text and hexadecimal sequences
        parts = []
        splitLine = re.split(r'(~[A-Za-z0-9]+~)', line)
        splitLine = [part for part in splitLine if part]
        parts.extend(splitLine)
        # Process each substring
        processedParts = []
        for part in parts:
            # Repeat last pointer function
            if part.startswith("&"):
                cumulativeLength.pop()
                copyLength = totalBytes
                totalBytes = cumulativeLength[-1]
                cumulativeLength.append(totalBytes)
                totalBytes = copyLength
                continue
            # If it is a hexadecimal sequence
            elif re.match(hexCode, part):
                processedParts.append(bytes([int(part[1:3], 16)])) 
                totalBytes += 1
            else:
                # Encode the sequence using the .tbl table
                i = 0
                encodedPart = bytearray()
                while i < len(part):
                    # Try to match the longest possible sequence starting from the current position
                    for length in range(min(longestChar, len(part) - i), 0, -1):
                        seq = part[i:i+length]
                        # If the sequence is found in the character table, encode it
                        if seq in charTable:
                            encodedPart.append(charTable[seq])
                            totalBytes += 1
                            i += length
                            break
                    else:
                         # If no sequence is found, encode the character individually (ASCII)
                        encodedPart.append(ord(part[i]))
                        totalBytes += 1
                        i += 1
                
                # Add the encoded part to processed parts
                processedParts.append(encodedPart)

        # Replace the hexadecimal sequences with their values
        finalLine = bytearray()
        for part in processedParts:
            finalLine.extend(part)

        # Add the processed line to the final result
        encodedData.extend(finalLine)
        
        # Mark the end of the line as a pointer (cumulative length)
        for char in part:
            if char in lineBreakers:
                cumulativeLength.append(totalBytes)

    # Remove the unnecessary pointer at the end
    cumulativeLength.pop()
    
    return encodedData, cumulativeLength

def calculatePointer2Bytes(listCumulativeLength, firstPointer, headerSize):
    """
    Calculates and returns the pointer data after adjusting each pointer with the header size
    and encoding them in little-endian format.

    Parameters:
        pointersList (list): A list of pointers to adjust and encode.
        headerSize (int): The header size to subtract from each pointer.

    Returns:
        bytearray: The encoded pointer data in little-endian format.
    """
    # Add first pointer for each cumulative lenth generating pointer exact size.
    pointersList = [ptr + firstPointer for ptr in listCumulativeLength]

    # Subtract the header size from each pointer in the list
    pointersList = [ptr - headerSize for ptr in pointersList]
    
    # Convert the list of pointers to bytearray (Little-endian encoding)
    pointersData = bytearray()
    for ptr in pointersList:
        pointersData.append(ptr & 0xFF)                 # Least significant byte
        pointersData.append((ptr >> 8) & 0xFF)          # Most significant byte
    return pointersData

def calculatePointer2BytesBigEndian(listCumulativeLength, firstPointer, headerSize):
    """
    Calculates and returns the pointer data after adjusting each pointer with the header size
    and encoding them in big-endian format.

    Parameters:
        pointersList (list): A list of pointers to adjust and encode.
        headerSize (int): The header size to subtract from each pointer.

    Returns:
        bytearray: The encoded pointer data in big-endian format.
    """
    # Add first pointer for each cumulative lenth generating pointer exact size.
    pointersList = [ptr + firstPointer for ptr in listCumulativeLength]

    # Subtract the header size from each pointer in the list
    pointersList = [ptr - headerSize for ptr in pointersList]
    
    # Convert the list of pointers to bytearray (Big-endian encoding)
    pointersData = bytearray()
    for ptr in pointersList:
        pointersData.append((ptr >> 8) & 0xFF)      # Most significant byte
        pointersData.append(ptr & 0xFF)             # Least significant byte
    return pointersData

def calculatePointer2BytesSeparated(listCumulativeLength, firstPointer, headerSize):
    """
    Calculates and returns the pointer data after adjusting each pointer with the header size
    and encoding them separate bytes (lsb first, msb later) in little-endian format.

    Parameters:
        listCumulativeLength (list): A list of cumulative pointer lengths to adjust.
        firstPointer (int): The first pointer to add to each cumulative length.
        headerSize (int): The header size to subtract from each pointer.
        
    Returns:
        bytearray: The encoded pointer data in little-endian format.
    """
    # Add first pointer for each cumulative lenth generating pointer exact size.
    pointersList = [ptr + firstPointer for ptr in listCumulativeLength]

    # Subtract the header size from each pointer in the list
    pointersList = [ptr - headerSize for ptr in pointersList]

    # Generate the separated bytes in little-endian order (LSB first, MSB second)
    separatedBytes = [
        (ptr & 0xFF) for ptr in pointersList
    ] + [
        ((ptr >> 8) & 0xFF) for ptr in pointersList 
    ]
    return bytearray(separatedBytes)

def calculatePointer3Bytes(listCumulativeLength, firstPointer, headerSize=None):
    """
    Calculates and returns the pointer data after adjusting each pointer with the header size
    and encoding 2 last bytes in little-endian format.

    Parameters:
        pointersList (list): A list of pointers to adjust and encode.
        headerSize (int): The header size to subtract from each pointer.

    Returns:
        bytearray: The encoded pointer data in big-endian format.
    """
    # Add first pointer for each cumulative lenth generating pointer exact size.
    pointersList = [ptr + firstPointer for ptr in listCumulativeLength]

    # Process each pointer
    pointersData = bytearray()
    for ptr in pointersList:
        bank = (ptr >> 16) & 0xFF
        last2Bytes = ptr & 0xFFFF
        invert = ((last2Bytes  >> 8) & 0xFF) | ((last2Bytes & 0xFF) << 8)
        # Append the bank byte and the two bytes little-endian
        pointersData.append(bank)
        pointersData.append((invert >> 8) & 0xFF)     # Least significant byte
        pointersData.append(invert & 0xFF)            # Most significan byte

    return pointersData
    
def calculatePointer4Bytes(listCumulativeLength, firstPointer, headerSize=None):
    """
    Calculates and returns the pointer data after adjusting each pointer with the header size
    and encoding them in big-endian format.

    Parameters:
        pointersList (list): A list of pointers to adjust and encode.
        headerSize (int): The header size to subtract from each pointer.

    Returns:
        bytearray: The encoded pointer data in big-endian format.
    """
    # Add first pointer for each cumulative lenth generating pointer exact size.
    pointersList = [ptr + firstPointer for ptr in listCumulativeLength]

    # Format
    for ptr in pointersList:
        ptr = ptr & 0xFFFFFFFF
    
    # Convert the list of pointers to bytearray (Big-endian encoding)
    pointersData = bytearray()
    for ptr in pointersList:
        pointersData.append((ptr >> 24) & 0xFF)     # Most significant byte
        pointersData.append((ptr >> 16) & 0xFF)     # Second byte
        pointersData.append((ptr >> 8) & 0xFF)      # Thirth byte
        pointersData.append(ptr & 0xFF)             # Least significant byte
    return pointersData

def writePointers(romFile, startOffset, data):
    """
    Writes data to the ROM at the specified offset.
    
    Parameters:
        romFile (str): The path to the ROM file.
        startOffset (int): The offset in the ROM file where data should be written.
        data (bytes or bytearray): The data to write to the ROM.
    """
    with open(romFile, "r+b") as f: 
        f.seek(startOffset)
        f.write(data)
        
def writeText(romFile, startOffset, maxSize, data):
    """
    Writes data to the ROM at the specified offset.
    
    Parameters:
        romFile (str): The path to the ROM file.
        startOffset (int): The offset in the ROM file where data should be written.
        data (bytes or bytearray): The data to write to the ROM.
    """
    # Check that the size of the data does not exceed the maximum allowed
    if len(data) > int(maxSize):
        excess = len(data) - int(maxSize)
        return False
    
    # Check free space
    freeSpace = int(maxSize) - len(data)

    # Fill free space
    filledData = data + b'\xFF' * freeSpace
        
    with open(romFile, "r+b") as f: 
        f.seek(startOffset)
        f.write(filledData)
        return True
