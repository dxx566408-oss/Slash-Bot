import discord
from discord import app_commands
from discord.ext import commands
from utils.settings_logic import load_settings # الربط بلوحة التحكم

class UserCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="user", description="عرض معلومات الحساب بالتفصيل")
    @app_commands.describe(member="العضو المراد رؤية معلوماته")
    async def user_info(self, interaction: discord.Interaction, member: discord.Member = None):
        # 1. التحقق من حالة الأمر في لوحة التحكم
        settings = load_settings()
        if not settings.get("user", {}).get("enabled", True):
            return await interaction.response.send_message("❌ هذا الأمر معطل حالياً من لوحة التحكم.", ephemeral=True)

        # 2. تأجيل الاستجابة لمنع خطأ الـ Timeout
        await interaction.response.defer()
        
        target = member or interaction.user
        
        # 3. تحويل التواريخ
        created_ts = int(target.created_at.timestamp())
        joined_ts = int(target.joined_at.timestamp()) if target.joined_at else None
        
        # 4. بناء الإيمبد
        embed = discord.Embed(title=f"👤 معلومات المستخدم: {target.display_name}", color=0xff0000)
        embed.set_thumbnail(url=target.display_avatar.url)
        
        embed.add_field(name="🆔 الآيدي", value=f"`{target.id}`", inline=True)
        embed.add_field(name="🏷️ اليوزر", value=f"`{target.name}`", inline=True)
        
        embed.add_field(name="🗓️ إنشاء الحساب", value=f"<t:{created_ts}:D> (<t:{created_ts}:R>)", inline=False)
        
        if joined_ts:
            embed.add_field(name="📥 دخول السيرفر", value=f"<t:{joined_ts}:D> (<t:{joined_ts}:R>)", inline=False)
        
        embed.add_field(name="🎭 أعلى رتبة", value=target.top_role.mention, inline=False)
        
        embed.set_footer(text=f"طلب بواسطة: {interaction.user.name}", icon_url=interaction.user.display_avatar.url)

        # 5. الإرسال باستخدام followup
        await interaction.followup.send(embed=embed)

async def setup(bot):
    await bot.add_cog(UserCog(bot))
