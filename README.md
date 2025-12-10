# Subtitle Manipulation Command Line Tool

## 🎯 Project Goal

The primary goal of this project is to provide a robust and versatile command-line interface (CLI) tool for handling common tasks related to subtitle files, specifically focusing on **ASS/SSA**, **SRT**, and plain **TXT** formats. It is especially useful for Persian (RTL) localization, translation workflows, and dialogue preparation.

***The tool is designed to support both AI-assisted and human translation workflows.***

## ✨ Core Capabilities

The tool is built around a simple CLI (`cli_tool.py`) that offers several key functionalities:

1.  **Dialogue Extraction:** Extracting clean dialogue text (e.g., English) from ASS or SRT files and saving it to a plain TXT file.
    * **Features:** Optional sequential prefixing (`1-`, `2-`, ...) for easy line tracking during translation. **The extracted text (prefixed or not) is ready to be fed to an AI translator or given to a human translator.**
2.  **Dialogue Replacement (ASS):** Replacing the original dialogue text in an ASS file with a translated one (e.g., Persian from a TXT file), while preserving all original timing and styling information.
    * ***Note: SRT replacement functionality is planned for future development.***
3.  **Prefix Removal:** Removing the sequential prefixes (`1-`, `2-`, `...`) from a TXT file, which is useful after the translation is done.
4.  **Right-to-Left (RTL) Fixer:** Applying the **Right-to-Left Embedding (RLE - \u202b)** Unicode character to correctly display Persian and other RTL languages in various environments.
    * **Supported Files:** TXT, SRT, and ASS files.
    * **Logic:**
        * **TXT:** Adds RLE to the beginning of every line.
        * **SRT:** Adds RLE to the beginning of every dialogue line, skipping timestamps and sequence numbers.
        * **ASS:** Intelligently adds RLE after any styling codes (`{\an5}`, `{\i1}`) and after every line break (`\N`).

## 🛠️ Usage Instructions

The tool operates via a command-line interface. To start, navigate to the directory containing `cli_tool.py` and run it:

```bash
python cli_tool.py
````

This will launch the `SubToolCLI>` prompt.

### 1\. Dialogue Extraction

Extracts dialogues from subtitle files into a clean `.txt` file.

| Command | Description |
| :--- | :--- |
| `extract_ass` | Extracts dialogue from an ASS/SSA file. |
| `extract_srt` | Extracts dialogue from an SRT file. |

**Syntax:**

```bash
# Basic Extraction (no prefix)
extract_ass "C:/Path/to/my_subtitle.ass" N

# Extraction with sequential line prefixes (e.g., '1-', '2-', ...)
extract_srt "/path/to/another_file.srt" Y
```

### 2\. Dialogue Replacement (ASS)

Replaces the dialogue text in an original ASS file with translations from a TXT file. The resulting text is ready for insertion into the final ASS file.

**Syntax:**

```bash
replace_ass "<path/to/translations.txt>" "<path/to/original.ass>"
# Example:
# replace_ass "C:/project/extracted_translated.txt" "C:/project/original_movie.ass"
```

### 3\. RTL Fixer

Applies the RLE character to fix rendering issues for RTL languages (like Persian) in various file types.

**Syntax:**

```bash
# Fix a plain TXT file:
RTL "/path/to/persian_translation.txt" N

# Fix an SRT file (the N/Y flag is currently only a placeholder in the implementation):
RTL "C:/path/to/fixed_sub.srt"
```

**Note:** The `rtl_fixer.py` function `process_rtl_file` currently only implements the RLE fix for text display direction. The optional word reversal flag (`Y/N`) is present in the CLI but its corresponding logic for word-order reversal is not yet implemented in the core function.

### 4\. Prefix Remover

Removes the sequential line prefixes (e.g., `1-`, `10-`) that were added during the extraction phase.

**Syntax:**

```bash
remove_prefix "/path/to/your_file_with_prefixes.txt"
# This will create a new file named: your_file_with_prefixes_no_prefix.txt
```

### General Commands

| Command | Description |
| :--- | :--- |
| `help` or `?` | Lists all available commands. |
| `exit` | Closes the CLI. |

-----

## ⚙️ Example Workflow (Persian Translation)

1.  **Extract English Dialogues:** Extract the original dialogues from your ASS file and add prefixes.

    ```bash
    SubToolCLI> extract_ass "original_en.ass" Y
    # Output: original_en_extracted.txt (e.g., 1-Hello, 2-How are you?)
    ```

2.  **Translate (AI or Human):** Take the `original_en_extracted.txt` file, translate the content (leaving the prefixes), and save it as `persian_translated.txt`.

3.  **Fix RTL (Optional but Recommended):** Apply the RLE character to your translated text file to ensure correct display.

    ```bash
    SubToolCLI> RTL "persian_translated.txt" N
    # Output: persian_translated_RLE_fixed.txt
    ```

4.  **Remove Prefixes:** Remove the sequential prefixes from the *RLE-fixed* file.

    ```bash
    SubToolCLI> remove_prefix "persian_translated_RLE_fixed.txt"
    # Output: persian_translated_RLE_fixed_no_prefix.txt (Ready for replacement)
    ```

5.  **Replace Dialogues:** Inject the clean, RLE-fixed Persian dialogues back into the original ASS file.

    ```bash
    SubToolCLI> replace_ass "persian_translated_RLE_fixed_no_prefix.txt" "original_en.ass"
    # Output: original_en_Persian.ass (The final file with Persian subtitles)
    ```