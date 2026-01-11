import discord
from discord import app_commands
from discord.ext import commands
import os

# إعدادات البوت الأساسية
class MyBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.members = True  # ضروري لجلب بيانات الأعضاء مثل البروفايل
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        # مزامنة أوامر السلاش لتظهر في الديسكورد
        await self.tree.sync()
        print(f"تم بنجاح مزامنة أوامر Slash bot")

bot = MyBot()

@bot.event
async def on_ready():
    print(f'تم تشغيل البوت باسم: {bot.user}')

# --- أوامر السلاش ---

@bot.tree.command(name="profile", description="عرض بيانات ملفك الشخصي")
async def profile(interaction: discord.Interaction, user: discord.Member = None):
    user = user or interaction.user
    embed = discord.Embed(title=f"ملف {user.name} - مشروع هرمينيا", color=discord.Color.red())
    embed.set_thumbnail(url=user.display_avatar.url)
    embed.add_field(name="الاسم الكامل", value=user.global_name or user.name)
    embed.add_field(name="المعرف (ID)", value=f"`{user.id}`")
    embed.add_field(name="انضم للديسكورد", value=user.created_at.strftime("%Y/%m/%d"))
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="avatar", description="عرض صورة الحساب")
async def avatar(interaction: discord.Interaction, user: discord.Member = None):
    user = user or interaction.user
    embed = discord.Embed(title=f"صورة {user.name}", color=discord.Color.red())
    embed.set_image(url=user.display_avatar.url)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="mrad", description="عرض رصيدك من عملة مراد")
async def mrad(interaction: discord.Interaction):
    # نظام وهمي للعملة حالياً
    await interaction.response.send_message(f"💰 رصيدك الحالي في نظام هرمينيا هو: **500 mrad**")

# تشغيل البوت باستخدام التوكن
# ملاحظة: سنستخدم المتغيرات البيئية لاحقاً في Render للأمان
token = os.getenv("DISCORD_TOKEN")
bot.run(token)
