# cli_tool.py (FINAL ROBUST VERSION with RTL FIXER)

import cmd
import os
import shlex 
# Import all required modules
from ass_parser import extract_dialogue_text_from_ass
from srt_parser import extract_dialogue_text_from_srt
from ass_replacer import replace_ass_dialogues
from rtl_fixer import process_rtl_file # <-- NEW: Import for RTL functionality

class SubtitleToolShell(cmd.Cmd):
    
    prompt = 'SubToolCLI> '
    intro = "\nWelcome to the Subtitle Tool CLI. Type 'help' or '?' for commands.\n"
    
    def do_exit(self, line):
        """Exits the command-line environment."""
        print("Goodbye!")
        return True

    # --- Command 1: Extract ASS ---
    def do_extract_ass(self, line):
        """
        Extracts dialogue texts from an ASS file and saves them to a TXT file.
        Usage: extract_ass "/path/to/your file with spaces.ass"
        """
        self._parse_and_call(line, 1, 'ass', extract_dialogue_text_from_ass, self._process_file)

    # --- Command 2: Extract SRT ---
    def do_extract_srt(self, line):
        """
        Extracts dialogue texts from an SRT file and saves them to a TXT file.
        Usage: extract_srt "/path/to/your file with spaces.srt"
        """
        self._parse_and_call(line, 1, 'srt', extract_dialogue_text_from_srt, self._process_file)

    # --- Command 3: Replace ASS Dialogues with Persian (ROBUST VERSION) ---
    def do_replace_ass(self, line):
        """
        Replaces English dialogue in an ASS file with Persian translation from a TXT file.
        
        Usage: replace_ass "<path/to/translations.txt>" "<path/to/original.ass>"
        (Quotation marks are REQUIRED for paths with spaces or special characters)
        """
        self._parse_and_call(line, 2, 'ass_replace', replace_ass_dialogues, self._replace_ass_handler)
        
    # --- Command 4: RTL Fixer (NEW COMMAND) ---
    def do_RTL(self, line): 
        """
        Fixes RTL display issues in a Persian TXT file by moving ending punctuation
        (., ..., ,, ;, !) to the start of the line. Saves output to a new file.
        
        Usage: RTL "/path/to/your_extracted.txt"
        """
        self._parse_and_call(line, 1, 'rtl_fix', process_rtl_file, self._rtl_handler)

    # --- Handler for replace_ass logic ---
    def _replace_ass_handler(self, args, file_type, extraction_function):
        """Handles the specific logic for the replace_ass command."""
        translation_file_path = args[0]
        ass_file_path = args[1]
        
        print(f"Loading translations from: {translation_file_path}")
        print(f"Processing ASS file: {ass_file_path}")
        
        # Call the replace function from ass_replacer.py
        result = extraction_function(ass_file_path, translation_file_path) # extraction_function here is replace_ass_dialogues
        
        if result.startswith("ERROR"):
            print(f"\n❌ Operation Failed: {result}")
        else:
            print("\n✅ Translation replacement successful!")
            print(f"   New Persian ASS file created at: {result}")

    # --- Handler for RTL Fixer Logic (NEW HANDLER) ---
    def _rtl_handler(self, args, file_type, processing_function):
        """Handles the specific logic for the RTL command."""
        full_path = args[0]
        
        print(f"Starting RTL correction on file: {full_path}...")
        
        # processing_function here is process_rtl_file
        result_path = processing_function(full_path) 
        
        if result_path.startswith("ERROR"):
            print(f"\n❌ Operation Failed: {result_path}")
        else:
            print("\n✅ RTL Correction successful!")
            print(f"   New RTL-Fixed file created at: {result_path}")


    # --- Centralized Argument Parsing ---
    def _parse_and_call(self, line, expected_args, file_type, extraction_function, handler_function):
        """
        Parses the command line using shlex and validates the number of arguments.
        """
        try:
            # Robustly split arguments, correctly handling quotes
            args = shlex.split(line) 
        except ValueError as e:
            print(f"ERROR parsing arguments (check for unmatched quotes): {e}")
            return
            
        if len(args) != expected_args:
            print("ERROR: Invalid number of arguments.")
            if expected_args == 1:
                if file_type == 'rtl_fix':
                    print("Usage: RTL \"/path/to/file.txt\"")
                else:
                    print(f"Usage: extract_{file_type} \"/path/to/file.{file_type}\"")
            elif expected_args == 2:
                print("Usage: replace_ass \"<path/to/translations.txt>\" \"<path/to/original.ass>\"")
            return
        
        # Call the specific handler logic
        handler_function(args, file_type, extraction_function)


    # --- Helper Method to handle common logic for extraction ---
    def _process_file(self, args, file_type, extraction_function):
        """
        A general method to handle file processing and saving output for extract_ass/srt.
        """
        full_path = args[0]
        
        if not full_path:
            # Should not happen if _parse_and_call passed, but good for safety
            print(f"ERROR: Please provide the full path to the {file_type.upper()} file.")
            return

        print(f"Processing {file_type.upper()} file: {full_path}...")
        
        # 1. Call the appropriate extraction function
        texts = extraction_function(full_path)

        if texts and not texts[0].startswith("ERROR"):
            # 2. Determine the output filename
            base_name, _ = os.path.splitext(full_path)
            output_filename = base_name + "_extracted.txt"
            
            # 3. Save the output
            try:
                with open(output_filename, 'w', encoding='utf-8') as outfile:
                    outfile.write('\n'.join(texts))
                
                print("\n✅ Extraction successful!")
                print(f"   File Type: {file_type.upper()}")
                print(f"   Output saved to: {output_filename}")
                print(f"   The file contains {len(texts)} lines of dialogue.")
                
            except Exception as e:
                print(f"ERROR saving output file: {e}")
            
        else:
            print(texts[0])

if __name__ == '__main__':
    SubtitleToolShell().cmdloop()