# HexString 1.3.0 by Koda
# 
# This program is a tool designed for ROM hacking and script extraction/insertion.
# It allows users to extract text from a ROM, manipulate it, and then reinsert the modified text back into the ROM.
# 
# Features:
# - Extract text from ROM files
# - Modify the extracted text
# - Insert the modified text back into the ROM
# - Configurable options for pointers, end offsets, and more
#
# Dependencies:
# - PyQt5 
# - Custom libraries for ROM reading, writing, and text decoding
#
# License:
# This program is licensed under the GNU General Public License v3 (GPL-3.0).
# You can redistribute and/or modify it under the terms of the GPL-3.0 License.
# For more details, see the LICENSE file in the project directory.
#
# Author: Koda
# Version: 1.3.0
#
# Date: 28-04-2025
import sys
import os
import io
import json
import cli
from decoder import Decoder
from encoder import Encoder
from cli import CLI
from PyQt5.QtWidgets import QApplication, QMainWindow, QAction, QSizePolicy, QSpacerItem, QMenuBar, QMenu, QGridLayout, QVBoxLayout, QWidget, QMessageBox, QPlainTextEdit, QTabWidget, QLineEdit, QFileDialog, QLabel, QPushButton, QHBoxLayout, QGroupBox, QRadioButton, QComboBox, QCheckBox, QToolTip, QTextEdit, QDialog, QDialogButtonBox, QProgressBar
from PyQt5.QtGui import QIcon, QRegExpValidator
from PyQt5.QtCore import QRegExp, Qt
from PyQt5 import QtCore, QtGui
from ctypes import windll

