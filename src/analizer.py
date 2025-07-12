import re
import string
from collections import Counter

class Analizer:
    def __init__(self):
        """
        Initializes the Analizer class.
        """
        pass

    def read_script(file):
        """
        Reads a file containing the game's text. 

        
        Parameters:
            file (str): The path to the file to read.
        
        Returns:
            text_data (list): A list of strings, each representing a line of text from the file.

        """
        with open(file, "r", encoding='UTF-8') as f:
            script = [
                line.rstrip('\n') for line in f.readlines()
                if not (line.startswith(";") or line.startswith("@") or line.startswith("|") or line.startswith("&"))
            ]
        return script

    def format_display(counter):
        """
        Returns a string representing the counter sorted by:
        - frequency (descending)
        - ASCII value (ascending) when equal frequency
        """
        sorted_items = sorted(
            counter.items(),
            key=lambda item: (-item[1], item[0])
        )
        lines = [f"{char}={count}" for char, count in sorted_items]
        return "\n".join(lines)
    
    def character_counter(script, bracket_index):
        """
        Counts the frequency characters in a given text ignore raw bytes codes.
    
        Args:
            text (list): The input text to analyze.
            bracket_index (int): Raw bytes brackets

        Returns:
            collections.Counter: A counter object with character frequencies.
        """
        if bracket_index == 0:
            raw_byte = r'(~[0-9A-Fa-f]{2}~)'
        elif bracket_index == 1:
            raw_byte = r'(\[[0-9A-Fa-f]{2}\])'
        elif bracket_index == 2:
            raw_byte = r'(\{[0-9A-Fa-f]{2}\})'
        elif bracket_index == 3:
            raw_byte = r'(<[0-9A-Fa-f]{2}>)'
            
        char_counter = Counter()

        for line in script:
            clean_raw_bytes = re.sub(raw_byte, '', line)
            char_counter.update(clean_raw_bytes)

        return char_counter


    def unused_characters(counter, dictionary_index):
        """
        Returns a sorted list of characters (including space) based on dictionary_index
        that do not appear in the counter.

        Args:
            counter (collections.Counter): Characters used in the script.
            dictionary_index (int):
                0 - Uppercase only (A-Z + ' ')
                1 - Lowercase only (a-z + ' ')
                2 - Uppercase + lowercase (A-Z + a-z + ' ')
                3 - Uppercase + lowercase + digits + punctuation + ' '
                4 - Romanji + digits + Japanese + ' '

        Returns:
            collections.Counter: A counter object with character frequencies.
        """
        if dictionary_index == 0:
            valid_characters = set(string.ascii_uppercase)
        elif dictionary_index == 1:
            valid_characters = set(string.ascii_lowercase)
        elif dictionary_index == 2:
            valid_characters = set(string.ascii_letters)
        elif dictionary_index == 3:
            valid_characters = set(string.ascii_letters + string.digits + string.punctuation)
        elif dictionary_index == 4:
            valid_characters = set(
                chr(cp) for cp in range(0x3041, 0x30A0)
            ).union(
                chr(cp) for cp in range(0x30A1, 0x3100)
            ).union(string.ascii_letters + string.digits)
        else:
            raise ValueError("Invalid dictionary index.")

        # Add space in all dictionaries
        valid_characters.add(' ')

        used_characters = set(counter.keys())
        unused_characters = valid_characters - used_characters
        
        return Counter({char: 0 for char in unused_characters})

    def multi_length_mte_counter(script, bracket_index, maximum_frequencies, max_char_long):
        """
        Finds the most useful sequences for DTE/MTE compression without overlap, and returns a Counter.

        Args:
            script (list of str): Lines of cleaned text.
            bracket_index (int): Format of hex codes to ignore.
            maximum_frequencies (int): Maximum number of results.
            max_char_long (int): Maximum length of sequences to consider.

        Returns:
            Counter: {sequence: gain} without overlapping.
        """
        if bracket_index == 0:
            raw_byte = r'~[0-9A-Fa-f]{2}~'
        elif bracket_index == 1:
            raw_byte = r'\[[0-9A-Fa-f]{2}\]'
        elif bracket_index == 2:
            raw_byte = r'\{[0-9A-Fa-f]{2}\}'
        elif bracket_index == 3:
            raw_byte = r'<[0-9A-Fa-f]{2}>'
        else:
            raise ValueError("Invalid bracket index")

         # Join all text and remove hex codes
        full_text = re.sub(raw_byte, '', ''.join(script))
        sequence_counter = Counter()

        # Count all possible sequences
        for length in range(max_char_long, 1, -1):
            for i in range(len(full_text) - length + 1):
                substr = full_text[i:i + length]
                sequence_counter[substr] += 1

        # Calculate gains
        scored = [
            (seq, freq, freq * (len(seq) - 1))
            for seq, freq in sequence_counter.items()
            if freq > 1
        ]
        scored.sort(key=lambda x: (-x[2], x[0]))

        # Anti-overlap filter
        occupied = [False] * len(full_text)
        selected = {}

        for seq, _, _ in scored:
            seq_len = len(seq)
            positions = []

            for i in range(len(full_text) - seq_len + 1):
                if full_text[i:i + seq_len] == seq and not any(occupied[i:i + seq_len]):
                    positions.append(i)

            if len(positions) >= 2:
                for i in positions:
                    for j in range(i, i + seq_len):
                        occupied[j] = True

                gain = len(positions) * (seq_len - 1)
                selected[seq] = gain

            if len(selected) >= maximum_frequencies:
                break

        return Counter(selected)
