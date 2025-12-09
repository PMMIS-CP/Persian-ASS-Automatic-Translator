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
                line = line.strip('\n') # Keep line breaks for output consistency
                
                if line.startswith('Dialogue:'):
                    dialogue_counter += 1
                    
                    # خط را به 10 بخش تقسیم می‌کند (متن دیالوگ در ایندکس 9 است)
                    parts = line.split(',', 9)
                    
                    if len(parts) == 10:
                        # بخش اطلاعات دیالوگ (قبل از متن)
                        dialogue_info = parts[0:9]
                        
                        # متن اصلی (انگلیسی)
                        english_text = parts[9].strip()
                        
                        # تگ‌های فرمت‌دهی ASS را از متن اصلی جدا می‌کنیم
                        # (مثلا {\an5} یا تگ‌های رنگ) تا در متن ترجمه جدید قرار داده شوند.
                        # این کار تضمین می‌کند که فرمت‌دهی حفظ شود.
                        format_tags = re.findall(r'\{[^}]*\}', english_text)
                        
                        
                        if translation_index < len(translations):
                            persian_text = translations[translation_index]
                            
                            # اضافه کردن تگ‌ها به ابتدای متن فارسی جدید
                            # این فرض می‌کند که تگ‌ها باید در ابتدای متن باقی بمانند.
                            new_text = "".join(format_tags) + persian_text
                            
                            # ساختار دهی مجدد خط دیالوگ جدید
                            new_line = ",".join(dialogue_info) + "," + new_text
                            output_lines.append(new_line)
                            
                            translation_index += 1
                        else:
                            # اگر تعداد ترجمه‌ها کمتر از دیالوگ‌ها باشد، خط اصلی را حفظ می‌کنیم.
                            output_lines.append(line)
                            print(f"Warning: Missing translation for dialogue line {dialogue_counter}. Keeping original text.")
                    else:
                        # اگر خط دیالوگ ساختار استاندارد را نداشت، آن را بدون تغییر حفظ می‌کنیم.
                        output_lines.append(line)
                else:
                    # خطوط غیر دیالوگ (مانند [Script Info], [V4+ Styles] و ...) را حفظ می‌کنیم.
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