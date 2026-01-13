import discord
from discord import app_commands
from discord.ext import commands
import os, json, time, random, io
from PIL import Image, ImageDraw
from datetime import datetime
from flask import Flask, render_template, request, jsonify
from threading import Thread

# إعدادات الأوامر
DEFAULT_SETTINGS = {
    "moveme": {"enabled": True, "description": "ينقلك إلى روم صوتي."},
    "profile": {"enabled": True, "description": "عرض بطاقة التعريف الشخصية."},
    "user": {"enabled": True, "description": "عرض معلومات الحساب."},
    "avatar": {"enabled": True, "description": "عرض الصورة الشخصية."},
    "daily": {"enabled": True, "description": "المكافأة اليومية."}
}

def get_settings():
    if not os.path.exists('settings.json'):
        with open('settings.json', 'w') as f: json.dump(DEFAULT_SETTINGS, f, indent=4)
    with open('settings.json', 'r') as f: return json.load(f)

# --- إعداد محرك البوت (SlashBot) ---

class SlashBot(commands.Bot):
    def __init__(self):
        # تفعيل جميع الحواس (Intents) للبوت ليتمكن من قراءة الرسائل والفويس
        intents = discord.Intents.all()
        super().__init__(command_prefix="!", intents=intents)
        
        # إعداد قاعدة البيانات
        self.data_file = "database.json"
        
        # التأكد من وجود ملف قاعدة البيانات عند التشغيل لتجنب أخطاء القراءة
        if not os.path.exists(self.data_file):
            with open(self.data_file, "w") as f: 
                json.dump({}, f)
                print("📁 تم إنشاء ملف database.json جديد")
        
        # تحميل بيانات المستخدمين
        with open(self.data_file, "r") as f: 
            self.users_data = json.load(f)
            
        self.voice_times = {} # لتخزين وقت دخول الأعضاء للفويس مؤقتاً

    # دالة حفظ البيانات (تستدعيها عند كل تغيير في الرصيد أو الخبرة)
    def save_data(self):
        with open(self.data_file, "w") as f: 
            json.dump(self.users_data, f, indent=4)

    # دالة ربط أوامر السلاش (/) مع ديسكورد عند تشغيل البوت
    async def setup_hook(self):
        await self.tree.sync()
        print(f"✅ تم تسجيل أوامر السلاش لبوت: {self.user}")

# إنشاء الكائن الأساسي للبوت
bot = SlashBot()

# --- إعدادات Flask والمسارات ---
app = Flask(__name__, template_folder='templates')

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    settings = get_settings()
    # الآن 'bot' معرف في الخطوة السابقة، لذا لن يظهر خطأ
    return render_template('dashboard.html', 
                           settings=settings, 
                           total_users=len(bot.users_data))

@app.route('/toggle_command', methods=['POST'])
def toggle_command():
    data = request.json
    cmd_name = data.get('command')
    settings = get_settings()
    if cmd_name in settings:
        settings[cmd_name]['enabled'] = not settings[cmd_name]['enabled']
        with open('settings.json', 'w') as f: json.dump(settings, f, indent=4)
        return jsonify({"status": "success"})
    return jsonify({"status": "error"}), 400

# --- تشغيل Flask في Thread منفصل ---
def run():
    # استخدام المنفذ الذي يطلبه Render تلقائياً
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()

# --- دالة صنع صورة الكابتشا ---
def create_captcha_image(text):
    img = Image.new('RGB', (150, 60), color=(43, 45, 49))
    d = ImageDraw.Draw(img)
    d.text((55, 20), text, fill=(255, 0, 0)) 
    for i in range(8):
        d.line([(random.randint(0,150), random.randint(0,60)), 
                (random.randint(0,150), random.randint(0,60))], 
               fill=(100, 100, 100))
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)
    return img_byte_arr

# --- إعدادات البوت الأساسية ---
class HermenyaBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.all()
        super().__init__(command_prefix="!", intents=intents)
        self.data_file = "database.json"
        self.users_data = self.load_data()
        self.voice_times = {}

    def load_data(self):
        if os.path.exists(self.data_file):
            with open(self.data_file, "r") as f: return json.load(f)
        return {}

    def save_data(self):
        with open(self.data_file, "w") as f: json.dump(self.users_data, f, indent=4)

    async def setup_hook(self):
        await self.tree.sync()
        print("✅ تم مزامنة جميع الأوامر بنجاح")

bot = HermenyaBot()

