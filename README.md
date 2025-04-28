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

pip install -r requirements.txt

cd src

build.bat
```
## Usage

Synopsis:
```
HexString [-d | -e] inFileName outFileName
```

Description:

```
HexString -d <pointersFormat> <romFile> <PointersStartAddress> <PointerTableSize> <HeaderSize> <LineBreaker> <outFile> [tblFile] - Decode text from ROM file.

HexString -e <pointersFormat> <TextFile> <TextStartAddress> <TextSize> <PointersStartAddress> <HeaderSize> <romFile> [tblFile] - Encode text to ROM file.

-h - Display help

-v - Output version information
```
List of pointer format supported:
```
-2b  --2 bytes little endian
-2bb --2 bytes big endian
-2bs --2 bytes splitted (lsb-msb)
-3b  --3 bytes (gba format)
-4b  --4 bytes (mega drive - big endian)
```
The program doesn't handle many exceptions, so try to provide the correct information to avoid issues. For more information, read the attached readme.txt.

## Frecuency Answer Questions

### 1.- Can I use this tool in my personal project?

Of course, there's no need to ask. Feel free to use it in your project. I only ask that you mention me as contributor.

### 2.- I found a error, can you fix it?

Yes, but give me some time. In fact, you can make a pull request if you manage to fix any error or add any new functionality.

### 3.- Could you add new functionalities? I need it to work in this specific way.

Absolutely not, I don't plan on doing much more than what's already included. If you need something specific, you'll have to do it on your own. Feel free to work with my code however you like, as long as you mention me, it's no problem.
