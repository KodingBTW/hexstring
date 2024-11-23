import sys
import os

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
    
    with open(tblFile, "r", encoding="ISO-8859-1", errors="ignore") as f:
        for line in f:
            if line.startswith("/"):
                continue  
            if "=" in line:
                hexValue, chars = line.split("=",1)
                try:
                    hexValue = int(hexValue, 16)
                    chars = chars.rstrip("\n")
                    charTable[hexValue] = chars 
                except ValueError:
                    continue      
    return charTable

def processPointers(data, header):
    """
    Processes the pointer data by reversing byte pairs and adding a specified header.
    
    Parameters:
        data (bytes): The raw pointer data read from the ROM.
        header (int): The offset to add to each pointer.
    
    Returns:
        list: A list of processed pointers as integers.
    """
    result = []
    for i in range(0, len(data), 2):
        # Read two bytes as a pair and reverse the order (big-endian)
        pair = data[i:i + 2][::-1]  
        # Convert the reversed pair to an integer
        value = int.from_bytes(pair, byteorder='big') + header
        result.append(value)
    return result

def extractTexts(romData, addressesList, lineBreakers, charTable=None):
    """
    Extracts texts from the ROM data at specified addresses until a line breaker is encountered.
    
    Parameters:
        romData (bytes): The complete ROM data.
        addresses (list): A list of addresses to read the texts from.
        lineBreakers (set): A set of byte values used as line breakers.
        charTable (dict): A dictionary mapping byte values to characters or sequences.
    
    Returns:
        tuple: A list of extracted texts and the total bytes read.
    """
    texts = []
    totalBytesRead = 0
    for addr in addressesList:
        text = bytearray()
        while True:
            byte = romData[addr]
            totalBytesRead += 1  
            if byte in lineBreakers:
                breakerByte = byte
                break
            
            # If tbl file is provided, map the byte using the table
            if charTable:
                char = charTable.get(byte, chr(byte))
                if char:
                    # If single character
                    if len(char) == 1:
                        text.append(ord(char))
                    # If multiple characters (DTE/MTE)    
                    else:  
                        for c in char:
                            text.append(ord(c))  
            # If Tbl file is not provided, map using ASCII
            else:
                char = chr(byte)  
                text.append(ord(char))  

            addr += 1  

        # Add the breaker byte to the text
        if breakerByte is not None:
            text.append(breakerByte)  
        texts.append(text.decode('ISO-8859-1', errors='ignore'))

    return texts, totalBytesRead

def parseLineBreakers(string):
    """
    Parse a string of comma-separated hexadecimal values into a set of integers.
    
    Parameters:
        string (str): A string containing hexadecimal values separated by commas (e.g. '0x04,0x05').
    
    Returns:
        lineBreakers: A set of integer values representing the line breakers.
    """
    lineBreakers = set()
    for byte in string.split(','):
        byte = byte.strip() 
        if byte.startswith('0x'):  
            lineBreakers.add(int(byte, 16))
        else:
            try:
                lineBreakers.add(int(byte)) 
            except ValueError:
                continue  
    return lineBreakers

def writeOutFile(file, scriptText):
    with open(file, "w", encoding='ISO-8859-1') as f:
        for line in scriptText:
            f.write(f"{line}\n")

