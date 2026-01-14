import io
import random
import string
from captcha.image import ImageCaptcha
import discord

def generate_captcha():
    # توليد 5 أرقام عشوائية
    captcha_text = ''.join(random.choices(string.digits, k=5))
    
    # إعدادات الصورة (أبعاد كبيرة لضمان وضوح التشويش)
    image = ImageCaptcha(width=300, height=120)
    
    # توليد الصورة مع الضجيج التلقائي (الخطوط والنقاط)
    data = image.generate(captcha_text)
    
    # تحويل البيانات لملف جاهز لديسكورد
    file = discord.File(io.BytesIO(data.read()), filename="captcha.png")
    
    return captcha_text, file
