import discord
from discord import app_commands
from discord.ext import commands

class ProfileCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="profile", description="عرض مستواك في هذا السيرفر فقط")
    async def profile(self, interaction: discord.Interaction, member: discord.Member = None):
        target = member or interaction.user
        
        # استيراد الدالة من العقل (main.py)
        from main import get_stats
        stats = get_stats(target.id, interaction.guild.id)
        
        embed = discord.Embed(title=f"🏠 ملف {target.display_name} المحلي", color=0xff0000)
        embed.set_thumbnail(url=target.display_avatar.url)
        embed.add_field(name="المستوى", value=f"⭐ `{stats['level']}`", inline=True)
        embed.add_field(name="الخبرة", value=f"✨ `{stats['xp']}/20`", inline=True)
        embed.add_field(name="الرسائل", value=f"✉️ `{stats['msg_count']}`", inline=False)
        
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(ProfileCog(bot))
