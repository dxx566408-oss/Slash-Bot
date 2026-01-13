import discord
from discord import app_commands
from discord.ext import commands

class UserCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="user", description="عرض معلومات الحساب بالتفصيل")
    @app_commands.describe(member="العضو المراد رؤية معلوماته")
    async def user_info(self, interaction: discord.Interaction, member: discord.Member = None):
        # تأجيل الاستجابة لمنع خطأ التوقف (Timeout)
        await interaction.response.defer()
        
        target = member or interaction.user
        
        # تحويل التواريخ إلى طوابع زمنية لديسكورد
        created_ts = int(target.created_at.timestamp())
        joined_ts = int(target.joined_at.timestamp())
        
        embed = discord.Embed(title=f"👤 معلومات: {target.display_name}", color=0xff0000)
        embed.set_thumbnail(url=target.display_avatar.url)
        
        # معلومات الحساب
        embed.add_field(name="🆔 الآيدي", value=f"`{target.id}`", inline=True)
        embed.add_field(name="🏷️ اليوزر", value=f"`{target.name}`", inline=True)
        
        # التواريخ (باستخدام تنسيق الوقت الديناميكي في ديسكورد)
        embed.add_field(name="🗓️ إنشاء الحساب", value=f"<t:{created_ts}:D> (<t:{created_ts}:R>)", inline=False)
        embed.add_field(name="📥 دخول السيرفر", value=f"<t:{joined_ts}:D> (<t:{joined_ts}:R>)", inline=False)
        
        # إضافة أعلى رتبة للعضو لمزيد من الفخامة
        embed.add_field(name="🎭 أعلى رتبة", value=target.top_role.mention, inline=False)
        
        # الإرسال باستخدام followup لأننا استخدمنا defer
        await interaction.followup.send(embed=embed)

async def setup(bot):
    await bot.add_cog(UserCog(bot))
