import discord
from discord import app_commands
from discord.ext import commands
import os
import json
import time
import random
from datetime import datetime
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
        print("✅ تم مزامنة جميع الأوامر بنجاح")

bot = HermenyaBot()

# --- دالة جلب البيانات ---
def get_stats(user_id):
    uid = str(user_id)
    if uid not in bot.users_data:
        bot.users_data[uid] = {
            "mrad": 0, "level": 0, "xp": 0, 
            "msg_count": 0, "voice_seconds": 0, "rank": "عضو"
        }
    return bot.users_data[uid]

# --- نظام الحسبة التلقائية ---
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
            while stats["voice_seconds"] >= 300:
                stats["xp"] += 1
                stats["voice_seconds"] -= 300
                if stats["xp"] >= 20:
                    stats["level"] += 1
                    stats["xp"] = 0
            bot.save_data()

# --- 1. أمر مراد (أحمر فاقع) ---
@bot.tree.command(name="mrad", description="عرض وتحويل رصيد مراد")
async def mrad(interaction: discord.Interaction, user: discord.Member = None, amount: int = None, add_amount: int = None):
    MY_ID = 1371432836946726934 
    
    if add_amount is not None:
        if interaction.user.id == MY_ID:
            stats = get_stats(interaction.user.id)
            stats["mrad"] += add_amount
            bot.save_data()
            return await interaction.response.send_message(f"✅ تم إضافة `{add_amount}` لرصيدك يا مطورنا!")
        else:
            return await interaction.response.send_message("❌ هذا الخيار للمطور فقط!", ephemeral=True)

    if amount is None:
        target = user or interaction.user
        s = get_stats(target.id)
        return await interaction.response.send_message(embed=discord.Embed(description=f"💰 رصيد **{target.mention}** هو: `{s['mrad']}` مراد", color=0xff0000))

    # نظام التحويل
    sender_s = get_stats(interaction.user.id)
    if amount <= 0 or sender_s["mrad"] < amount:
        return await interaction.response.send_message("❌ رصيدك لا يكفي للتحويل!", ephemeral=True)

    captcha = str(random.randint(1111, 9999))
    await interaction.response.send_message(
        embed=discord.Embed(
            title="🛡️ تحقق", 
            description=f"اكتب الرقم للتأكيد: **`{captcha}`**", 
            color=0xff0000
        )
    )

    def check(m): return m.author == interaction.user and m.channel == interaction.channel
    try:
        msg_res = await bot.wait_for('message', check=check, timeout=30.0)
        if msg_res.content == captcha:
            await msg_res.delete()
            await interaction.delete_original_response()
            
            receiver_s = get_stats(user.id)
            sender_s["mrad"] -= amount
            receiver_s["mrad"] += amount
            bot.save_data()
            await interaction.followup.send(f"✅ تم تحويل `{amount}` إلى {user.mention}")
        else:
            await msg_res.delete()
            await interaction.followup.send("❌ الرقم غير صحيح، تم إلغاء العملية.", ephemeral=True)
    except TimeoutError:
        await interaction.followup.send("⚠️ انتهى الوقت، تم إلغاء العملية.")

# --- 2. أمر النرد (أحمر فاقع) ---
@bot.tree.command(name="dice", description="إلقاء حجر نرد")
async def dice(interaction: discord.Interaction, bet: int = None):
    s = get_stats(interaction.user.id)
    if bet and (bet <= 0 or s["mrad"] < bet): return await interaction.response.send_message("❌ رصيد غير كافٍ", ephemeral=True)
    res = random.randint(1, 6)
    msg = f"🎲 النرد: **{res}**"
    if bet:
        if res >= 4: s["mrad"] += bet; msg += f"\n🎉 ربحت `{bet}`"
        else: s["mrad"] -= bet; msg += f"\n❌ خسرت `{bet}`"
        bot.save_data()
    await interaction.response.send_message(embed=discord.Embed(description=msg, color=0xff0000))

# --- 3. أمر الأفاتار (أحمر فاقع) ---
@bot.tree.command(name="avatar", description="عرض صورة الحساب")
async def avatar(interaction: discord.Interaction, member: discord.Member = None):
    target = member or interaction.user
    avatar_url = target.display_avatar.with_size(1024).url
    embed = discord.Embed(title=f"صورة {target.name}", url=avatar_url, color=0xff0000)
    embed.set_image(url=avatar_url)
    await interaction.response.send_message(embed=embed)

