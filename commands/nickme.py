import discord
from discord import app_commands
from discord.ext import commands
from utils.settings_logic import load_settings # الربط بلوحة التحكم

class NicknameCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="nickme", description="تغيير لقبك (الاسم المستعار) داخل هذا السيرفر")
    @app_commands.describe(new_nickname="الاسم الجديد الذي تريده (اتركه فارغاً لإزالة اللقب)")
    async def nickme(self, interaction: discord.Interaction, new_nickname: str = None):
        # 1. التحقق من حالة الأمر في لوحة التحكم
        settings = load_settings()
        if not settings.get("nickme", {}).get("enabled", True):
            return await interaction.response.send_message("❌ هذا الأمر معطل حالياً من لوحة التحكم.", ephemeral=True)

        try:
            # 2. محاولة تغيير اللقب
            await interaction.user.edit(nick=new_nickname)
            
            if new_nickname:
                await interaction.response.send_message(f"✅ تم تغيير لقبك بنجاح إلى: **{new_nickname}**", ephemeral=True)
            else:
                await interaction.response.send_message(f"✅ تم إعادة ضبط لقبك إلى الاسم الأصلي بنجاح.", ephemeral=True)
                
        except discord.Forbidden:
            # رسالة واضحة في حال فشل الصلاحيات
            await interaction.response.send_message(
                "❌ **فشل التغيير!** البوت لا يملك صلاحية لتغيير اسمك.\n"
                "💡 تأكد أن رتبة البوت أعلى من رتبتك في إعدادات السيرفر.", 
                ephemeral=True
            )
        except Exception as e:
            await interaction.response.send_message(f"⚠️ حدث خطأ غير متوقع: {e}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(NicknameCog(bot))
