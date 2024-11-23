# HexString
HexString is a text dumper that creates a binary file which you can edit with your favorite text editor. It also allows automatic pointer calculation, making it much easier and faster to translate a ROM. It supports compression via DTE/MTE.

## Requirements
To compile you can use pyinstaller library. 

```
pip install pyinstaller
```
## Build
```
git clone https://github.com/KodingBTW/hexstring

cd hexstring

pyinstaller --onefile -c --icon=icon.ico main.py --name HexString
```
## Usage

Synopsis:
```
HexString [-d | -e] inFileName outFileName
```

Description:

```
HexString -d <romFile> <PointersStartAddress> <PointerTableSize> <HeaderSize> <LineBreaker> <outFile> [tblFile] - Decode text from ROM file.

HexString -e <TextFile> <TextStartAddress> <TextSize> <PointersStartAddress> <HeaderSize> <romFile> [tblFile] - Encode text to ROM file.

-h - Display help

-v - Output version information
```
The program doesn't handle many exceptions, so try to provide the correct information to avoid issues. For more information, read the attached readme.txt.

## Frecuency Answer Questions

### 1.- Can I use this tool in my personal project?

Of course, there's no need to ask. Feel free to use it in your project. I only ask that you mention me as contributor.

### 2.- I found a error, can you fix it?

Yes, but give me some time. In fact, you can make a pull request if you manage to fix any error or add any new functionality.

### 3.- Could you add new functionalities? I need it to work in this specific way.

Absolutely not, I don't plan on doing much more than what's already included. If you need something specific, you'll have to do it on your own. Feel free to work with my code however you like, as long as you mention me, it's no problem.
