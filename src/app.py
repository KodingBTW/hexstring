# This program is a tool designed for dump scripts from ROM games
# It allows users to extract text, edit it, and then reinsert the modified text back into the ROM.
# 
# Features:
# - Extract text from ROM files
# - Modify the extracted text
# - Insert the modified text back into the ROM
# - Configurable options for pointers, end offsets, and more
#
# Dependencies:
# - Check requirements.txt
#
# License:
# This program is licensed under the GNU General Public License v3 (GPL-3.0).
# You can redistribute and/or modify it under the terms of the GPL-3.0 License.
# For more details, see the LICENSE file in the project directory.
#
# Build Information:
# Check config.py

import sys
import os
import io
import json
from config import app_name, version, author, date, hour, license, url, resources_path, icon_file
from decoder import Decoder
from encoder import Encoder
from lempel_ziv import Lempel_ziv
from analizer import Analizer
from cli import CLI
from PyQt5.QtWidgets import QApplication, QMainWindow, QAction, QSizePolicy, QSpacerItem, QMenuBar, QMenu, QGridLayout, QVBoxLayout, QWidget, QMessageBox, QPlainTextEdit, QTabWidget, QLineEdit, QFileDialog, QLabel, QPushButton, QHBoxLayout, QGroupBox, QRadioButton, QComboBox, QCheckBox, QToolTip, QTextEdit, QDialog, QDialogButtonBox, QProgressBar
from PyQt5.QtGui import QIcon, QRegExpValidator
from PyQt5.QtCore import QRegExp, Qt, QSettings
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
        self.main_window.use_custom_brackets_for_hex_codes_list.setCurrentIndex(0)
        self.main_window.fill_free_space_byte_checkbox.setChecked(False)
        self.main_window.fill_free_space_byte_input.setText("FF")  
        self.main_window.use_split_pointers_checkbox.setChecked(False)
        self.main_window.lsb_offset_input.clear()
        self.main_window.msb_offset_input.clear()
        self.main_window.size_input.clear()   
        self.main_window.not_use_end_line_checkbox.setChecked(False)

        # Compressed Text Tools Fields
        self.main_window.use_compression_algorithm_method_checkbox.setChecked(False)
        self.main_window.compression_method_list.setCurrentIndex(0)
        self.main_window.compression_type_list.setCurrentIndex(0)
        
        # Script analisys tools Fields
        self.main_window.search_combination_checkbox.setChecked(False)
        self.main_window.compare_to_dictionary_list.setCurrentIndex(0)
        self.main_window.max_frecuencies_input.setText("99")
        self.main_window.max_char_lenght_input.setText("2")
        self.main_window.characters_counter_output.clear()
        self.main_window.unused_characters_output.clear()
        self.main_window.best_combinations_output.clear()

        # Set buttons disabled
        self.main_window.extract_button.setDisabled(True)
        self.main_window.insert_button.setDisabled(True)

        # Reset Progress Bar
        self.main_window.progress_bar.setValue(0)
        
        # Reset Console
        self.main_window.show_console.clear()
        
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
        #self.main_window.dump_text_tab.setMaximumHeight(627)
        #self.main_window.tabs.setMaximumHeight(656)
        self.main_window.setFixedSize(475, 866) if is_checked else self.main_window.setFixedSize(475, 720)
        
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

    def toggle_not_use_end_line(self, state):
        is_checked = self.main_window.not_use_end_line_checkbox.isChecked()
        self.main_window.end_line_label.setDisabled(not is_checked)
        self.main_window.end_line_input.setDisabled(not is_checked)
        self.main_window.end_line_label.setEnabled(not is_checked)
        self.main_window.end_line_input.setEnabled(not is_checked)

    def toggle_fill_free_space(self, state):
        is_checked = self.main_window.fill_free_space_byte_checkbox.isChecked()
        self.main_window.fill_free_space_byte_input.setEnabled(not is_checked)
        self.main_window.fill_free_space_byte_input.setDisabled(not is_checked)

    def toggle_use_compression_method_options(self, state):
        is_checked = self.main_window.use_compression_algorithm_method_checkbox.isChecked()
        self.main_window.compression_method_list.setEnabled(not is_checked)
        self.main_window.compression_type_list.setEnabled(not is_checked)
        self.main_window.compression_method_list.setDisabled(not is_checked)
        self.main_window.compression_type_list.setDisabled(not is_checked)

    def toggle_seach_combinations(self, state):
        is_checked = self.main_window.search_combination_checkbox.isChecked()
        self.main_window.max_frecuencies_input.setEnabled(not is_checked)
        self.main_window.max_char_lenght_input.setEnabled(not is_checked)
        self.main_window.max_frecuencies_input.setDisabled(not is_checked)
        self.main_window.max_char_lenght_input.setDisabled(not is_checked)

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

    @staticmethod
    def update_compression_types(index, type_list):
        type_list.clear()
        if index == 0:  # Lempel-Ziv
            type_list.addItems(["LZ77", "LZSS", "LZW"])
        elif index == 1:  # Golomb
            type_list.addItems(["4 bits", "5 bits"])               
        
    def process_extraction(self, out_file):
        # CONSTANTS OPTIONS
        self.main_window.progress_bar.setVisible(True)
        self.main_window.progress_bar.setValue(0)
        use_compression_algorithm = self.main_window.use_compression_algorithm_method_checkbox.isChecked()
        no_comments_lines = self.main_window.not_comment_lines_checkbox.isChecked()
        bracket_index = self.main_window.use_custom_brackets_for_hex_codes_list.currentIndex()     
        use_split_pointers_method = self.main_window.use_split_pointers_checkbox.isChecked()
        no_use_end_lines_for_split = self.main_window.not_use_end_line_checkbox.isChecked()
        endianness = self.main_window.endianness_list.currentIndex() 

        try:
            # VARIABLE OPTIONS
            text_start_offset = int(self.main_window.text_start_offset_input.text(), 16)
            text_end_offset = int(self.main_window.text_end_offset_input.text(), 16)
            if text_start_offset > text_end_offset:
                self.show_error_dialog("Text start offset can't be higher than text end offset.")
                print("Error: Extraction aborted!")
                self.main_window.progress_bar.setValue(0)
                return    
            text_size = text_end_offset - text_start_offset + 1
            base = int(self.main_window.pointers_base_input.text(), 16)
            rom_file = self.main_window.selected_rom_file_name.text()
            tbl_file = self.main_window.selected_tbl_file_name.text()
            self.main_window.progress_bar.setValue(5)
            
        except (ValueError, UnboundLocalError):
            self.show_error_dialog("Please fill in all required fields.")
            print("Error: Extraction aborted!")
            self.main_window.progress_bar.setValue(0)
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
                self.main_window.progress_bar.setValue(0)
                return
            lsb = Decoder.read_rom(rom_file, lsb_ptr_offset, split_ptr_size)
            msb = Decoder.read_rom(rom_file, msb_ptr_offset, split_ptr_size)
            format_pointers = Decoder.process_pointers_split_2_bytes(lsb, msb, base)