class Functions:
    def __init__(self, main_window):
        self.main_window = main_window

    def reset_fields(self):
        # Uncompressed Text Fields
        self.main_window.selected_rom_file_name.clear()
        self.main_window.selected_tbl_file_name.clear()
        self.main_window.selected_script_file_name.clear()
        self.main_window.radio_2_bytes.setChecked(True)
        self.main_window.endianness_list.setCurrentIndex(0)
        self.main_window.pointers_start_offset_input.clear()
        self.main_window.pointers_end_offset_input.clear()
        self.main_window.pointers_base_input.clear()
        self.main_window.text_start_offset_input.clear()
        self.main_window.text_end_offset_input.clear()
        self.main_window.end_line_input.clear()

        # Advanced Options Fields (Uncompressed Text Fields)
        self.main_window.not_comment_lines_checkbox.setChecked(False)
        self.main_window.use_custom_brackets_for_hex_codes_checkbox.setChecked(False) 
        self.main_window.use_custom_brackets_for_hex_codes_list.setCurrentIndex(0)
        self.main_window.fill_free_space_byte_checkbox.setChecked(False)
        self.main_window.fill_free_space_byte_input.setText("FF")  
        self.main_window.use_split_pointers_checkbox.setChecked(False)
        self.main_window.lsb_offset_input.clear()
        self.main_window.msb_offset_input.clear()
        self.main_window.size_input.clear()   
        self.main_window.ignore_end_line_checkbox.setChecked(False)
        self.main_window.not_use_end_line_checkbox.setChecked(False)

        # Set buttons disabled
        self.main_window.extract_button.setDisabled(True)
        self.main_window.insert_button.setDisabled(True)
        
    def create_prefix_label(self):
        prefix_label = QLabel("0x")
        prefix_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        prefix_label.setStyleSheet("color: grey;")
        return prefix_label

    def set_uppercase_formatting(self, line_edit):
        line_edit.textChanged.connect(lambda: line_edit.setText(line_edit.text().upper()))

    def disable_layout_widgets(self, layout):
        for i in range(layout.count()):
            item = layout.itemAt(i)
            if item is not None:
                widget = item.widget()
                if widget is not None:
                    widget.setDisabled(True)

    def toggle_advanced_options(self):
        is_checked = self.main_window.expand_button.isChecked()
        self.main_window.advanced_options_container.setVisible(is_checked)
        self.main_window.expand_button.setText("Hide Advanced Options" if is_checked else "Show Advanced Options")
        self.main_window.setFixedSize(475, 875) if is_checked else self.main_window.setFixedSize(475, 667)
        
    def toggle_split_pointers(self, state):
        is_checked = self.main_window.use_split_pointers_checkbox.isChecked()
        self.main_window.lsb_offset_label.setDisabled(not is_checked)
        self.main_window.lsb_offset_input.setDisabled(not is_checked)
        self.main_window.msb_offset_label.setDisabled(not is_checked)
        self.main_window.msb_offset_input.setDisabled(not is_checked)
        self.main_window.size_label.setDisabled(not is_checked)
        self.main_window.size_input.setDisabled(not is_checked)
        self.main_window.pointers_start_offset_input.setEnabled(not is_checked)
        self.main_window.pointers_end_offset_input.setEnabled(not is_checked)
        self.toggle_set_pointers_groupbox(not is_checked)

    def toggle_set_pointers_groupbox(self, enable):
        widgets_to_enable = [
            self.main_window.pointers_length_label, self.main_window.radio_2_bytes, self.main_window.radio_3_bytes, self.main_window.radio_4_bytes,
            self.main_window.endianness_label, self.main_window.endianness_list
        ]
    
        for widget in widgets_to_enable:
            widget.setEnabled(enable)

    def toggle_ignore_end_line_before_decoding(self, state):
        is_checked = self.main_window.ignore_end_line_checkbox.isChecked()
        self.main_window.not_use_end_line_checkbox.setDisabled(not is_checked)
        self.main_window.not_use_end_line_checkbox.setEnabled(not is_checked)

    def toggle_not_use_end_line(self, state):
        is_checked = self.main_window.not_use_end_line_checkbox.isChecked()
        self.main_window.ignore_end_line_checkbox.setDisabled(not is_checked)
        self.main_window.end_line_label.setDisabled(not is_checked)
        self.main_window.end_line_input.setDisabled(not is_checked)
        self.main_window.ignore_end_line_checkbox.setEnabled(not is_checked)
        self.main_window.end_line_label.setEnabled(not is_checked)
        self.main_window.end_line_input.setEnabled(not is_checked)

    def toggle_custom_brackets(self, state):
        is_checked = self.main_window.use_custom_brackets_for_hex_codes_checkbox.isChecked()
        self.main_window.use_custom_brackets_for_hex_codes_list.setEnabled(not is_checked)
        self.main_window.use_custom_brackets_for_hex_codes_list.setDisabled(not is_checked)

    def toggle_fill_free_space(self, state):
        is_checked = self.main_window.fill_free_space_byte_checkbox.isChecked()
        self.main_window.fill_free_space_byte_input.setEnabled(not is_checked)
        self.main_window.fill_free_space_byte_input.setDisabled(not is_checked)
    
    def show_error_dialog(self, message):
        error_dialog = QMessageBox(self.main_window)
        error_dialog.setIcon(QMessageBox.Critical)
        error_dialog.setWindowTitle("Error")
        error_dialog.setText(message)
        error_dialog.setStandardButtons(QMessageBox.Ok)
        error_dialog.exec_()

    def show_success_dialog(self, message):
        success_dialog = QMessageBox(self.main_window)
        success_dialog.setIcon(QMessageBox.Information)
        success_dialog.setWindowTitle("Success")
        success_dialog.setText(message)
        success_dialog.setStandardButtons(QMessageBox.Ok)
        success_dialog.exec_()

    def enable_extract_button(self):
        if self.main_window.selected_rom_file_name.text() != "" and self.main_window.selected_tbl_file_name.text() != "":
            self.main_window.extract_button.setDisabled(False)
        else:
            self.main_window.extract_button.setDisabled(True)

    def enable_insert_button(self):
        if self.main_window.selected_rom_file_name.text() != "" and self.main_window.selected_tbl_file_name.text() != "" and self.main_window.selected_script_file_name.text() != "":
            self.main_window.insert_button.setDisabled(False)
        else:
            self.main_window.insert_button.setDisabled(True)
        
    def process_extraction(self, out_file):
        # CONSTANTS OPTIONS
        no_comments_lines = self.main_window.not_comment_lines_checkbox.isChecked()
        use_custom_brackets = self.main_window.use_custom_brackets_for_hex_codes_checkbox.isChecked()
        bracket_index = self.main_window.use_custom_brackets_for_hex_codes_list.currentIndex()     
        use_split_pointers_method = self.main_window.use_split_pointers_checkbox.isChecked()
        ignore_end_lines_code_until_decode = self.main_window.ignore_end_line_checkbox.isChecked()
        no_use_end_lines_for_split = self.main_window.not_use_end_line_checkbox.isChecked()
        endianness = self.main_window.endianness_list.currentIndex()

        try:
            # VARIABLE OPTIONS
            text_start_offset = int(self.main_window.text_start_offset_input.text(), 16)
            text_end_offset = int(self.main_window.text_end_offset_input.text(), 16)
            if text_start_offset > text_end_offset:
                self.show_error_dialog("Text start offset can't be higher than text end offset.")
                print("Error: Extraction aborted!")
                return    
            text_size = text_end_offset - text_start_offset + 1
            base = int(self.main_window.pointers_base_input.text(), 16)
            rom_file = self.main_window.selected_rom_file_name.text()
            tbl_file = self.main_window.selected_tbl_file_name.text()
            
        except (ValueError, UnboundLocalError):
            self.show_error_dialog("Please fill in all required fields.")
            print("Error: Extraction aborted!")
            return

        #GET POINTERS
        if use_split_pointers_method:
            try:
                lsb_ptr_offset = int(self.main_window.lsb_offset_input.text(), 16)
                msb_ptr_offset = int(self.main_window.msb_offset_input.text(), 16)
                split_ptr_size = int(self.main_window.size_input.text(), 16)
            except (ValueError, UnboundLocalError):
                self.show_error_dialog("Please fill in all required fields.")
                print("Error: Extraction aborted!")
                return
            lsb = Decoder.read_rom(rom_file, lsb_ptr_offset, split_ptr_size)
            msb = Decoder.read_rom(rom_file, msb_ptr_offset, split_ptr_size)
            format_pointers = Decoder.process_pointers_split_2_bytes(lsb, msb, base)     
        else:
            try:
                pointers_start_offset = int(self.main_window.pointers_start_offset_input.text(), 16)
                pointers_end_offset = int(self.main_window.pointers_end_offset_input.text(), 16)
            except (ValueError, UnboundLocalError):
                self.show_error_dialog("Please fill in all required fields.")
                print("Error: Extraction aborted!")
                return
            if pointers_start_offset > pointers_end_offset:
                self.show_error_dialog("Pointers start offset can't be higher than pointers end offset.")
                print("Error: Extraction aborted!")
                return
            pointers_size = pointers_end_offset - pointers_start_offset + 1
            try:
                table_pointers = Decoder.read_rom(rom_file, pointers_start_offset, pointers_size)
            except FileNotFoundError as e:
                self.show_error_dialog(f"{e}")
                print("Error: Extraction aborted!")
                return
                       
            if self.main_window.radio_2_bytes.isChecked():
                format_pointers = Decoder.process_pointers_2_bytes(table_pointers, base, endianness)
                pointers_lenght = 2
                
            elif self.main_window.radio_3_bytes.isChecked():
                format_pointers = Decoder.process_pointers_3_bytes(table_pointers, base, endianness)
                pointers_lenght = 3
                
            elif self.main_window.radio_4_bytes.isChecked():                
                format_pointers = Decoder.process_pointers_4_bytes(table_pointers, base, endianness)
                pointers_lenght = 4

        # Load ROM data to RAM
        try:
            rom_data = Decoder.read_rom(rom_file, 0, os.path.getsize(rom_file))
        except FileNotFoundError as e:
            self.show_error_dialog(f"{e}")
            print("Error: Extraction aborted!")
            return

        # Check bracket
        if not use_custom_brackets:
            bracket_index = 0

        # Load char table to RAM
        try:
            char_table = Decoder.read_tbl(tbl_file, bracket_index)
        except FileNotFoundError as e:
            self.show_error_dialog(f"{e}")
            print("Error: Extraction aborted!")
            return

        # Decode Script
        if no_use_end_lines_for_split:
            script, total_bytes_read, lines_lenght = Decoder.decode_script_no_end_line(rom_data, format_pointers, text_end_offset + 1, char_table, bracket_index)            
        else:
            try:
                end_line = Decoder.parse_end_lines(self.main_window.end_line_input.text())
            except (ValueError, UnboundLocalError):
                self.show_error_dialog("Please fill in all required fields.")
                print("Error: Extraction aborted!")
                return    
            script, total_bytes_read, lines_lenght = Decoder.decode_script(rom_data, format_pointers, end_line, char_table, ignore_end_lines_code_until_decode, bracket_index)

        # Write Script
        if use_split_pointers_method and no_use_end_lines_for_split:
            decode_script = Decoder.write_out_file(out_file, script, lsb_ptr_offset, msb_ptr_offset + split_ptr_size - 1, split_ptr_size, format_pointers, lines_lenght, None, no_comments_lines)
            print(f"TEXT BLOCK SIZE: {text_size} / {hex(text_size)} bytes.")
            print(f"PTR_TABLE BLOCK SIZE: {split_ptr_size * 2} / {hex(split_ptr_size) * 2} bytes. Located {split_ptr_size} pointers.")
        elif use_split_pointers_method:
            decode_script = Decoder.write_out_file(out_file, script, lsb_ptr_offset, msb_ptr_offset + split_ptr_size - 1, split_ptr_size, format_pointers, lines_lenght, end_line, no_comments_lines)
            print(f"TEXT BLOCK SIZE: {text_size} / {hex(text_size)} bytes.")
            print(f"PTR_TABLE BLOCK SIZE: {split_ptr_size * 2} / {hex(split_ptr_size) * 2} bytes. Located {split_ptr_size} pointers.")
        elif no_use_end_lines_for_split:
            decode_script = Decoder.write_out_file(out_file, script, pointers_start_offset, pointers_start_offset + pointers_size - 1, pointers_size, format_pointers, lines_lenght, None, no_comments_lines)
            print(f"TEXT BLOCK SIZE: {text_size} / {hex(text_size)} bytes.")
            print(f"PTR_TABLE BLOCK SIZE: {pointers_size} / {hex(pointers_size)} bytes. Located {pointers_size//pointers_lenght} pointers.")
        else:
            decode_script = Decoder.write_out_file(out_file, script, pointers_start_offset, pointers_start_offset + pointers_size - 1, pointers_size, format_pointers, lines_lenght, end_line, no_comments_lines)
            print(f"TEXT BLOCK SIZE: {text_size} / {hex(text_size)} bytes.")
            print(f"PTR_TABLE BLOCK SIZE: {pointers_size} / {hex(pointers_size)} bytes. Located {pointers_size//pointers_lenght} pointers.")
        self.show_success_dialog("Script extracted successfully!")
        print("Script extracted successfully!")
            
    def process_insertion(self, rom_file):
        # CONSTANTS OPTIONS
        no_comments_lines = self.main_window.not_comment_lines_checkbox.isChecked()
        bracket_index = self.main_window.use_custom_brackets_for_hex_codes_list.currentIndex()
        bracket_index = self.main_window.use_custom_brackets_for_hex_codes_list.currentIndex()
        fill_free_space = self.main_window.fill_free_space_byte_checkbox.isChecked()
        if not fill_free_space and self.main_window.fill_free_space_byte_input.text() == "":
            fill_free_space_byte = bytes([0xFF])      
        else:
            try:
                fill_free_space_byte = bytes([int(self.main_window.fill_free_space_byte_input.text(), 16)])
            except ValueError:
                self.show_error_dialog(f"Fill byte is empty.")
                print("Error: Insertion aborted!")
                return
        not_use_end_lines = self.main_window.not_use_end_line_checkbox.isChecked()
        endianness = self.main_window.endianness_list.currentIndex()

        # VARIABLE OPTIONS
        try:
            original_text_start_offset = int(self.main_window.text_start_offset_input.text(), 16)
            original_text_end_offset = int(self.main_window.text_end_offset_input.text(), 16)
            if original_text_start_offset > original_text_end_offset:
                self.show_error_dialog("Text start offset can't be higher than text end offset.")
                print("Error: Insertion aborted!")
                return 
            original_text_size = original_text_end_offset - original_text_start_offset + 1
            base = int(self.main_window.pointers_base_input.text(), 16)
            rom_file = self.main_window.selected_rom_file_name.text()
            tbl_file = self.main_window.selected_tbl_file_name.text()
            script_file = self.main_window.selected_script_file_name.text()
        except (ValueError, UnboundLocalError):
            self.show_error_dialog("Please fill in all required fields.")
            print("Error: Insertion aborted!")
            return

        # Read Script file
        try:
            new_script, ignore1, ignore2, ignore3, ignore4 = Encoder.read_script(script_file)
        except FileNotFoundError as e:
            self.show_error_dialog(f"{e}")
            print("Error: Insertion aborted!")
            return

        # Parse line breakers.
        if not not_use_end_lines:
            try:
                end_line = Decoder.parse_end_lines(self.main_window.end_line_input.text())
            except ValueError:
                self.show_error_dialog("Please fill in all required fields.")
                print("Error: Insertion aborted!")
                return
                         
        # Load the character table
        try:
            char_table, longest_char = Encoder.read_tbl(tbl_file, bracket_index)
        except FileNotFoundError as e:
            self.show_error_dialog(f"{e}")
            print("Error: Insertion aborted!")
            return

        # Encode Text
        if not_use_end_lines:
            new_script_data, new_script_size, cumulative_lenghts = Encoder.encode_script(new_script, None, char_table, longest_char, not_use_end_lines, bracket_index)
        else:
            new_script_data, new_script_size, cumulative_lenghts = Encoder.encode_script(new_script, end_line, char_table, longest_char, not_use_end_lines, bracket_index)

        # Format Pointers
        if self.main_window.use_split_pointers_checkbox.isChecked():
            original_pointers_start_offset = int(self.main_window.lsb_offset_input.text(), 16)
            original_pointers_end_offset = int(self.main_window.msb_offset_input.text(), 16)
            if original_pointers_start_offset > original_pointers_end_offset:
                self.show_error_dialog("Pointers start offset can't be higher than pointers end offset.")
                print("Error: Extraction aborted!")
                return
            original_pointers_size = int(self.main_window.size_input.text(), 16)
            new_pointers_data_lsb, new_pointers_data_msb, new_pointers_size = Encoder.calculate_pointers_2_bytes_split(cumulative_lenghts, original_text_start_offset, base)
        else:
            try:
                original_pointers_start_offset = int(self.main_window.pointers_start_offset_input.text(), 16) 
                original_pointers_end_offset = int(self.main_window.pointers_end_offset_input.text(), 16)
            except (ValueError, UnboundLocalError):
                self.show_error_dialog("Please fill in all required fields.")
                print("Error: Insertion aborted!")
                return    
            if original_pointers_end_offset < original_pointers_start_offset:
                self.show_error_dialog(f"Error invalid offsets!")
                print("Error: Insertion aborted!")
                return
            original_pointers_size = original_pointers_end_offset - original_pointers_start_offset + 1
            if self.main_window.radio_2_bytes.isChecked():
                new_pointers_data, new_pointers_size = Encoder.calculate_pointers_2_bytes(cumulative_lenghts, original_text_start_offset, base, endianness)
                pointers_lenght = 2
                
            elif self.main_window.radio_3_bytes.isChecked():
                new_pointers_data, new_pointers_size = Encoder.calculate_pointers_3_bytes(cumulative_lenghts, original_text_start_offset, base, endianness)
                pointers_lenght = 3
                
            elif self.main_window.radio_4_bytes.isChecked():                
                new_pointers_data, new_pointers_size = Encoder.calculate_pointers_4_bytes(cumulative_lenghts, original_text_start_offset, base, endianness)
                pointers_lenght = 4
                
        # Write ROM
        if new_script_size > original_text_size:
            print(f"ERROR: script size has exceeded its maximum size. Remove {new_script_size - original_text_size} bytes.")
            return
        if new_pointers_size > original_pointers_size:
            print(f"ERROR: table pointer size has exceeded its maximum size. Remove {(new_pointers_size - original_pointers_size)//2} lines in script.")
            return
        try:
            free_space_script = Encoder.write_rom(rom_file, original_text_start_offset, original_text_size, new_script_data, fill_free_space, fill_free_space_byte)
            print(f"Script text write to address {hex(original_text_start_offset)}, {free_space_script} bytes free.")
        except FileNotFoundError as e:
            self.show_error_dialog(f"{e}")
            print("Error: Insertion aborted!")
            return
            
        if not self.main_window.use_split_pointers_checkbox.isChecked():
            free_space_pointers = Encoder.write_rom(rom_file, original_pointers_start_offset, original_pointers_size, new_pointers_data, fill_free_space, fill_free_space_byte)
            print(f"Pointer table write to address {hex(original_pointers_start_offset)}, {free_space_pointers//pointers_lenght} lines/pointers left.")

        else:
            free_space_pointers = Encoder.write_rom(rom_file, original_pointers_start_offset, original_pointers_size, new_pointers_data_lsb, fill_free_space, fill_free_space_byte)
            free_space_pointers = Encoder.write_rom(rom_file, original_pointers_end_offset, original_pointers_size, new_pointers_data_msb, fill_free_space, fill_free_space_byte)
            print(f"Pointer table write to address {hex(original_pointers_start_offset)}, {free_space_pointers//2} lines/pointers left.")
        self.show_success_dialog("Script inserted successfully!")
        print("Script inserted successfully!")
               
