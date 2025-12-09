# srt_parser.py

def extract_dialogue_text_from_srt(srt_file_path):
    """
    Extracts dialogue texts from an SRT file and returns them as a list.

    SRT format blocks:
    1
    00:00:04,509 --> 00:00:09,731
    Hi! I'm fine
    (empty line)

    Args:
        srt_file_path (str): The full path to the SRT file.

    Returns:
        list: A list of strings, where each string is a dialogue line.
    """
    dialogue_texts = []
    
    try:
        with open(srt_file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
            # Flags and variables
            is_dialogue_block = False
            
            for line in lines:
                line = line.strip()
                
                # Check for empty line, which marks the end of a block
                if not line:
                    is_dialogue_block = False
                    continue
                
                # Check if line is a timestamp (e.g., 00:00:04,509 --> 00:00:09,731)
                # Timestamps contain "-->"
                if "-->" in line:
                    # Next line(s) will be dialogue text
                    is_dialogue_block = True
                    continue
                
                # Check if line is a block number (e.g., "1", "2")
                # This check is basic, assuming block numbers are only digits.
                if line.isdigit():
                    continue

                # If it's not empty, not a timestamp, and not a block number, it must be the dialogue text.
                if is_dialogue_block:
                    dialogue_texts.append(line)
        
        return dialogue_texts

    except FileNotFoundError:
        return [f"ERROR: File not found at {srt_file_path}"]
    except Exception as e:
        return [f"ERROR processing file: {e}"]