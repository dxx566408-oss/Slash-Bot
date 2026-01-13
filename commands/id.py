import discord
from discord import app_commands
from discord.ext import commands

class IdCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="id", description="عرض معرف الحساب (ID) ومعلومات سريعة")
    @app_commands.describe(member="العضو الذي تريد معرفة الآيدي الخاص به")
    async def id_info(self, interaction: discord.Interaction, member: discord.Member = None):
        target = member or interaction.user
        
        embed = discord.Embed(title="🆔 معرف العضو", color=0xff0000)
        embed.set_thumbnail(url=target.display_avatar.url)
        
        embed.add_field(name="العضو", value=target.mention, inline=True)
        embed.add_field(name="الآيدي", value=f"`{target.id}`", inline=True)
        
        # إضافة تاريخ إنشاء الحساب لمزيد من الفائدة
        created_at = target.created_at.strftime("%Y/%m/%d")
        embed.add_field(name="تاريخ إنشاء الحساب", value=f"`{created_at}`", inline=False)
        
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(IdCog(bot))