class Console(io.StringIO):
    def __init__(self, console):
        super().__init__()
        self.console = console

    def write(self, text):
        text = text.rstrip('\n')
        self.console.append(text)
       
class FileHandler:
    def __init__(self, main_window):
        self.main_window = main_window
        self.functions = Functions(main_window)

##    def dragEnterEvent(self, event):
##        if event.mimeData().hasUrls():
##            event.accept()
##        else:
##            event.ignore()
##
##    def dropEvent(self, event):
##        file_path = event.mimeData().urls()[0].toLocalFile()
##        self.open_config(file_path)

    def open_config(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self.main_window, "Open config file", "", "Config files (*.json);;All Files (*)", options=options)

        if file_name:
            try:
                with open(file_name, 'r') as file:
                    config_data = json.load(file)

                    # Files Config
                    self.main_window.selected_rom_file_name.setText(config_data.get("rom_file", ""))
                    self.main_window.selected_tbl_file_name.setText(config_data.get("tbl_file", ""))
                    self.main_window.selected_script_file_name.setText(config_data.get("script_file", ""))

                    # Pointers Config
                    pointer_size = config_data.get("pointer_size", "")
                    if pointer_size == "2 bytes":
                        self.main_window.radio_2_bytes.setChecked(True)
                    elif pointer_size == "3 bytes":
                        self.main_window.radio_3_bytes.setChecked(True)
                    elif pointer_size == "4 bytes":
                        self.main_window.radio_4_bytes.setChecked(True)

                    self.main_window.endianness_list.setCurrentIndex(config_data.get("endianess", 0))

                    # Offset Configs
                    self.main_window.pointers_start_offset_input.setText(config_data.get("pointers_start_offset", ""))
                    self.main_window.pointers_end_offset_input.setText(config_data.get("pointers_end_offset", ""))
                    self.main_window.pointers_base_input.setText(config_data.get("pointers_base", ""))
                    self.main_window.text_start_offset_input.setText(config_data.get("text_start_offset", ""))
                    self.main_window.text_end_offset_input.setText(config_data.get("text_end_offset", ""))
                    self.main_window.end_line_input.setText(config_data.get("end_line", ""))
                    self.main_window.fill_free_space_byte_input.setText(config_data.get("fill_free_space_byte", ""))
                    self.main_window.lsb_offset_input.setText(config_data.get("split_ptr_lsb_offset", ""))
                    self.main_window.msb_offset_input.setText(config_data.get("split_ptr_msb_offset", ""))
                    self.main_window.size_input.setText(config_data.get("split_ptr_size", ""))

                    # Advanced Options Config
                    self.main_window.not_comment_lines_checkbox.setChecked(config_data.get("no_use_comments_lines", False))
                    self.main_window.use_custom_brackets_for_hex_codes_checkbox.setChecked(config_data.get("use_custom_brackets", False))
                    self.main_window.use_custom_brackets_for_hex_codes_list.setCurrentIndex(config_data.get("brackets", 0))
                    self.main_window.fill_free_space_byte_checkbox.setChecked(config_data.get("fill_free_space", False))
                    self.main_window.use_split_pointers_checkbox.setChecked(config_data.get("use_split_pointers", False))
                    self.main_window.ignore_end_line_checkbox.setChecked(config_data.get("ignore_end_line", False))
                    self.main_window.not_use_end_line_checkbox.setChecked(config_data.get("not_use_end_line", False))

                print("Config imported successfully!")
                self.functions.enable_extract_button()
                self.functions.enable_insert_button()
            except Exception as e:
                self.functions.show_error_dialog("Error importing config")
                print(f"Error importing config: {e}")
                return

    def save_config(self):
        options = QFileDialog.Options()
        rom_file = self.main_window.selected_rom_file_name.text()
        if rom_file:
            file_name, _ = QFileDialog.getSaveFileName(self.main_window, "Save config file", os.path.splitext(rom_file)[0] + "_config", "Config files (*.json);;All Files (*)", options=options)
        else:
            file_name, _ = QFileDialog.getSaveFileName(self.main_window, "Save config file", "config", "Config files (*.json);;All Files (*)", options=options)
        if file_name:
            try:
                config_data = {}

                # Select Files Configs
                rom_file_path = self.main_window.selected_rom_file_name.text().strip()
                if rom_file_path:
                    config_data["rom_file"] = rom_file_path

                tbl_file_path = self.main_window.selected_tbl_file_name.text().strip()
                if tbl_file_path:
                    config_data["tbl_file"] = tbl_file_path

                script_file_path = self.main_window.selected_script_file_name.text().strip()
                if script_file_path:
                    config_data["script_file"] = script_file_path

                # Set Pointers Configs
                if self.main_window.radio_2_bytes.isChecked():
                    config_data["pointer_size"] = "2 bytes"
                    
                elif self.main_window.radio_3_bytes.isChecked():
                    config_data["pointer_size"] = "3 bytes"
                    
                elif self.main_window.radio_4_bytes.isChecked():
                    config_data["pointer_size"] = "4 bytes"
                    
                config_data["endianess"] = self.main_window.endianness_list.currentIndex()

                # Set Offset Configs
                pointers_start_offset = self.main_window.pointers_start_offset_input.text().strip()
                if pointers_start_offset:
                    config_data["pointers_start_offset"] = pointers_start_offset

                pointers_end_offset = self.main_window.pointers_end_offset_input.text().strip()
                if pointers_end_offset:
                    config_data["pointers_end_offset"] = pointers_end_offset
                
                pointers_base = self.main_window.pointers_base_input.text().strip()
                if pointers_base:
                    config_data["pointers_base"] = pointers_base

                text_start_offset = self.main_window.text_start_offset_input.text().strip()
                if text_start_offset:
                    config_data["text_start_offset"] = text_start_offset

                text_end_offset = self.main_window.text_end_offset_input.text().strip()
                if text_end_offset:
                    config_data["text_end_offset"] = text_end_offset

                end_line = self.main_window.end_line_input.text().strip()
                if end_line:
                    config_data["end_line"] = end_line

                fill_free_space_byte = self.main_window.fill_free_space_byte_input.text().strip()
                if fill_free_space_byte:
                    config_data["fill_free_space_byte"] = fill_free_space_byte

                split_ptr_lsb_offset = self.main_window.lsb_offset_input.text().strip()
                if split_ptr_lsb_offset:
                    config_data["split_ptr_lsb_offset"] = split_ptr_lsb_offset

                split_ptr_msb_offset = self.main_window.msb_offset_input.text().strip()
                if split_ptr_msb_offset:
                    config_data["split_ptr_msb_offset"] = split_ptr_msb_offset

                split_ptr_size = self.main_window.size_input.text().strip()
                if split_ptr_size:
                    config_data["split_ptr_size"] = split_ptr_size

                # Advanced Options Configs
                config_data["no_use_comments_lines"] = self.main_window.not_comment_lines_checkbox.isChecked()
                config_data["use_custom_brackets"] = self.main_window.use_custom_brackets_for_hex_codes_checkbox.isChecked()
                config_data["brackets"] = self.main_window.use_custom_brackets_for_hex_codes_list.currentIndex()
                config_data["fill_free_space"] = self.main_window.fill_free_space_byte_checkbox.isChecked()           
                config_data["use_split_pointers"] = self.main_window.use_split_pointers_checkbox.isChecked()
                config_data["ignore_end_line"] = self.main_window.ignore_end_line_checkbox.isChecked()
                config_data["not_use_end_line"] = self.main_window.not_use_end_line_checkbox.isChecked()

                with open(file_name, 'w') as file:
                    json.dump(config_data, file, indent=4)
                print("Config exported successfully!")
            except Exception as e:
                self.functions.show_error_dialog("Error exporting config")
                print(f"Error exporting config: {e}")
                return

    def select_rom_file(self):
        try:
            options = QFileDialog.Options()
            rom_file, _ = QFileDialog.getOpenFileName(self.main_window, "Select ROM file", "", 
            "All ROM files (*.nes *.fds *.smc *.sfc *.gb *.gbc *.gbs *.gba *.sms *.gg *.bin *.gen *.md *.smd *.pce *.sgx *.cue *.hes *.sg *.vb);;"
            "NES ROM files (*.nes *.fds);;"
            "SNES ROM files (*.smc *.sfc);;"
            "GB ROM files (*.gb *.gbc *.gbs *.gba);;"
            "SMS/GG ROM files (*.sms *.gg);;"
            "MEGADRIVE/GENESIS ROM files (*.bin *.gen *.md *.smd);;"
            "PC Engine ROM files (*.pce *.sgx *.cue *.hes);;"
            "SG-1000 ROM files (*.sg);;"
            "Virtual Boy ROM files (*.vb);;"
            "All Files (*)", 
            options=options)

            if rom_file:
                self.main_window.selected_rom_file_name.setText(rom_file)
                print(f"Selected ROM: {rom_file}")
                self.functions.enable_extract_button()
                self.functions.enable_insert_button()
        except Exception as e:
            self.functions.show_error_dialog("Error selecting ROM file: {e}")
            print(f"Error selecting ROM file: {e}")
            return

    def select_tbl_file(self):
        try:
            options = QFileDialog.Options()
            tbl_file, _ = QFileDialog.getOpenFileName(self.main_window, "Select TBL file", "", "Thingy table files (*.tbl);;All Files (*)", options=options)

            if tbl_file:
                self.main_window.selected_tbl_file_name.setText(tbl_file)
                print(f"Selected TBL: {tbl_file}")
                self.functions.enable_extract_button()
                self.functions.enable_insert_button()
        except Exception as e:
            self.functions.show_error_dialog("Error selecting TBL file: {e}")
            print(f"Error selecting TBL file: {e}")
            return

    def select_script_file(self):
        try:
            options = QFileDialog.Options()
            script_file, _ = QFileDialog.getOpenFileName(self.main_window, "Select Script file", "", "All Data files (*.bin *.txt);;Binary files (*.bin);;Text files (*.txt);;All Files (*)", options=options)

            if script_file:
                self.main_window.selected_script_file_name.setText(script_file)
                print(f"Selected Script: {script_file}")
                self.functions.enable_insert_button()
        except Exception as e:
            self.functions.show_error_dialog("Error selecting Script file: {e}")
            print(f"Error selecting Script file: {e}")
            return

    def select_output_file(self):
        try:
            options = QFileDialog.Options()
            rom_file = self.main_window.selected_rom_file_name.text()
            if rom_file:
                out_file, _ = QFileDialog.getSaveFileName(self.main_window, "Select Output File", os.path.splitext(rom_file)[0] + "_script",
                "All Data files (*.bin *.txt);;Binary files (*.bin);;Text files (*.txt);;All Files (*)", options=options)
            else:
                out_file, _ = QFileDialog.getSaveFileName(self.main_window, "Select Output File", "script",
                "All Data files (*.bin *.txt);;Binary files (*.bin));;Text files (*.txt);;All Files (*)", options=options)

            if out_file:
                print(f"Output file selected: {out_file}")
                self.functions.process_extraction(out_file)
        except Exception as e:
            self.functions.show_error_dialog("Error selecting Output file: {e}")
            print(f"Error selecting Output file: {e}")
            return

