import json
import os

DATA_FILE = "database.json"

def load_from_json():
    """تحميل البيانات من الملف عند تشغيل البوت"""
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                return json.load(f)
        except:
            return {}
    return {}

def get_stats(users_data, uid, gid=None):
    """جلب بيانات العضو وتجهيزها إذا كانت غير موجودة"""
    uid = str(uid)
    if uid not in users_data:
        users_data[uid] = {}
    
    # إذا طلبنا بيانات سيرفر محدد (البيانات المحلية)
    if gid:
        gid = str(gid)
        if gid not in users_data[uid]:
            users_data[uid][gid] = {
                "msg_count": 0, 
                "voice_seconds": 0, 
                "xp": 0, 
                "level": 1, 
                "mrad": 0,
                "daily_activity": {},
                "daily_voice": {}
            }
        return users_data[uid][gid]
    
    # إذا طلبنا البيانات العالمية (مجموع كل السيرفرات)
    global_stats = {"msg_count": 0, "voice_seconds": 0, "xp": 0, "level": 0, "mrad": 0}
    for g_id, g_data in users_data[uid].items():
        if isinstance(g_data, dict):
            for key in global_stats:
                global_stats[key] += g_data.get(key, 0)
    return global_stats

def save_to_json(data):
    """حفظ البيانات في ملف database.json بشكل آمن"""
    try:
        with open(DATA_FILE, "w") as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        print(f"Error saving database: {e}")
