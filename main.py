import discord
from discord import app_commands
from discord.ext import commands
import os, json, time, random, io
from datetime import datetime
from flask import Flask, render_template, request, jsonify
from threading import Thread

# --- استيراد الملحقات ---
from utils.database_utils import get_stats, save_to_json
from utils.settings_logic import load_settings, update_setting, DEVELOPER_ID

class HermenyaBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.all()
        # إضافة اسم المستخدم كـ "العقل"
        super().__init__(command_prefix="!", intents=intents)
        self.data_file = "database.json"
        
        # تحميل البيانات بأمان
        if not os.path.exists(self.data_file):
            with open(self.data_file, "w") as f: json.dump({}, f)
            
        with open(self.data_file, "r") as f: 
            try:
                self.users_data = json.load(f)
            except:
                self.users_data = {}
            
        self.voice_times = {}

    def save_data(self):
        save_to_json(self.users_data)

    async def setup_hook(self):
        # تحميل الملفات من مجلد الأوامر
        if not os.path.exists('./commands'):
            os.makedirs('./commands')
            
        for filename in os.listdir('./commands'):
            if filename.endswith('.py'):
                try:
                    await self.load_extension(f'commands.{filename[:-3]}')
                    print(f'✅ Loaded: {filename}')
                except Exception as e:
                    print(f'❌ Failed to load {filename}: {e}')
        
        await self.tree.sync()
        print("✅ Slash Commands Synced")

bot = HermenyaBot()

# --- Flask Dashboard ---
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
    current_settings = load_settings()
    if cmd_name in current_settings:
        new_status = not current_settings[cmd_name]['enabled']
        if update_setting(cmd_name, new_status):
            return jsonify({"status": "success", "new_status": new_status})
    return jsonify({"status": "error"}), 400

# --- الأحداث الأساسية ---
@bot.event
async def on_message(message):
    if message.author.bot or not message.guild: return
    
    uid, gid = str(message.author.id), str(message.guild.id)
    stats = get_stats(bot.users_data, uid, gid)
    
    # السطر القديم (اتركه كما هو)
    stats["msg_count"] += 1 
    
    # السطر الجديد المطلوب لكي يعمل أمر level
    stats["ms"] = stats.get("ms", 0) + 1 
    
    bot.save_data()
    await bot.process_commands(message)

@bot.event
async def on_voice_state_update(member, before, after):
    if member.bot or not member.guild: return
    uid, gid = str(member.id), str(member.guild.id)
    
    # دخول الروم
    if before.channel is None and after.channel is not None:
        bot.voice_times[member.id] = time.time()
        
    # خروج من الروم
    elif before.channel is not None and after.channel is None:
        if member.id in bot.voice_times:
            duration = int(time.time() - bot.voice_times.pop(member.id))
            stats = get_stats(bot.users_data, uid, gid)
            
            # السطر القديم
            stats["voice_seconds"] += duration 
            
            # السطر الجديد المطلوب (تراكم الثواني)
            stats["vs"] = stats.get("vs", 0) + duration 
            
            bot.save_data()

# --- التشغيل السحابي ---
def run():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)

if __name__ == "__main__":
    t = Thread(target=run)
    t.start()
    
    # توكن البوت (سيتم وضعه في إعدادات Render)
    token = os.environ.get("DISCORD_TOKEN")
    if token:
        bot.run(token)
    else:
        print("❌ CRITICAL ERROR: DISCORD_TOKEN NOT FOUND!")
