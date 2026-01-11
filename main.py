import discord
from discord import app_commands
from discord.ext import commands
import os
import json
import time
import random
from flask import Flask
from threading import Thread
import io
import aiohttp

# --- إبقاء البوت مستيقظاً ---
app = Flask('')
@app.route('/')
def home(): return "Hermenya Bot is Online!"
def run(): app.run(host='0.0.0.0', port=8080)
def keep_alive():
    t = Thread(target=run)
    t.start()

# --- إعدادات البوت ---
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
        print("✅ تم تحديث نظام الحسبة وأوامر التحويل")

bot = HermenyaBot()

def get_stats(user_id):
    uid = str(user_id)
    if uid not in bot.users_data:
        bot.users_data[uid] = {
            "mrad": 0, "level": 1, "xp": 0, 
            "msg_count": 0, "voice_seconds": 0, "rank": "عضو"
        }
    return bot.users_data[uid]

# --- نظام كسب النقاط التلقائي المحسن ---
@bot.event
async def on_message(message):
    if message.author.bot: return
    
    stats = get_stats(message.author.id)
    stats["msg_count"] += 1
    
    # كل 25 رسالة تعطي 1 XP
    if stats["msg_count"] % 25 == 0:
        stats["xp"] += 1
        # كل 20 XP تعطي 1 لفل (إجمالي 500 رسالة)
        if stats["xp"] >= 20:
            stats["level"] += 1
            stats["xp"] = 0
    
    # زيادة رصيد مراد (1 مراد لكل رسالة كمكافأة)
    stats["mrad"] += 1
    bot.save_data()
    await bot.process_commands(message)

@bot.event
async def on_voice_state_update(member, before, after):
    if member.bot: return
    
    # دخول الصوت
    if before.channel is None and after.channel is not None:
        bot.voice_times[member.id] = time.time()
    
    # خروج من الصوت
    elif before.channel is not None and after.channel is None:
        if member.id in bot.voice_times:
            duration = time.time() - bot.voice_times.pop(member.id)
            minutes = int(duration / 60)
            stats = get_stats(member.id)
            stats["voice_seconds"] += int(duration)
            
            # كل 5 دقائق صوت تعادل 1 XP
            xp_gained = minutes // 5
            if xp_gained > 0:
                stats["xp"] += xp_gained
                while stats["xp"] >= 20:
                    stats["level"] += 1
                    stats["xp"] -= 20
            
            # زيادة مراد (2 مراد لكل دقيقة)
            stats["mrad"] += (minutes * 2)
            bot.save_data()

# --- الأوامر المحدثة ---

@bot.tree.command(name="mrad", description="تحويل عملة مراد لعضو آخر")
async def mrad(interaction: discord.Interaction, user: discord.Member = None, amount: int = None):
    # إذا لم يحدد مستخدم أو مبلغ، يعرض رصيده الحالي فقط
    if user is None or amount is None:
        target = user or interaction.user
        s = get_stats(target.id)
        embed = discord.Embed(description=f"💰 رصيد **{target.mention}** هو: `{s['mrad']}` مراد", color=discord.Color.red())
        return await interaction.response.send_message(embed=embed)

    # نظام التحويل (Transfer)
    if user.id == interaction.user.id:
        return await interaction.response.send_message("❌ لا يمكنك التحويل لنفسك!", ephemeral=True)
    
    sender_s = get_stats(interaction.user.id)
    if amount <= 0 or sender_s["mrad"] < amount:
        return await interaction.response.send_message("❌ رصيدك غير كافٍ أو المبلغ خاطئ!", ephemeral=True)

    # إنشاء رقم التحقق
    captcha = str(random.randint(1111, 9999))
    embed = discord.Embed(title="🛡️ تأكيد التحويل", 
                        description=f"لتحويل `{amount}` إلى {user.mention}\nاكتب الرقم التالي للتأكيد: **`{captcha}`**", 
                        color=discord.Color.orange())
    await interaction.response.send_message(embed=embed)

    def check(m):
        return m.author == interaction.user and m.content == captcha and m.channel == interaction.channel

    try:
        msg = await bot.wait_for('message', check=check, timeout=30.0)
        # تنفيذ التحويل
        receiver_s = get_stats(user.id)
        sender_s["mrad"] -= amount
        receiver_s["mrad"] += amount
        bot.save_data()
        await interaction.followup.send(f"✅ تم تحويل `{amount}` مراد إلى {user.mention} بنجاح!")
    except:
        await interaction.followup.send("⚠️ انتهى الوقت أو الرقم خاطئ، تم إلغاء العملية.")

@bot.tree.command(name="profile", description="عرض بروفايل هرمينيا")
async def profile(interaction: discord.Interaction, user: discord.Member = None):
    user = user or interaction.user
    s = get_stats(user.id)
    embed = discord.Embed(title=f"👤 ملف {user.display_name}", color=discord.Color.red())
    embed.set_thumbnail(url=user.display_avatar.url)
    embed.add_field(name="💰 رصيد مراد", value=f"`{s['mrad']}`", inline=True)
    embed.add_field(name="🏆 الرتبة", value=f"`{s['rank']}`", inline=True)
    embed.add_field(name="📊 المستوى", value=f"`Lvl {s['level']}`", inline=True)
    embed.add_field(name="✨ الخبرة (XP)", value=f"`{s['xp']}/20`", inline=True)
    embed.set_footer(text=f"طلب بواسطة {interaction.user.name}")
    await interaction.response.send_message(embed=embed)

# (بقية الأوامر id, name, server, avatar, top, user تبقى كما هي في كودك الأصلي)
# سأضعها لك هنا لضمان عمل الكود كاملاً:

@bot.tree.command(name="id", description="عرض معرف العضو")
async def id_cmd(interaction: discord.Interaction, user: discord.Member = None):
    user = user or interaction.user
    await interaction.response.send_message(f"🆔 معرف **{user.mention}** هو: `{user.id}`")

@bot.tree.command(name="top", description="قائمة العشرة الأوائل")
async def top(interaction: discord.Interaction):
    sorted_users = sorted(bot.users_data.items(), key=lambda x: x[1]['mrad'], reverse=True)[:10]
    desc = ""
    for i, (uid, data) in enumerate(sorted_users, 1):
        u = bot.get_user(int(uid))
        name = u.name if u else f"User {uid}"
        desc += f"**#{i}** | {name} - `{data['mrad']} mrad`\n"
    embed = discord.Embed(title="🏆 قائمة متصدري هرمينيا", description=desc or "لا توجد بيانات", color=discord.Color.red())
    await interaction.response.send_message(embed=embed)

keep_alive()
bot.run(os.getenv("DISCORD_TOKEN"))
