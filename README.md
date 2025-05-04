# HexString
HexString is a text dumper that lets you extract text from a ROM using a simple and friendly user interface, which you can then edit with your favorite text editor. It also allows for automatic pointer computation, making translation to ROM faster and easier. It supports compression of pointers of different lengths and formats, as well as compression using DTE/MTE.

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
1. Open ROM file and tbl file
2. Select pointers format (lenght and endiannes)
3. Fill all spaces in "Set Offsets"
4. Press "Extract script and save", a window will appear,
select output file and save
5. Edit the file with you favorite text editor, I 
recomment use  Notepad++, always use UTF-8

To insert Script:
1. Import Script in Select Files
2. Refill all spaces or use open config in file
tab
3. Press insert Script to ROM

More information in README.txt

## Console 
HexString allows the use of console commands for script creation using the included "console.exe"
```
console.exe [extract | insert] inFileName outFileName
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
		2bb 		2 bytes big endian
		3b		3 bytes little endian
		3bb		3 bytes big endian
		4b		4 bytes little endian
		4bb		4 bytes big endian
```
See cli_commands.txt for detailed commands.
Note: Command lines don't handle to much exception, try to avoid using correct commands.

## Frecuency Answer Questions

### 1.- Can I use this tool in my personal project?

Of course, there's no need to ask. Feel free to use it in your project. I only ask that you mention me as contributor.

### 2.- I found a error, can you fix it?

Yes, but give me some time. In fact, you can make a pull request if you manage to fix any error or add any new functionality.

### 3.- Could you add new functionalities? I need it to work in this specific way.

Absolutely not. If you need something specific, you'll have to do it on your own. Feel free to work with my code however you like, as long as you mention me, it's no problem.
