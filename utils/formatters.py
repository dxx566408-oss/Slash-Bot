def format_time(seconds):
    """تحويل الثواني إلى تنسيق مقروء (ساعة، دقيقة، ثانية)"""
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    
    parts = []
    if hours > 0: parts.append(f"{hours} ساعة")
    if minutes > 0: parts.append(f"{minutes} دقيقة")
    if secs > 0 or not parts: parts.append(f"{secs} ثانية")
    
    return " و ".join(parts)

def create_progress_bar(current, total, length=10):
    """إنشاء شريط تقدم مرئي (مثلاً للـ XP)"""
    if total <= 0: return "░" * length
    full_count = int((current / total) * length)
    empty_count = length - full_count
    return "█" * full_count + "░" * empty_count

def format_number(number):
    """تنسيق الأرقام الكبيرة (مثلاً 1000 تصبح 1,000)"""
    return "{:,}".format(number)
