import discord
from discord import app_commands
from discord.ext import commands

class ServerInfo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="server", description="عرض معلومات السيرفر بالتفصيل")
    async def server_info(self, interaction: discord.Interaction):
        guild = interaction.guild
        
        # حساب الإحصائيات
        total_members = guild.member_count
        bot_count = len([m for m in guild.members if m.bot])
        human_count = total_members - bot_count
        
        # تاريخ إنشاء السيرفر وتحويله لتنسيق ديسكورد الزمني
        created_ts = int(guild.created_at.timestamp())
        
        # إنشاء الإيمبد
        embed = discord.Embed(color=0x2b2d31) 
        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)
        
        # الحقول بتنسيقك الخاص
        embed.add_field(
            name="", 
            value=f"👑 **مملوك بواسطة**\n{guild.owner.mention}", 
            inline=True
        )
        embed.add_field(
            name="", 
            value=f"📅 **تاريخ الانشاء**\n<t:{created_ts}:D>\n**<t:{created_ts}:R>**", 
            inline=True
        )
        embed.add_field(
            name="", 
            value=f"🆔 **ايدي السيرفر**\n`{guild.id}`", 
            inline=True
        )

        embed.add_field(
            name="", 
            value=f"👥 **الأعضاء ({total_members})**\nالاعضاء: `{human_count}`\nالبوتات: `{bot_count}`", 
            inline=True
        )

        embed.add_field(
            name="", 
            value=f"💬 **الرومات ({len(guild.channels)})**\nكتابي: `{len(guild.text_channels)}` | صوتي: `{len(guild.voice_channels)}`", 
            inline=True
        )

        embed.add_field(
            name="", 
            value=f"✨ **التعزيزات**\nعدد البوستات: `{guild.premium_subscription_count}`", 
            inline=True
        )
        
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(ServerInfo(bot))