##            for ptr in format_pointers:
##                print(f"Pointer: 0x{ptr:06X}")
        else:
            try:
                pointers_start_offset = int(self.main_window.pointers_start_offset_input.text(), 16)
                pointers_end_offset = int(self.main_window.pointers_end_offset_input.text(), 16)
            except (ValueError, UnboundLocalError):
                self.show_error_dialog("Please fill in all required fields.")
                print("Error: Extraction aborted!")
                self.main_window.progress_bar.setValue(0)
                return
            if pointers_start_offset > pointers_end_offset:
                self.show_error_dialog("Pointers start offset can't be higher than pointers end offset.")
                print("Error: Extraction aborted!")
                return
            pointers_size = pointers_end_offset - pointers_start_offset + 1
            try:
                table_pointers = Decoder.read_rom(rom_file, pointers_start_offset, pointers_size)
            except Exception as e:
                self.show_error_dialog(f"{e}")
                print("Error: Extraction aborted!")
                self.main_window.progress_bar.setValue(0)
                return
                       
            if self.main_window.radio_2_bytes.isChecked():
                format_pointers = Decoder.process_pointers_2_bytes(table_pointers, base, endianness)
                pointers_length = 2
                
            elif self.main_window.radio_3_bytes.isChecked():
                format_pointers = Decoder.process_pointers_3_bytes(table_pointers, base, endianness)
                pointers_length = 3
                
            elif self.main_window.radio_4_bytes.isChecked():                
                format_pointers = Decoder.process_pointers_4_bytes(table_pointers, base, endianness)
                pointers_length = 4
        self.main_window.progress_bar.setValue(10)

        # Load ROM data to RAM
        try:
            rom_data = Decoder.read_rom(rom_file, 0, os.path.getsize(rom_file))
            self.main_window.progress_bar.setValue(15)
        except Exception as e:
            self.show_error_dialog(f"{e}")
            print("Error: Extraction aborted!")
            self.main_window.progress_bar.setValue(0)
            return
        
        # Load char table to RAM
        try:
            char_table = Decoder.read_tbl(tbl_file)
            self.main_window.progress_bar.setValue(20)
        except Exception as e:
            self.show_error_dialog(f"{e}")
            print("Error: Extraction aborted!")
            self.main_window.progress_bar.setValue(0)
            return

        # Decompress Script (if needed)
        if not use_compression_algorithm:
            pass
        else:
            try:
                selected_method = self.main_window.compression_method_list.currentIndex()
                type_index = self.main_window.compression_type_list.currentIndex()
                # Lempel-Ziv
                if selected_method == 0:
                    # LZ77
                    if type_index == 0:
                        rom_data, rom_data_size, rom_data_end_offset, original_data_size = Lempel_ziv.decompress_lz77(rom_data, text_start_offset)
                    # LZSS
                    elif type_index == 1:
                        rom_data, rom_data_size, rom_data_end_offset, original_data_size = Lempel_ziv.decompress_lzss(rom_data, text_start_offset)
                    # LZW
                    elif type_index == 2:
                        rom_data, rom_data_size, rom_data_end_offset, original_data_size = Lempel_ziv.decompress_lzw(rom_data, text_start_offset, 12)

                # Golomb Rice
                elif selected_method == 1:
                    # 4 BITS
                    if type_index == 0:
                        pass
                    # 5 BITS
                    elif type_index == 1:
                        pass
                text_size = rom_data_size
                text_end_offset = rom_data_size - 1
                self.main_window.progress_bar.setValue(60)
            except Exception as e:
                self.show_error_dialog(f"Decompression error: {e}")
                print("Error: Extraction aborted!")
                self.main_window.progress_bar.setValue(0)
                return
                              
        # Decode Script
        try:
            if no_use_end_lines_for_split:
                script, total_bytes_read, lines_length = Decoder.decode_script_no_end_line(
                    rom_data, format_pointers, text_end_offset + 1, char_table, bracket_index
                )
            else:
                try:
                    end_line = Decoder.parse_end_lines(self.main_window.end_line_input.text())
                except (ValueError, UnboundLocalError):
                    self.show_error_dialog("Please fill in all required fields.")
                    print("Error: Extraction aborted!")
                    self.main_window.progress_bar.setValue(0)
                    return

                script, total_bytes_read, lines_length = Decoder.decode_script(
                    rom_data, format_pointers, end_line, char_table, bracket_index
                )

        except IndexError:
            self.show_error_dialog("Pointers out of ROM size.")
            self.main_window.progress_bar.setValue(0)
            return

        self.main_window.progress_bar.setValue(80)
        
        # Write Script
        if use_compression_algorithm and rom_data_size != 0:
            print(f"COMPRESSED SIZE: {original_data_size} / 0x{original_data_size:X} bytes.")
            print(f"DECOMPRESSED SIZE: {rom_data_size} / 0x{rom_data_size:X} bytes.")
            ratio = abs(original_data_size - rom_data_size) / rom_data_size
            print(f"RATIO: {ratio}, FINAL OFFSET: 0x{rom_data_end_offset:X}")
        if use_split_pointers_method and no_use_end_lines_for_split:
            decode_script = Decoder.write_out_file(out_file, script, lsb_ptr_offset, msb_ptr_offset + split_ptr_size - 1, split_ptr_size, format_pointers, lines_length, None, no_comments_lines)
            print(f"TEXT BLOCK SIZE: {text_size} / 0x{text_size:X} bytes.")
            print(f"PTR_TABLE BLOCK SIZE: {split_ptr_size * 2} / 0x{split_ptr_size * 2:X} bytes. {split_ptr_size} pointers found.")
        elif use_split_pointers_method:
            decode_script = Decoder.write_out_file(out_file, script, lsb_ptr_offset, msb_ptr_offset + split_ptr_size - 1, split_ptr_size, format_pointers, lines_length, end_line, no_comments_lines)
            print(f"TEXT BLOCK SIZE: {text_size} / 0x{text_size:X} bytes.")
            print(f"PTR_TABLE BLOCK SIZE: {split_ptr_size * 2} / 0x{split_ptr_size * 2:X} bytes. {split_ptr_size} pointers found.")
        elif no_use_end_lines_for_split:
            decode_script = Decoder.write_out_file(out_file, script, pointers_start_offset, pointers_start_offset + pointers_size - 1, pointers_size, format_pointers, lines_length, None, no_comments_lines)
            print(f"TEXT BLOCK SIZE: {text_size} / 0x{text_size:X} bytes.")
            print(f"PTR_TABLE BLOCK SIZE: {pointers_size} / 0x{pointers_size:X} bytes. {pointers_size // pointers_length} pointers found.")
        else:
            decode_script = Decoder.write_out_file(out_file, script, pointers_start_offset, pointers_start_offset + pointers_size - 1, pointers_size, format_pointers, lines_length, end_line, no_comments_lines)
            print(f"TEXT BLOCK SIZE: {text_size} / 0x{text_size:X} bytes.")
            print(f"PTR_TABLE BLOCK SIZE: {pointers_size} / 0x{pointers_size:X} bytes. {pointers_size // pointers_length} pointers found.")
        self.main_window.progress_bar.setValue(100)
        self.show_success_dialog("Script extracted successfully!")
        print("Script extracted successfully!")
        self.main_window.progress_bar.setValue(0)
            
    def process_insertion(self, rom_file):
        # CONSTANTS OPTIONS
        self.main_window.progress_bar.setVisible(True)
        self.main_window.progress_bar.setValue(0)
        use_compression_algorithm = self.main_window.use_compression_algorithm_method_checkbox.isChecked()
        no_comments_lines = self.main_window.not_comment_lines_checkbox.isChecked()
        bracket_index = self.main_window.use_custom_brackets_for_hex_codes_list.currentIndex()
        fill_free_space = self.main_window.fill_free_space_byte_checkbox.isChecked()
        if not fill_free_space and self.main_window.fill_free_space_byte_input.text() == "":
            fill_free_space_byte = bytes([0xFF])      
        else:
            try:
                fill_free_space_byte = bytes([int(self.main_window.fill_free_space_byte_input.text(), 16)])
            except ValueError:
                self.show_error_dialog("Fill byte is empty.")
                print("Error: Insertion aborted!")
                self.main_window.progress_bar.setValue(0)
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
                self.main_window.progress_bar.setValue(0)
                return 
            original_text_size = original_text_end_offset - original_text_start_offset + 1
            base = int(self.main_window.pointers_base_input.text(), 16)
            rom_file = self.main_window.selected_rom_file_name.text()
            tbl_file = self.main_window.selected_tbl_file_name.text()
            script_file = self.main_window.selected_script_file_name.text()
            self.main_window.progress_bar.setValue(5)
        except (ValueError, UnboundLocalError):
            self.show_error_dialog("Please fill in all required fields.")
            print("Error: Insertion aborted!")
            self.main_window.progress_bar.setValue(0)
            return
        
        # Read Script file
        try:
            new_script, ignore1, ignore2, ignore3, ignore4 = Encoder.read_script(script_file)
            self.main_window.progress_bar.setValue(10)
        except Exception as e:
            self.show_error_dialog(f"{e}")
            print("Error: Insertion aborted!")
            self.main_window.progress_bar.setValue(0)
            return

        # Parse line breakers.
        if not not_use_end_lines:
            try:
                end_line = Decoder.parse_end_lines(self.main_window.end_line_input.text())
                self.main_window.progress_bar.setValue(15)
            except ValueError:
                self.show_error_dialog("Please fill in all required fields.")
                print("Error: Insertion aborted!")
                self.main_window.progress_bar.setValue(0)
                return
                         
        # Load the character table
        try:
            char_table, longest_char = Encoder.read_tbl(tbl_file)
            self.main_window.progress_bar.setValue(20)
        except Exception as e:
            self.show_error_dialog(f"{e}")
            print("Error: Insertion aborted!")
            self.main_window.progress_bar.setValue(0)
            return

        # Encode Text
        if not_use_end_lines:
            new_script_data, new_script_size, cumulative_lengths = Encoder.encode_script(new_script, None, char_table, longest_char, not_use_end_lines, bracket_index)
        else:
            new_script_data, new_script_size, cumulative_lengths = Encoder.encode_script(new_script, end_line, char_table, longest_char, not_use_end_lines, bracket_index)
        self.main_window.progress_bar.setValue(50)

        # Compress Text (If needed)
        if not use_compression_algorithm:
            relative_start = False
            self.main_window.progress_bar.setValue(90)
        else:
            try:
                selected_method = self.main_window.compression_method_list.currentIndex()
                type_index = self.main_window.compression_type_list.currentIndex()
                # Lempel-Ziv
                if selected_method == 0:
                    # LZ77
                    if type_index == 0:
                        new_script_data, compressed_new_script_size, decompressed_script_size = Lempel_ziv.compress_lz77(new_script_data)
                    # LZSS
                    elif type_index == 1:
                        new_script_data, compressed_new_script_size, decompressed_script_size = Lempel_ziv.compress_lzss(new_script_data)
                    # LZW
                    elif type_index == 2:
                        new_script_data, compressed_new_script_size, decompressed_script_size = Lempel_ziv.compress_lzw(new_script_data, 12)

                # Golomb Rice
                elif selected_method == 1:
                    # 4 BITS
                    if type_index == 0:
                        pass
                    # 5 BITS
                    elif type_index == 1:
                        pass
                new_script_size = compressed_new_script_size
                relative_start = True
                self.main_window.progress_bar.setValue(90)
            except Exception as e:
                self.show_error_dialog(f"Compression error: {e}")
                print("Error: Extraction aborted!")
                self.main_window.progress_bar.setValue(0)
                return
            
        # Format Pointers
        if self.main_window.use_split_pointers_checkbox.isChecked():
            original_pointers_start_offset = int(self.main_window.lsb_offset_input.text(), 16)
            original_pointers_end_offset = int(self.main_window.msb_offset_input.text(), 16)
            if original_pointers_start_offset > original_pointers_end_offset:
                self.show_error_dialog("Pointers start offset can't be higher than pointers end offset.")
                print("Error: Extraction aborted!")
                self.main_window.progress_bar.setValue(0)
                return
            original_pointers_size = int(self.main_window.size_input.text(), 16)
            new_pointers_data_lsb, new_pointers_data_msb, new_pointers_size = Encoder.calculate_pointers_2_bytes_split(cumulative_lengths, original_text_start_offset, relative_start, base)
        else:
            try:
                original_pointers_start_offset = int(self.main_window.pointers_start_offset_input.text(), 16) 
                original_pointers_end_offset = int(self.main_window.pointers_end_offset_input.text(), 16)
            except (ValueError, UnboundLocalError):
                self.show_error_dialog("Please fill in all required fields.")
                print("Error: Insertion aborted!")
                self.main_window.progress_bar.setValue(0)
                return    
            if original_pointers_end_offset < original_pointers_start_offset:
                self.show_error_dialog(f"Error invalid offsets!")
                print("Error: Insertion aborted!")
                self.main_window.progress_bar.setValue(0)
                return
            original_pointers_size = original_pointers_end_offset - original_pointers_start_offset + 1
            if self.main_window.radio_2_bytes.isChecked():
                new_pointers_data, new_pointers_size = Encoder.calculate_pointers_2_bytes(cumulative_lengths, original_text_start_offset, relative_start, base, endianness)
                pointers_length = 2
                
            elif self.main_window.radio_3_bytes.isChecked():
                new_pointers_data, new_pointers_size = Encoder.calculate_pointers_3_bytes(cumulative_lengths, original_text_start_offset, relative_start, base, endianness)
                pointers_length = 3
                
            elif self.main_window.radio_4_bytes.isChecked():                
                new_pointers_data, new_pointers_size = Encoder.calculate_pointers_4_bytes(cumulative_lengths, original_text_start_offset, relative_start, base, endianness)
                pointers_length = 4
            self.main_window.progress_bar.setValue(90)
                
        # Write ROM
        if new_script_size > original_text_size:
            self.main_window.progress_bar.setValue(100)
            self.show_error_dialog(f"ERROR: Script size has exceeded its maximum size. Remove {new_script_size - original_text_size} bytes.")
            print(f"ERROR: Script size has exceeded its maximum size. Remove {new_script_size - original_text_size} bytes.")
            self.main_window.progress_bar.setValue(0)
            return
        if new_pointers_size > original_pointers_size:
            self.main_window.progress_bar.setValue(100)
            self.show_error_dialog(f"ERROR: Table pointer size has exceeded its maximum size. Remove {(new_pointers_size - original_pointers_size)} lines in script.")
            print(f"ERROR: Table pointer size has exceeded its maximum size. Remove {(new_pointers_size - original_pointers_size)} lines in script.")
            self.main_window.progress_bar.setValue(0)
            return
        if use_compression_algorithm and decompressed_script_size != 0:
            print(f"COMPRESSED SIZE: {compressed_new_script_size} / 0x{compressed_new_script_size:X} bytes.")
            print(f"DECOMPRESSED SIZE: {decompressed_script_size} / 0x{decompressed_script_size:X} bytes.")
            print(f"RATIO: {abs(compressed_new_script_size - decompressed_script_size) / decompressed_script_size}")
        try:
            free_space_script = Encoder.write_rom(rom_file, original_text_start_offset, original_text_size, new_script_data, fill_free_space, fill_free_space_byte)
            print(f"Script written at address 0x{original_text_start_offset:X}, {free_space_script} bytes of free space.")
        except Exception as e:
            self.show_error_dialog(f"{e}")
            print("Error: Insertion aborted!")
            self.main_window.progress_bar.setValue(0)
            return
            
        if not self.main_window.use_split_pointers_checkbox.isChecked():
            free_space_pointers = Encoder.write_rom(rom_file, original_pointers_start_offset, original_pointers_size, new_pointers_data, False, fill_free_space_byte)
            print(f"Pointers table written at address 0x{original_pointers_start_offset:X}, {free_space_pointers // pointers_length} lines/pointers left.")

        else:
            free_space_pointers = Encoder.write_rom(rom_file, original_pointers_start_offset, original_pointers_size, new_pointers_data_lsb, False, fill_free_space_byte)
            free_space_pointers = Encoder.write_rom(rom_file, original_pointers_end_offset, original_pointers_size, new_pointers_data_msb, False, fill_free_space_byte)
            print(f"Pointers table written at address 0x{original_pointers_start_offset:X}, {free_space_pointers // 2} lines/pointers left.")

        self.main_window.progress_bar.setValue(100)
        self.show_success_dialog("Script inserted successfully!")
        print("Script inserted successfully!")
        self.main_window.progress_bar.setValue(0)

    def process_script_analysis(self, script_file):
        self.main_window.best_combinations_output.clear()
        search_combinations = self.main_window.search_combination_checkbox.isChecked()
        bracket_index = self.main_window.use_custom_brackets_for_hex_codes_list.currentIndex()
        dictionary_index = self.main_window.compare_to_dictionary_list.currentIndex()
        try:
            script_file = self.main_window.selected_script_file_name.text()
            script_file = Analizer.read_script(script_file)
            self.main_window.progress_bar.setValue(10)
        except Exception as e:
            self.show_error_dialog(f"{e}")
            print("Error: Analysis aborted!")
            self.main_window.progress_bar.setValue(0)
            return

        single_characters = Analizer.character_counter(script_file, bracket_index)
        unused_characters = Analizer.unused_characters(single_characters, dictionary_index)
             
        formatted_single_characters = Analizer.format_display(single_characters)
        formatted_unused_characters = Analizer.format_display(unused_characters)
        
        self.main_window.characters_counter_output.setPlainText(formatted_single_characters)
        self.main_window.unused_characters_output.setPlainText(formatted_unused_characters)
        self.main_window.progress_bar.setValue(20)

        if search_combinations:
            try:
                max_frecuencies = int(self.main_window.max_frecuencies_input.text())
                max_char = int(self.main_window.max_char_lenght_input.text())
            except (ValueError, UnboundLocalError):
                self.main_window.characters_counter_output.clear()
                self.main_window.unused_characters_output.clear()
                self.show_error_dialog("Please fill in all required fields.")
                print("Error: Analysis aborted!")
                self.main_window.progress_bar.setValue(0)
                return
            mte_optimizer = Analizer.multi_length_mte_counter(script_file, bracket_index, max_frecuencies, max_char)
            formatted_mte_optimizer = Analizer.format_display(mte_optimizer)
            self.main_window.best_combinations_output.setPlainText(formatted_mte_optimizer)
        
        self.main_window.progress_bar.setValue(100)
        self.show_success_dialog("Done!")
        print("Done!")   
        self.main_window.progress_bar.setValue(0)
        
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
        self.settings = QSettings(f"{author}", f"{app_name}")
        self.last_config_path = self.settings.value("Path", "", type=str)
        #self.last_version = self.settings.value("Version", f"{version}", type=str)
        self.settings.setValue("Version", f"{version}")
        self.has_loaded_config = False

    def open_config(self):
        options = QFileDialog.Options()
        start_dir = self.last_config_path or ""
        file_name, _ = QFileDialog.getOpenFileName(self.main_window, "Open config file", start_dir, "Config files (*.json);;All Files (*)", options=options)

        if file_name:
            try:
                with open(file_name, 'r') as file:
                    self.last_config_path = file_name
                    self.has_loaded_config = True
                    self.settings.setValue("Path", file_name)

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
                    self.main_window.use_custom_brackets_for_hex_codes_list.setCurrentIndex(config_data.get("brackets", ""))
                    self.main_window.not_comment_lines_checkbox.setChecked(config_data.get("no_use_comments_lines", False)) 
                    self.main_window.fill_free_space_byte_checkbox.setChecked(config_data.get("fill_free_space", False))
                    self.main_window.use_split_pointers_checkbox.setChecked(config_data.get("use_split_pointers", False))
                    self.main_window.not_use_end_line_checkbox.setChecked(config_data.get("not_use_end_line", False))

                    # Compression Tools Config
                    self.main_window.use_compression_algorithm_method_checkbox.setChecked(config_data.get("use_compression_method", False)) 
                    self.main_window.compression_method_list.setCurrentIndex(config_data.get("compression_algorithm", 0))
                    self.main_window.compression_type_list.setCurrentIndex(config_data.get("compression_variant", 0))

                    # Analysis Tools Config
                    self.main_window.compare_to_dictionary_list.setCurrentIndex(config_data.get("compare_to_dictionary", 0))
                    self.main_window.search_combination_checkbox.setChecked(config_data.get("search_combinations", False))
                    if "max_frecuencies" in config_data:
                        self.main_window.max_frecuencies_input.setText(config_data["max_frecuencies"])

                    if "max_char_lenght" in config_data:
                        self.main_window.max_char_lenght_input.setText(config_data["max_char_lenght"])
                
                self.functions.enable_extract_button()
                self.functions.enable_insert_button()
                print("Config imported successfully!")
            except Exception as e:
                self.functions.enable_extract_button()
                self.functions.enable_insert_button()
                self.functions.show_error_dialog(f"Error importing config {e}")
                print(f"Error importing config: {e}")
                return

    def save_config(self):
        options = QFileDialog.Options()
        script_file = self.main_window.selected_script_file_name.text()
        rom_file = self.main_window.selected_rom_file_name.text()

        if self.has_loaded_config and self.last_config_path:
            suggested_name = self.last_config_path
        elif script_file:
            suggested_name = os.path.splitext(script_file)[0] + "_config"
        elif rom_file:
            suggested_name = os.path.splitext(rom_file)[0] + "_config"
        else:
            suggested_name = "config"

        file_name, _ = QFileDialog.getSaveFileName(self.main_window, "Save config file", suggested_name, "Config files (*.json);;All Files (*)", options=options)
            
        if file_name:
            try:
                self.last_config_path = file_name
                self.has_loaded_config = True
                self.settings.setValue("Path", file_name)
                
                config_data = {}
                
                # Program Data
                config_data["app_name"] = app_name
                config_data["version"] = version

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
                config_data["brackets"] = self.main_window.use_custom_brackets_for_hex_codes_list.currentIndex()
                config_data["fill_free_space"] = self.main_window.fill_free_space_byte_checkbox.isChecked()           
                config_data["use_split_pointers"] = self.main_window.use_split_pointers_checkbox.isChecked()
                config_data["not_use_end_line"] = self.main_window.not_use_end_line_checkbox.isChecked()

                # Compression tools configs
                
                config_data["use_compression_method"] = self.main_window.use_compression_algorithm_method_checkbox.isChecked()
                config_data["compression_algorithm"] = self.main_window.compression_method_list.currentIndex()
                config_data["compression_variant"] = self.main_window.compression_type_list.currentIndex()

                # Analysis tools configs

                config_data["compare_to_dictionary"] = self.main_window.compare_to_dictionary_list.currentIndex()
                config_data["search_combinations"] = self.main_window.search_combination_checkbox.isChecked()

                max_frecuencies = self.main_window.max_frecuencies_input.text().strip()
                if max_frecuencies:
                    config_data["max_frecuencies"] = max_frecuencies

                max_char_lenght = self.main_window.max_char_lenght_input.text().strip()
                if max_char_lenght:
                    config_data["max_char_lenght"] = max_char_lenght
        
                # Save
                with open(file_name, 'w') as file:
                    json.dump(config_data, file, indent=4)
                saved_config = True
                print("Config exported successfully!")
            except Exception as e:
                self.functions.show_error_dialog(f"Error exporting config {e}")
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
            self.functions.show_error_dialog(f"Error selecting ROM file: {e}")
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
            self.functions.show_error_dialog(f"Error selecting TBL file: {e}")
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
            self.functions.show_error_dialog(f"Error selecting Script file: {e}")
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
        except ValueError as e:
            self.functions.show_error_dialog(f"Error selecting Output file: {e}")
            print(f"Error selecting Output file: {e}")
            return

