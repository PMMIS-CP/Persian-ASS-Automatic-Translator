# cli_tool.py (FINAL ROBUST VERSION with RTL FIXER + Prefix Option + Prefix Remover + OPTIONAL WORD RTL)

import cmd
import os
import shlex
import json
from ass_parser import extract_dialogue_text_from_ass
from srt_parser import extract_dialogue_text_from_srt
from ass_replacer import replace_ass_dialogues
from rtl_fixer import process_rtl_file 
from prefix_remover import remove_line_prefixes
from gemini_api import translate_text
from openai_api import translate_text_openai

class SubtitleToolShell(cmd.Cmd):
    
    prompt = 'SubToolCLI> '
    intro = "\nWelcome to the Subtitle Tool CLI. Type 'help' or '?' for commands.\n"
    
    def do_exit(self, line):
        """Exits the command-line environment."""
        print("Goodbye!")
        return True

    # --- Command 1: Extract ASS (Updated Usage) ---
    def do_extract_ass(self, line):
        """
        Extracts dialogue texts from an ASS file and saves them to a TXT file.
        Usage: extract_ass "/path/to/your file with spaces.ass" [add_prefix_Y/N]
        (add_prefix_Y/N is optional. Use 'Y' to prepend '1-', '2-', ... to all lines.)
        """
        self._parse_and_call(line, (1, 2), 'ass', extract_dialogue_text_from_ass, self._process_file)

    # --- Command 2: Extract SRT (Updated Usage) ---
    def do_extract_srt(self, line):
        """
        Extracts dialogue texts from an SRT file and saves them to a TXT file.
        Usage: extract_srt "/path/to/your file with spaces.srt" [add_prefix_Y/N]
        (add_prefix_Y/N is optional. Use 'Y' to prepend '1-', '2-', ... to all lines.)
        """
        self._parse_and_call(line, (1, 2), 'srt', extract_dialogue_text_from_srt, self._process_file)

    # --- Command 3: Replace ASS Dialogues with Persian (ROBUST VERSION) ---
    def do_replace_ass(self, line):
        """
        Replaces English dialogue in an ASS file with Persian translation from a TXT file.
        
        Usage: replace_ass "<path/to/translations.txt>" "<path/to/original.ass>"
        """
        self._parse_and_call(line, 2, 'ass_replace', replace_ass_dialogues, self._replace_ass_handler)
        
    # --- Command 4: RTL Fixer (MODIFIED COMMAND) ---
    def do_RTL(self, line): 
        """
        Fixes RTL display issues in a Persian TXT file by moving ending punctuation 
        (., ..., ,, !, :) to the start. Optionally, reverses the word order.
        
        Usage: RTL "/path/to/your_extracted.txt" [Y/N for word RTL]
        (Y/N is optional. Use 'Y' to enable word order reversal, default is N)
        """
        # Expected args is now 1 or 2
        self._parse_and_call(line, (1, 2), 'rtl_fix', process_rtl_file, self._rtl_handler)

    # --- Command 5: Prefix Remover ---
    def do_remove_prefix(self, line): 
        """
        Removes sequential prefixes (e.g., '1-', '2-', ...) from the start of a TXT file's lines.
        
        Usage: remove_prefix "/path/to/your_file_with_prefixes.txt"
        """
        self._parse_and_call(line, 1, 'prefix_remove', remove_line_prefixes, self._prefix_remover_handler)

    # --- Handler for replace_ass logic (No change) ---
    def _replace_ass_handler(self, args, file_type, extraction_function, add_prefix=False):
        """Handles the specific logic for the replace_ass command."""
        translation_file_path = args[0]
        ass_file_path = args[1]
        
        print(f"Loading translations from: {translation_file_path}")
        print(f"Processing ASS file: {ass_file_path}")
        
        result = extraction_function(ass_file_path, translation_file_path) 
        
        if result.startswith("ERROR"):
            print(f"\n❌ Operation Failed: {result}")
        else:
            print("\n✅ Translation replacement successful!")
            print(f"   New Persian ASS file created at: {result}")

    # --- Handler for RTL Fixer Logic (MODIFIED HANDLER) ---
    def _rtl_handler(self, args, file_type, processing_function, add_prefix=False):
        """Handles the specific logic for the RTL command."""
        full_path = args[0]
        
        # Check for the optional second argument passed by _parse_and_call
        fix_words_flag = False
        if len(args) == 2 and args[1].upper() == 'Y':
            fix_words_flag = True
            
        print(f"Starting RTL correction on file: {full_path}")
        print(f"Word RTL Reversal enabled: {'Yes' if fix_words_flag else 'No'}")
        
        # Pass the new flag to the processing function (rtl_fixer.process_rtl_file)
        result_path = processing_function(full_path, fix_words_flag=fix_words_flag) 
        
        if result_path.startswith("ERROR"):
            print(f"\n❌ Operation Failed: {result_path}")
        else:
            print("\n✅ RTL Correction successful!")
            print(f"   New RTL-Fixed file created at: {result_path}")

    # --- Handler for Prefix Remover Logic (No change) ---
    def _prefix_remover_handler(self, args, file_type, processing_function, add_prefix=False): 
        """Handles the specific logic for the remove_prefix command."""
        full_path = args[0]
        
        print(f"Starting prefix removal on file: {full_path}...")
        
        result_path = processing_function(full_path) 
        
        if result_path.startswith("ERROR"):
            print(f"\n❌ Operation Failed: {result_path}")
        else:
            print("\n✅ Prefix removal successful!")
            print(f"   New file without prefixes created at: {result_path}")

    # --- Centralized Argument Parsing (MODIFIED FOR RTL) ---
    def _parse_and_call(self, line, expected_args, file_type, extraction_function, handler_function):
        """
        Parses the command line using shlex and validates the number of arguments.
        """
        try:
            args = shlex.split(line) 
        except ValueError as e:
            print(f"ERROR parsing arguments (check for unmatched quotes): {e}")
            return
            
        num_args = len(args)
        
        if isinstance(expected_args, tuple):
            min_args, max_args = expected_args
            is_valid = (num_args >= min_args and num_args <= max_args)
        else:
            min_args = max_args = expected_args
            is_valid = (num_args == expected_args)
            
        if not is_valid:
            print("ERROR: Invalid number of arguments.")
            if file_type in ('ass', 'srt'):
                print(f"Usage: extract_{file_type} \"/path/to/file.{file_type}\" [add_prefix_Y/N]")
            elif file_type == 'rtl_fix':
                print("Usage: RTL \"/path/to/file.txt\" [Y/N for word RTL]")
            elif file_type == 'ass_replace':
                print("Usage: replace_ass \"<path/to/translations.txt>\" \"<path/to/original.ass>\"")
            elif file_type == 'prefix_remove': 
                print("Usage: remove_prefix \"/path/to/file.txt\"")
            return
        
        add_prefix = False
        if file_type in ('ass', 'srt') and num_args == 2:
            prefix_arg = args[1].upper()
            if prefix_arg == 'Y':
                add_prefix = True
                args = args[:1] 
            elif prefix_arg == 'N':
                args = args[:1]
            else:
                print("ERROR: Optional argument must be 'Y' or 'N' for prefix feature.")
                return

        if file_type == 'rtl_fix' and num_args == 2:
            rtl_word_arg = args[1].upper()
            if rtl_word_arg not in ('Y', 'N'):
                print("ERROR: Optional argument for word RTL must be 'Y' or 'N'.")
                return
        handler_function(args, file_type, extraction_function, add_prefix)


    # --- Helper Method to handle common logic for extraction (No change) ---
    def _process_file(self, args, file_type, extraction_function, add_prefix=False):
        """
        A general method to handle file processing and saving output for extract_ass/srt.
        """
        full_path = args[0]
        
        if not full_path:
            print(f"ERROR: Please provide the full path to the {file_type.upper()} file.")
            return

        print(f"Processing {file_type.upper()} file: {full_path}...")
        
        texts = extraction_function(full_path, add_prefix)

        if texts and not texts[0].startswith("ERROR"):
            base_name, _ = os.path.splitext(full_path)
            output_filename = base_name + "_extracted.txt"
            
            try:
                with open(output_filename, 'w', encoding='utf-8') as outfile:
                    outfile.write('\n'.join(texts))
                
                print("\n✅ Extraction successful!")
                print(f"   File Type: {file_type.upper()}")
                print(f"   Prefix Added: {'Yes' if add_prefix else 'No'}")
                print(f"   Output saved to: {output_filename}")
                print(f"   The file contains {len(texts)} lines of dialogue.")
                
            except Exception as e:
                print(f"ERROR saving output file: {e}")
            
        else:
            print(texts[0])

    # --- Command: Full ASS Translation Pipeline ---
    def do_translate_ass(self, line):
        """
        کل فرآیند ترجمه زیرنویس ASS را با استفاده از API جمنای و تنظیمات داخلی انجام می‌دهد.
        
        استفاده: translate_ass "<ass_file_path>" "<gemini_api_key>"
        
        تنظیمات پرامپت از فایل 'translation_config.json' خوانده می‌شود.
        """
        CONFIG_FILE = "translation_config.json" # <--- نام ثابت فایل تنظیمات
        
        try:
            args = shlex.split(line)
        except ValueError:
            print("ERROR: Could not parse arguments. Ensure all paths are correctly quoted.")
            return

        if len(args) != 2:
            print("ERROR: Incorrect number of arguments.")
            print("Usage: translate_ass \"<ass_file_path>\" \"<gemini_api_key>\"")
            return
            
        ass_file_path, gemini_api_key = args
        
        if not os.path.exists(ass_file_path):
            print(f"ERROR: ASS file not found at {ass_file_path}")
            return
            
        # --- ۱. خواندن تنظیمات پرامپت از فایل JSON ---
        print("\n--- 1. Reading Translation Configuration ---")
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            
            prompt_data = config_data.get("prompt_settings", {})
            if not prompt_data:
                print(f"ERROR: 'prompt_settings' not found in {CONFIG_FILE}.")
                return
                
            print(f"✅ Configuration loaded successfully from {CONFIG_FILE}.")
            print(f"   Target Language: {prompt_data.get('target_lang', 'N/A')}")
            print(f"   Translation Tone: {prompt_data.get('tone', 'N/A')}")
            
        except FileNotFoundError:
            print(f"FATAL ERROR: Configuration file '{CONFIG_FILE}' not found. Please create it.")
            return
        except json.JSONDecodeError:
            print(f"FATAL ERROR: Invalid JSON format in '{CONFIG_FILE}'. Check the file structure.")
            return
        except Exception as e:
            print(f"ERROR reading configuration file: {e}")
            return
        
        # --- ۲. استخراج متن با پیشوند (توسط ass_parser.py) ---
        print("\n--- 2. Extraction with Prefix (Using ass_parser) ---")
        extracted_texts_with_prefix = extract_dialogue_text_from_ass(ass_file_path, add_prefix=True)
        # ... (بقیه منطق استخراج و بررسی خطا)
        
        if not extracted_texts_with_prefix or extracted_texts_with_prefix[0].startswith("ERROR"):
            print(f"Extraction Error: {extracted_texts_with_prefix[0] if extracted_texts_with_prefix else 'No dialogue lines found.'}")
            return
            
        original_line_count = len(extracted_texts_with_prefix)
        input_text_for_ai = "\n".join(extracted_texts_with_prefix)
        print(f"✅ Extracted {original_line_count} dialogue lines with prefixes.")
        
        # --- ۳. ارسال به Gemini AI برای ترجمه ---
        print("\n--- 3. Sending to Gemini AI or OpenAI AI for Translation ---")

        translated_lines_with_prefix = translate_text_openai(
            gemini_api_key, # نام متغیر آرگومان را gemini_api_key نگه می‌داریم، اما کلید OpenAI را ارسال می‌کنیم
            input_text_for_ai, 
            prompt_data
        )
        # ***********************************
        
        if translated_lines_with_prefix and translated_lines_with_prefix[0].startswith("ERROR"):
            print(f"AI Translation Error: {translated_lines_with_prefix[0]}")
            return
            
        translated_line_count = len(translated_lines_with_prefix)

        # ارسال دیکشنری تنظیمات به جای رشته JSON خام
        translated_lines_with_prefix = translate_text(gemini_api_key, input_text_for_ai, prompt_data)
        
        if translated_lines_with_prefix and translated_lines_with_prefix[0].startswith("ERROR"):
            print(f"AI Translation Error: {translated_lines_with_prefix[0]}")
            return
            
        translated_line_count = len(translated_lines_with_prefix)

        # --- ۴. بررسی تطابق تعداد خطوط و هشدار (Critical Step) ---
        if translated_line_count != original_line_count:
            print(f"\n❌ WARNING: Line count mismatch!")
            print(f"   Original lines expected: {original_line_count}")
            print(f"   Translated lines received: {translated_line_count}")
            
            retry = input("Do you want to retry the AI operation? (Y/N): ").strip().upper()
            if retry != 'Y':
                print("Translation aborted by user due to line count mismatch.")
                return
            
            print("Please adjust the prompt or check the input file and run the command again.")
            return

        print(f"✅ AI Translation successful. Line count verified: {translated_line_count} lines match original.")
        
        # --- ۵. ذخیره خروجی خام ترجمه (با پیشوند) برای ورودی مرحله بعد ---
        base_name, _ = os.path.splitext(ass_file_path)
        ai_output_txt_path = base_name + "_AI_translated_raw.txt"
        
        try:
            with open(ai_output_txt_path, 'w', encoding='utf-8') as f:
                f.write("\n".join(translated_lines_with_prefix))
            print(f"   Raw translation (with prefixes) saved to: {ai_output_txt_path}")
        except Exception as e:
            print(f"ERROR saving AI raw output file: {e}")
            return
            
        # --- ۶. حذف پیشوندهای ترتیبی (توسط prefix_remover.py) ---
        print("\n--- 6. Removing Sequential Prefixes (Using prefix_remover) ---")
        no_prefix_path = remove_line_prefixes(ai_output_txt_path)
        
        if no_prefix_path.startswith("ERROR"):
            print(f"Prefix Remover Error: {no_prefix_path}")
            return
        print(f"✅ Prefixes removed. Output saved to: {no_prefix_path}")

        # --- ۷. اعمال فیکس RTL (توسط rtl_fixer.py) ---
        print("\n--- 7. Applying RTL (Right-to-Left) Fixes (Using rtl_fixer) ---")
        rtl_fixed_path = process_rtl_file(no_prefix_path, fix_words_flag=False)
        
        if rtl_fixed_path.startswith("ERROR"):
            print(f"RTL Fixer Error: {rtl_fixed_path}")
            return
        print(f"✅ RTL fix applied. Output saved to: {rtl_fixed_path}")

        # --- ۸. جایگذاری دیالوگ‌ها در فایل ASS اصلی (توسط ass_replacer.py) ---
        print("\n--- 8. Replacing Dialogues in Original ASS File (Using ass_replacer) ---")
        final_ass_path = replace_ass_dialogues(ass_file_path, rtl_fixed_path)

        if final_ass_path.startswith("ERROR"):
            print(f"ASS Replacer Error: {final_ass_path}")
            return

        print("\n=======================================================")
        print("🎉 Translation Pipeline Completed Successfully! 🎉")
        print(f"Original ASS File: {ass_file_path}")
        print(f"Final Translated ASS File: {final_ass_path}")
        print("=======================================================")

if __name__ == '__main__':
    SubtitleToolShell().cmdloop()