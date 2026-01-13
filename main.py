import discord
from discord import app_commands
from discord.ext import commands
import os, json, time, random, io
from datetime import datetime
from flask import Flask, render_template, request, jsonify
from threading import Thread

# --- استيراد الملحقات الجديدة ---
from utils.database_utils import get_stats, save_to_json
from utils.settings_logic import load_settings, update_setting, DEVELOPER_ID

# --- إعدادات البوت الأساسية ---
class HermenyaBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.all()
        super().__init__(command_prefix="!", intents=intents)
        self.data_file = "database.json"
        
        # التأكد من وجود ملف قاعدة البيانات
        if not os.path.exists(self.data_file):
            with open(self.data_file, "w") as f: json.dump({}, f)
            
        with open(self.data_file, "r") as f: 
            self.users_data = json.load(f)
            
        self.voice_times = {}

    def save_data(self):
        save_to_json(self.users_data)

    async def setup_hook(self):
        # تحميل الملفات من مجلد الأوامر تلقائياً
        for filename in os.listdir('./commands'):
            if filename.endswith('.py'):
                try:
                    await self.load_extension(f'commands.{filename[:-3]}')
                    print(f'✅ تم تحميل: {filename}')
                except Exception as e:
                    print(f'❌ خطأ في تحميل {filename}: {e}')
        
        await self.tree.sync()
        print("✅ تم مزامنة أوامر السلاش بنجاح")

bot = HermenyaBot()

# --- إعدادات Flask للوحة التحكم ---
app = Flask(__name__, template_folder='templates')

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    settings = load_settings()
    return render_template('dashboard.html', 
                           settings=settings, 
                           total_users=len(bot.users_data))

@app.route('/toggle_command', methods=['POST'])
def toggle_command():
    data = request.json
    cmd_name = data.get('command')
    # استخدام الدالة من الملحقات
    if update_setting(cmd_name, not load_settings()[cmd_name]['enabled']):
        return jsonify({"status": "success"})
    return jsonify({"status": "error"}), 400

# --- أحداث البوت (اللفل والنشاط) ---
@bot.event
async def on_message(message):
    if message.author.bot or not message.guild: return
    
    uid, gid = str(message.author.id), str(message.guild.id)
    today = datetime.now().strftime("%Y-%m-%d")
    
    # استخدام get_stats المستوردة من الملحقات
    stats = get_stats(bot.users_data, uid, gid)
    stats["msg_count"] += 1
    
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
    uid, gid = str(member.id), str(member.guild.id)
    today = datetime.now().strftime("%Y-%m-%d")
    
    if before.channel is None and after.channel is not None:
        bot.voice_times[member.id] = time.time()
    elif before.channel is not None and after.channel is None:
        if member.id in bot.voice_times:
            duration = int(time.time() - bot.voice_times.pop(member.id))
            stats = get_stats(bot.users_data, uid, gid)
            stats["voice_seconds"] += duration 
            
            if "daily_voice" not in stats: stats["daily_voice"] = {}
            stats["daily_voice"][today] = stats["daily_voice"].get(today, 0) + duration
            
            while stats["voice_seconds"] >= 300:
                stats["xp"] += 1
                stats["voice_seconds"] -= 300
                if stats["xp"] >= 20:
                    stats["level"] += 1
                    stats["xp"] = 0
            bot.save_data()

# --- تشغيل Flask و Discord Bot ---
def run():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

if __name__ == "__main__":
    Thread(target=run).start()
    token = os.environ.get("DISCORD_TOKEN")
    if token:
        bot.run(token)
    else:
        print("❌ خطأ: لم يتم العثور على التوكن!")
