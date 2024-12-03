def readRom(romFile, startAddress, tableSize):
    """
    Reads a segment of the ROM file from startOffset to endOffset.
    
    Parameters:
        romFile (str): The path to the ROM file.
        startOffset (int): The starting position in the file to read from.
        tableSize (int): Table pointer Size.
    
    Returns:
        bytes: The data read from the ROM file.
    """
    with open(romFile, "rb") as f:
        f.seek(startAddress)
        data = f.read(tableSize)
    return data

def readTbl(tblFile):
    """
    Reads a .tbl file to create a character mapping table (supports DTE/MTE).
    
    Parameters:
        tblFile (str): The path to the .tbl file.
    
    Returns:
        dict: A dictionary where the keys are byte values (int) and the values are strings (characters or sequences).
    """
    charTable = {}   
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
                    charTable[hexValue] = chars 
                except ValueError:
                    continue
    return charTable

def processPointers2Bytes(data, header):
    """
    Processes the pointer data by converting it to pairs and transforming it to big-endian,
    then adding the header offset.
    
    Parameters:
        data (bytes): The raw pointer data read from the ROM.
        header (int): The offset to add to each pointer.
    
    Returns:
        list: A list of processed pointers as integers.
    """
    result = []
    for i in range(0, len(data), 2):
        # Read two bytes as a pair and convert to big-endian
        pair = data[i:i + 2][::-1]  
        # Convert the pair to an integer
        value = int.from_bytes(pair, byteorder='big') + header
        result.append(value)
    return result

def processPointers2BytesBigEndian(data, header):
    """
    Processes the pointer data by converting it to pairs,
    then adding the header offset.
    
    Parameters:
        data (bytes): The raw pointer data read from the ROM.
        header (int): The offset to add to each pointer.
    
    Returns:
        list: A list of processed pointers as integers.
    """
    result = []
    for i in range(0, len(data), 2):
        # Read two bytes as a pair and convert to big-endian
        pair = data[i:i + 2]
        # Convert the pair to an integer
        value = int.from_bytes(pair, byteorder='big') + header
        result.append(value)
    return result

def processPointers2BytesSeparated(data, header):
    """
    Processes the pointer data by converting it to pairs and transforming it to big-endian,
    then adding the header offset.
    
    Parameters:
        data (bytes): The raw pointer data read from the ROM.
        header (int): The offset to add to each pointer.
    
    Returns:
        list: A list of processed pointers as integers.
    """
    result = []
    half = len(data) // 2
    for i in range(half):
        # reorder list
        firstByte = data[i]
        secondByte = data[i + half]
        # Read two bytes as a pair and convert to big-endian
        pair = [firstByte, secondByte][::-1]  
        # Convert the pair to an integer
        value = int.from_bytes(pair, byteorder='big') + header
        result.append(value)
    return result


def processPointers3Bytes(data, header):
    """
    Processes the pointer data by converting it to triplets of 3 bytes, 
    then reversing the last two bytes, and transforming to big-endian,
    and adding the header offset.
    
    Parameters:
        data (bytes): The raw pointer data read from the ROM.
        header (int): The offset to add to each pointer.
    
    Returns:
        list: A list of processed pointers as integers.
    """
    result = []
    for i in range(0, len(data), 3):
        # Read three bytes as a triplet
        triplet = data[i:i + 3]
        
        # Get last two byte of the triplet and convert to big-endian
        get2Bytes = triplet[1:][::-1]
        
        # Convert the final triplet to an integer
        value = int.from_bytes(get2Bytes, byteorder='big') + header
        result.append(value)    
    return result

def processPointers4Bytes(data, header):
    """
    Processes the pointer data by converting it to pairs and transforming it to big-endian,
    then adding the header offset.
    
    Parameters:
        data (bytes): The raw pointer data read from the ROM.
        header (int): The offset to add to each pointer.
    
    Returns:
        list: A list of processed pointers as integers.
    """
    result = []
    for i in range(0, len(data), 4):
        # Read four bytes as a quartet
        quartet = data[i:i + 4]
        
        # Get last two byte of the quartet
        get2Bytes = quartet[2:]
        
        # Convert the final triplet to an integer
        value = int.from_bytes(get2Bytes, byteorder='big') + header
        result.append(value)
    return result

