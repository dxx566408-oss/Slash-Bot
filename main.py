import discord
from discord import app_commands
from discord.ext import commands
import os
from flask import Flask
from threading import Thread

# --- خدعة لإبقاء البوت حياً على Render المجاني ---
app = Flask('')

@app.route('/')
def home():
    return "I am alive!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()
# ----------------------------------------------

class MyBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.members = True
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        await self.tree.sync()
        print(f"تم مزامنة أوامر Slash bot بنجاح")

bot = MyBot()

@bot.tree.command(name="profile", description="عرض بيانات ملفك الشخصي")
async def profile(interaction: discord.Interaction, user: discord.Member = None):
    user = user or interaction.user
    embed = discord.Embed(title=f"ملف {user.name} - هرمينيا", color=discord.Color.red())
    embed.set_thumbnail(url=user.display_avatar.url)
    embed.add_field(name="المعرف (ID)", value=f"`{user.id}`")
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="mrad", description="عرض رصيدك من عملة مراد")
async def mrad(interaction: discord.Interaction):
    await interaction.response.send_message(f"💰 رصيدك في مشروع هرمينيا: **500 mrad**")

# تشغيل السيرفر الوهمي ثم البوت
keep_alive()
token = os.getenv("DISCORD_TOKEN")
bot.run(token)
