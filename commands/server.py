import discord
from discord import app_commands
from discord.ext import commands

class ServerCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="server", description="عرض معلومات السيرفر الحالية")
    async def server_info(self, interaction: discord.Interaction):
        guild = interaction.guild
        
        # تجهيز المعلومات
        owner = guild.owner.mention if guild.owner else "غير معروف"
        created_at = guild.created_at.strftime("%Y/%m/%d")
        member_count = guild.member_count
        boost_count = guild.premium_subscription_count
        
        embed = discord.Embed(title=f"🏰 معلومات سيرفر: {guild.name}", color=0xff0000)
        
        # وضع أيقونة السيرفر إذا وجدت
        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)
        
        embed.add_field(name="👑 صاحب السيرفر", value=owner, inline=True)
        embed.add_field(name="🆔 آيدي السيرفر", value=f"`{guild.id}`", inline=True)
        embed.add_field(name="📅 تاريخ الإنشاء", value=f"`{created_at}`", inline=True)
        embed.add_field(name="👥 عدد الأعضاء", value=f"`{member_count}`", inline=True)
        embed.add_field(name="💎 عدد البوستات", value=f"`{boost_count}`", inline=True)
        embed.add_field(name="💬 عدد الرومات", value=f"`{len(guild.channels)}`", inline=True)
        
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(ServerCog(bot))