def extractTexts(romData, addressesList, lineBreakers, charTable):
    """
    Extracts texts from the ROM data at specified addresses until a line breaker is encountered.
    
    Parameters:
        romData (bytes): The complete ROM data.
        addressesList (list): A list of addresses to read the texts from.
        lineBreakers (set): A set of byte values used as line breakers.
        charTable (dict): A dictionary mapping byte values to characters or sequences.
    
    Returns:
        tuple: Containing:
            - texts (list): Script text.
            - totalBytesRead (int): Total text block size.
            - linesLength (int): Lenght of each line.
    
        tuple: A list of extracted texts, the total bytes read, and the lengths of each extracted line in bytes.
    """
    texts = []  
    linesLength = []
    bytesLineCounter = 0
    total= 0

    # Loop over each starting address in the list
    for addr in addressesList:
        text = bytearray()
        
        while True:
            byte = romData[addr]  
            bytesLineCounter += 1

            # If the byte is a line-breaker, stop extracting
            if byte in lineBreakers:
                breakerByte = byte
                break

            # Map the byte using charTable to get the character
            char = charTable.get(byte, None)  
            if char:
                # If single character
                if len(char) == 1:
                    text.append(ord(char))
                # If multiple characters (DTE/MTE)
                else:  
                    for c in char:
                        text.append(ord(c))
            # If byte is not in charTable, print in format ~hex~
            else:
                hexValue = format(byte, '02X')
                text.extend(f"~{hexValue}~".encode('UTF-8'))
            addr += 1
            
        # Add the breaker byte to the text
        if breakerByte is not None:
            char = charTable.get(breakerByte, None)
            if char:
                # if assigned to a single character
                if len(char) == 1:
                    text.append(ord(char))
                # if assigned to a chain characters
                else:
                    for c in char:
                        text.append(ord(c))
            else:
                # If the breaker byte doesn't have a mapping,  print in format ~hex~
                hexValue = format(breakerByte, '02X')
                text.extend(f"~{hexValue}~".encode('UTF-8'))
                            
        # Convert byte array to string
        decodeText = text.decode('iso-8859-1', errors='replace')

        # Append the decoded text to the list
        texts.append(decodeText)
        linesLength.append(bytesLineCounter)
        total = total + bytesLineCounter
        bytesLineCounter = 0

    # Calculate total bytes read 
    totalBytesRead = abs((addressesList[-1] + linesLength[-1]) - addressesList[0])

    return texts, totalBytesRead, linesLength

def parseLineBreakers(string):
    """
    Parse a string of comma-separated hexadecimal values into a set of integers.
    
    Parameters:
        string (str): A string containing hexadecimal values separated by commas.
    
    Returns:
        lineBreakers: A set of integer values representing the line breakers.
    """
    lineBreakers = set()
    for byte in string.split(','):
        byte = byte.strip() 
        lineBreakers.add(int(byte, 16))
        
    return lineBreakers

def formatHexString(hexString):
    """
    Takes a string of hex values separated by commas
    and returns a string separated by ~.
    
    Parameters:
        hexString (str): A comma-separated string of hex values.
    
    Returns:
        str: The formatted string.
    """
    # Eliminar los prefijos '0x' y los espacios
    hexValues = hexString.split(',')
    
    # Formatear cada valor eliminando '0x' y envolviéndolos en '~'
    formattedValues = [f"-{val.strip()[2:].zfill(2).upper()}" for val in hexValues]
    
    # Unir los valores con el delimitador vacío
    formattedString = ''.join(formattedValues)
    
    return formattedString

def writeOutFile(file, scriptText, pointersStartAddress, pointerTableSize, addressList, linesLenght, lineBreaker):
    """
    Writes data to a file, formatting each line with a semicolon and newline.
    
    Parameters:
        file (str): The path to the output file.
        scriptText (list): A list of strings representing the script content to write to the file.
        pointersStartAddress (int): The starting address of the pointer table.
        pointerTableSize (int): The size of the pointer table).
        addressList (list): A list of addresses corresponding to each line in the script.
        linesLenght (list): A list of the length of each line in the script.
        lineBreaker (int): A value used to split lines.
    """     
    with open(file, "w", encoding='UTF-8') as f:
        formattedString = formatHexString(lineBreaker)
        f.write(f";{{{pointersStartAddress:08X}-{(pointersStartAddress + pointerTableSize - 1):08X}-{pointerTableSize:08X}}}{formattedString}\n")
        i = 0
        for line in scriptText:
            # Format the address as uppercase hex with leading zeros (8 digits wide)
            addressStr = f"{addressList[i]:08X}"
            # Write the formatted address followed by the line content and length
            f.write(f"@{i+1}\n")
            f.write(f";{addressStr}{{{line}}}#{len(line)}#{linesLenght[i]}\n")
            f.write(f"{line}\n")
            f.write("|\n")
            i += 1
