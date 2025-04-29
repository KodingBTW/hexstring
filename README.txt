------------------------------------------------------

Nombre:			HexString
Autor:			koda
Latest Version:  	1.3.0
URL:			https://traduccioneskoda.blogspot.com/
				https://github.com/KodingBTW/hexstring
Last Update:	28/04/2024

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
V1.3.0
- Graphical interface added

- Maintained legacy CLI (Watch cli_commands.txt)

- Tons of new options added

- Support 2 bytes, 3 bytes and 4 bytes pointers for
little and big endian.

- Now you can save and load .json configs

- You can select whether you want comments on lines.

- Added the use of custom brackets for raw hexadecimals.

- Option to fill the free space with a specific byte.
- Support for split pointers (LSB/MSB).

- Smart function that allows you to ignore any control
code at the beginning of a line that is equal to the
end-of-line code.

- Function that ignores the use of an end-of-line code
to count pointers. (It will split based on the length of
the pointer; to insert each line in the file, it will be
a pointer.)

- Added About tab

- Added Reset fields tab

- Optimized code

V1.2
- Now empty line before linebreaker are corrected
readed.

- You can replace linbreaker for text end offset
and the program will split text with the pointer
table.

- 4 bytes pointer are correctly interpreted.

V1.1.0

Bugs Fixed:
- If you split the text when editing, it was 
misinterpreted by the encoder as a new pointer. 
(Thanks to Wave).

- The text block counter function is now smarter. 
If two pointers point to the same text it will be 
counted only once.

New features:
- Added text comments, use ";" at begining of a new 
line. (it still can be used at character)

- line with @ or | will be ignore too

- Now more exceptions are handled, and an error 
text will be displayed giving more information.

- Characters not found in the .tbl file will now be 
printed in the following ~hex~ format. (The "~" symbol
is reserved, and will be ignored if used in the 
tbl).

-In the same way when encoding, if ~hex~ is found
it will be encoded with its corresponding hex form. 
If any character in the text is not assigned to the 
dictionary, it will be copied into its ASCCI format.

- Added support for pointers of other formats and 
lengths.
	2bytes little endian
	2bytes big endian
	2bytes splitted (lsb-msb)
	3bytes (gba format)
	4bytes (mega drive - big endian)

- Now when decoding the text, a comment will be 
automatically created that contains: the address of 
the line, a copy of the text, character length.

- Added previous pointer copy functionality, just 
deletes the line and adds the "&" character to the 
start of the line, then add his line breaker. The
pointer will be the same as the previous one, very 
useful if several pointers point to the same line.

V1.0.0
- Decoding ROM Data.
- Encoding binary files.
- Automatic updates pointers table (Only 2 bytes).
- Support .tbl dictionaries.
- Support for DTE/MTE enconding/decoding.
- Support Latin1 characters.

------------------------------------------------------
3 - HOW TO USE IT?
------------------------------------------------------
This program requires a certain level of romhacking 
skill.

Requeriments:
- Know how to create a thingy .tbl table
- Know how indentify pointers format
- Know how to find pointers
- Know how to edit sources and fonts
- Edition with some text editor (ex: Notepad++)
- A basic sense how a rom work.

To export script:

1.- Open ROM file and tbl file

2.- Select pointers format (lenght and endiannes)

3.- Fill all space in "Set Offsets"

*Pointers Base: Distance beetween text offset and 
the pointer (inverted if pointers are in little endian)

Ecuation
(Text Address for the pointer - pointer inverted)

Example: for Goof Troop (U).snes

ROMK Pointer format are 2 bytes little endian, so the
pointer is "81 E8", so you invert to $E881, 
the text address is "$05E881", so if you use the 
ecuation: $5E881 - $E881 = $50000

*End Line: Code used to split lines by pointers. 
It is possible to use multiple lines separated by ",". 
If it is not clear, I recommend using the advanced option 
"not use end lines"

4.- Press "Extract script and save", a window'll appear,
select output file and save

5.- Edit the file with you favorite text editor, I 
recomment use  Notepad++, always use UTF-8

NOTE: save config for easily insertion if you wanna
translate in multiple sesions.

To insert Script:

1.- Import Script in Select Files

2.- Refill all onformation or use open config in file
tab

3.- Press insert Script to ROM


------------------------------------------------------
4 - CLI (LEGACY)
------------------------------------------------------

Use console.exe for cli commands if you dont want use
interface. Check cli_commands.txt for all commands


------------------------------------------------------
5 - TO DO:
------------------------------------------------------

- Possibly add new algorithms for compressed text