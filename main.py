## HexString
## Source code by koda
## release 23/11/2024 --version 1.0

import sys
import os
import decoder as de
import encoder as en

def main():
    
    if len(sys.argv) not in [8, 9]:
        sys.stdout.write("Usage: -d <romFile> <PointersStartAddress> <PointerTableSize> <HeaderSize> <LineBreaker> <outFile> [tblFile]\n")
        sys.stdout.write("       -e <TextFile> <TextStartAddress> <TextSize> <PointersStartAddress> <HeaderSize> <romFile> [tblFile]\n")
        sys.stdout.write("       -h show help.\n")
        sys.stdout.write("       -v show version.\n")
        sys.exit(1)

    if sys.argv[1] == '-d':
        
        # Decoding arg.
        romFile = sys.argv[2]                                   # ROM file path
        pointersStartAddress = int(sys.argv[3], 16)             # Start offset of pointer table
        pointerTableSize = int(sys.argv[4], 16)                 # Pointer table size
        headerSize = int(sys.argv[5], 16)                       # Header size
        lineBreaker = de.parseLineBreakers(sys.argv[6])         # Parse the line breaker input (comma-separated)
        outFile = sys.argv[7]                                   # Output file for the extracted text
        tblFile = sys.argv[8] if len(sys.argv) == 9 else None   # Optional .tbl file argument

        # Read ROM pointers table
        tablePointers = de.readRom(romFile, pointersStartAddress, pointerTableSize)

        # Process read pointers
        pointersList = de.processPointers(tablePointers, headerSize)

        # Read the complete ROM data to extract texts
        romData = de.readRom(romFile, 0, os.path.getsize(romFile))

        # Load the character table if provided
        charTable = None
        if tblFile:
            print("Decoding with TBL")
            charTable = de.readTbl(tblFile)
            
        # Extract the texts
        texts, totalBytesRead = de.extractTexts(romData, pointersList, lineBreaker, charTable)

         # Writing the text to a file
        de.writeOutFile(outFile, texts)
        print(f"TEXT BLOCK SIZE: {totalBytesRead} bytes.")
        print(f"Text extracted to {outFile}")
        print("Decoding complete.\n")
        sys.exit(1)
    
    elif sys.argv[1] == '-e':
        
        # Encoding arg.
        scriptFile = sys.argv[2]                                # Input file with Script
        textStartAddress = int(sys.argv[3], 16)                 # Start offset of text script
        textSize = int(sys.argv[4], 16)                         # Text length size
        pointersStartAddress = int(sys.argv[5], 16)             # Start offset of pointer table
        headerSize = int(sys.argv[6], 16)                       # Header size
        romFile = sys.argv[7]                                   # ROM file path
        tblFile = sys.argv[8] if len(sys.argv) == 9 else None   # Optional .tbl file argument

        # Read the text file
        textScript = en.readScriptFile(scriptFile)

        # Load the character table if provided
        charTable = None
        if tblFile:
            print("Encoding with TBL")
            charTable = en.readTblFileInverted(tblFile)

        # Encode the text
        encodedText, pointersList = en.encodeText(textScript, textStartAddress, charTable)

        # Format pointers
        encodedPointers = en.calculatePointers(pointersList, headerSize)

        # Check that the size of the data does not exceed the maximum allowed
        if len(encodedText) > int(textSize):
            excess = len(encodedText) - int(textSize)
            sys.stdout.write("ERROR: The number of bytes read exceeds the maximum block limit.\n")
            sys.stdout.write(f"Remove {excess} bytes from {scriptFile} file.\n") 
            sys.exit(1)

        # Check free bytes
        freeBytes = int(textSize) - len(encodedText)
            
        # Write the text to the ROM
        en.writeROM(romFile, textStartAddress, encodedText)

        # Write the pointers to the ROM
        en.writeROM(romFile, pointersStartAddress, encodedPointers)

        print(f"Text written at offset {hex(textStartAddress)}.")
        print(f"Pointers table written at offset {hex(pointersStartAddress)} with {len(pointersList)} pointers.")
        print(f"FREE SPACE: {freeBytes} bytes.")
        print(f"Data written to {romFile}")
        print("Encoding complete.\n")
        sys.exit(1)

    elif sys.argv[1] == '-h':
        print("\nUsage: HexString [-d|e] [input_file output_file]")
        print(" -d  --decode   decode from ROM")
        print(" -e  --encode   encode from raw binary text")
        print(" -h  --help     show help")
        print(" -v  --version  show version number")

    elif sys.argv[1] == '-v':
        print("\nHexSring created by koda, version 1.0")

    else:
        sys.stdout.write("Usage: -d <romFile> <PointersStartAddress> <PointerTableSize> <HeaderSize> <LineBreaker> <outFile> [tblFile]\n")
        sys.stdout.write("       -e <TextFile> <TextStartAddress> <TextSize> <PointersStartAddress> <HeaderSize> <romFile> [tblFile]\n")
        sys.stdout.write("       -h show help.\n")
        sys.stdout.write("       -v show version.\n")
        sys.exit(1)

if __name__ == '__main__':
    main()
