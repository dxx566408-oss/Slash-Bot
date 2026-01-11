import discord
from discord import app_commands
from discord.ext import commands
import os
import json
import time
import random
from datetime import datetime, timedelta
from flask import Flask
from threading import Thread

# --- تشغيل السيرفر لإبقاء البوت حياً ---
app = Flask('')
@app.route('/')
def home(): return "Hermenya Bot is Online!"
def run(): app.run(host='0.0.0.0', port=8080)
def keep_alive():
    t = Thread(target=run)
    t.start()

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
        print("✅ تم مزامنة جميع الأوامر الـ 11 بنجاح")

bot = HermenyaBot()

# --- دالة جلب البيانات (تبدأ من الصفر دائماً) ---
def get_stats(user_id):
    uid = str(user_id)
    if uid not in bot.users_data:
        bot.users_data[uid] = {
            "mrad": 0, "level": 0, "xp": 0, 
            "msg_count": 0, "voice_seconds": 0, "rank": "عضو"
        }
    return bot.users_data[uid]

# --- نظام الحسبة التلقائية (رسائل وصوت) ---
@bot.event
async def on_message(message):
    if message.author.bot: return
    stats = get_stats(message.author.id)
    stats["msg_count"] += 1
    if stats["msg_count"] % 25 == 0:
        stats["xp"] += 1
        if stats["xp"] >= 20:
            stats["level"] += 1
            stats["xp"] = 0
    bot.save_data()
    await bot.process_commands(message)

@bot.event
async def on_voice_state_update(member, before, after):
    if member.bot: return
    if before.channel is None and after.channel is not None:
        bot.voice_times[member.id] = time.time()
    elif before.channel is not None and after.channel is None:
        if member.id in bot.voice_times:
            duration = int(time.time() - bot.voice_times.pop(member.id))
            stats = get_stats(member.id)
            stats["voice_seconds"] += duration 
            while stats["voice_seconds"] >= 300: # 5 دقائق تراكمية
                stats["xp"] += 1
                stats["voice_seconds"] -= 300
                if stats["xp"] >= 20:
                    stats["level"] += 1
                    stats["xp"] = 0
            bot.save_data()

# --- 1. أمر مراد (عرض وتحويل) ---
@bot.tree.command(name="mrad", description="عرض الرصيد أو تحويل عملة مراد")
async def mrad(interaction: discord.Interaction, user: discord.Member = None, amount: int = None):
    if amount is None:
        target = user or interaction.user
        s = get_stats(target.id)
        return await interaction.response.send_message(embed=discord.Embed(description=f"💰 رصيد **{target.mention}** هو: `{s['mrad']}` مراد", color=discord.Color.red()))

    if user is None or user.id == interaction.user.id or user.bot:
        return await interaction.response.send_message("❌ منشن شخصاً حقيقياً للتحويل.", ephemeral=True)
    
    sender_s = get_stats(interaction.user.id)
    if amount <= 0 or sender_s["mrad"] < amount:
        return await interaction.response.send_message("❌ رصيدك غير كافٍ!", ephemeral=True)

    captcha = str(random.randint(1111, 9999))
    await interaction.response.send_message(embed=discord.Embed(title="🛡️ تحقق", description=f"اكتب الرقم للتأكيد: **`{captcha}`**", color=discord.Color.orange()))

    def check(m): return m.author == interaction.user and m.content == captcha and m.channel == interaction.channel
    try:
        await bot.wait_for('message', check=check, timeout=30.0)
        receiver_s = get_stats(user.id)
        sender_s["mrad"] -= amount
        receiver_s["mrad"] += amount
        bot.save_data()
        await interaction.followup.send(f"✅ تم تحويل `{amount}` إلى {user.mention}")
    except: await interaction.followup.send("⚠️ ألغيت العملية.")

# --- 2. أمر المستوى ---
@bot.tree.command(name="level", description="مستوى التفاعل في السيرفر")
async def level(interaction: discord.Interaction, user: discord.Member = None):
    user = user or interaction.user
    s = get_stats(user.id)
    embed = discord.Embed(title=f"📊 مستوى {user.display_name}", color=discord.Color.red())
    embed.add_field(name="Lvl", value=f"`{s['level']}`")
    embed.add_field(name="XP", value=f"`{s['xp']}/20`")
    await interaction.response.send_message(embed=embed)

# --- 3. أمر البروفايل العالمي ---
@bot.tree.command(name="profile", description="البطاقة العالمية للعضو")
async def profile(interaction: discord.Interaction, user: discord.Member = None):
    user = user or interaction.user
    s = get_stats(user.id)
    embed = discord.Embed(title=f"👤 بروفايل {user.name}", color=discord.Color.red())
    embed.add_field(name="💰 إجمالي مراد", value=f"`{s['mrad']}`")
    embed.add_field(name="🏆 الرتبة", value=f"`{s['rank']}`")
    await interaction.response.send_message(embed=embed)