class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Class instances
        self.functions = Functions(self)  
        self.file_handler = FileHandler(self)

        # Initial setup
        self.setWindowTitle(f"{app_name} v{version}")   
        icon_path = os.path.join(resources_path, icon_file)
        self.setWindowIcon(QIcon(icon_path))
        
        self.setFixedSize(475, 720)  #475, 720
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        central_layout = QVBoxLayout()
        self.tabs = QTabWidget(self)

        # Create tab environmnet
        self.create_tabs()
        central_widget.setLayout(central_layout)
        self.create_menu()

        # Configure tooltip
        QApplication.instance().setStyleSheet("QToolTip { background-color: yellow; color: black; border: 1px solid black; }")

        # Progress Bar
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setFixedHeight(20)
        self.progress_bar.setVisible(True)
        
        # Main window sketch
        central_layout.addWidget(self.tabs)
        central_layout.addWidget(self.create_console())
        central_layout.addWidget(self.progress_bar)

    def create_menu(self):
        menubar = self.menuBar()

        # Create file menu
        file_menu = menubar.addMenu('File')

        # File functions
        new_action = QAction('New', self)
        new_action.setShortcut('Ctrl+N')
        new_action.triggered.connect(self.functions.reset_fields)
        open_action = QAction('Open config', self)
        open_action.setShortcut('Ctrl+O')
        open_action.triggered.connect(self.file_handler.open_config)
        save_action = QAction('Save config', self)
        save_action.setShortcut('Ctrl+S')
        save_action.triggered.connect(self.file_handler.save_config)
        exit_action = QAction('Exit', self)
        exit_action.setShortcut('Alt+F4')
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
        about_action.setShortcut('F1')
        about_action.triggered.connect(self.show_about)

        # Help add functions
        help_menu.addAction(about_action)
         
    def create_tabs(self):
        # Create dump text tab
        dump_text_tab = QWidget()
        #dump_text_tab.setMaximumHeight(481)
        dump_text_layout = QVBoxLayout()
        dump_text_layout.addWidget(self.create_select_file_groupbox(), alignment=Qt.AlignTop)
        dump_text_layout.addWidget(self.create_set_pointers_groupbox(), alignment=Qt.AlignTop)
        dump_text_layout.addWidget(self.create_set_offsets_groupbox(), alignment=Qt.AlignTop)
        dump_text_layout.addWidget(self.create_advanced_options_groupbox(), alignment=Qt.AlignTop)       
        dump_text_layout.addLayout(self.create_actions_buttons())
        dump_text_tab.setLayout(dump_text_layout)

        # Create compress script tools
        compression_tools_tab = QWidget()
        compression_tools_layout = QVBoxLayout()
        compression_tools_layout.addWidget(self.create_compression_tools_groupbox(), alignment=Qt.AlignTop)
        compression_tools_tab.setLayout(compression_tools_layout)
        
        # Create analysis tool tab 
        analysis_tool_tab = QWidget()
        analysis_tool_layout = QVBoxLayout()
        analysis_tool_layout.addWidget(self.create_analysis_tool_options_groupbox(), alignment=Qt.AlignTop)
        analysis_tool_layout.addWidget(self.create_analysis_tool_output_groupbox(), alignment=Qt.AlignTop)
        analysis_tool_tab.setLayout(analysis_tool_layout)

        # Add to QTabWidget
        #self.tabs.setMaximumHeight(510)
        self.tabs.addTab(dump_text_tab, "Dump Text")
        self.tabs.addTab(compression_tools_tab, "Compress Script Tools")
        self.tabs.addTab(analysis_tool_tab, "Script Analysis Tools")
        
    def show_size(self):
        width = self.width()
        height = self.height()
        QMessageBox.information(self, "Window size", f"Width: {width} px\nHeight: {height} px")
        
    def create_analysis_tool_options_groupbox(self):
        group_box = QGroupBox()
        layout = QVBoxLayout()

        # Dictionary Option
        dictionary_layout = QHBoxLayout()
        self.compare_to_dictionary_label = QLabel("Compare Dictionary:", self)
        self.compare_to_dictionary_list = QComboBox()
        self.compare_to_dictionary_list.addItem("Only Uppercase", 0)
        self.compare_to_dictionary_list.addItem("Only Lowercase", 1)
        self.compare_to_dictionary_list.addItem("Both", 2)
        self.compare_to_dictionary_list.addItem("Both + Special", 3)
        self.compare_to_dictionary_list.addItem("Romanji + Jap", 4)
        dictionary_layout.addWidget(self.compare_to_dictionary_label)
        dictionary_layout.addWidget(self.compare_to_dictionary_list)
        dictionary_layout.addStretch()

        # Checkbox
        self.search_combination_checkbox = QCheckBox("Optimize DTE/MTE.", self)
        self.search_combination_checkbox.stateChanged.connect(self.functions.toggle_seach_combinations)

        # Max Frecuencies Option
        max_frecuencies_layout = QHBoxLayout()
        max_frecuencies_layout_help = "Maximum number of combinations to search for.\nInterval(10-129)."
        self.max_frecuencies_label = QLabel("Max frecuencies:", self)
        self.max_frecuencies_label.setToolTip(max_frecuencies_layout_help)
        self.max_frecuencies_input = QLineEdit(self)
        self.max_frecuencies_input.setDisabled(True)
        self.max_frecuencies_input.setFixedWidth(30)
        self.max_frecuencies_input.setText("99")
        self.max_frecuencies_input.setValidator(QRegExpValidator(QRegExp(r'(1[0-2][0-9]|10[0-9]|[1-9][0-9]|10|11[0-8]|12[0-8])'), self))
        self.max_frecuencies_input.setToolTip(max_frecuencies_layout_help)

        max_frecuencies_layout.addWidget(self.max_frecuencies_label)
        max_frecuencies_layout.addWidget(self.max_frecuencies_input)

        # Max Char Lenght Option
        max_char_lenght_layout = QHBoxLayout()
        max_char_lenght_layout_help = "Maximum length of compressions to search for.\nInterval(2-15)."
        self.max_char_lenght_label = QLabel("Max Combinations Lenght:", self)
        self.max_char_lenght_label.setToolTip(max_char_lenght_layout_help)
        self.max_char_lenght_input = QLineEdit(self)
        self.max_char_lenght_input.setDisabled(True)
        self.max_char_lenght_input.setFixedWidth(30)
        self.max_char_lenght_input.setText("2")
        self.max_char_lenght_input.setValidator(QRegExpValidator(QRegExp(r'([2-9]|1[0-5])'), self))
        self.max_char_lenght_input.setToolTip(max_char_lenght_layout_help)

        max_frecuencies_layout.addWidget(self.max_char_lenght_label)
        max_frecuencies_layout.addWidget(self.max_char_lenght_input)
        max_frecuencies_layout.addStretch()
        
        # Optimize button
        center_button_layout = QHBoxLayout()
        
        self.optimize_button = QPushButton("Search", self)
        self.optimize_button.setFixedWidth(100)
        self.optimize_button.clicked.connect(self.functions.process_script_analysis)

        center_button_layout.addStretch()
        center_button_layout.addWidget(self.optimize_button)
        center_button_layout.addStretch()
        
        # Layout Config
        layout.addLayout(dictionary_layout)
        layout.addWidget(self.search_combination_checkbox)
        layout.addLayout(max_frecuencies_layout) 
        layout.addLayout(center_button_layout) 
        
        group_box.setLayout(layout)
        return group_box
    
    def create_analysis_tool_output_groupbox(self):
        group_box = QGroupBox()
        layout = QVBoxLayout()

        # Characters counter
        self.characters_counter_label = QLabel("Characters Counter:", self)
        self.characters_counter_output = QPlainTextEdit(self)
        self.characters_counter_output.setReadOnly(True)
        self.characters_counter_output.setMinimumHeight(80)

        # Unused characters
        self.unused_characters_label = QLabel("Unused Characters:", self)
        self.unused_characters_output = QPlainTextEdit(self)
        self.unused_characters_output.setReadOnly(True)
        self.unused_characters_output.setMinimumHeight(80)

        # Best combinations
        self.best_combinations_label = QLabel("DTE/MTE Optimizer:", self)
        self.best_combinations_output = QPlainTextEdit(self)
        self.best_combinations_output.setReadOnly(True)
        self.best_combinations_output.setMinimumHeight(80)

        # Layout Order
       
        layout.addWidget(self.characters_counter_label)
        layout.addWidget(self.characters_counter_output)

        layout.addWidget(self.unused_characters_label)
        layout.addWidget(self.unused_characters_output)

        layout.addWidget(self.best_combinations_label)
        layout.addWidget(self.best_combinations_output)

        group_box.setLayout(layout)
        return group_box

    def create_compression_tools_groupbox(self):
        group_box = QGroupBox()
        group_box.setMaximumHeight(140)
        layout = QVBoxLayout()

        # Use compression/decompression tools
        self.use_compression_algorithm_method_checkbox = QCheckBox("Use compression algorithm method (experimental).", self)
        self.use_compression_algorithm_method_checkbox.stateChanged.connect(self.functions.toggle_use_compression_method_options)
        layout.addWidget(self.use_compression_algorithm_method_checkbox)

        # Compression Method
        method_layout = QHBoxLayout()
        method_label = QLabel("Compression Algorithm:")
        self.compression_method_list = QComboBox()
        self.compression_method_list.setDisabled(True)
        self.compression_method_list.setFixedWidth(120)
        self.compression_method_list.addItem("Lempel-Ziv", 0)
        #self.compression_method_list.addItem("Golomb-Rice", 1)
        method_layout.addWidget(method_label)
        method_layout.addWidget(self.compression_method_list)
        method_layout.addStretch()
        layout.addLayout(method_layout)

        # Variant
        type_layout = QHBoxLayout()
        type_label = QLabel("Variant:")
        self.compression_type_list = QComboBox()
        self.compression_type_list.setDisabled(True)
        self.compression_type_list.setFixedWidth(120)
        type_layout.addWidget(type_label)
        type_layout.addWidget(self.compression_type_list)
        type_layout.addStretch()
        layout.addLayout(type_layout)

        # Connect with function
        self.compression_method_list.currentIndexChanged.connect(
            lambda index: Functions.update_compression_types(index, self.compression_type_list)
        )
        # Update Variant
        Functions.update_compression_types(
            self.compression_method_list.currentIndex(), self.compression_type_list
        )
        group_box.setLayout(layout)
        return group_box

    def create_select_file_groupbox(self):
        group_box = QGroupBox("Select Files", self)
        group_box.setMinimumHeight(120)
        group_box.setMaximumHeight(120)
        group_box.setMinimumWidth(400)
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
        group_box.setMinimumWidth(400)
        layout = QVBoxLayout()

        # Pointers Length
        pointers_length_layout = QHBoxLayout()
        self.pointers_length_label = QLabel("Pointers Length:", self)
        self.radio_2_bytes = QRadioButton("2 bytes", self)
        self.radio_3_bytes = QRadioButton("3 bytes", self)
        self.radio_4_bytes = QRadioButton("4 bytes", self)
        self.radio_2_bytes.setChecked(True)
        pointers_length_layout.addWidget(self.pointers_length_label)
        #pointers_length_layout.addStretch()
        pointers_length_layout.addWidget(self.radio_2_bytes)
        pointers_length_layout.addWidget(self.radio_3_bytes)
        pointers_length_layout.addWidget(self.radio_4_bytes)
        layout.addLayout(pointers_length_layout)

        # Endianness
        endianness_layout = QHBoxLayout()
        self.endianness_label = QLabel("Endianness:", self)
        self.endianness_list = QComboBox(self)
        self.endianness_list.setMinimumWidth(160)
        self.endianness_list.addItem("Little Endian", 0)
        self.endianness_list.addItem("Big Endian", 1)
        self.endianness_list.setCurrentIndex(0)
        endianness_layout.addWidget(self.endianness_label)
        endianness_layout.addStretch()
        endianness_layout.addWidget(self.endianness_list)
        endianness_layout.addStretch()
        layout.addLayout(endianness_layout)

        # Add all to group box
        group_box.setLayout(layout)

        return group_box

    def create_set_offsets_groupbox(self):
        group_box = QGroupBox("Set Offsets", self)
        group_box.setMinimumHeight(130)
        group_box.setMaximumHeight(130)
        group_box.setMinimumWidth(400)
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
        self.end_line_label.setToolTip('Code used to split pointers.\nTip: Use multiple separated by ","')
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
        #group_box.setFixedHeight(50)
        group_box.setMinimumWidth(400)
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

        # Use custom brackets for raw hex codes.
        self.use_custom_brackets_for_hex_codes_label = QLabel(" ●  Brackets for raw bytes:", self)
        self.use_custom_brackets_for_hex_codes_label.setToolTip("Unassigned characters in the table will be represented between them.")
        self.use_custom_brackets_for_hex_codes_list = QComboBox(self)
        self.use_custom_brackets_for_hex_codes_list.setFixedWidth(50)
        self.use_custom_brackets_for_hex_codes_list.addItem("~ ~", 0)
        self.use_custom_brackets_for_hex_codes_list.addItem("[ ]", 1)
        self.use_custom_brackets_for_hex_codes_list.addItem("{ }", 2)
        self.use_custom_brackets_for_hex_codes_list.addItem("< >", 3)
        self.use_custom_brackets_for_hex_codes_list.setCurrentIndex(0)
        
        use_custom_brackets = QHBoxLayout()
        use_custom_brackets.setContentsMargins(0, 0, 0, 0)
        use_custom_brackets.addWidget(self.use_custom_brackets_for_hex_codes_label)
        use_custom_brackets.addWidget(self.use_custom_brackets_for_hex_codes_list)
        use_custom_brackets.addStretch()                                          
        
        use_custom_brackets_widget = QWidget(self)
        use_custom_brackets_widget.setLayout(use_custom_brackets)

        advanced_layout.addWidget(use_custom_brackets_widget)

        # Not comment lines 
        self.not_comment_lines_checkbox = QCheckBox("Don't comment lines.", self)
        self.not_comment_lines_checkbox.setToolTip("Use this if you don't want a duplicate line as a comment.\n"'Note: comments will start with ";".') 
        advanced_layout.addWidget(self.not_comment_lines_checkbox)

        # Fill free space with byte

        self.fill_free_space_byte_checkbox = QCheckBox("Fill free space:", self)
        self.fill_free_space_byte_checkbox.setToolTip("Use this if you want to fill the free space left when you insert the script with a custom byte.\nOnly when inserted.")
        self.fill_free_space_byte_checkbox.stateChanged.connect(self.functions.toggle_fill_free_space)
        self.fill_free_space_byte_input = QLineEdit(self)
        self.fill_free_space_byte_input.setPlaceholderText("FF")
        self.fill_free_space_byte_input.setText("FF")
        self.fill_free_space_byte_input.setValidator(QRegExpValidator(QRegExp("[0-9A-Fa-f,]{1,2}")))
        self.fill_free_space_byte_input.setDisabled(True)
        self.fill_free_space_byte_input.setFixedWidth(25)
        self.functions.set_uppercase_formatting(self.fill_free_space_byte_input)

        fill_free_space = QHBoxLayout()
        fill_free_space.setSpacing(0)
        fill_free_space.setContentsMargins(0, 0, 0, 0)
        fill_free_space.addWidget(self.fill_free_space_byte_checkbox)
        fill_free_space.addWidget(self.functions.create_prefix_label())
        fill_free_space.addWidget(self.fill_free_space_byte_input)
        fill_free_space.addStretch()

        fill_free_space_widget = QWidget(self)
        fill_free_space_widget.setLayout(fill_free_space)

        advanced_layout.addWidget(fill_free_space_widget)
        
        
        # Use split pointers extraction (2 bytes only)
        self.use_split_pointers_checkbox = QCheckBox("Use split pointers method.", self)
        self.use_split_pointers_checkbox.setToolTip("Use it if the pointer table is divided into 2 parts.\nLSB: Lest significant bytes.\nMSB: Most significant bytes.\nSize: Numbers of pointers <hex>.")
        self.use_split_pointers_checkbox.stateChanged.connect(self.functions.toggle_split_pointers)
        advanced_layout.addWidget(self.use_split_pointers_checkbox)

        self.lsb_offset_label = QLabel("LSB Offset:", self)
        self.lsb_offset_input = QLineEdit(self)
        self.lsb_offset_input.setPlaceholderText("000000")
        self.lsb_offset_input.setFixedWidth(60)
        self.lsb_offset_input.setValidator(QRegExpValidator(QRegExp("[0-9A-Fa-f]{1,8}")))
        self.functions.set_uppercase_formatting(self.lsb_offset_input)

        self.msb_offset_label = QLabel("  MSB Offset:", self)
        self.msb_offset_input = QLineEdit(self)
        self.msb_offset_input.setPlaceholderText("000000")
        self.msb_offset_input.setFixedWidth(60)
        self.msb_offset_input.setValidator(QRegExpValidator(QRegExp("[0-9A-Fa-f]{1,8}")))
        self.functions.set_uppercase_formatting(self.msb_offset_input)

        self.size_label = QLabel("  Size:", self)
        self.size_input = QLineEdit(self)
        self.size_input.setPlaceholderText("0000")
        self.size_input.setFixedWidth(40)
        self.size_input.setValidator(QRegExpValidator(QRegExp("[0-9A-Fa-f]{1,8}")))
        self.functions.set_uppercase_formatting(self.size_input)

        split_pointers_layout = QHBoxLayout()
        split_pointers_layout.setSpacing(0)

        split_pointers_layout.addWidget(self.lsb_offset_label)
        split_pointers_layout.addWidget(self.functions.create_prefix_label())
        split_pointers_layout.addWidget(self.lsb_offset_input)
        #split_pointers_layout.addStretch()

        split_pointers_layout.addWidget(self.msb_offset_label)
        split_pointers_layout.addWidget(self.functions.create_prefix_label())
        split_pointers_layout.addWidget(self.msb_offset_input)
        #split_pointers_layout.addStretch()

        split_pointers_layout.addWidget(self.size_label)
        split_pointers_layout.addWidget(self.functions.create_prefix_label())
        split_pointers_layout.addWidget(self.size_input)
        split_pointers_layout.addStretch()

        self.functions.disable_layout_widgets(split_pointers_layout)
        advanced_layout.addLayout(split_pointers_layout)

        # Not use end line
        self.not_use_end_line_checkbox = QCheckBox("Not use end line code for split lines (use pointers length).", self)
        self.not_use_end_line_checkbox.setToolTip("Use this if the game does not support a fixed line ending code,\nAt 'extract' lines will be split based on the difference between pointers.\nAt 'Insert' pointer will be calculated based in every line length in the script.")
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
        self.show_console.setMinimumWidth(400)
        self.show_console.setReadOnly(True)
        
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
            f"<div align='right'><span style='color:gray;'>Build: {version}_{date}{hour}</span></div><br>"
            f"{app_name} v{version}.<br>"
            f"Created by {author}.<br><br>"
            "Home: "
            f"<a href='{url}'>{url}</a>"
        )
        about_text = QLabel()
        about_text.setTextFormat(Qt.RichText)
        about_text.setText(about_version)
        about_text.setFixedHeight(100)
        about_text.setOpenExternalLinks(True)
        about_text.setAlignment(Qt.AlignCenter)

        license_groupbox = QGroupBox("GNU General Public License")
        license_groupbox.setStyleSheet("""
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 10px;
                font-weight: bold;
            }
        """)
        license_layout = QVBoxLayout()
    
        license_text = QTextEdit()
        license_text.setMinimumHeight(120)
        license_text.setReadOnly(True)
        license_text.setTextInteractionFlags(Qt.TextBrowserInteraction)
        license_text.setText(f"{license}")
        
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
        print("Use console.exe to use cli commands.")
        exit(1)
        
    else:
        # Dependencies
        basedir = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.dirname(__file__)
        icon_path = os.path.join(basedir, resources_path, icon_file)
        if not os.path.exists(icon_path):
            app = QApplication(sys.argv)
            error_window = QWidget()
            functions = Functions(error_window)
            functions.show_error_dialog(f"File not found: {icon_path}")
            sys.exit(1)

        app = QApplication(sys.argv)   
        app.setWindowIcon(QtGui.QIcon(icon_path))
        process = app_name + version
        windll.shell32.SetCurrentProcessExplicitAppUserModelID(process)
        hexstring = MyWindow()
        hexstring.show()
        #debbug
        sys._excepthook = sys.excepthook 
        def exception_hook(exctype, value, traceback):
            print(exctype, value, traceback)
            sys._excepthook(exctype, value, traceback) 
            sys.exit(1) 
        sys.excepthook = exception_hook

        sys.exit(app.exec_())
