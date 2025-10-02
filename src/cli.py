import argparse
import sys
import os
import json
from config import app_name, version, author, license, date, hour
from decoder import Decoder
from encoder import Encoder

class CustomArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        print(f"\n{message}\n")
        CLI.show_help()
        sys.exit(1)

    def print_help(self):
        CLI.show_help()
        sys.exit(1)

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
        # This auxiliar function handle the problem with negative hex and parsel entry with ", compatible with .json GUI config."""
        value = value.strip('"')
        if value.startswith('0x') or value.startswith('-0x'):
            value = value.replace('0x', '')
        
        if value.startswith('-'):
            return -int(value[1:], 16)
        return int(value, 16)
    
    @staticmethod
    def pointer_info(pointer):
        if pointer == '2b':
            return("Little Endian - 2 bytes")
        elif pointer == '2bb':
            return("Big Endian - 2 bytes")
        elif pointer == '3b':
            return("Little Endian - 3 bytes")
        elif pointer == '3bb':
            return("Big Endian - 3 bytes")
        elif pointer == '4b':
            return("Little Endian - 4 bytes")
        elif pointer == '4bb':
            return("Big Endian - 4 bytes")
        else:
            return("Undefined pointer.")

    @staticmethod
    def show_help():
        print("+----------------------------------------------------------------------------------")
        print(f"| {app_name} v{version} by {author}")
        print("+----------------------------------------------------------------------------------")
        print(f"| Usage:")
        print("|   extract           Extract script from ROM")
        print("|   insert            Insert script into ROM")
        print("|   extractconfig     Extract script using .json config.")
        print("|   insertconfig      Insert script using .json config.")
        print("|   -v                Show build version.")
        print("|   -help -?          Show this message.")
        print("+----------------------------------------------------------------------------------")
        print("| Options:")
        print("|  --rom <path>                             Path to the ROM file.")
        print("|  --file <path>                            Input/Output file.")
        print("|  --tbl <path>                             Path to the tbl file.")
        print("|  --p <format>                             Pointers format.")
        print("|  --pointers-offset <hex_value>            Start offset of the pointers table.")
        print("|  --pointers-size <hex_value>              Size of the pointers table.")
        print("|  --base <base>                            Base address.")
        print("|  --end-line <end_line>                    End line (Needed for extract).")
        print("|  --text-offset <hex_value>                Text start offset (Needed for insert).")
        print("|  --text-size <hex_value>                  Text size (Needed for insert).")
        print("|  --use-custom-brackets <0|1|2|3>          Custom brackets for raw hex (optional).")
        print("|  --no-comments                            Disables comments (optional).")
        print("|  --fill <hex_value>                       Fill value in hex (optional).")
        print("|  --use-split-pointers <lsb> <msb> <size>  Split pointers method (optional).")
        print("|  --no-use-end-lines  <hex_value>          Do not use end lines (optional).")
        print("+----------------------------------------------------------------------------------")
        sys.exit(1)

    def handle_extract_config(self):
        config_file = self.args.config
        if not os.path.exists(config_file):
            print(f"\nERROR: Config file '{config_file}' not found.")
            sys.exit(1)

        # Get the directory of the config file
        config_dir = os.path.dirname(os.path.abspath(config_file))

        with open(config_file, "r", encoding="utf-8") as f:
            config = json.load(f)

        # Validate config
        json_version = config.get("version", "0.0.0")
        if tuple(map(int, json_version.split("."))) < (1, 4, 0):
            print(f"\nERROR: Config version {json_version} is lower than required 1.4.0")
            sys.exit(1)
            
        # Validate required fields
        required_fields = ["rom_file", "tbl_file", "script_file", "pointers_base", "text_start_offset", "text_end_offset"]
        for field in required_fields:
            if field not in config or not config[field]:
                print(f"\nERROR: Missing or empty required field '{field}' in config.")
                sys.exit(1)

        # Build parser
        argv = ["extract"]

        # Get config, paths relative directory
        rom_path = os.path.join(config_dir, config["rom_file"])
        argv += ["--rom", rom_path]
        tbl_path = os.path.join(config_dir, config["tbl_file"])
        argv += ["--tbl", tbl_path]
        script_path = os.path.join(config_dir, config["script_file"])
        argv += ["--file", script_path]
            
        # Don't touch this
        # Fix negative entry for .json and bypass negative entry with 0x by user.
        base_str = config["pointers_base"]
        if base_str.startswith("-"):
            base_val = f'"-{base_str[1:]}"'
        else:
            base_val = base_str
        argv += ["--base", base_val]

        argv += ["--use-custom-brackets", str(config["brackets"])]
            
        # Get pointers
        if config.get("use_split_pointers", False):
            split_ptr_lsb_offset = config.get("split_ptr_lsb_offset")
            split_ptr_msb_offset = config.get("split_ptr_msb_offset")
            split_ptr_size = config.get("split_ptr_size")
            argv += ["--use-split-pointers", f"{split_ptr_lsb_offset}", f"{split_ptr_msb_offset}", f"{split_ptr_size}"]
        else:
            pointer_size = config["pointer_size"]
            endianess = config.get("endianess", 0)
            size_num = str(pointer_size).split()[0]
            if size_num in {"2", "3", "4"}:
                value = f"{size_num}b"
                if endianess == 1:
                    value += "b"
                argv += ["--p", value]
                argv += ["--pointers-offset", config["pointers_start_offset"]]
                ptr_size = int(config["pointers_end_offset"], 16) - int(config["pointers_start_offset"], 16) + 1
                argv += ["--pointers-size", hex(ptr_size)]
            else:
                print(f"\nERROR: Unsupported pointer_size '{pointer_size}'")
                sys.exit(1)
            
        # Get Advanced Options 
        if config.get("not_use_end_line") is True:
            text_end = config.get("text_end_offset")
            argv.extend(['--no-use-end-lines', text_end])
            
        # Save Parser
        parser = self.setup_parser()
        self.args = parser.parse_args(argv)

    def handle_insert_config(self):
        config_file = self.args.config
        if not os.path.exists(config_file):
            print(f"\nERROR: Config file '{config_file}' not found.")
            sys.exit(1)

        # Get the directory of the config file
        config_dir = os.path.dirname(os.path.abspath(config_file))

        with open(config_file, "r", encoding="utf-8") as f:
            config = json.load(f)

        # Validate config
        json_version = config.get("version", "0.0.0")
        if tuple(map(int, json_version.split("."))) < (1, 4, 0):
            print(f"\nERROR: Config version {json_version} is lower than required 1.4.0")
            sys.exit(1)
            
        # Validate required fields
        required_fields = ["rom_file", "tbl_file", "script_file", "pointers_base", "text_start_offset", "text_end_offset"]
        for field in required_fields:
            if field not in config or not config[field]:
                print(f"\nERROR: Missing or empty required field '{field}' in config.")
                sys.exit(1)

        # Build parser
        argv = ["insert"]

        # Get config, paths relative directory
        rom_path = os.path.join(config_dir, config["rom_file"])
        argv += ["--rom", rom_path]
        tbl_path = os.path.join(config_dir, config["tbl_file"])
        argv += ["--tbl", tbl_path]
        script_path = os.path.join(config_dir, config["script_file"])
        argv += ["--file", script_path]

        # Don't touch this
        # Fix negative entry for .json and bypass negative entry with 0x by user.
        base_str = config["pointers_base"]
        if base_str.startswith("-"):
            base_val = f'"-{base_str[1:]}"'
        else:
            base_val = base_str

        argv += ["--base", base_val]
        
        argv += ["--text-offset", config["text_start_offset"]]
        text_size = int(config["text_end_offset"], 16) - int(config["text_start_offset"], 16) + 1
        argv += ["--text-size", hex(text_size)]
        argv += ["--use-custom-brackets", str(config["brackets"])]

        # Get pointers
        if config.get("use_split_pointers", False):
            split_ptr_lsb_offset = config.get("split_ptr_lsb_offset")
            split_ptr_msb_offset = config.get("split_ptr_msb_offset")
            split_ptr_size = config.get("split_ptr_size")
            argv += ["--use-split-pointers", f"{split_ptr_lsb_offset}", f"{split_ptr_msb_offset}", f"{split_ptr_size}"]
        else:
            pointer_size = config["pointer_size"]
            endianess = config.get("endianess", 0)
            size_num = str(pointer_size).split()[0]
            if size_num in {"2", "3", "4"}:
                value = f"{size_num}b"
                if endianess == 1:
                    value += "b"
                argv += ["--p", value]
                argv += ["--pointers-offset", config["pointers_start_offset"]]
            else:
                print(f"\nERROR: Unsupported pointer_size '{pointer_size}'")
                sys.exit(1)
            
        # Get Advanced Options 
        if config.get("not_use_end_line") is True:
            text_end = config.get("text_end_offset")
            argv.extend(['--no-use-end-lines', text_end])
        if config.get("fill_free_space") is True:
            fill_val = config.get("fill_free_space_byte")
            argv.extend(["--fill", fill_val])

        # Save Parser
        parser = self.setup_parser()
        self.args = parser.parse_args(argv)

    def handle_extract(self):
        print("+----------------------------------------------------------------------------------")
        print(f"| {app_name} v{version} by {author}")
        print("+----------------------------------------------------------------------------------")
        print("| Summary:")
        print(f"|   ROM File: {self.args.rom}")
        print(f"|   Output File: {self.args.file}")
        print(f"|   Table File: {self.args.tbl}")
        if self.args.use_split_pointers is None:
            print(f"|   Pointers Format: {CLI.pointer_info(self.args.p)}")
        if self.args.use_split_pointers is not None:
            lsb_ptr_offset, msb_ptr_offset, split_ptr_size = self.args.use_split_pointers
            print(f"|   Split Pointers LSB Offset: 0x{lsb_ptr_offset:X}")
            print(f"|   Split Pointers MSB Offset: 0x{msb_ptr_offset:X}")
            print(f"|   Split Pointers Size: {split_ptr_size} / 0x{split_ptr_size:X}")
        else:
            print(f"|   Pointers Start Offset: 0x{self.args.pointers_offset:X}")
            print(f"|   Pointers Size: {self.args.pointers_size} / 0x{self.args.pointers_size:X}")
        #print(f"|   Base: {self.args.base:X}")
        base_display = f"-0x{abs(self.args.base):X}" if self.args.base < 0 else f"0x{self.args.base:X}"
        print(f"|   Base: {base_display}")
        if not self.args.no_use_end_lines:
            print(f"|   End Line: {self.args.end_line.upper()}")
        if self.args.use_custom_brackets is not None:
            print(f"|   Bracket Type: {self.args.use_custom_brackets}")
        print("+----------------------------------------------------------------------------------")
        if self.args.no_comments or self.args.use_split_pointers is not None or self.args.no_use_end_lines:
            print("| Advanced Options:")
            if self.args.no_comments:
                print("|   Comments disabled.")       
            if self.args.use_split_pointers is not None:
                print(f"|   Use split pointers method.")      
            if self.args.no_use_end_lines:
                print("|   Don't use end lines.")
            print("+----------------------------------------------------------------------------------")

        # Get Options

        rom_file = self.args.rom
        tbl_file = self.args.tbl
        out_file = self.args.file
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
        if self.args.use_split_pointers and self.args.no_use_end_lines:
            decode_script = Decoder.write_out_file(out_file, script, lsb_ptr_offset, msb_ptr_offset + split_ptr_size - 1, split_ptr_size, format_pointers, lines_length, None, no_comments_lines)
            print(f"|   Script Size: {total_bytes_read} / 0x{total_bytes_read:X} bytes.")
            print(f"|   Pointers Table Size: {split_ptr_size * 2} / 0x{split_ptr_size * 2:X} bytes. {split_ptr_size} pointers found.")
        elif self.args.use_split_pointers:
            decode_script = Decoder.write_out_file(out_file, script, lsb_ptr_offset, msb_ptr_offset + split_ptr_size - 1, split_ptr_size, format_pointers, lines_length, end_line, no_comments_lines)
            print(f"|   Script Size: {total_bytes_read} / 0x{total_bytes_read:X} bytes.")
            print(f"|   Pointers Table Size: {split_ptr_size * 2} / 0x{split_ptr_size * 2:X} bytes. {split_ptr_size} pointers found.")
        elif self.args.no_use_end_lines:
            decode_script = Decoder.write_out_file(out_file, script, pointers_start_offset, pointers_start_offset + pointers_size - 1, pointers_size, format_pointers, lines_length, None, no_comments_lines)
            print(f"|   Script Size: {total_bytes_read} / 0x{total_bytes_read:X} bytes.")
            print(f"|   Pointers Table Size: {pointers_size} / 0x{pointers_size:X} bytes. {pointers_size//pointers_length} pointers found.")
        else:
            decode_script = Decoder.write_out_file(out_file, script, pointers_start_offset, pointers_start_offset + pointers_size - 1, pointers_size, format_pointers, lines_length, end_line, no_comments_lines)
            print(f"|   Script Size: {total_bytes_read} / 0x{total_bytes_read:X} bytes.")
            print(f"|   Pointers Table Size: {pointers_size} / 0x{pointers_size:X} bytes. {pointers_size//pointers_length} pointers found.")
        print("|   Extraction Done!")
        print("+----------------------------------------------------------------------------------")


    def handle_insert(self):
        print("+----------------------------------------------------------------------------------")
        print(f"| {app_name} v{version} by {author}")
        print("+----------------------------------------------------------------------------------")
        print("| Summary:")
        print(f"|   ROM File: {self.args.rom}")
        print(f"|   Input File: {self.args.file}")
        print(f"|   Table File: {self.args.tbl}") 
        if self.args.use_split_pointers is None:
            print(f"|   Pointers Format: {CLI.pointer_info(self.args.p)}")
        if self.args.use_split_pointers is not None:
            lsb_ptr_offset, msb_ptr_offset, split_ptr_size = self.args.use_split_pointers
            print(f"|   Split Pointers LSB Offset: 0x{lsb_ptr_offset:X}")
            print(f"|   Split Pointers MSB Offset: 0x{msb_ptr_offset:X}")
            print(f"|   Split Pointers Size: {split_ptr_size} / 0x{split_ptr_size:X}")
        else:
            print(f"|   Pointers Start Offset: 0x{self.args.pointers_offset:X}")    
        print(f"|   Text Start Offset: 0x{self.args.text_offset:X}")
        print(f"|   Text Size: {self.args.text_size} / 0x{self.args.text_size:X}")
        #print(f"|   Base: {self.args.base:X}")
        base_display = f"-0x{abs(self.args.base):X}" if self.args.base < 0 else f"0x{self.args.base:X}"
        print(f"|   Base: {base_display}")
        if self.args.use_custom_brackets is not None:
            print(f"|   Bracket Type: {self.args.use_custom_brackets}")
        print("+----------------------------------------------------------------------------------")
        if self.args.fill is not None or self.args.use_split_pointers is not None or self.args.no_use_end_lines:
            print("| Advanced Options:")
            if self.args.fill is not None:
                print(f"|   Fill Value: 0x{self.args.fill:X}")   
            if self.args.use_split_pointers is not None:
                print(f"|   Use split pointers method.") 
            if self.args.no_use_end_lines:
                print("|   Don't use end lines.")
            print("+----------------------------------------------------------------------------------")

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
            print(f"\nERROR: Script size has exceeded its maximum size. Remove {new_script_size - original_text_size} bytes.\n")
            sys.exit(1)
        if new_pointers_size > original_pointers_size:
            print(f"\nERROR: Table pointer size has exceeded its maximum size. Remove {(new_pointers_size - original_pointers_size)//2} lines in script.\n")
            sys.exit(1)         
        free_space_script = Encoder.write_rom(rom_file, original_text_start_offset, original_text_size, new_script_data, fill_free_space, fill_free_space_byte)
        print(f"|   Script written at address 0x{original_text_start_offset:X}, {free_space_script} bytes of free space.")

        if self.args.use_split_pointers is None:
            free_space_pointers = Encoder.write_rom(rom_file, original_pointers_start_offset, original_pointers_size, new_pointers_data, False, fill_free_space_byte)
            print(f"|   Pointers table written at address 0x{original_pointers_start_offset:X}, {free_space_pointers//pointers_length} lines/pointers left.")

        else:
            free_space_pointers = Encoder.write_rom(rom_file, original_pointers_start_offset, original_pointers_size, new_pointers_data_lsb, False, fill_free_space_byte)
            free_space_pointers = Encoder.write_rom(rom_file, original_pointers_end_offset, original_pointers_size, new_pointers_data_msb, False, fill_free_space_byte)
            print(f"|   Pointers table written at address 0x{original_pointers_start_offset:X}, {free_space_pointers//2} lines/pointers left.")
        print("|   Insertion Done!")
        print("+----------------------------------------------------------------------------------")


    def setup_parser(self):
        parser = CustomArgumentParser(
            description="HexString: A tool for extracting and inserting texts into ROM files."
        )

        # Version argument
        parser.add_argument('-v', '--version', action='version', version=f"{app_name} by {author}, Build: {version}_{date}{hour}")

        # Subcommands
        subparsers = parser.add_subparsers(dest='command', help='subcommand help')

        # Extract
        extract_parser = subparsers.add_parser('extract', help='Extract text from ROM')
        extract_parser.add_argument('--rom', required=True, help='ROM file')
        extract_parser.add_argument('--file', required=True, help='Output file')
        extract_parser.add_argument('--tbl', required=True, help='Tbl file')     
        extract_parser.add_argument('--p', choices=['2b', '2bb', '3b', '3bb', '4b', '4bb'],
                                    help='Pointers format')
        extract_parser.add_argument('--pointers-offset', type=lambda x: int(x, 16),
                                    help='Start offset of the pointer table (hex value)')
        extract_parser.add_argument('--pointers-size', type=lambda x: int(x, 16),
                                    help='Size of the pointer table (hex value)')
        extract_parser.add_argument('--base', required=True, type=CLI.auto_int,
                                    help='Base address')
        extract_parser.add_argument('--end-line', help='End line byte for split pointes')


        # Extract Advanced Options
        extract_parser.add_argument('--no-comments', action='store_true', help='Disables comments')
        extract_parser.add_argument('--use-custom-brackets', choices=[0, 1, 2, 3], type=int, default=0, help='Choose custom bracket number. (Default: 0)')
        extract_parser.add_argument('--use-split-pointers', nargs=3, type=lambda x: int(x, 16), 
                                    help='Needed three arguments: lsb_offset, msb_offset, size for split pointers')
        extract_parser.add_argument('--no-use-end-lines', type=lambda x: int(x, 16), 
                                    help='Provide a hexadecimal value text_end_offset')

        # Insert
        insert_parser = subparsers.add_parser('insert', help='Insert text into ROM')
        insert_parser.add_argument('--rom', required=True, help='ROM file')
        insert_parser.add_argument('--file', required=True, help='Input file')
        insert_parser.add_argument('--tbl', required=True, help='Tbl file')
        
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

        # Insert Advanced Options
        insert_parser.add_argument('--use-custom-brackets', choices=[0, 1, 2, 3], type=int, default=0, help='Choose custom bracket number. (Default: 0)')
        insert_parser.add_argument('--fill', nargs='?', default=None, const='FF', type=lambda x: int(x, 16) if x else None, help='Fill value in hex (default: 0xFF)')
        insert_parser.add_argument('--use-split-pointers', nargs=3, type=lambda x: int(x, 16), 
                                    help='Three hex values: lsb, msb, size for split pointers')
        insert_parser.add_argument('--no-use-end-lines', type=lambda x: int(x, 16), 
                                    help='Provide text end offset address')

        # Extract Script Config
        extractconfig_parser = subparsers.add_parser('extractconfig', help='Extract using JSON config file')
        extractconfig_parser.add_argument('config', help='Path to config.json')
        
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
        elif self.args.command == 'extractconfig':
            self.handle_extract_config()
            self.handle_extract()
        elif self.args.command == 'insertconfig':
            self.handle_insert_config()
            self.handle_insert()
        else:
            self.show_help()

