import discord
from discord import app_commands
from discord.ext import commands
from utils.settings_logic import load_settings

class NickmeCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="nickme", description="تغيير اسمك المستعار (Nickname) داخل هذا السيرفر")
    @app_commands.describe(new_nick="الاسم الجديد الذي تريد ظهوره للآخرين")
    async def nickme(self, interaction: discord.Interaction, new_nick: str):
        # 1. التحقق من لوحة التحكم
        settings = load_settings()
        if not settings.get("nickme", {}).get("enabled", True):
            return await interaction.response.send_message("❌ هذا الأمر معطل حالياً.", ephemeral=True)

        # 2. التحقق من الصلاحيات (البوت يجب أن يكون له صلاحية Manage Nicknames)
        if not interaction.guild.me.guild_permissions.manage_nicknames:
            return await interaction.response.send_message("❌ ليس لدي صلاحية (إدارة الألقاب) للقيام بذلك.", ephemeral=True)

        # 3. محاولة تغيير الاسم
        try:
            await interaction.user.edit(nick=new_nick)
            
            embed = discord.Embed(
                description=f"✅ تم تغيير اسمك المستعار بنجاح إلى: **{new_nick}**",
                color=0x00ff00
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        except discord.Forbidden:
            # تحدث هذه المشكلة إذا كان المستخدم صاحب رتبة أعلى من البوت أو هو "الأونر"
            await interaction.response.send_message("❌ لا يمكنني تغيير اسمك لأن رتبتك أعلى مني أو أنك صاحب السيرفر.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ حدث خطأ غير متوقع: {e}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(NickmeCog(bot))
