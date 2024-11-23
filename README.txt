------------------------------------------------------

Nombre:   		HexString
Autor:     		koda
Latest Version:  	1.0
URL:			https://traduccioneskoda.blogspot.com/
Last Update:    23/11/2024

------------------------------------------------------
1 - WHAT'S THIS?
------------------------------------------------------

HexString allows you to dump the text of a ROM, then 
reinsert it in order to modify and translate it into 
other languages. By providing the correct parameters, 
this program will also modify the pointer table. This 
automates the entire process, and you only need to 
focus on translating.

------------------------------------------------------
2 - WHAT'S NEW
------------------------------------------------------

V1.0
- Decoding ROM Data.
- Encoding binary files.
- Automatic updates pointers table (Only 2 bytes).
- Support .tbl dictionaries.
- Support for DTE/MTE enconding/decoding.
- Support Latin1 characters.

------------------------------------------------------
3 - HOW TO USE IT?
------------------------------------------------------

To decode:

Use the Windows console and type -d, then fill in the 
arguments:

- romFile: ROM file name.

- pointersStartAddress: Address where the pointer table 
begins.

- pointerTableSize: Size of the pointers, in hexadecimal.

- headerSize: The size of the header (Formula: take the 
first pointer in the table, reverse it, and subtract 
the address where the text begins) in hexadecimal.

- lineBreaker: Code used in the ROM to break the text 
strings, e.g., 0x00 or 0xFF. (If there is more than 
one, separate with commas).
- outFile: Output file, it can be a .bin or .txt file.

- tblFile: (optional) If provided, it decodes using a 
.tbl file; otherwise, it uses ASCII.
Para codificar:

Then edit the output file with your favorite text editor
(I recommend Notepad++).


To encode:

Use the Windows console and type -e, then fill in the 
arguments:

- textFile: File with the text.

- textStartAddress: Address where the text block begins.

- textSize: Size of the text block, in hexadecimal.

- pointersStartAddress: Address where the pointer table 
begins.

- headerSize: The size of the header (Formula: take the
first pointer in the table, reverse it, and subtract the 
address where the text begins) in hexadecimal.

- romFile: ROM file name.

- tblFile: (optional) If provided, it decodes using a .tbl
file; otherwise, it uses ASCII.

Tips:

-To avoid typing the arguments repeatedly, I recommend 
creating a .bat file for quicker operation.

-Before you begin, it's recommended to make a copy of the
 ROM and back up any progress you have.
 
-You can dump the text and then reinsert it. Use a 
hexadecimal comparator to check for discrepancies.

-If you notice that the text size exceeds the available 
space in the text block when reinserting, you can search 
for empty space in the ROM or simply increase the ROM size.


------------------------------------------------------
4 - TO DO:
------------------------------------------------------

- I assume at some point I’ll add support for 3-byte 
 pointers.

- A graphical interface—unlikely, as it requires a 
lot of work, which I don't have time for right now.