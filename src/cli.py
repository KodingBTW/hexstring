import argparse
import sys
import os
import json
from config import app_name, version, author, license
from decoder import Decoder
from encoder import Encoder

class CLI:
    def __init__(self):
        self.args = None

    def clear():
        if os.name == 'nt': 
            os.system('cls')
        else:
            os.system('clear')
            
    @staticmethod
    def auto_int(value):
        """Auxiliar function for negative base numbers"""
        try:
            return int(value, 0)
        except ValueError:
            if value.startswith("-"):
                return -int(value[1:], 16)
            return int(value, 16)

    def show_help(self):
        print("\n########################################")
        print(f"########### {app_name} v{version} ###########")
        print("########################################")
        print(f"\nUsage: console.exe [-h] [-v] {{extract,insert}} [OPTIONS]\n")
        print("  extract           Extract script from ROM")
        print("  insert            Insert script into ROM")
        print("  -h                Show this message.")
        print("  -v                Show version")
        print("\nOPTIONS:")
        print("  --rom <path>                             Path to the ROM file.")
        print("  --p <format>                             Pointers format.")
        print("  --pointers-offset <hex_value>            Start offset of the pointer table.")
        print("  --pointers-size <hex_value>              Size of the pointer table.")
        print("  --base <base>                            Base address.")
        print("  --end-line <end_line>                    End line (only for extract).")
        print("  --out <path>                             Output file for extract.")
        print("  --tbl <path>                             Path to the tbl file.")
        print("  --text-offset <hex_value>                Text start offset (only for insert).")
        print("  --text-size <hex_value>                  Text size (only for insert).")
        print("  --no-comments                            Disables comments (optional).")
        print("  --use-custom-brackets <0|1|2|3>          Choose a number for custom brackets (optional, Default: 0).")
        print("  --fill <hex_value>                       Fill value in hex (optional, Default: 0xFF).")
        print("  --use-split-pointers <lsb> <msb> <size>  Three hexadecimal numbers for split pointers (optional).")
        print("  --no-use-end-lines  <hex_value>          Do not use end lines (optional).\n")

    def handle_get_config(self):
        config_file = self.args.config
        if not os.path.exists(config_file):
            print(f"ERROR: Config file '{config_file}' not found.")
            sys.exit(1)

        # Get the directory of the config file
        config_dir = os.path.dirname(os.path.dirname(os.path.abspath(config_file)))

        with open(config_file, "r", encoding="utf-8") as f:
            config = json.load(f)

        # Validate config
        json_version = config.get("version", "0.0.0")
        if tuple(map(int, json_version.split("."))) < (1, 4, 0):
            print(f"ERROR: Config version {json_version} is lower than required 1.4.0")
            sys.exit(1)

        # Build parser
        argv = ["insert"]

        # Get config, using paths relative to config file's directory
        if "rom_file" in config:
            rom_path = os.path.join(config_dir, config["rom_file"])
            argv += ["--rom", rom_path]
        if "tbl_file" in config:
            tbl_path = os.path.join(config_dir, config["tbl_file"])
            argv += ["--tbl", tbl_path]
        if "script_file" in config:
            script_path = os.path.join(config_dir, config["script_file"])
            argv += ["--file", script_path]
        if "pointers_start_offset" in config:
            argv += ["--pointers-offset", config["pointers_start_offset"]]
        if "pointers_base" in config:
            base_val = int(config["pointers_base"], 16)
            argv += ["--base", str(base_val)]
        if "text_start_offset" in config:
            argv += ["--text-offset", config["text_start_offset"]]
        if "text_end_offset" in config and "text_start_offset" in config:
            size = int(config["text_end_offset"], 16) - int(config["text_start_offset"], 16) + 1
            argv += ["--text-size", hex(size)]

        # Format Pointers
        if "pointer_size" in config and "endianess" in config:
            pointer_size = config["pointer_size"]
            endianess = config.get("endianess", 0)

            size_num = str(pointer_size).split()[0]
            if size_num in {"2", "3", "4"}:
                value = f"{size_num}b"
                if endianess == 1:
                    value += "b"
                argv += ["--p", value]
            else:
                print(f"ERROR: Unsupported pointer_size '{pointer_size}'")
                sys.exit(1)

        # Get Advanced Options
        if config.get("not_use_end_line", False):
            end_offset = config.get("pointers_end_offset")
            argv += ["--no-use-end-lines", end_offset]

        if config.get("fill_free_space", False):
            fill_val = config.get("fill_free_space_byte")
            argv += ["--fill", fill_val]

        if config.get("no_use_comments_lines", False):
            argv += ["--no-comments"]

        if "brackets" in config:
            argv += ["--use-custom-brackets", str(config["brackets"])]

        # Save Parser
        parser = self.setup_parser()
        self.args = parser.parse_args(argv)

    def handle_extract(self):
        print("\n########################################")
        print(f"########### {app_name} v{version} ###########")
        print("########################################")
        print("\nExtracting using config:\n")
        print(f"ROM File: {self.args.rom}")
        print(f"Pointers Format: {self.args.p}")
        print(f"Pointers Start Offset: {self.args.pointers_offset:x}")
        print(f"Pointers Size: {self.args.pointers_size:x}")
        print(f"Base Address: {self.args.base:x}")
        print(f"End Line: {self.args.end_line:x}")
        print(f"Output File: {self.args.out}")
        print(f"Table File: {self.args.tbl}")
        if self.args.use_custom_brackets is not None:
            print(f"Brackets type: {self.args.use_custom_brackets}\n")

        print("Advanced Options:\n")

        if self.args.no_comments:
            print("Comments are disabled.")
         
        if self.args.use_split_pointers is not None:
            print(f"Using split pointers method, lsb offset: {self.args.use_split_pointers[0]:x}, msb offset: {self.args.use_split_pointers[1]:x}, size: {self.args.use_split_pointers[2]:x}")
        
        if self.args.no_use_end_lines:
            print("Not using end lines.")

        # Get Options

        rom_file = self.args.rom
        tbl_file = self.args.tbl
        out_file = self.args.out
        base = self.args.base
        no_comments_lines = self.args.no_comments
        
        # Get Pointers
        if self.args.use_split_pointers is not None:
            lsb_ptr_offset, msb_ptr_offset, split_ptr_size = self.args.use_split_pointers
            lsb = Decoder.read_rom(rom_file, lsb_ptr_offset, split_ptr_size)
            msb = Decoder.read_rom(rom_file, msb_ptr_offset, split_ptr_size)
            format_pointers = Decoder.process_pointers_split_2_bytes(lsb, msb, base)
        else:
            pointers_start_offset = self.args.pointers_offset
            pointers_size = self.args.pointers_size
            table_pointers = Decoder.read_rom(rom_file, pointers_start_offset, pointers_size)
            if self.args.p == '2b':
                format_pointers = Decoder.process_pointers_2_bytes(table_pointers, base, 0)
                pointers_length = 2
            elif self.args.p == '2bb':
                format_pointers = Decoder.process_pointers_2_bytes(table_pointers, base, 1)
                pointers_length = 2
            elif self.args.p == '3b':
                format_pointers = Decoder.process_pointers_3_bytes(table_pointers, base, 0)
                pointers_length = 3
            elif self.args.p == '3bb':
                format_pointers = Decoder.process_pointers_3_bytes(table_pointers, base, 1)
                pointers_length = 3
            elif self.args.p == '4b':
                format_pointers = Decoder.process_pointers_4_bytes(table_pointers, base, 0)
                pointers_length = 4
            elif self.args.p == '4bb':
                format_pointers = Decoder.process_pointers_4_bytes(table_pointers, base, 1)
                pointers_length = 4
            else:
                print("\nError: Invalid pointers format!")
                sys.exit(1)

        # Load ROM data to RAM
        rom_data = Decoder.read_rom(rom_file, 0, os.path.getsize(rom_file))

        # Check brackets
        bracket_index = self.args.use_custom_brackets

        # Load char table to RAM
        char_table = Decoder.read_tbl(tbl_file)

        # Decode Script
        if self.args.no_use_end_lines:
            script, total_bytes_read, lines_length = Decoder.decode_script_no_end_line(rom_data, format_pointers, self.args.no_use_end_lines + 1, char_table, bracket_index)
        else:
            end_line = Decoder.parse_end_lines(self.args.end_line)       
            script, total_bytes_read, lines_length = Decoder.decode_script(rom_data, format_pointers, end_line, char_table, bracket_index)
            
        # Write Script
        if self.args.use_split_pointers is not None and self.args.no_use_end_lines:
            decode_script = Decoder.write_out_file(out_file, script, lsb_ptr_offset, msb_ptr_offset + split_ptr_size - 1, split_ptr_size, format_pointers, lines_length, None, no_comments_lines)
            print(f"\nTEXT BLOCK SIZE: {total_bytes_read} / {hex(total_bytes_read)} bytes.")
            print(f"PTR_TABLE BLOCK SIZE: {split_ptr_size * 2} / {hex(split_ptr_size) * 2} bytes. Located {split_ptr_size} pointers.")
        elif self.args.use_split_pointers is not None:
            decode_script = Decoder.write_out_file(out_file, script, lsb_ptr_offset, msb_ptr_offset + split_ptr_size - 1, split_ptr_size, format_pointers, lines_length, end_line, no_comments_lines)
            print(f"\nTEXT BLOCK SIZE: {total_bytes_read} / {hex(total_bytes_read)} bytes.")
            print(f"PTR_TABLE BLOCK SIZE: {split_ptr_size * 2} / {hex(split_ptr_size) * 2} bytes. Located {split_ptr_size} pointers.")
        elif self.args.no_use_end_lines:
            decode_script = Decoder.write_out_file(out_file, script, pointers_start_offset, pointers_start_offset + pointers_size - 1, pointers_size, format_pointers, lines_length, None, no_comments_lines)
            print(f"\nTEXT BLOCK SIZE: {total_bytes_read} / {hex(total_bytes_read)} bytes.")
            print(f"PTR_TABLE BLOCK SIZE: {pointers_size} / {hex(pointers_size)} bytes. Located {pointers_size//pointers_length} pointers.")
        else:
            decode_script = Decoder.write_out_file(out_file, script, pointers_start_offset, pointers_start_offset + pointers_size - 1, pointers_size, format_pointers, lines_length, end_line, no_comments_lines)
            print(f"\nTEXT BLOCK SIZE: {total_bytes_read} / {hex(total_bytes_read)} bytes.")
            print(f"PTR_TABLE BLOCK SIZE: {pointers_size} / {hex(pointers_size)} bytes. Located {pointers_size//pointers_length} pointers.")
        print("Extraction Done!\n")


    def handle_insert(self):
        print("\n########################################")
        print(f"########### {app_name} v{version} ###########")
        print("########################################")
        print("\nInserting using config:\n")
        print(f"Input File: {self.args.file}")
        print(f"Pointers Format: {self.args.p}")
        print(f"Text Start Offset: {self.args.text_offset:x}")
        print(f"Text Size: {self.args.text_size:x}")
        print(f"Pointers Start Offset: {self.args.pointers_offset:x}")
        print(f"Base Address: {self.args.base:x}")
        print(f"ROM File: {self.args.rom}")
        print(f"Table File: {self.args.tbl}") 
        if self.args.use_custom_brackets is not None:
            print(f"Brackets type: {self.args.use_custom_brackets}\n")

        print("Advanced Options:\n")
        
        if self.args.fill is not None:
            print(f"Fill value: {self.args.fill:x}")
        
        if self.args.use_split_pointers is not None:
            print(f"Using split pointers method, lsb offset: {self.args.use_split_pointers[0]:x}, msb offset: {self.args.use_split_pointers[1]:x}, size: {self.args.use_split_pointers[2]:x}")
        
        if self.args.no_use_end_lines:
            print("Not using end lines.")

        # Get Options

        rom_file = self.args.rom
        tbl_file = self.args.tbl
        input_file = self.args.file
        base = self.args.base
        original_text_start_offset = self.args.text_offset
        original_text_size = self.args.text_size

        # Check if fill free space
        if self.args.fill is None:
            fill_free_space = False
            fill_free_space_byte = None
        else:
            fill_free_space = True
            fill_free_space_byte = bytes([self.args.fill])
        
        # Read Script file
        new_script, _, original_pointers_end_offset, original_pointers_size, script_end_lines = Encoder.read_script(input_file)

        # Parse End Lines
        if self.args.no_use_end_lines:
            end_line = self.args.no_use_end_lines
        else:
            try:
                end_line = Decoder.parse_end_lines(script_end_lines)
            except AttributeError:
                print('\nERROR: No detected end lines in first line of script config and using "No_use_end_lines = False"')
                sys.exit(1)

        # Check brackets
        bracket_index = self.args.use_custom_brackets

        # Load the character table
        char_table, longest_char = Encoder.read_tbl(tbl_file)

        # Encode Text
        if self.args.no_use_end_lines:
            new_script_data, new_script_size, cumulative_lengths = Encoder.encode_script(new_script, None, char_table, longest_char, self.args.no_use_end_lines, bracket_index)
        else:
            new_script_data, new_script_size, cumulative_lengths = Encoder.encode_script(new_script, end_line, char_table, longest_char, self.args.no_use_end_lines, bracket_index)

        # Format Pointers
        if self.args.use_split_pointers is not None:
            original_pointers_start_offset, original_pointers_end_offset, original_pointers_size = self.args.use_split_pointers
            new_pointers_data_lsb, new_pointers_data_msb, new_pointers_size = Encoder.calculate_pointers_2_bytes_split(cumulative_lengths, original_text_start_offset, False, base)
        else:
            original_pointers_start_offset = self.args.pointers_offset
            if self.args.p == '2b':
                new_pointers_data, new_pointers_size = Encoder.calculate_pointers_2_bytes(cumulative_lengths, original_text_start_offset, False, base, 0)
                pointers_length = 2
            elif self.args.p == '2bb':
                new_pointers_data, new_pointers_size = Encoder.calculate_pointers_2_bytes(cumulative_lengths, original_text_start_offset, False, base, 1)
                pointers_length = 2
            elif self.args.p == '3b':
                new_pointers_data, new_pointers_size = Encoder.calculate_pointers_3_bytes(cumulative_lengths, original_text_start_offset, False, base, 0)
                pointers_length = 3
            elif self.args.p == '3bb':
                new_pointers_data, new_pointers_size = Encoder.calculate_pointers_3_bytes(cumulative_lengths, original_text_start_offset, False, base, 1)
                pointers_length = 3
            elif self.args.p == '4b':
                new_pointers_data, new_pointers_size = Encoder.calculate_pointers_4_bytes(cumulative_lengths, original_text_start_offset, False, base, 0)
                pointers_length = 4
            elif self.args.p == '4bb':
                new_pointers_data, new_pointers_size = Encoder.calculate_pointers_4_bytes(cumulative_lengths, original_text_start_offset, False, base, 1)
                pointers_length = 4
            else:
                print("\nError: Invalid pointers format!")
                sys.exit(1)

        # Write ROM
        if new_script_size > original_text_size:
            print(f"\nERROR: script size has exceeded its maximum size. Remove {new_script_size - original_text_size} bytes.\n")
            sys.exit(1)
        if new_pointers_size > original_pointers_size:
            print(f"\nERROR: table pointer size has exceeded its maximum size. Remove {(new_pointers_size - original_pointers_size)//2} lines in script.\n")
            sys.exit(1)         
        free_space_script = Encoder.write_rom(rom_file, original_text_start_offset, original_text_size, new_script_data, fill_free_space, fill_free_space_byte)
        print(f"\nScript text write to address {hex(original_text_start_offset)}, {free_space_script} bytes free.")

        if not self.args.use_split_pointers is not None:
            free_space_pointers = Encoder.write_rom(rom_file, original_pointers_start_offset, original_pointers_size, new_pointers_data, False, fill_free_space_byte)
            print(f"Pointer table write to address {hex(original_pointers_start_offset)}, {free_space_pointers//pointers_length} lines/pointers left.")

        else:
            free_space_pointers = Encoder.write_rom(rom_file, original_pointers_start_offset, original_pointers_size, new_pointers_data_lsb, False, fill_free_space_byte)
            free_space_pointers = Encoder.write_rom(rom_file, original_pointers_end_offset, original_pointers_size, new_pointers_data_msb, False, fill_free_space_byte)
            print(f"Pointer table write to address {hex(original_pointers_start_offset)}, {free_space_pointers//2} lines/pointers left.")
        print("Insertion Done!\n")

    def setup_parser(self):
        parser = argparse.ArgumentParser(
            description="HexString: A tool for extracting and inserting scripts into ROM files."
        )

        # General
        parser.add_argument('-v', '--version', action='version', version=f"{app_name} v{version} by {author}")

        # Subcomands
        subparsers = parser.add_subparsers(dest='command', help='subcommand help')

        # Extract
        extract_parser = subparsers.add_parser('extract', help='Extract data from ROM')
        extract_parser.add_argument('--rom', required=True, help='Path to the ROM file')
        extract_parser.add_argument('--p', choices=['2b', '2bb', '3b', '3bb', '4b', '4bb'],
                                    help='Pointers format')
        extract_parser.add_argument('--pointers-offset', type=lambda x: int(x, 16),
                                    help='Start offset of the pointer table (hex value)')
        extract_parser.add_argument('--pointers-size', type=lambda x: int(x, 16),
                                    help='Size of the pointer table (hex value)')
        extract_parser.add_argument('--base', required=True, type=CLI.auto_int,
                                    help='Base address')
        extract_parser.add_argument('--end-line', help='End line for the extract process')
        extract_parser.add_argument('--out', required=True, help='Output file for the extracted data')
        extract_parser.add_argument('--tbl', required=True, help='Path to the tbl file')

        # Extract Advanced Options
        extract_parser.add_argument('--no-comments', action='store_true', help='Disables comments')
        extract_parser.add_argument('--use-custom-brackets', choices=[0, 1, 2, 3], type=int, default=0, help='Choose custom bracket number. (Default: 0)')
        extract_parser.add_argument('--use-split-pointers', nargs=3, type=lambda x: int(x, 16), 
                                    help='Needed three arguments: lsb_offset, msb_offset, size for split pointers')
        extract_parser.add_argument('--no-use-end-lines', type=lambda x: int(x, 16), 
                                    help='Provide a hexadecimal value text_end_offset')

        # Insert
        insert_parser = subparsers.add_parser('insert', help='Insert data into ROM')
        insert_parser.add_argument('--file', required=True, help='Input file with the text data')
        insert_parser.add_argument('--p', choices=['2b', '2bb', '3b', '3bb', '4b', '4bb'],
                                    help='Pointers format')
        insert_parser.add_argument('--text-offset', required=True, type=lambda x: int(x, 16),
                                    help='Text start offset (hex value)')
        insert_parser.add_argument('--text-size', required=True, type=lambda x: int(x, 16),
                                    help='Text size (hex value)')
        insert_parser.add_argument('--pointers-offset', type=lambda x: int(x, 16),
                                    help='Start offset of the pointer table (hex value)')
        insert_parser.add_argument('--base', required=True, type=CLI.auto_int,
                                    help='Base address')
        insert_parser.add_argument('--rom', required=True, help='Path to the ROM file')
        insert_parser.add_argument('--tbl', required=True, help='Path to the tbl file')

        # Insert Advanced Options
        insert_parser.add_argument('--use-custom-brackets', choices=[0, 1, 2, 3], type=int, default=0, help='Choose custom bracket number. (Default: 0)')
        insert_parser.add_argument('--fill', nargs='?', default=None, const='FF', type=lambda x: int(x, 16) if x else None, help='Fill value in hex (default: 0xFF)')
        insert_parser.add_argument('--use-split-pointers', nargs=3, type=lambda x: int(x, 16), 
                                    help='Three hex values: lsb, msb, size for split pointers')
        insert_parser.add_argument('--no-use-end-lines', type=lambda x: int(x, 16), 
                                    help='Provide a hexadecimal value text_end_offset')
        # Insert Script Config
        insertconfig_parser = subparsers.add_parser('insertconfig', help='Insert using JSON config file')
        insertconfig_parser.add_argument('config', help='Path to config.json')
        
        return parser

    def parse_arguments(self):
        parser = self.setup_parser()
        self.args = parser.parse_args()

    def run(self):
        if self.args.command == 'extract':
            self.handle_extract()
        elif self.args.command == 'insert':
            self.handle_insert()
        elif self.args.command == 'insertconfig':
            self.handle_get_config()
            self.handle_insert()
        else:
            self.show_help()

