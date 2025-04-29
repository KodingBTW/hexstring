# HexString
HexString is a text dumper that creates a binary file which you can edit with your favorite text editor. It also allows automatic pointer calculation, making it much easier and faster to translate a ROM. It supports compression different pointers lenght and formats, also support compression via DTE/MTE.

## Requirements
To compile you can use pyinstaller library. 

```
pip install pyinstaller
```
## Build
```
git clone https://github.com/KodingBTW/hexstring

cd hexstring

pip install -r requirements.txt

cd src

build.bat
```
## Interface
![image](https://github.com/user-attachments/assets/5733b562-6103-4d32-8df7-a58b505d75aa)

To export script:
1.- Open ROM file and tbl file
2.- Select pointers format (lenght and endiannes)
3.- Fill all space in "Set Offsets"
4.- Press "Extract script and save", a window'll appear,
select output file and save
5.- Edit the file with you favorite text editor, I 
recomment use  Notepad++, always use UTF-8

To insert Script:
1.- Import Script in Select Files
2.- Refill all onformation or use open config in file
tab
3.- Press insert Script to ROM

## Console 
```
HexString [-d | -e] inFileName outFileName
```

Description:

```
For extraction:

console.exe extract --rom <romFile> --p <pointersFormat> --pointers-offset <pointersStartOffset> --pointers-size <tablePointersSize> --base <base> --end-line <end_lines> --out <outFile> --tbl <tblFile> [Advanced Options]

For insert:

console.exe insert --file <inputFile> --p <pointersFormat> --text-offset <textStartOffset> --text-size <textSize> --pointers-offset <pointersStartOffset> --base <base> --rom <romName> --tbl <tblFile> [Advanced Options]

-h - Display help

-v - Output version information
```
List of pointer format supported:
```
		2b 		2 bytes little endian
		2bb 	2 bytes big endian
		3b		3 bytes little endian
		3bb		3 bytes big endian
		4b		4 bytes little endian
		4bb		4 bytes big endian
```
Watch cli_commands.txt for detailed commands.
Command lines don't handle to much exception, try to avoid using correct commands.
## Frecuency Answer Questions

### 1.- Can I use this tool in my personal project?

Of course, there's no need to ask. Feel free to use it in your project. I only ask that you mention me as contributor.

### 2.- I found a error, can you fix it?

Yes, but give me some time. In fact, you can make a pull request if you manage to fix any error or add any new functionality.

### 3.- Could you add new functionalities? I need it to work in this specific way.

Absolutely not, I don't plan on doing much more than what's already included. If you need something specific, you'll have to do it on your own. Feel free to work with my code however you like, as long as you mention me, it's no problem.
