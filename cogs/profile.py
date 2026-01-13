import discord
from discord import app_commands
from discord.ext import commands

class ProfileCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # تعريف أمر السلاش داخل الكلاس
    @app_commands.command(name="profile", description="عرض مستواك في هذا السيرفر فقط")
    async def profile(self, interaction: discord.Interaction, member: discord.Member = None):
        target = member or interaction.user
        
        # استدعاء دالة جلب البيانات من ملف العقل (main.py)
        from main import get_stats
        stats = get_stats(target.id, interaction.guild.id)
        
        # بناء بطاقة البروفايل (Embed)
        embed = discord.Embed(
            title=f"🏠 ملف {target.display_name} المحلي", 
            color=0xff0000
        )
        embed.set_thumbnail(url=target.display_avatar.url)
        
        embed.add_field(name="المستوى", value=f"⭐ `{stats['level']}`", inline=True)
        embed.add_field(name="الخبرة", value=f"✨ `{stats['xp']}/20`", inline=True)
        embed.add_field(name="الرسائل", value=f"✉️ `{stats['msg_count']}`", inline=False)
        
        await interaction.response.send_message(embed=embed)

# دالة الربط مع العقل (main.py)
async def setup(bot):
    await bot.add_cog(ProfileCog(bot))
