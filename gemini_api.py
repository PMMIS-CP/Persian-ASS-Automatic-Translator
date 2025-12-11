# gemini_api.py

import json
from google import genai
from google.genai import types
from typing import Dict, Any

def translate_text(api_key: str, text_content: str, prompt_data: Dict[str, Any]) -> list[str]:
    """
    متن ساب‌تایتل را با استفاده از تنظیمات دیکشنری برای ترجمه به API جمنای ارسال می‌کند.
    
    Args:
        api_key (str): کلید API جمنای.
        text_content (str): کل محتوای فایل TXT (شامل پیشوندهای 1-، 2- و...).
        prompt_data (Dict[str, Any]): یک دیکشنری حاوی دستورالعمل‌های ترجمه (مثل زبان مبدا، مقصد و لحن).
    
    Returns:
        list[str]: لیستی از خطوط ترجمه شده (با حفظ پیشوندهای 1-، 2- و...)، یا لیستی با پیام خطا.
    """
    try:
        # ۱. راه‌اندازی کلاینت
        client = genai.Client(api_key=api_key)

        # ۲. استخراج تنظیمات از دیکشنری
        source_lang = prompt_data.get("source_lang", "English")
        target_lang = prompt_data.get("target_lang", "Persian")
        tone = prompt_data.get("tone", "professional")
        extra_instruction = prompt_data.get("extra_instruction", "")
        
        # ۳. ساخت دستورالعمل سیستمی برای مدل (System Instruction)
        system_instruction = (
            f"You are a professional subtitle translator. Your task is to translate the provided subtitle lines "
            f"from {source_lang} to {target_lang}. Preserve the line-by-line structure EXACTLY. "
            f"Each line starts with a sequential prefix (e.g., '1-', '2-') which you MUST include in the output "
            f"at the start of the translated text. The tone of the translation should be {tone}. "
            f"{extra_instruction.strip()} "
            f"Do not add any extra text, explanations, or formatting. Only return the translated lines with their original prefixes."
        )
        
        # ۴. فراخوانی مدل جمنای
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=text_content,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction
            )
        )

        # ۵. پردازش پاسخ و بازگرداندن خطوط
        translated_lines = [line.strip() for line in response.text.split('\n') if line.strip()]
        
        return translated_lines

    except Exception as e:
        return [f"ERROR calling Gemini API: {e}"]