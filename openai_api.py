# openai_api.py

from openai import OpenAI
from typing import Dict, Any
import time

def translate_text_openai(api_key: str, text_content: str, prompt_data: Dict[str, Any]) -> list[str]:
    """
    متن ساب‌تایتل را با استفاده از API OpenAI (GPT-3.5-Turbo) ترجمه می‌کند.
    
    Args:
        api_key (str): کلید API اوپن‌ای‌آی (sk-proj-...).
        text_content (str): کل محتوای فایل TXT که حاوی خطوط دیالوگ به همراه پیشوندهای ترتیبی است.
        prompt_data (Dict[str, Any]): دیکشنری حاوی دستورالعمل‌های ترجمه (مثل زبان مبدا، مقصد و لحن).

    Returns:
        list[str]: لیستی از خطوط ترجمه شده (با حفظ پیشوندهای 1-، 2- و...)، یا لیستی حاوی پیام خطا.
    """
    # تنظیمات تلاش مجدد
    MAX_RETRIES = 5
    RETRY_DELAY = 10 # ثانیه
    
    # ۱. استخراج تنظیمات
    source_lang = prompt_data.get("source_lang", "English")
    target_lang = prompt_data.get("target_lang", "Persian")
    tone = prompt_data.get("tone", "professional")
    extra_instruction = prompt_data.get("extra_instruction", "")

    # ۲. ساخت دستورالعمل سیستمی (System Prompt)
    system_instruction = (
        f"You are a professional subtitle translator. Your task is to translate the provided subtitle lines "
        f"from {source_lang} to {target_lang}. Preserve the line-by-line structure EXACTLY. "
        f"Each line starts with a sequential prefix (e.g., '1-', '2-') which you MUST include in the output "
        f"at the start of the translated text. The tone of the translation should be {tone}. "
        f"{extra_instruction.strip()} "
        f"Do not add any extra text, explanations, or any formatting other than the translated lines with their original prefixes."
    )

    for attempt in range(MAX_RETRIES):
        try:
            print(f"   Attempt {attempt + 1}/{MAX_RETRIES} to call OpenAI API...")
            
            # ۳. راه‌اندازی کلاینت
            client = OpenAI(api_key=api_key)

            # ۴. فراخوانی مدل
            response = client.chat.completions.create(
                model="gpt-3.5-turbo", # مدل پیشنهادی برای سرعت و هزینه کم
                messages=[
                    {"role": "system", "content": system_instruction},
                    {"role": "user", "content": text_content}
                ],
                temperature=0.0 # ترجمه باید دقیق باشد، نه خلاقانه
            )

            # ۵. پردازش پاسخ و بازگرداندن خطوط
            translated_text = response.choices[0].message.content.strip()
            # خطوط خروجی را بر اساس newline جدا می‌کنیم
            translated_lines = [line.strip() for line in translated_text.split('\n') if line.strip()]
            
            return translated_lines

        except Exception as e:
            error_message = f"ERROR calling OpenAI API on attempt {attempt + 1}: {e}"
            
            # بررسی کنیم آیا خطا مربوط به سرور یا Rate Limit است
            if "Rate limit" in str(e) or "500" in str(e) or "503" in str(e):
                if attempt < MAX_RETRIES - 1:
                    print(f"   {error_message}. Retrying in {RETRY_DELAY} seconds...")
                    time.sleep(RETRY_DELAY)
                else:
                    return [error_message]
            else:
                # خطاهای دیگر (مثل مشکل در کلید API یا پرامپت)
                return [error_message]
    
    return [f"FATAL ERROR: Failed to translate after {MAX_RETRIES} attempts."]