# --- 4. أمر التوب ---
@bot.tree.command(name="top", description="أغنى 10 في مراد")
async def top(interaction: discord.Interaction):
    sorted_users = sorted(bot.users_data.items(), key=lambda x: x[1]['mrad'], reverse=True)[:10]
    desc = "\n".join([f"**#{i+1}** | <@{uid}> - `{d['mrad']}`" for i, (uid, d) in enumerate(sorted_users)])
    await interaction.response.send_message(embed=discord.Embed(title="🏆 توب مراد", description=desc or "لا بيانات", color=discord.Color.red()))

# --- 5. النرد ---
@bot.tree.command(name="dice", description="لعبة النرد")
async def dice(interaction: discord.Interaction, bet: int = None):
    s = get_stats(interaction.user.id)
    if bet and (bet <= 0 or s["mrad"] < bet): return await interaction.response.send_message("❌ رصيد غير كافٍ", ephemeral=True)
    res = random.randint(1, 6)
    msg = f"🎲 النرد: **{res}**"
    if bet:
        if res >= 4: s["mrad"] += bet; msg += f"\n🎉 ربحت `{bet}`"
        else: s["mrad"] -= bet; msg += f"\n❌ خسرت `{bet}`"
        bot.save_data()
    await interaction.response.send_message(msg)

# --- أوامر المعلومات (6-11) ---
@bot.tree.command(name="avatar")
async def avatar(i: discord.Interaction, u: discord.Member = None):
    u = u or i.user
    await i.response.send_message(embed=discord.Embed(color=discord.Color.red()).set_image(url=u.display_avatar.url))

@bot.tree.command(name="id")
async def id_cmd(i: discord.Interaction, u: discord.Member = None):
    u = u or i.user
    await i.response.send_message(f"🆔: `{u.id}`")

@bot.tree.command(name="server")
async def server(i: discord.Interaction):
    await i.response.send_message(f"🏰: **{i.guild.name}** | الأعضاء: `{i.guild.member_count}`")

@bot.tree.command(name="name", description="عرض اليوزر نيم والدسبلي نيم والنك نيم")
@app_commands.describe(member="العضو المراد فحص أسمائه")
async def name_info(interaction: discord.Interaction, member: discord.Member = None):
    target = member or interaction.user
    
    # 1. اليوزر نيم (الأصلي)
    username = target.name
    # 2. الدسبلي نيم (الاسم الظاهر في الملف الشخصي)
    display_name = target.display_name
    # 3. النك نيم (اللقب داخل السيرفر - قد يكون None)
    nick_name = target.nick

    embed = discord.Embed(title="🏷️ قائمة الأسماء", color=0x000000)
    embed.add_field(name="اليوزر نيم (Username)", value=f"`{username}`", inline=False)
    embed.add_field(name="الدسبلي نيم (Display Name)", value=f"`{display_name}`", inline=False)
    
    # التحقق: إذا كان النك نيم موجوداً (ليس None) قم بعرضه
    if nick_name:
        embed.add_field(name="النك نيم (Nickname)", value=f"`{nick_name}`", inline=False)
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="user", description="عرض معلومات الحساب وتاريخ الانضمام")
@app_commands.describe(member="العضو الذي تريد رؤية معلوماته")
async def user_info(interaction: discord.Interaction, member: discord.Member = None):
    target = member or interaction.user
    
    # تحويل التواريخ إلى طوابع زمنية لديسكورد
    # :D تعني التاريخ (يوم/شهر/سنة)
    # :R تعني الوقت النسبي (قبل كم)
    created_ts = int(target.created_at.timestamp())
    joined_ts = int(target.joined_at.timestamp())
    
    embed = discord.Embed(title=f"👤 معلومات العضو: {target.display_name}", color=0x000000) # لون أسود فخم
    embed.set_thumbnail(url=target.display_avatar.url)
    
    embed.add_field(
        name="🗓️ تاريخ إنشاء الحساب", 
        value=f"أنشأ حسابه في: <t:{created_ts}:D>\nأي قبل: **<t:{created_ts}:R>**", 
        inline=False
    )
    
    embed.add_field(
        name="📥 تاريخ دخول السيرفر", 
        value=f"دخل السيرفر في: <t:{joined_ts}:D>\nأي قبل: **<t:{joined_ts}:R>**", 
        inline=False
    )

    await interaction.response.send_message(embed=embed)

@bot.command()
async def ping(ctx): await ctx.send(f"🏓 Pong! `{round(bot.latency * 1000)}ms`")

keep_alive()
bot.run(os.getenv("DISCORD_TOKEN"))
