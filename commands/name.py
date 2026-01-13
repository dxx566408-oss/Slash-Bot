import discord
from discord import app_commands
from discord.ext import commands
from utils.settings_logic import load_settings # لربطه بلوحة التحكم

class NameInfo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="name", description="عرض جميع أسماء العضو بالتفصيل")
    @app_commands.describe(member="العضو المراد فحص أسمائه")
    async def name_info(self, interaction: discord.Interaction, member: discord.Member = None):
        # 1. التحقق من حالة الأمر في لوحة التحكم
        settings = load_settings()
        if not settings.get("name", {}).get("enabled", True):
            return await interaction.response.send_message("❌ هذا الأمر معطل حالياً من لوحة التحكم.", ephemeral=True)

        target = member or interaction.user
        
        # 2. جلب أنواع الأسماء الثلاثة في ديسكورد
        user_name = target.name  # @username
        global_name = target.global_name if target.global_name else "لا يوجد" # الاسم الظاهر العام
        server_nick = target.nick if target.nick else "لا يوجد لقب" # اللقب داخل السيرفر

        # 3. بناء الإيمبد
        embed = discord.Embed(
            title="🏷️ قائمة الأسماء", 
            description=f"تفاصيل الأسماء لـ: {target.mention}", 
            color=0xff0000
        )
        
        embed.add_field(name="Username (الأصلي)", value=f"`{user_name}`", inline=False)
        embed.add_field(name="Display Name (العالمي)", value=f"`{global_name}`", inline=False)
        embed.add_field(name="Server Nickname (اللقب)", value=f"`{server_nick}`", inline=False)
        
        embed.set_author(name=target.name, icon_url=target.display_avatar.url)
        embed.set_footer(text=f"طلب بواسطة: {interaction.user.name}")

        await interaction.response.send_message(embed=embed)

# دالة الربط الأساسية
async def setup(bot):
    await bot.add_cog(NameInfo(bot))
