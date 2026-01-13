import json
import os

# آيدي المطور (أنت)
DEVELOPER_ID = 1371432836946726934

# القائمة الكاملة للأوامر التي برمجناها لتظهر في لوحة التحكم
DEFAULT_SETTINGS = {
    "moveme": {"enabled": True, "description": "نقل العضو إلى روم صوتي آخر."},
    "profile": {"enabled": True, "description": "عرض بطاقة التفاعل واللفل المحلية."},
    "globalprofile": {"enabled": True, "description": "عرض الإحصائيات الشاملة في كل السيرفرات."},
    "user": {"enabled": True, "description": "عرض معلومات الحساب والتواريخ."},
    "avatar": {"enabled": True, "description": "عرض وتحميل الصورة الشخصية."},
    "mrad": {"enabled": True, "description": "نظام العملة (مراد) والتحويل بالكابتشا."},
    "name": {"enabled": True, "description": "عرض سجل أسماء العضو بالتفصيل."},
    "nickme": {"enabled": True, "description": "تغيير اللقب الشخصي داخل السيرفر."},
    "server": {"enabled": True, "description": "عرض إحصائيات ومعلومات السيرفر."},
    "ping": {"enabled": True, "description": "فحص سرعة استجابة البوت."}
}

SETTINGS_FILE = 'settings.json'

def load_settings():
    """تحميل الإعدادات أو إنشاء ملف جديد إذا كان مفقوداً"""
    if not os.path.exists(SETTINGS_FILE):
        save_settings(DEFAULT_SETTINGS)
        return DEFAULT_SETTINGS
    
    try:
        with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return DEFAULT_SETTINGS

def save_settings(settings):
    """دالة مساعدة لحفظ الإعدادات"""
    with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
        json.dump(settings, f, indent=4, ensure_ascii=False)

def update_setting(command_name, status):
    """تحديث حالة أمر معين (True/False)"""
    settings = load_settings()
    if command_name in settings:
        settings[command_name]['enabled'] = (status is True or status == 'true')
        save_settings(settings)
        return True
    return False