class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Class instances
        self.functions = Functions(self)  
        self.file_handler = FileHandler(self)

        # Initial setup
        self.setWindowTitle('HexString v1.3.0')   
        icon_path = os.path.join('resources', 'icon.ico')
        self.setWindowIcon(QIcon(icon_path))
        
        self.setFixedSize(475, 667)  #475, 667
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        self.tabs = QTabWidget(self)
        central_layout = QVBoxLayout()
        central_layout.addWidget(self.tabs)

##        self.progress_bar = QProgressBar(self)
##        self.progress_bar.setRange(0, 100)
##        self.progress_bar.setValue(0) 
##        self.progress_bar.setVisible(False)
##        central_layout.addWidget(self.progress_bar)
        
        # Create tab environmnet
        self.create_tabs()
        central_widget.setLayout(central_layout)
        self.create_menu()

        # Configure tooltip
        QApplication.instance().setStyleSheet("QToolTip { background-color: yellow; color: black; border: 1px solid black; }")

        # Drop configs (experimental)
        #self.setAcceptDrops(True)

##    def dragEnterEvent(self, event):
##        self.file_handler.dragEnterEvent(event)
##
##    def dropEvent(self, event):
##        self.file_handler.dropEvent(event)
        
    def create_menu(self):
        menubar = self.menuBar()

        # Create file menu
        file_menu = menubar.addMenu('File')

        # File functions
        new_action = QAction('New', self)
        new_action.triggered.connect(self.functions.reset_fields)
        open_action = QAction('Open config', self)
        open_action.triggered.connect(self.file_handler.open_config)
        save_action = QAction('Save config', self)
        save_action.triggered.connect(self.file_handler.save_config)
        exit_action = QAction('Exit', self)
        exit_action.triggered.connect(self.close)

        # File add functions
        file_menu.addAction(new_action) 
        file_menu.addAction(open_action)
        file_menu.addAction(save_action)
        file_menu.addSeparator() 
        file_menu.addAction(exit_action)

        # Create help menu
        help_menu = menubar.addMenu('Help')

        # Help functions
        about_action = QAction('About', self)
        about_action.triggered.connect(self.show_about)

        # Help add functions
        help_menu.addAction(about_action)
         
    def create_tabs(self):
        # Create dump text tab
        dump_text_tab = QWidget()
        dump_text_layout = QVBoxLayout()
        
        # Extract Fuctions
        dump_text_layout.addWidget(self.create_select_file_groupbox())
        dump_text_layout.addWidget(self.create_set_pointers_groupbox())
        dump_text_layout.addWidget(self.create_set_offsets_groupbox())
        dump_text_layout.addWidget(self.create_advanced_options_groupbox())       
        dump_text_layout.addWidget(self.create_console())
        dump_text_layout.addLayout(self.create_actions_buttons())
        dump_text_tab .setLayout(dump_text_layout)

        # Create miscellaneous tab
        miscellaneous_tab = QWidget()
        miscellaneous_layout = QVBoxLayout()
        
        miscellaneous_tab.setLayout(miscellaneous_layout)

        # Add to QTabWidget
        self.tabs.addTab(dump_text_tab, "Uncompressed Text")
        #self.tabs.addTab(miscellaneous_tab, "Compressed Text")

    def create_select_file_groupbox(self):
        group_box = QGroupBox("Select Files", self)
        group_box.setMinimumHeight(120)
        group_box.setMaximumHeight(120)
        group_box.setMaximumWidth(430)
        layout = QVBoxLayout()

        # Open ROM
        select_layout = QHBoxLayout()
        self.select_rom_label = QLabel("Open ROM:", self)
        self.selected_rom_file_name = QLineEdit(self)
        self.selected_rom_file_name.setPlaceholderText("No file selected")
        self.selected_rom_file_name.setReadOnly(True)
        self.select_rom_button = QPushButton("...", self)
        self.select_rom_button.clicked.connect(self.file_handler.select_rom_file)
        self.select_rom_button.setFixedWidth(30)

        select_layout.addWidget(self.select_rom_label)
        select_layout.addWidget(self.selected_rom_file_name)
        select_layout.addWidget(self.select_rom_button)
        layout.addLayout(select_layout)

        # Open TBL
        self.open_tbl_label = QLabel("Open TBL:", self)
        self.selected_tbl_file_name = QLineEdit(self)
        self.selected_tbl_file_name.setPlaceholderText("No file selected")
        self.selected_tbl_file_name.setReadOnly(True)
        self.select_tbl_button = QPushButton("...", self)
        self.select_tbl_button.clicked.connect(self.file_handler.select_tbl_file)
        self.select_tbl_button.setFixedWidth(30)

        tbl_select_layout = QHBoxLayout()
        tbl_select_layout.addWidget(self.open_tbl_label)
        tbl_select_layout.addWidget(self.selected_tbl_file_name)
        tbl_select_layout.addWidget(self.select_tbl_button)
        layout.addLayout(tbl_select_layout)

        # Open Script
        self.open_script_label = QLabel("Open Script:", self)
        self.selected_script_file_name = QLineEdit(self)
        self.selected_script_file_name.setPlaceholderText("No file selected")
        self.selected_script_file_name.setReadOnly(True)
        self.select_script_button = QPushButton("...", self)
        self.select_script_button.clicked.connect(self.file_handler.select_script_file)
        self.select_script_button.setFixedWidth(30)

        script_select_layout = QHBoxLayout()
        script_select_layout.addWidget(self.open_script_label)
        script_select_layout.addWidget(self.selected_script_file_name)
        script_select_layout.addWidget(self.select_script_button)
        layout.addLayout(script_select_layout)

        group_box.setLayout(layout)
        return group_box

    def create_set_pointers_groupbox(self):
        group_box = QGroupBox("Set Pointers", self)
        group_box.setMinimumHeight(100)
        group_box.setMaximumHeight(100)
        group_box.setMaximumWidth(430)
        layout = QVBoxLayout()

        # Pointers Length
        pointers_length_layout = QHBoxLayout()
        self.pointers_length_label = QLabel("Pointers Length:", self)
        self.radio_2_bytes = QRadioButton("2 bytes", self)
        self.radio_3_bytes = QRadioButton("3 bytes", self)
        self.radio_4_bytes = QRadioButton("4 bytes", self)
        self.radio_2_bytes.setChecked(True)
        pointers_length_layout.addWidget(self.pointers_length_label)
        pointers_length_layout.addWidget(self.radio_2_bytes)
        pointers_length_layout.addWidget(self.radio_3_bytes)
        pointers_length_layout.addWidget(self.radio_4_bytes)
        layout.addLayout(pointers_length_layout)

        # Endianness
        endianness_layout = QGridLayout()
        self.endianness_label = QLabel("Endianness:", self)
        self.endianness_spacer_label = QLabel("", self)
        self.endianness_spacer_label.setFixedWidth(70)
        self.endianness_list = QComboBox(self)
        self.endianness_list.addItem("Little Endian", 0)
        self.endianness_list.addItem("Big Endian", 1)
        self.endianness_list.setCurrentIndex(0)
        endianness_layout.addWidget(self.endianness_label, 0, 0)
        endianness_layout.addWidget(self.endianness_list, 0, 1)
        endianness_layout.addWidget(self.endianness_spacer_label, 0, 2)
        layout.addLayout(endianness_layout)

        # Add all to group box
        group_box.setLayout(layout)

        return group_box

    def create_set_offsets_groupbox(self):
        group_box = QGroupBox("Set Offsets", self)
        group_box.setMinimumHeight(130)
        group_box.setMaximumHeight(130)
        group_box.setMaximumWidth(430)
        group_layout = QGridLayout()
        group_layout.setSpacing(0)

        # Spacer
        self.spacer_label = QLabel("", self)
        self.spacer_label.setFixedWidth(20)
        
        # Pointers Start Offset
        self.pointers_start_offset_label = QLabel("Pointers Start Offset:", self)
        self.pointers_start_offset_input = QLineEdit(self)
        self.pointers_start_offset_input.setPlaceholderText("00000000")
        self.pointers_start_offset_input.setFixedWidth(65)
        self.pointers_start_offset_input.setMaxLength(8)
        self.pointers_start_offset_input.setValidator(QRegExpValidator(QRegExp("[0-9A-Fa-f]{1,8}")))
        self.functions.set_uppercase_formatting(self.pointers_start_offset_input)

        # Text Start Offset
        self.text_start_offset_label = QLabel("Text Start Offset:", self)
        self.text_start_offset_input = QLineEdit(self)
        self.text_start_offset_input.setPlaceholderText("00000000")
        self.text_start_offset_input.setFixedWidth(65)
        self.text_start_offset_input.setMaxLength(8)
        self.text_start_offset_input.setValidator(QRegExpValidator(QRegExp("[0-9A-Fa-f]{1,8}")))
        self.functions.set_uppercase_formatting(self.text_start_offset_input)
    
        # Pointers End Offset   
        self.pointers_end_offset_label = QLabel("Pointers End Offset:")
        self.pointers_end_offset_input = QLineEdit(self)
        self.pointers_end_offset_input.setPlaceholderText("00000000")
        self.pointers_end_offset_input.setFixedWidth(65)
        self.pointers_end_offset_input.setMaxLength(8)
        self.pointers_end_offset_input.setValidator(QRegExpValidator(QRegExp("[0-9A-Fa-f]{1,8}")))
        self.functions.set_uppercase_formatting(self.pointers_end_offset_input)

        # Text End Offset
        self.text_end_offset_label = QLabel("Text End Offset:", self)
        self.text_end_offset_input = QLineEdit(self)
        self.text_end_offset_input.setPlaceholderText("00000000")
        self.text_end_offset_input.setFixedWidth(65)
        self.text_end_offset_input.setMaxLength(8)
        self.text_end_offset_input.setValidator(QRegExpValidator(QRegExp("[0-9A-Fa-f]{1,8}")))
        self.functions.set_uppercase_formatting(self.text_end_offset_input)
        
        # Pointers Base Offset   
        self.pointers_base_label = QLabel("Pointers Base:")
        self.pointers_base_label.setToolTip("Difference between pointers and text.\nIf the ROM has a header, add it.")
        self.pointers_base_input = QLineEdit(self)
        self.pointers_base_input.setPlaceholderText("00000000")
        self.pointers_base_input.setFixedWidth(65)
        self.pointers_base_input.setMaxLength(9)
        self.pointers_base_input.setValidator(QRegExpValidator(QRegExp("^[-]?[0-9A-Fa-f]{1,8}$")))
        self.functions.set_uppercase_formatting(self.pointers_base_input)
        
        # End Line Split Code     
        self.end_line_label = QLabel("End Line:")
        self.end_line_label.setToolTip('Code used to split lines.\nTip: Use multiple separated by ","')
        self.end_line_input = QLineEdit(self)
        self.end_line_input.setPlaceholderText("00,00,00")
        self.end_line_input.setFixedWidth(65)
        self.end_line_input.setMaxLength(11)
        self.end_line_input.setValidator(QRegExpValidator(QRegExp("^([0-9A-Fa-f]{2})(,([0-9A-Fa-f]{2}))*$")))
        self.functions.set_uppercase_formatting(self.end_line_input)

        # Grid Layout
        group_layout.addWidget(self.pointers_start_offset_label, 0, 0)
        group_layout.addWidget(self.functions.create_prefix_label(), 0, 1)
        group_layout.addWidget(self.pointers_start_offset_input, 0, 2)
        group_layout.addWidget(self.spacer_label, 0, 3)
        group_layout.addWidget(self.text_start_offset_label,0, 4)
        group_layout.addWidget(self.functions.create_prefix_label(), 0, 5)
        group_layout.addWidget(self.text_start_offset_input, 0, 6)
        
        group_layout.addWidget(self.pointers_end_offset_label, 1, 0)
        group_layout.addWidget(self.functions.create_prefix_label(), 1, 1)
        group_layout.addWidget(self.pointers_end_offset_input, 1, 2)
        group_layout.addWidget(self.text_end_offset_label, 1, 4)
        group_layout.addWidget(self.functions.create_prefix_label(), 1, 5)
        group_layout.addWidget(self.text_end_offset_input, 1, 6)

        group_layout.addWidget(self.pointers_base_label, 2, 0)
        group_layout.addWidget(self.functions.create_prefix_label(), 2, 1)
        group_layout.addWidget(self.pointers_base_input, 2, 2)
        group_layout.addWidget(self.end_line_label, 2, 4)
        group_layout.addWidget(self.functions.create_prefix_label(), 2, 5)
        group_layout.addWidget(self.end_line_input, 2, 6)

        group_box.setLayout(group_layout)
        
        return group_box

    def create_advanced_options_groupbox(self):
        group_box = QGroupBox(self)
        group_box.setMaximumWidth(430)
        layout = QVBoxLayout()

        # Create advance options button
        self.expand_button = QPushButton("Show Advanced Options", self)
        self.expand_button.setFixedWidth(200)
        self.expand_button.setCheckable(True)
        self.expand_button.setChecked(False)
        self.expand_button.clicked.connect(self.functions.toggle_advanced_options)

        # Button content
        self.advanced_options_container = QWidget(self) 
        advanced_layout = QVBoxLayout()
        advanced_layout.setContentsMargins(0, 0, 0, 0)

        # 1.- Not comment lines 
        self.not_comment_lines_checkbox = QCheckBox("Not duplicate line as a comment.", self)
        self.not_comment_lines_checkbox.setToolTip("Use this if you don't want a duplicate line as a comment.\n"'Note: comments will start with ";".') 
        advanced_layout.addWidget(self.not_comment_lines_checkbox)

        # 2.- Use custom brackets for raw hex codes.
        self.use_custom_brackets_for_hex_codes_checkbox = QCheckBox("Use custom brackets for raw hex codes.", self)
        self.use_custom_brackets_for_hex_codes_checkbox.setToolTip("Unassigned characters in the table will be represented between them.")
        self.use_custom_brackets_for_hex_codes_checkbox.toggled.connect(self.functions.toggle_custom_brackets)
        self.use_custom_brackets_for_hex_codes_list = QComboBox(self)
        self.use_custom_brackets_for_hex_codes_list.setFixedWidth(50)
        self.use_custom_brackets_for_hex_codes_list.setDisabled(True)
        self.use_custom_brackets_for_hex_codes_list.addItem("~ ~", 0)
        self.use_custom_brackets_for_hex_codes_list.addItem("[ ]", 1)
        self.use_custom_brackets_for_hex_codes_list.addItem("{ }", 2)
        self.use_custom_brackets_for_hex_codes_list.addItem("< >", 3)
        self.use_custom_brackets_for_hex_codes_list.setCurrentIndex(0)
        self.use_custom_brackets_for_hex_codes_spacer = QLabel("", self)
        self.use_custom_brackets_for_hex_codes_spacer.setFixedWidth(80)
        
        use_custom_brackets = QHBoxLayout()
        use_custom_brackets.setContentsMargins(0, 0, 0, 0)
        use_custom_brackets.setSpacing(0)
        use_custom_brackets.addWidget(self.use_custom_brackets_for_hex_codes_checkbox)
        use_custom_brackets.addWidget(self.use_custom_brackets_for_hex_codes_list)
        use_custom_brackets.addWidget(self.use_custom_brackets_for_hex_codes_spacer)                                             
        
        use_custom_brackets_widget = QWidget(self)
        use_custom_brackets_widget.setLayout(use_custom_brackets)

        advanced_layout.addWidget(use_custom_brackets_widget)


        # 3.- Fill free space with byte

        self.fill_free_space_byte_checkbox = QCheckBox("Fill free space when inserting with the next byte.", self)
        self.fill_free_space_byte_checkbox.setToolTip("Use this if you want to fill the free space left when you insert the script with a custom byte.\nOnly when inserted.")
        self.fill_free_space_byte_checkbox.stateChanged.connect(self.functions.toggle_fill_free_space)
        self.fill_free_space_byte_input = QLineEdit(self)
        self.fill_free_space_byte_input.setPlaceholderText("FF")
        self.fill_free_space_byte_input.setText("FF")
        self.fill_free_space_byte_input.setValidator(QRegExpValidator(QRegExp("[0-9A-Fa-f,]{1,2}")))
        self.fill_free_space_byte_input.setDisabled(True)
        self.fill_free_space_byte_input.setFixedWidth(25)
        self.functions.set_uppercase_formatting(self.fill_free_space_byte_input)
        self.fill_free_space_byte_spacer = QLabel ("", self)
        self.fill_free_space_byte_spacer.setFixedWidth(50)

        fill_free_space = QHBoxLayout()
        fill_free_space.setSpacing(0)
        fill_free_space.setContentsMargins(0, 0, 0, 0)
        fill_free_space.addWidget(self.fill_free_space_byte_checkbox)
        fill_free_space.addWidget(self.functions.create_prefix_label())
        fill_free_space.addWidget(self.fill_free_space_byte_input)
        fill_free_space.addWidget(self.fill_free_space_byte_spacer)

        fill_free_space_widget = QWidget(self)
        fill_free_space_widget.setLayout(fill_free_space)

        advanced_layout.addWidget(fill_free_space_widget)
        
        
        # 4.- Use split pointers extraction (2 bytes only)
        self.use_split_pointers_checkbox = QCheckBox("Use split pointers method (2 bytes only).", self)
        self.use_split_pointers_checkbox.setToolTip("Use it if the pointer table is divided into 2 parts.\nLSB: Lest significant bytes.\nMSB: Most significant bytes.\nSize: Numbers of pointers <hex>.")
        self.use_split_pointers_checkbox.stateChanged.connect(self.functions.toggle_split_pointers)
        advanced_layout.addWidget(self.use_split_pointers_checkbox)

        self.spacer_label = QLabel("", self)
        self.spacer_label.setFixedWidth(10)

        self.lsb_offset_label = QLabel("LSB Offset:", self)
        self.lsb_offset_input = QLineEdit(self)
        self.lsb_offset_input.setPlaceholderText("000000")
        self.lsb_offset_input.setFixedWidth(60)
        self.lsb_offset_input.setValidator(QRegExpValidator(QRegExp("[0-9A-Fa-f]{1,8}")))
        self.functions.set_uppercase_formatting(self.lsb_offset_input)

        self.msb_offset_label = QLabel("MSB Offset:", self)
        self.msb_offset_input = QLineEdit(self)
        self.msb_offset_input.setPlaceholderText("000000")
        self.msb_offset_input.setFixedWidth(60)
        self.msb_offset_input.setValidator(QRegExpValidator(QRegExp("[0-9A-Fa-f]{1,8}")))
        self.functions.set_uppercase_formatting(self.msb_offset_input)

        self.size_label = QLabel("Size:", self)
        self.size_input = QLineEdit(self)
        self.size_input.setPlaceholderText("0000")
        self.size_input.setFixedWidth(40)
        self.size_input.setValidator(QRegExpValidator(QRegExp("[0-9A-Fa-f]{1,8}")))
        self.functions.set_uppercase_formatting(self.size_input)

        grid_layout = QGridLayout()
        grid_layout.setSpacing(0)

        grid_layout.addWidget(self.lsb_offset_label, 0, 0)
        grid_layout.addWidget(self.functions.create_prefix_label(), 0, 1)
        grid_layout.addWidget(self.lsb_offset_input, 0, 2)
        grid_layout.addWidget(self.spacer_label, 0,3)

        grid_layout.addWidget(self.msb_offset_label, 0, 4)
        grid_layout.addWidget(self.functions.create_prefix_label(), 0, 5)
        grid_layout.addWidget(self.msb_offset_input, 0, 6)
        grid_layout.addWidget(self.spacer_label, 0, 7)

        grid_layout.addWidget(self.size_label, 0, 8)
        grid_layout.addWidget(self.functions.create_prefix_label(), 0, 9)
        grid_layout.addWidget(self.size_input, 0, 10)

        self.functions.disable_layout_widgets(grid_layout)
        advanced_layout.addLayout(grid_layout)
        
        # 5.- Ignore end line codes before decoding box.
        self.ignore_end_line_checkbox = QCheckBox("At extract ignore end line code until some character are decoded.", self)
        self.ignore_end_line_checkbox.setToolTip("Use this if the game has a control code at the start equal to the end of the line.\nOnly when extracted.")
        self.ignore_end_line_checkbox.stateChanged.connect(self.functions.toggle_ignore_end_line_before_decoding)
        advanced_layout.addWidget(self.ignore_end_line_checkbox)

        # 6.- Not use end line
        self.not_use_end_line_checkbox = QCheckBox("Not use end line code for split lines (Use pointers lenght).", self)
        self.not_use_end_line_checkbox.setToolTip("Use this if the game does not support a fixed line ending code,\nAt 'extract' lines will be split based on the difference between pointers.\nAt 'Insert' pointer will be calculated based in every line lenght in the script.")
        self.not_use_end_line_checkbox.stateChanged.connect(self.functions.toggle_not_use_end_line)
        advanced_layout.addWidget(self.not_use_end_line_checkbox)


        self.advanced_options_container.setLayout(advanced_layout)
        self.advanced_options_container.setVisible(False)

        # Added Button
        layout.addWidget(self.expand_button)
        layout.addWidget(self.advanced_options_container)
        group_box.setLayout(layout)
        
        return group_box

    def create_console(self):
        console_widget = QWidget(self)
        layout = QVBoxLayout()

        self.show_console = QTextEdit(self)
        self.show_console.setMinimumHeight(80)
        self.show_console.setMaximumHeight(80)
        self.show_console.setMaximumWidth(430)
        self.show_console.setReadOnly(True)