# --- نظام الحسبة المطور مع دعم التواريخ ---
@bot.event
async def on_message(message):
    if message.author.bot or not message.guild: return
    
    uid = str(message.author.id)
    gid = str(message.guild.id)
    today = datetime.now().strftime("%Y-%m-%d")
    
    stats = get_stats(uid, gid)
    stats["msg_count"] += 1
    
    # تسجيل النشاط اليومي للترتيب
    if "daily_activity" not in stats: stats["daily_activity"] = {}
    stats["daily_activity"][today] = stats["daily_activity"].get(today, 0) + 1
    
    if stats["msg_count"] % 25 == 0:
        stats["xp"] += 1
        if stats["xp"] >= 20:
            stats["level"] += 1
            stats["xp"] = 0
            
    bot.save_data()
    await bot.process_commands(message)

@bot.event
async def on_voice_state_update(member, before, after):
    if member.bot or not member.guild: return
    uid = str(member.id)
    gid = str(member.guild.id)
    today = datetime.now().strftime("%Y-%m-%d")
    
    if before.channel is None and after.channel is not None:
        bot.voice_times[member.id] = time.time()
    elif before.channel is not None and after.channel is None:
        if member.id in bot.voice_times:
            duration = int(time.time() - bot.voice_times.pop(member.id))
            stats = get_stats(uid, gid)
            stats["voice_seconds"] += duration 
            
            # تسجيل نشاط الفويس اليومي للترتيب
            if "daily_voice" not in stats: stats["daily_voice"] = {}
            stats["daily_voice"][today] = stats["daily_voice"].get(today, 0) + duration
            
            while stats["voice_seconds"] >= 300:
                stats["xp"] += 1
                stats["voice_seconds"] -= 300
                if stats["xp"] >= 20:
                    stats["level"] += 1
                    stats["xp"] = 0
            bot.save_data()

@bot.command()
async def ping(ctx): await ctx.send(f"🏓 Pong! `{round(bot.latency * 1000)}ms`")

