# Subtitle Dialogue Processing and Persian RTL Fixer CLI Tool

This project provides a simple, command-line interface (CLI) tool for handling subtitle files, specifically focusing on extracting dialogues from **SRT** and **ASS/SSA** formats, and crucially, replacing dialogues in ASS files with Persian translations while applying a necessary **Right-to-Left (RTL) punctuation fix** for proper display.

The tool is designed to assist subtitlers who need to translate content and address common display issues with Persian script in video players.

## 🚀 Features

* **Extract Dialogues (ASS/SRT):** Easily extract all dialogue texts from a given `.ass` or `.srt` file into a clean, line-by-line `.txt` file for translation.
* **Replace Dialogues (ASS):** Replace the original dialogue text in an `.ass` file with translated text from a `.txt` file, while **preserving all ASS formatting tags** and timing information (crucial for styles, positioning, and effects).
* **Persian RTL Punctuation Fix:** A dedicated command to correct the common LTR display issue in Persian text where ending punctuation (e.g., `!`, `.` , `،` , `...`) appears on the left side of the sentence instead of the right. It moves these marks to the start of the line (e.g., `متن!` becomes `!متن`).

## 🛠️ Requirements

The project is written in standard Python and has no external dependencies beyond the built-in modules (`os`, `re`, `cmd`, `shlex`).

* **Python 3.x**

## 📦 How to Run

1.  Save all Python files (`cli_tool.py`, `ass_parser.py`, `srt_parser.py`, `ass_replacer.py`, `rtl_fixer.py`) in the same directory.
2.  Open your terminal or command prompt.
3.  Navigate to the project directory.
4.  Run the CLI tool using Python:

    ```bash
    python cli_tool.py
    ```

    You will be greeted by the `SubToolCLI>` prompt.

## ✍️ Commands Reference

All file paths containing spaces **MUST** be enclosed in double quotes (`"`).

### 1. Extract Dialogues

Extracts dialogue text and saves it to a new file named `[original_filename]_extracted.txt`.

| Command | Description | Example Usage |
| :--- | :--- | :--- |
| `extract_ass` | Extracts dialogues from an ASS/SSA file. | `extract_ass "C:/Subtitles/Movie.ass"` |
| `extract_srt` | Extracts dialogues from an SRT file. | `extract_srt "./data/Episode 1.srt"` |

### 2. Fix RTL Punctuation

Applies the RTL punctuation correction to a Persian `.txt` file and saves the output to `[original_filename]_RTL.txt`. This step is highly recommended **after** the translation is complete and **before** replacing the dialogues.

| Command | Description | Example Usage |
| :--- | :--- | :--- |
| `RTL` | Moves trailing punctuation to the start of the line for RTL correction. | `RTL "C:/Translations/Translated.txt"` |

### 3. Replace ASS Dialogues

Replaces the dialogue text in an original ASS file with the content of the translation file. It saves the output to a new file named `[original_filename]_Persian.ass`.

**IMPORTANT:** The number of lines in the translation TXT file must match the number of dialogue lines in the original ASS file for a successful replacement.

| Command | Description | Example Usage |
| :--- | :--- | :--- |
| `replace_ass` | Replaces the English text in the ASS file with the translated Persian text. | `replace_ass "C:/Translations/Translated_RTL.txt" "C:/Subtitles/Original.ass"` |

### 4. Exit

| Command | Description |
| :--- | :--- |
| `exit` | Exits the CLI tool. |

## 💡 Recommended Workflow

The intended process for localizing a subtitle file from English (or any LTR language) to Persian is:

1.  **Extract:**
    ```
    SubToolCLI> extract_ass "original_en.ass" 
    # Creates original_en_extracted.txt
    ```

2.  **Translate:**
    * Manually translate the lines in `original_en_extracted.txt` to Persian. (Save the result as `translated_fa.txt`).

3.  **Fix RTL:**
    ```
    SubToolCLI> RTL "translated_fa.txt"
    # Creates translated_fa_RTL.txt (ready for replacement)
    ```

4.  **Replace:**
    ```
    SubToolCLI> replace_ass "translated_fa_RTL.txt" "original_en.ass"
    # Creates original_en_Persian.ass (final, formatted file)
    ```

## 📝 Code Overview

### `cli_tool.py`

* The main entry point using Python's `cmd` module.
* Handles command parsing, argument validation using `shlex` (to support paths with spaces), and delegates logic to specific handler functions.

### `ass_parser.py`

* Contains `extract_dialogue_text_from_ass()`.
* Uses `line.split(',', 9)` to reliably isolate the 10th field (dialogue text) in a `Dialogue:` line.
* Uses `re.sub(r'\{[^}]*\}', '', raw_text)` to strip all ASS format/tag information (`{\...}`).

### `srt_parser.py`

* Contains `extract_dialogue_text_from_srt()`.
* Parses SRT blocks by ignoring block numbers and timestamp lines (`-->`) and capturing the subsequent line(s) as dialogue text.

### `rtl_fixer.py`

* Contains `fix_rtl_punctuation()` and `process_rtl_file()`.
* Crucially, it replaces all English commas (`,`) with Persian commas ( `،` ) before fixing.
* The main function `fix_rtl_punctuation()` identifies trailing punctuation (`.`, `...`, `،`, `!`) and moves it to the start of the line to solve the LTR rendering issue in media players.

### `ass_replacer.py`

* Contains `replace_ass_dialogues()`.
* Reads the translations and iterates through the original ASS file.
* For each `Dialogue:` line, it extracts the original ASS formatting tags (`re.findall(r'\{[^}]*\}', english_text)`) and prepends them to the new Persian text before writing the new line, ensuring **perfect style preservation**.
