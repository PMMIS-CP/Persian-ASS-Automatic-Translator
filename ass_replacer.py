# ass_replacer.py

import os
import re

def replace_ass_dialogues(ass_file_path, translation_file_path):
    """
    Reads Persian translations from a TXT file and replaces the dialogue text 
    in the ASS file, preserving all formatting and timing information.
    
    Args:
        ass_file_path (str): The full path to the original ASS file.
        translation_file_path (str): The full path to the TXT file containing the translations (one dialogue per line).

    Returns:
        str: Path to the newly created ASS file or an error message.
    """
    
    # 1. Read Translation Texts (Persian)
    try:
        with open(translation_file_path, 'r', encoding='utf-8') as f:
            translations = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        return f"ERROR: Translation file not found at {translation_file_path}"
    except Exception as e:
        return f"ERROR reading translation file: {e}"

    # 2. Process ASS File and Replace Dialogues
    output_lines = []
    translation_index = 0
    dialogue_counter = 0

    try:
        with open(ass_file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip('\n') # Preserve line breaks for output consistency
                
                if line.startswith('Dialogue:'):
                    dialogue_counter += 1
                    
                    # Split the line into 10 parts (the dialogue text is at index 9)
                    parts = line.split(',', 9)
                    
                    if len(parts) == 10:
                        # Dialogue information section (before the text content)
                        dialogue_info = parts[0:9]
                        
                        # The original (English) text content
                        english_text = parts[9].strip()
                        
                        # Extract ASS formatting tags from the original text
                        # (e.g., {\an5} or color tags) to be placed in the new translated text.
                        # This ensures that styling is preserved.
                        format_tags = re.findall(r'\{[^}]*\}', english_text)
                        
                        
                        if translation_index < len(translations):
                            persian_text = translations[translation_index]
                            
                            # Add the extracted tags to the beginning of the new Persian text
                            # This assumes the tags should remain at the start of the text.
                            new_text = "".join(format_tags) + persian_text
                            
                            # Reconstruct the new dialogue line
                            new_line = ",".join(dialogue_info) + "," + new_text
                            output_lines.append(new_line)
                            
                            translation_index += 1
                        else:
                            # If the number of translations is less than the dialogues, keep the original line.
                            output_lines.append(line)
                            print(f"Warning: Missing translation for dialogue line {dialogue_counter}. Keeping original text.")
                    else:
                        # If the dialogue line does not have the standard structure, keep it unchanged.
                        output_lines.append(line)
                else:
                    # Preserve non-dialogue lines (e.g., [Script Info], [V4+ Styles], etc.).
                    output_lines.append(line)
        
        if translation_index < len(translations):
             print(f"Warning: {len(translations) - translation_index} extra translation line(s) were ignored.")

        # 3. Save the new ASS file
        base_name, ext = os.path.splitext(ass_file_path)
        output_file_path = base_name + "_Persian" + ext
        
        with open(output_file_path, 'w', encoding='utf-8') as outfile:
            outfile.write('\n'.join(output_lines))
            
        return output_file_path

    except FileNotFoundError:
        return f"ERROR: Original ASS file not found at {ass_file_path}"
    except Exception as e:
        return f"An unexpected error occurred during processing: {e}"