# --- أمر الترتيب (TOP) المطور والشامل ---
@bot.tree.command(name="top", description="عرض الترتيب العام أو ترتيب عضو معين مع السياق")
@app_commands.describe(
    category="نوع الإحصائية (رسائل أو فويس) - اتركها فارغة لعرض الاثنين",
    member="العضو المراد رؤية ترتيبه وما حوله",
    timeframe="الفترة الزمنية (يوم، أسبوع، شهر، الكل)"
)
@app_commands.choices(category=[
    app_commands.Choice(name="الرسائل (Text)", value="msg"),
    app_commands.Choice(name="الفويس (Voice)", value="voice")
], timeframe=[
    app_commands.Choice(name="اليوم (Day)", value="day"),
    app_commands.Choice(name="الأسبوع (Week)", value="week"),
    app_commands.Choice(name="الشهر (Month)", value="month"),
    app_commands.Choice(name="الكل (All Time)", value="all")
])
async def top(
    interaction: discord.Interaction, 
    category: str = None, 
    member: discord.Member = None, 
    timeframe: str = "all"
):
    await interaction.response.defer()
    gid = str(interaction.guild.id)
    now = datetime.now()
    leaderboard = []

    # 1. تجميع البيانات وحساب السكور بناءً على الاختيارات
    for uid, data in bot.users_data.items():
        if gid in data:
            s_data = data[gid]
            m_score = 0
            v_score = 0

            # حساب الرسائل
            if timeframe == "all":
                m_score = s_data.get("msg_count", 0)
                v_score = s_data.get("voice_seconds", 0)
            else:
                act_key = "daily_activity"
                voi_key = "daily_voice"
                for d_str, val in s_data.get(act_key, {}).items():
                    try:
                        delta = (now - datetime.strptime(d_str, "%Y-%m-%d")).days
                        if (timeframe == "day" and delta == 0) or \
                           (timeframe == "week" and delta <= 7) or \
                           (timeframe == "month" and delta <= 30):
                            m_score += val
                    except: continue
                for d_str, val in s_data.get(voi_key, {}).items():
                    try:
                        delta = (now - datetime.strptime(d_str, "%Y-%m-%d")).days
                        if (timeframe == "day" and delta == 0) or \
                           (timeframe == "week" and delta <= 7) or \
                           (timeframe == "month" and delta <= 30):
                            v_score += val
                    except: continue

            # تحديد "السكور الأساسي" للترتيب بناءً على الفئة المختارة
            primary_score = m_score if category == "msg" else v_score if category == "voice" else (m_score + (v_score // 60))
            
            if primary_score > 0:
                leaderboard.append({
                    "id": int(uid), 
                    "msg": m_score, 
                    "voice": v_score, 
                    "sort_val": primary_score
                })

    # 2. الترتيب
    leaderboard.sort(key=lambda x: x["sort_val"], reverse=True)

    if not leaderboard:
        return await interaction.followup.send("❌ لا توجد بيانات مسجلة لهذه الفترة.")

    # 3. تحديد نطاق العرض (السياق أو التوب 10)
    if member:
        m_idx = next((i for i, x in enumerate(leaderboard) if x["id"] == member.id), None)
        if m_idx is None:
            return await interaction.followup.send(f"❌ {member.mention} ليس لديه نشاط في هذه الفترة.")
        start, end = max(0, m_idx - 5), min(len(leaderboard), m_idx + 6)
        display_list = [(i + 1, leaderboard[i]) for i in range(start, end)]
    else:
        display_list = [(i + 1, leaderboard[i]) for i in range(min(10, len(leaderboard)))]

    # 4. بناء الإيمبد
    t_map = {"msg": "✉️ رسائل", "voice": "🎙️ فويس", None: "📊 ترتيب عام"}
    f_map = {"day": "اليوم", "week": "الأسبوع", "month": "الشهر", "all": "الكل"}
    
    embed = discord.Embed(
        title=f"{t_map[category]} | {f_map[timeframe]}",
        color=0xff0000,
        timestamp=now
    )

    desc = ""
    for rank, item in display_list:
        prefix = "➡️ " if member and item["id"] == member.id else ""
        medal = {1: "🥇", 2: "🥈", 3: "🥉"}.get(rank, f"`#{rank}`")
        
        # تنسيق النص بناءً على الفئة المختارة (أو كلاهما)
        score_info = ""
        if category == "msg":
            score_info = f"**{item['msg']}** رسالة"
        elif category == "voice":
            score_info = f"**{item['voice']//3600}**س و **{(item['voice']%3600)//60}**د"
        else:
            score_info = f"✉️`{item['msg']}` | 🎙️`{item['voice']//60}د`"

        desc += f"{prefix}{medal} <@{item['id']}> — {score_info}\n"

    embed.description = desc
    if interaction.guild.icon: embed.set_thumbnail(url=interaction.guild.icon.url)
    embed.set_footer(text=f"طلب بواسطة: {interaction.user.name}", icon_url=interaction.user.display_avatar.url)
    
    await interaction.followup.send(embed=embed)

# --- أمر مزامنة الرسائل القديمة (للمطور فقط) ---
@bot.tree.command(name="sync_history", description="مزامنة الرسائل القديمة (للمطور فقط)")
@app_commands.describe(limit="عدد الرسائل التي يتم فحصها في كل روم (مثلاً 1000)")
async def sync_history(interaction: discord.Interaction, limit: int = 1000):
    # تحقق أنك المطور فقط من يستخدم الأمر
    if interaction.user.id != 1371432836946726934: 
        return await interaction.response.send_message("❌ هذا الأمر للمطور فقط!", ephemeral=True)

    await interaction.response.defer(ephemeral=True)
    gid = str(interaction.guild.id)
    count = 0

    for channel in interaction.guild.text_channels:
        try:
            async for message in channel.history(limit=limit):
                if message.author.bot: continue
                
                uid = str(message.author.id)
                today = message.created_at.strftime("%Y-%m-%d")
                
                # جلب البيانات وتحديثها
                stats = get_stats(uid, gid)
                stats["msg_count"] += 1
                
                # تحديث النشاط اليومي بناءً على تاريخ الرسالة القديمة
                if "daily_activity" not in stats: stats["daily_activity"] = {}
                stats["daily_activity"][today] = stats["daily_activity"].get(today, 0) + 1
                
                # تحديث الـ XP والمستوى
                if stats["msg_count"] % 25 == 0:
                    stats["xp"] += 1
                    if stats["xp"] >= 20:
                        stats["level"] += 1
                        stats["xp"] = 0
                count += 1
        except Exception as e:
            print(f"تعذر قراءة روم {channel.name}: {e}")

    bot.save_data()
    await interaction.followup.send(f"✅ تمت المزامنة! تم جرد `{count}` رسالة قديمة بنجاح.")

# --- تشغيل Flask و Discord Bot معاً ---

def run():
    # Render يتطلب ربط المنفذ بشكل ديناميكي
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()

if __name__ == "__main__":
    keep_alive() # تشغيل الموقع في الخلفية
    
    # جلب التوكن من إعدادات Render السرية وليس من الكود
    token = os.environ.get("DISCORD_TOKEN") 
    if token:
        bot.run(token)
    else:
        print("❌ خطأ: لم يتم العثور على DISCORD_TOKEN في إعدادات Render")
