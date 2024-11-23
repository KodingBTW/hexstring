import sys

def readScriptFile(file):
    """
    Reads a file with a game's text (can be .txt or .bin file).
    
    Parameters:
        file (str): The path to the file to read.
    
    Returns:
        list: A list of strings, each representing a line of text from the file.
    """
    with open(file, "r", encoding='iso-8859-1', errors="replace") as f:
        textData = [line.rstrip() for line in f.readlines()]
    return textData

def readTblFileInverted(tblFile):
    """
    Reads a .tbl file to create a character mapping table.
    
    Parameters:
        tblFile (str): The path to the .tbl file.
    
    Returns:
        dict: A dictionary where the keys are strings (characters or sequences) and the values are byte values (int).                        
    """
    charTable = {}
    
    with open(tblFile, "r", encoding="ISO-8859-1", errors="replace") as f:
        for line in f:
            if line.startswith("/"):
                continue
            if "=" in line:
                hexValue, chars = line.split("=",1)
                try:
                    hexValue = int(hexValue, 16)
                    chars = chars.rstrip("\n")
                    charTable[chars] = hexValue 
                except ValueError:
                    continue      
    return charTable

def encodeText(texts, address, charTable = None):
    """
    Encodes the texts into bytes (Support DTE/MTE enconding)
    
    Parameters:
        texts (list): A list of strings to encode.
        address (int): The starting offset for the text in the ROM.
        charTable (dict): A dictionary mapping characters or sequences values to bytes. 
        
    Returns:
        tuple: A tuple containing:
            - bytearray: The encoded text data.
            - pointets: Pointers list.
    """
    encodedData = bytearray()
    totalBytes = 0  
    pointers = [address]  
    
    for line in texts:
        # If charTable is provided, use it to encode the text (DTE/MTE algorithm).
        if charTable:
            i = 0
            while i < len(line):
                # Try to match the longest possible sequence from the current position
                for length in range(min(3, len(line) - i), 0, -1): 
                    seq = line[i:i+length]  
                    if seq in charTable:  
                        encodedData.append(charTable[seq]) 
                        totalBytes += 1 
                        i += length  
                        break
                else:
                    # If no sequence matched, encode the single character normally (ASCII)
                    encodedData.append(ord(line[i]))
                    totalBytes += 1 
                    i += 1  
        else:       
            # If not tbl provided use ASCII encoding 
            encodedData.extend(line.encode('iso-8859-1', errors='replace'))
            
            # Update the byte counter
            totalBytes += len(line.encode('iso-8859-1', errors='replace'))

        # Add next pointer
        pointers.append(address + totalBytes)
        
    # Remove the innecesary extra pointer
    pointers.pop()
    return encodedData, pointers

def calculatePointers(pointersList, headerSize):
    """
    Calculates and returns the pointer data after adjusting each pointer with the header size
    and encoding them in little-endian format.

    Parameters:
        pointersList (list): A list of pointers to adjust and encode.
        headerSize (int): The header size to subtract from each pointer.

    Returns:
        bytearray: The encoded pointer data in little-endian format.
    """
    # Subtract the header size from each pointer in the list
    pointersList = [ptr - headerSize for ptr in pointersList]

    # Reverse bytes (Little-endian encoding)
    pointersList = [((ptr >> 8) & 0xFF) | ((ptr & 0xFF) << 8) for ptr in pointersList]  

    # Convert the list of pointers to bytearray
    pointersData = bytearray()
    for ptr in pointersList:
        pointersData.append((ptr >> 8) & 0xFF)  # Most significant byte
        pointersData.append(ptr & 0xFF)         # Least significant byte
    return pointersData

def writeROM(romFile, startOffset, data):
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
