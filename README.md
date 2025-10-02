# HexString
HexString is a text extractor that allows you to easily extract and insert text from a ROM, greatly facilitating translation (or text editing for romhacks). It has a simple and user-friendly interface, where you can edit the extracted text with your favorite text editor. In addition, it performs automatic pointer calculations to speed up reinsertion into the ROM. It supports pointers of different sizes (2, 3, and 4 bytes) and formats (little or big endian), as well as compression using DTE/MTE, and even pointers divided into parts.

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
<img width="476" height="905" alt="hexstring" src="https://github.com/user-attachments/assets/6d63ad6a-27e3-4a6b-8d2e-df3f32b5cd42" />


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
console.exe [extract | insert | extractconfig | insertconfig] commands
```

Description:

```
CLI Commands

For extraction:

console.exe extract --rom <romFile> --file <outputFile> --tbl <tblFile> --p <pointersFormat> --pointers-offset <pointersStartOffset> --pointers-size <tablePointersSize> --base <base> --end-line <end_lines> [Advanced Options]

For insert:

console.exe insert --rom <romFile> --file <inputFile>  --tbl <tblFile> --p <pointersFormat> --text-offset <textStartOffset> --text-size <textSize> --pointers-offset <pointersStartOffset> --base <base> [Advanced Options]

extractconfig <config path>

insertconfig <config path>

-h - Display help

-v - Show build version
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
See cli_commands.txt for detailed commands.
Note: Command lines don't handle to much exception, try to avoid incorrect entries.

## Frecuency Answer Questions

### 1.- Can I use this tool in my personal project?

Of course, there's no need to ask. Feel free to use it in your project. I only ask that you mention me as contributor.

### 2.- I found a error, can you fix it?

Yes, but give me some time. In fact, you can make a pull request if you manage to fix any error or add any new functionality.

### 3.- Could you add new functionalities? I need it to work in this specific way.

Absolutely not. If you need something specific, you'll have to do it on your own. Feel free to work with my code however you like, as long as you mention me, it's no problem.
