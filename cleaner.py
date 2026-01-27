import re

def caption_cleaner(text):
    """
    এই ফাংশনটি ক্যাপশন থেকে সমস্ত লিঙ্ক এবং ইউজারনেম মুছে ফেলে।
    """
    if not text:
        return ""

    # ১. টেলিগ্রাম ইউজারনেম মোছার জন্য (@username)
    text = re.sub(r'@\w+', '', text)

    # ২. সব ধরণের ওয়েবসাইট লিঙ্ক মোছার জন্য (http://, https://, www.)
    text = re.sub(r'https?://\S+|www\.\S+', '', text)

    # ৩. টেলিগ্রামের শর্ট লিঙ্ক মোছার জন্য (t.me/...)
    text = re.sub(r't\.me\/\S+', '', text)

    # ৪. বাড়তি স্পেস বা ফাঁকা লাইন পরিষ্কার করা
    text = re.sub(r'\n\s*\n', '\n', text) # ডবল এন্টার বা বাড়তি গ্যাপ কমানো
    
    return text.strip()
  
