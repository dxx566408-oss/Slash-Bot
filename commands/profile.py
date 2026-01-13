import discord
from discord import app_commands
from discord.ext import commands
from utils.database_utils import get_stats # الاستيراد الصحيح
from utils.formatters import format_time, create_progress_bar # لجمال الإيمبد

class ProfileCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="profile", description="عرض بطاقة التعريف الشخصية وإحصائيات السيرفر")
    @app_commands.describe(member="العضو المراد رؤية بروفايله")
    async def profile(self, interaction: discord.Interaction, member: discord.Member = None):
        target = member or interaction.user
        
        # جلب البيانات باستخدام الدالة من الملحقات
        # نمرر bot.users_data لأن البيانات مخزنة داخل كائن البوت
        stats = get_stats(self.bot.users_data, target.id, interaction.guild.id)

        embed = discord.Embed(title=f"👤 ملف الشخصي: {target.display_name}", color=0xff0000)
        embed.set_thumbnail(url=target.display_avatar.url)
        
        # حساب شريط الخبرة (اللفل التالي يحتاج 20 XP كما في العقل)
        xp_bar = create_progress_bar(stats['xp'], 20)
        
        embed.add_field(name="المستوى (Level)", value=f"🏆 `{stats['level']}`", inline=True)
        embed.add_field(name="الرصيد (Mrad)", value=f"💰 `{stats['mrad']}`", inline=True)
        embed.add_field(name="الخبرة (XP)", value=f"{xp_bar} `{stats['xp']}/20`", inline=False)
        
        embed.add_field(name="الرسائل", value=f"📧 `{stats['msg_count']}`", inline=True)
        
        # استخدام منسق الوقت من الملحقات
        voice_time = format_time(stats['voice_seconds'])
        embed.add_field(name="وقت الفويس", value=f"🎙️ {voice_time}", inline=False)

        embed.set_footer(text=f"ID: {target.id}")
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(ProfileCog(bot))
