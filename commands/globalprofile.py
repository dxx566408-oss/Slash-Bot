import discord
from discord import app_commands
from discord.ext import commands

class GlobalProfile(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="globalprofile", description="عرض مستواك الإجمالي في كل السيرفرات")
    async def globalprofile(self, interaction: discord.Interaction, member: discord.Member = None):
        target = member or interaction.user
        
        # استيراد الدالة من ملف العقل الأساسي
        from main import get_stats
        stats = get_stats(target.id) 

        embed = discord.Embed(title=f"🌍 الحساب العالمي: {target.display_name}", color=0xff0000)
        embed.set_thumbnail(url=target.display_avatar.url)
        
        # عرض البيانات العالمية
        embed.add_field(name="المستوى العالمي", value=f"🏆 `{stats['level']}`", inline=True)
        embed.add_field(name="الخبرة الإجمالية", value=f"✨ `{stats['xp']}`", inline=True)
        embed.add_field(name="مجموع الرسائل", value=f"📧 `{stats['msg_count']}`", inline=False)
        
        # حساب الوقت بشكل جميل
        seconds = stats['voice_seconds']
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        embed.add_field(name="إجمالي وقت الفويس", value=f"🎙️ `{hours}` ساعة و `{minutes}` دقيقة", inline=False)
        
        await interaction.response.send_message(embed=embed)

# دالة الربط الضرورية
async def setup(bot):
    await bot.add_cog(GlobalProfile(bot))
