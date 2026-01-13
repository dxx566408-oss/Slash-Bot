import discord
from discord import app_commands
from discord.ext import commands
from utils.settings_logic import load_settings

class ServerInfo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="server", description="عرض معلومات السيرفر بالتفصيل")
    async def server_info(self, interaction: discord.Interaction):
        # 1. التحقق من لوحة التحكم
        settings = load_settings()
        if not settings.get("server", {}).get("enabled", True):
            return await interaction.response.send_message("❌ هذا الأمر معطل حالياً.", ephemeral=True)

        guild = interaction.guild
        
        # 2. حساب الإحصائيات (تأكد من تفعيل Members Intent في ملف العقل)
        total_members = guild.member_count
        bot_count = len([m for m in guild.members if m.bot]) if guild.chunked else "جاري الحساب..."
        human_count = (total_members - bot_count) if isinstance(bot_count, int) else "جاري الحساب..."
        
        created_ts = int(guild.created_at.timestamp())
        
        # 3. إنشاء الإيمبد بتنسيق نظيف
        embed = discord.Embed(title=f"📊 معلومات سيرفر {guild.name}", color=0x2b2d31) 
        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)
        
        if guild.banner:
            embed.set_image(url=guild.banner.url)

        # إضافة الحقول
        embed.add_field(name="👑 المالك", value=f"{guild.owner.mention}", inline=True)
        embed.add_field(name="🆔 آيدي السيرفر", value=f"`{guild.id}`", inline=True)
        embed.add_field(name="📅 أنشئ في", value=f"<t:{created_ts}:D>\n(<t:{created_ts}:R>)", inline=True)

        embed.add_field(
            name="👥 الأعضاء", 
            value=f"الإجمالي: `{total_members}`\nبشر: `{human_count}` | بوتات: `{bot_count}`", 
            inline=True
        )

        embed.add_field(
            name="💬 القنوات", 
            value=f"كتابي: `{len(guild.text_channels)}`\nصوتي: `{len(guild.voice_channels)}`", 
            inline=True
        )

        embed.add_field(
            name="✨ التعزيز (Boost)", 
            value=f"المستوى: `{guild.premium_tier}`\nالعدد: `{guild.premium_subscription_count}`", 
            inline=True
        )
        
        embed.set_footer(text=f"طلب بواسطة: {interaction.user.name}", icon_url=interaction.user.display_avatar.url)
        
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(ServerInfo(bot))
