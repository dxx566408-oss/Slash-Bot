import discord
from discord import app_commands
from discord.ext import commands
# الاستيراد الصحيح من الملحقات وليس من الماين
from utils.database_utils import get_stats 

class GlobalProfile(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="globalprofile", description="عرض مستواك الإجمالي في كل السيرفرات")
    async def globalprofile(self, interaction: discord.Interaction, member: discord.Member = None):
        target = member or interaction.user
        
        # 1. جلب البيانات العالمية (بدون تحديد gid) 
        # نمرر bot.users_data كأول متغير للدالة
        stats = get_stats(self.bot.users_data, target.id) 

        embed = discord.Embed(
            title=f"🌍 الحساب العالمي: {target.display_name}", 
            description="هذه الإحصائيات تجمع نشاطك من كافة السيرفرات التي يتواجد بها البوت.",
            color=0xff0000
        )
        embed.set_thumbnail(url=target.display_avatar.url)
        
        # 2. عرض البيانات العالمية
        embed.add_field(name="المستوى العالمي", value=f"🏆 `{stats['level']}`", inline=True)
        embed.add_field(name="الخبرة الإجمالية", value=f"✨ `{stats['xp']}`", inline=True)
        embed.add_field(name="مجموع الرسائل", value=f"📧 `{stats['msg_count']}`", inline=False)
        
        # 3. حساب الوقت (ساعات ودقائق)
        seconds = stats['voice_seconds']
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        embed.add_field(name="إجمالي وقت الفويس", value=f"🎙️ `{hours} ساعة` و `{minutes} دقيقة`", inline=False)
        
        embed.set_footer(text=f"طلب بواسطة: {interaction.user.name}")
        
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(GlobalProfile(bot))
