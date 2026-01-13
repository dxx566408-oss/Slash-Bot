import discord
from discord import app_commands
from discord.ext import commands
from utils.settings_logic import load_settings

class UserCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="user", description="عرض تاريخ إنشاء الحساب وتاريخ الانضمام")
    @app_commands.describe(member="العضو المراد رؤية تواريخه")
    async def user_info(self, interaction: discord.Interaction, member: discord.Member = None):
        # 1. التحقق من لوحة التحكم
        settings = load_settings()
        if not settings.get("user", {}).get("enabled", True):
            return await interaction.response.send_message("❌ هذا الأمر معطل حالياً.", ephemeral=True)

        # 2. تأجيل الاستجابة
        await interaction.response.defer()
        
        target = member or interaction.user
        
        # 3. تحويل التواريخ إلى طوابع زمنية (Timestamps)
        created_ts = int(target.created_at.timestamp())
        joined_ts = int(target.joined_at.timestamp()) if target.joined_at else None
        
        # 4. بناء الإيمبد المختصر
        embed = discord.Embed(
            title=f"⏳ تواريخ انضمام: {target.display_name}", 
            color=0xff0000
        )
        embed.set_thumbnail(url=target.display_avatar.url)
        
        # عرض تاريخ الإنشاء فقط
        embed.add_field(
            name="🗓️ إنشاء الحساب (العمر الكلي)", 
            value=f"<t:{created_ts}:D> (<t:{created_ts}:R>)", 
            inline=False
        )
        
        # عرض تاريخ الانضمام للسيرفر فقط
        if joined_ts:
            embed.add_field(
                name="📥 انضم للسيرفر في", 
                value=f"<t:{joined_ts}:D> (<t:{joined_ts}:R>)", 
                inline=False
            )
        
        embed.set_footer(text=f"طلب بواسطة: {interaction.user.name}")

        # 5. الإرسال
        await interaction.followup.send(embed=embed)

async def setup(bot):
    await bot.add_cog(UserCog(bot))
