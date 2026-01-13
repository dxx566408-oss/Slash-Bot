import discord
from discord import app_commands
from discord.ext import commands
from utils.database_utils import get_stats
from utils.formatters import format_time, create_progress_bar

class ProfileCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="profile", description="عرض بطاقة التعريف الشخصية وإحصائيات التفاعل")
    @app_commands.describe(member="العضو المراد رؤية بروفايله")
    async def profile(self, interaction: discord.Interaction, member: discord.Member = None):
        target = member or interaction.user
        
        # جلب البيانات
        stats = get_stats(self.bot.users_data, target.id, interaction.guild.id)

        # إنشاء الإيمبد
        embed = discord.Embed(title=f"👤 الملف الشخصي: {target.display_name}", color=0xff0000)
        embed.set_thumbnail(url=target.display_avatar.url)
        
        # حساب شريط الخبرة
        xp_bar = create_progress_bar(stats['xp'], 20)
        
        # الحقول الأساسية
        embed.add_field(name="المستوى (Level)", value=f"🏆 `{stats['level']}`", inline=True)
        embed.add_field(name="الرصيد (Mrad)", value=f"💰 `{stats['mrad']}`", inline=True)
        embed.add_field(name="الخبرة (XP)", value=f"{xp_bar} `{stats['xp']}/20`", inline=False)
        
        embed.add_field(name="الرسائل", value=f"📧 `{stats['msg_count']}`", inline=True)
        
        # تنسيق وقت الفويس
        voice_time = format_time(stats['voice_seconds'])
        embed.add_field(name="وقت الفويس", value=f"🎙️ {voice_time}", inline=False)

        # تمت إزالة الـ ID من التذييل (Footer) ليبقى نظيفاً
        embed.set_footer(text=f"طلب بواسطة: {interaction.user.display_name}")
        
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(ProfileCog(bot))
