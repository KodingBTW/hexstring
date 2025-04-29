# HexString(Console) 1.3.0 by Koda
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
# - CLI 
# 
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
import cli
from cli import CLI

    
if __name__ == '__main__':
    if len(sys.argv) > 1:
        cli = CLI()  
        cli.parse_arguments()
        cli.run()
    else:
        exit(1)

