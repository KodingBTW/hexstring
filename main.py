## HexString
## Source code by koda
## release 03/01/2025 --version 1.2 (no space)

import sys
import os
import decoder as de
import encoder as en

def showHelp():
    sys.stdout.write("Usage: -d <pointersFormat> <romFile> <PointersStartAddress> <PointerTableSize> <HeaderSize> <LineBreaker> <outFile> <tblFile>\n")
    sys.stdout.write("       -e <pointersFormat> <TextFile> <TextStartAddress> <TextSize> <PointersStartAddress> <HeaderSize> <romFile> <tblFile>\n")
    sys.stdout.write("       -h show help.\n")
    sys.stdout.write("       -v show version.\n")

def main():
    if len(sys.argv) == 1 or len(sys.argv) == 9:
        showHelp()
        sys.exit(1)
    # Decoding arguments
    if sys.argv[1] == '-d':
        # Pointers Format
        if sys.argv[2] == '-2b':
            pointersFormat = de.processPointers2Bytes
        elif sys.argv[2] == '-2bs':
            pointersFormat = de.processPointers2BytesSeparated
        elif sys.argv[2] == '-2bb':
            pointersFormat = de.processPointers2BytesBigEndian
        elif sys.argv[2] == '-3b':
            pointersFormat = de.processPointers3Bytes
        elif sys.argv[2] == '-4b':
            pointersFormat = de.processPointers4Bytes
        else:
            sys.stdout.write("Error: Pointers format argument not found.")
            sys.exit(1) 

        # Other Arguments
        romFile = sys.argv[3]                                       # ROM file path
        try:
            pointersStartAddress = int(sys.argv[4], 16)             # Start offset of pointer table
        except ValueError:
            print("Error: Incorrect hex value.")
            sys.exit(1)
        try:
            pointerTableSize = int(sys.argv[5], 16)                 # Pointer table size
        except ValueError:
            print("Error: Incorrect hex value.")
            sys.exit(1)
        try:
            headerSize = int(sys.argv[6], 16)                       # Header size
        except ValueError:
            print("Error: Incorrect hex value.")
            sys.exit(1)
        lineBreaker = sys.argv[7]                                   # Line breaker input
        outFile = sys.argv[8]                                       # Output file for the extracted text
        tblFile = sys.argv[9]                                       # Tbl file argument

        # Read ROM pointers table
        try:
            tablePointers = de.readRom(romFile, pointersStartAddress, pointerTableSize)
        except FileNotFoundError:
            print(f"Error: File {romFile} not found in directory.")
            sys.exit(1)

        # Parse line breakers.
        try:
            parseLineBreakers, isOffset = de.parseLineBreakers(lineBreaker)
        except ValueError:
            print("Error: Incorrect hex value.")
            sys.exit(1)
        
        # Process read pointers
        lineStartAddress = pointersFormat(tablePointers, headerSize)
        
        # Read the complete ROM data to extract texts
        romData = de.readRom(romFile, 0, os.path.getsize(romFile))

        # Load the character table
        try:
            charTable = de.readTbl(tblFile)
        except FileNotFoundError:
            print(f"Error: File {tblFile} not found in directory.")
            sys.exit(1)
        except UnicodeDecodeError:
            print(f"Error: File {tblFile} is not in UTF-8.")
            
        # Extract the texts
        try:
            if not isOffset:
                texts, totalBytesRead, linesLenght = de.extractTexts(romData, lineStartAddress, parseLineBreakers, charTable)
            else:
                texts, totalBytesRead, linesLenght = de.extractTextsNoLineBreakers(romData, lineStartAddress, parseLineBreakers, charTable)
        except IndexError:
            print(f"Error: Start address is bigger than the ROM size.")
            sys.exit(1)
            
        # Writing the text to a file
        de.writeOutFile(outFile, texts, pointersStartAddress, pointerTableSize, lineStartAddress, linesLenght, lineBreaker)
        print(f"TEXT BLOCK SIZE: {totalBytesRead} / {hex(totalBytesRead)} bytes.")
        print(f"Text extracted to {outFile}")
        print("Decoding complete.\n")
        sys.exit(1)
    
    elif sys.argv[1] == '-e':
        # Pointers Format
        if sys.argv[2] == '-2b':
            pointersFormat = en.calculatePointer2Bytes
        elif sys.argv[2] == '-2bs':
            pointersFormat = en.calculatePointer2BytesSeparated
        elif sys.argv[2] == '-2bb':
            pointersFormat = en.calculatePointer2BytesBigEndian
        elif sys.argv[2] == '-3b':
            pointersFormat = en.calculatePointer3Bytes
        elif sys.argv[2] == '-4b':
            pointersFormat = en.calculatePointer4Bytes
        else:
            sys.stdout.write("Error: Pointers format argument not found.")
            sys.exit(1)
            
        # Encoding arguments
        scriptFile = sys.argv[3]                                    # Input file with Script
        try:
            textStartAddress = int(sys.argv[4], 16)                 # Start offset of text script
        except ValueError:
            print("Error: Incorrect hex value.")
            sys.exit(1)
        try:
            textSize = int(sys.argv[5], 16)                         # Text length size
        except ValueError:
            print("Error: Incorrect hex value.")
            sys.exit(1)
        try:
            pointersStartAddress = int(sys.argv[6], 16)             # Start offset of pointer table
        except ValueError:
            print("Error: Incorrect hex value.")
            sys.exit(1)
        try:
            headerSize = int(sys.argv[7], 16)                       # Header size
        except ValueError:
            print("Error: Incorrect hex value.")
            sys.exit(1)
        romFile = sys.argv[8]                                       # ROM file path
        tblFile = sys.argv[9]                                       # Tbl file argument
    
        # Read the text file
        try:
            textScript, copyPointersStartAddress, pointersEndAddress, pointerTableSize, lineBreaker = en.readScriptFile(scriptFile)
        except FileNotFoundError:
            print(f"Error: File {scriptFile} not found in directory.")
            sys.exit(1)
        except AttributeError:
            print(f"Error: First line attributes not found in {scriptFile}.")
            sys.exit(1)
            
        # Parse line breakers.
        parseLineBreakers = de.parseLineBreakers(lineBreaker)
        
        # Load the character table if provided
        try:
            charTable, longestChar = en.readTblFileInverted(tblFile)
        except FileNotFoundError:
            print(f"Error: File {tblFile} not found in directory.")
            sys.exit(1)
        except UnicodeDecodeError:
            print(f"Error: File {tblFile} is not in UTF-8.")
            
        # Encode the text
        encodedText, pointersList = en.encodeText(textScript, parseLineBreakers, charTable, longestChar)
        
        # Format pointers
        encodedPointers = pointersFormat(pointersList, textStartAddress, headerSize)
        
        # Write the text to the ROM
        try:
            if en.writeText(romFile, textStartAddress, textSize, encodedText):
                # Write the pointers to the ROM
                en.writePointers(romFile, pointersStartAddress, encodedPointers)
                freeSpace = int(textSize) - len(encodedText)
                print(f"Text written at offset {hex(textStartAddress)}.")
                print(f"Pointers table written at offset {hex(pointersStartAddress)} with {len(pointersList)} pointers.")
                print(f"Free space: {freeSpace} bytes.")
                print(f"Data written to {romFile}")
                print("Encoding complete.\n")
                sys.exit(1)

            else:
                excess = len(encodedText) - int(textSize)
                sys.stdout.write("Error: The number of bytes read exceeds the maximum block limit.\n")
                sys.stdout.write(f"Remove {excess} bytes from {scriptFile} file.\n") 
                sys.exit(1)
                
        except FileNotFoundError:
            print(f"Error: File {romFile} not found in directory.")
            sys.exit(1)

    elif sys.argv[1] == '-h':
        print("\nUsage: HexString [-d|e] [input_file output_file]")
        print(" -d  --decode   decode from ROM")
        print(" -e  --encode   encode from raw binary text")
        print(" -h  --help     show help")
        print(" -v  --version  show version number\n")
        print(" ****** Pointers Format ****** \n")
        print(" -2b   --2bytes little endian")
        print(" -2bb  --2bytes big endian")
        print(" -2bs  --2bytes splitted lsb-msb")
        print(" -3b   --3bytes (bank/2bytespointer)")
        print(" -4b   --4bytes")
        sys.exit(1)
        
    elif sys.argv[1] == '-v':
        sys.stdout.write("\nHexSring created by koda, version 1.2")
        sys.exit(1)

    else:
        showHelp()
        sys.exit(1)

if __name__ == '__main__':
    main()