# --- 4. أمر الآيدي (أحمر فاقع) ---
@bot.tree.command(name="id", description="عرض الآيدي")
async def id_info(interaction: discord.Interaction, member: discord.Member = None):
    target = member or interaction.user
    embed = discord.Embed(title="🆔 معرف العضو", color=0xff0000)
    embed.add_field(name="العضو", value=target.mention, inline=True)
    embed.add_field(name="الآيدي", value=f"`{target.id}`", inline=True)
    embed.set_thumbnail(url=target.display_avatar.url)
    await interaction.response.send_message(embed=embed)

# --- 5. أمر السيرفر (أحمر فاقع) ---
@bot.tree.command(name="server", description="معلومات السيرفر")
async def server_info(interaction: discord.Interaction):
    guild = interaction.guild
    created_ts = int(guild.created_at.timestamp())
    embed = discord.Embed(title=f"🏡 سيرفر: {guild.name}", color=0xff0000)
    if guild.icon: embed.set_thumbnail(url=guild.icon.url)
    embed.add_field(name="👑 المالك", value=guild.owner.mention, inline=True)
    embed.add_field(name="📅 تاريخ الإنشاء", value=f"<t:{created_ts}:D>", inline=True)
    embed.add_field(name="👥 الأعضاء", value=f"`{guild.member_count}`", inline=True)
    await interaction.response.send_message(embed=embed)

# --- 6. أمر الأسماء (أحمر فاقع) ---
@bot.tree.command(name="name", description="عرض جميع أسماء العضو بالتفصيل")
@app_commands.describe(member="العضو المراد فحص أسمائه")
async def name_info(interaction: discord.Interaction, member: discord.Member = None):
    target = member or interaction.user
    
    # 1. اليوزر نيم الأصلي (الفريد)
    user_name = target.name
    
    # 2. الاسم العالمي (Global Name) - الاسم الذي يظهر في الملف الشخصي العام
    global_name = target.global_name if target.global_name else "لا يوجد"
    
    # 3. النيك نيم (Server Nickname) - اللقب داخل هذا السيرفر فقط
    server_nick = target.nick if target.nick else "لا يوجد لقب"

    embed = discord.Embed(
        title="🏷️ قائمة الأسماء", 
        description=f"تفاصيل الأسماء لـ: {target.mention}", 
        color=0xff0000
    )
    
    # إضافة الحقول بشكل منفصل وواضح
    embed.add_field(name="Username (الأصلي)", value=f"`{user_name}`", inline=False)
    embed.add_field(name="Display Name (العالمي)", value=f"`{global_name}`", inline=False)
    embed.add_field(name="Server Nickname (اللقب)", value=f"`{server_nick}`", inline=False)
    
    # وضع صورة العضو المصغرة
    embed.set_author(name=target.name, icon_url=target.display_avatar.url)
    
    await interaction.response.send_message(embed=embed)

# --- 7. أمر اليوزر (أحمر فاقع) ---
@bot.tree.command(name="user", description="عرض معلومات الحساب")
async def user_info(interaction: discord.Interaction, member: discord.Member = None):
    await interaction.response.defer()
    target = member or interaction.user
    created_ts = int(target.created_at.timestamp())
    joined_ts = int(target.joined_at.timestamp())
    embed = discord.Embed(title=f"👤 معلومات: {target.display_name}", color=0xff0000)
    embed.set_thumbnail(url=target.display_avatar.url)
    embed.add_field(name="🗓️ إنشاء الحساب", value=f"<t:{created_ts}:D> (<t:{created_ts}:R>)", inline=False)
    embed.add_field(name="📥 دخول السيرفر", value=f"<t:{joined_ts}:D> (<t:{joined_ts}:R>)", inline=False)
    await interaction.followup.send(embed=embed)

@bot.command()
async def ping(ctx): await ctx.send(f"🏓 Pong! `{round(bot.latency * 1000)}ms`")

keep_alive()
bot.run(os.getenv("DISCORD_TOKEN"))
