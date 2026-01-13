import io
import random
from PIL import Image, ImageDraw, ImageFont

def create_captcha_image(text):
    # 1. إعدادات الصورة
    width, height = 200, 80 # كبرنا العرض قليلاً للأمان
    background_color = (43, 45, 49) 
    img = Image.new('RGB', (width, height), color=background_color)
    d = ImageDraw.Draw(img)

    # 2. محاولة تحميل خط أوضح
    try:
        # سنحاول استخدام خط النظام الافتراضي بحجم كبير
        font = ImageFont.load_default() 
        # ملاحظة: يفضل مستقبلاً وضع ملف خط .ttf في مجلد utils واستدعاؤه هنا
    except:
        font = None

    # 3. رسم النص (توسيط النص بشكل أفضل)
    # رسم النص باللون الأحمر الصارخ كما تفضل
    d.text((60, 25), text, fill=(255, 0, 0), font=font)

    # 4. إضافة تشويش قوي (خطوط)
    for i in range(15):
        start = (random.randint(0, width), random.randint(0, height))
        end = (random.randint(0, width), random.randint(0, height))
        d.line([start, end], fill=(100, 100, 100), width=1)

    # 5. إضافة نقاط Noise
    for i in range(250): # زيادة النقاط لتعقيد المهمة على البوتات الأخرى
        d.point((random.randint(0, width), random.randint(0, height)), fill=(150, 150, 150))

    # 6. الحفظ في الذاكرة
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)
    
    return img_byte_arr
