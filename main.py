import discord
from discord import app_commands
from discord.ext import commands
import os
import json
import time
from flask import Flask
from threading import Thread

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
        print("✅ تم تحويل جميع الأوامر إلى نظام الإيمبد")

bot = HermenyaBot()

def get_stats(user_id):
    uid = str(user_id)
    if uid not in bot.users_data:
        bot.users_data[uid] = {
            "mrad": 0, "level": 1, "xp": 0, 
            "msg_count": 0, "voice_seconds": 0, "rank": "عضو"
        }
    return bot.users_data[uid]

# --- نظام كسب النقاط التلقائي ---
@bot.event
async def on_message(message):
    if message.author.bot: return
    stats = get_stats(message.author.id)
    stats["msg_count"] += 1
    stats["xp"] += 5
    stats["mrad"] += 1
    if stats["xp"] >= (stats["level"] * 100):
        stats["level"] += 1
        stats["xp"] = 0
    bot.save_data()

@bot.event
async def on_voice_state_update(member, before, after):
    if member.bot: return
    if before.channel is None and after.channel is not None:
        bot.voice_times[member.id] = time.time()
    elif before.channel is not None and after.channel is None:
        if member.id in bot.voice_times:
            duration = time.time() - bot.voice_times.pop(member.id)
            stats = get_stats(member.id)
            stats["voice_seconds"] += int(duration)
            stats["mrad"] += int(duration / 60) * 2
            bot.save_data()

# --- الأوامر بنظام الإيمبد الكامل ---

@bot.tree.command(name="profile", description="عرض بروفايل هرمينيا")
async def profile(interaction: discord.Interaction, user: discord.Member = None):
    user = user or interaction.user
    s = get_stats(user.id)
    embed = discord.Embed(title=f"👤 ملف {user.display_name}", color=discord.Color.red())
    embed.set_thumbnail(url=user.display_avatar.url)
    embed.add_field(name="💰 رصيد مراد", value=f"`{s['mrad']}`", inline=True)
    embed.add_field(name="🏆 الرتبة", value=f"`{s['rank']}`", inline=True)
    embed.add_field(name="📊 المستوى", value=f"`Lvl {s['level']}`", inline=True)
    embed.set_footer(text=f"طلب بواسطة {interaction.user.name}", icon_url=interaction.user.display_avatar.url)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="mrad", description="عرض رصيد المراد")
async def mrad(interaction: discord.Interaction, user: discord.Member = None):
    user = user or interaction.user
    s = get_stats(user.id)
    embed = discord.Embed(description=f"💰 رصيد **{user.mention}** الحالي هو: `{s['mrad']}` مراد", color=discord.Color.red())
    embed.set_footer(text=f"طلب بواسطة {interaction.user.name}")
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="id", description="عرض معرف العضو")
async def id_cmd(interaction: discord.Interaction, user: discord.Member = None):
    user = user or interaction.user
    embed = discord.Embed(description=f"🆔 معرف **{user.mention}** هو: `{user.id}`", color=discord.Color.red())
    embed.set_footer(text=f"طلب بواسطة {interaction.user.name}")
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="name", description="عرض أسماء العضو")
async def name_cmd(interaction: discord.Interaction, user: discord.Member = None):
    user = user or interaction.user
    embed = discord.Embed(title="🏷️ معلومات الأسماء", color=discord.Color.red())
    embed.add_field(name="Username", value=f"`{user.name}`", inline=False)
    embed.add_field(name="Display Name", value=f"`{user.display_name}`", inline=False)
    embed.add_field(name="Nickname", value=f"`{user.nick or 'لا يوجد'}`", inline=False)
    embed.set_footer(text=f"طلب بواسطة {interaction.user.name}")
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="server", description="بيانات السيرفر")
async def server(interaction: discord.Interaction):
    g = interaction.guild
    embed = discord.Embed(title=f"🏰 معلومات سيرفر {g.name}", color=discord.Color.red())
    if g.icon: embed.set_thumbnail(url=g.icon.url)
    embed.add_field(name="تاريخ التأسيس", value=f"<t:{int(g.created_at.timestamp())}:D>", inline=True)
    embed.add_field(name="عدد الأعضاء", value=f"`{g.member_count}`", inline=True)
    embed.add_field(name="المكان", value=f"`{g.preferred_locale}`", inline=True)
    embed.set_footer(text=f"طلب بواسطة {interaction.user.name}")
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="avatar", description="عرض صورة الحساب")
async def avatar(interaction: discord.Interaction, user: discord.Member = None):
    user = user or interaction.user
    embed = discord.Embed(title=f"🖼️ صورة {user.display_name}", color=discord.Color.red())
    embed.set_image(url=user.display_avatar.url)
    embed.set_footer(text=f"طلب بواسطة {interaction.user.name}")
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="top", description="قائمة العشرة الأوائل")
async def top(interaction: discord.Interaction):
    sorted_users = sorted(bot.users_data.items(), key=lambda x: x[1]['mrad'], reverse=True)[:10]
    desc = ""
    for i, (uid, data) in enumerate(sorted_users, 1):
        u = bot.get_user(int(uid))
        name = u.name if u else f"User {uid}"
        desc += f"**#{i}** | {name} - `{data['mrad']} mrad`\n"
    
    embed = discord.Embed(title="🏆 قائمة متصدري هرمينيا", description=desc or "لا توجد بيانات بعد", color=discord.Color.red())
    embed.set_footer(text=f"طلب بواسطة {interaction.user.name}")
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="user", description="تواريخ الدخول")
async def user_info(interaction: discord.Interaction, user: discord.Member = None):
    user = user or interaction.user
    embed = discord.Embed(title=f"📅 معلومات تواريخ {user.display_name}", color=discord.Color.red())
    embed.add_field(name="انضمام للديسكورد", value=f"<t:{int(user.created_at.timestamp())}:D> (<t:{int(user.created_at.timestamp())}:R>)", inline=False)
    embed.add_field(name="انضمام للسيرفر", value=f"<t:{int(user.joined_at.timestamp())}:D> (<t:{int(user.joined_at.timestamp())}:R>)", inline=False)
    embed.set_footer(text=f"طلب بواسطة {interaction.user.name}")
    await interaction.response.send_message(embed=embed)

keep_alive()
bot.run(os.getenv("DISCORD_TOKEN"))