##        self.show_console.setStyleSheet("""
##            background-color: black;
##            color: white;
##            font-family: Courier New, monospace;
##            font-size: 12px;
##        """)
        
        layout.addWidget(self.show_console)
        console_widget.setLayout(layout)
        sys.stdout = Console(self.show_console)

        return console_widget
    
    def create_actions_buttons(self):
        self.extract_button = QPushButton("Extract Script and Save", self)
        self.extract_button.clicked.connect(self.file_handler.select_output_file)
        self.extract_button.setFixedWidth(150)
        self.extract_button.setDisabled(True)

        self.insert_button = QPushButton("Insert Script to ROM", self)
        self.insert_button.clicked.connect(self.functions.process_insertion)
        self.insert_button.setFixedWidth(150)
        self.insert_button.setDisabled(True)

        button_layout = QHBoxLayout()
        
        button_layout.addWidget(self.extract_button)
        button_layout.addWidget(self.insert_button)

        return button_layout

    def show_about(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("About")
        dialog.setFixedSize(dialog.sizeHint())
        dialog.setWindowFlag(Qt.WindowContextHelpButtonHint, False)

        layout = QVBoxLayout()

        about_version = (
            "HexString v1.3.0.<br>"
            "Created by koda.<br><br>"
            "Home: "
            "<a href='https://github.com/KodingBTW/hexstring'>https://github.com/KodingBTW/hexstring</a><br><br>"
        )

        about_text = QLabel()
        about_text.setTextFormat(Qt.RichText)
        about_text.setText(about_version)
        about_text.setOpenExternalLinks(True)
        about_text.setAlignment(Qt.AlignCenter)

        license_groupbox = QGroupBox("GNU General Public License")
        #license_groupbox.setStyleSheet("background-color: #e0e0e0; border-radius: 5px; padding: 10px;")
        license_layout = QVBoxLayout()
    
        license_text = QTextEdit()
        license_text.setReadOnly(True)
        license_text.setTextInteractionFlags(Qt.TextBrowserInteraction)
        license_text.setText(
        """<p>This program is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; either version 3 of the License, or at your option any later version.</p>
        <p>This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.</p>
        <p>You should have received a copy of the GNU General Public License along with this program. If not, see <a href='https://www.gnu.org/licenses/'>https://www.gnu.org/licenses/</a>.</p>"""
        )
      
        license_layout.addWidget(license_text)
        license_groupbox.setLayout(license_layout)
        
        button = QDialogButtonBox(QDialogButtonBox.Ok)
        button.accepted.connect(dialog.accept)

        layout.addWidget(about_text)
        layout.addWidget(license_groupbox)
        layout.addWidget(button)

        dialog.setLayout(layout)
        dialog.exec_()
    
if __name__ == '__main__':
    if len(sys.argv) > 1:
        cli = CLI()  
        cli.parse_arguments()
        cli.run()
    else:
        app = QApplication(sys.argv)
        basedir = os.path.dirname(__file__)
        app.setWindowIcon(QtGui.QIcon(os.path.join(basedir, 'resources', 'hand.ico')))
        process = 'HexString130'
        windll.shell32.SetCurrentProcessExplicitAppUserModelID(process)
        hexstring = MyWindow()
        hexstring.show()
        #debbug
##        sys._excepthook = sys.excepthook 
##        def exception_hook(exctype, value, traceback):
##            print(exctype, value, traceback)
##            sys._excepthook(exctype, value, traceback) 
##            sys.exit(1) 
##        sys.excepthook = exception_hook

        sys.exit(app.exec_())
