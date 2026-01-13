import io
import random
from PIL import Image, ImageDraw, ImageFont

def create_captcha_image(text):
    """
    توليد صورة كابتشا تحتوي على نص مشوش لمنع البوتات.
    """
    # 1. إنشاء خلفية الصورة (لون داكن يتناسب مع ديسكورد)
    width, height = 170, 70
    background_color = (43, 45, 49) # لون رومات ديسكورد
    img = Image.new('RGB', (width, height), color=background_color)
    d = ImageDraw.Draw(img)

    # 2. رسم النص (باللون الأحمر كما في كودك الأصلي)
    # ملاحظة: إذا أردت استخدام خط معين، يمكنك تحميله هنا، حالياً سيستخدم الخط الافتراضي
    d.text((55, 25), text, fill=(255, 0, 0))

    # 3. إضافة تشويش (خطوط عشوائية) لزيادة الصعوبة
    for i in range(10):
        start_point = (random.randint(0, width), random.randint(0, height))
        end_point = (random.randint(0, width), random.randint(0, height))
        line_color = (random.randint(50, 150), random.randint(50, 150), random.randint(50, 150))
        d.line([start_point, end_point], fill=line_color, width=1)

    # 4. إضافة نقاط عشوائية (Noise)
    for i in range(100):
        d.point((random.randint(0, width), random.randint(0, height)), fill=(200, 200, 200))

    # 5. حفظ الصورة في ذاكرة مؤقتة (Buffer) بدلاً من القرص الصلب
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)
    
    return img_byte_arr
