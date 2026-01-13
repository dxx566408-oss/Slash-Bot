import json
import os

# آيدي المطور (أنت) - استخدمه للتحقق من الصلاحيات في الأوامر
DEVELOPER_ID = 1371432836946726934

# الإعدادات الافتراضية للوحة التحكم (Flask)
DEFAULT_SETTINGS = {
    "moveme": {"enabled": True, "description": "ينقلك إلى روم صوتي."},
    "profile": {"enabled": True, "description": "عرض بطاقة التعريف الشخصية."},
    "user": {"enabled": True, "description": "عرض معلومات الحساب."},
    "avatar": {"enabled": True, "description": "عرض الصورة الشخصية."},
    "daily": {"enabled": True, "description": "المكافأة اليومية."}
}

SETTINGS_FILE = 'settings.json'

def load_settings():
    """تحميل إعدادات لوحة التحكم من الملف أو إنشاؤها إذا لم توجد"""
    if not os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
            json.dump(DEFAULT_SETTINGS, f, indent=4, ensure_ascii=False)
        return DEFAULT_SETTINGS
    
    with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def update_setting(command_name, status):
    """تحديث حالة أمر معين (تفعيل/تعطيل) من لوحة التحكم"""
    settings = load_settings()
    if command_name in settings:
        settings[command_name]['enabled'] = status
        with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
            json.dump(settings, f, indent=4, ensure_ascii=False)
        return True
    return False
