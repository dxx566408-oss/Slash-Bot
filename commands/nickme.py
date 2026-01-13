import discord
from discord import app_commands
from discord.ext import commands

class NicknameCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="nickme", description="تغيير لقبك (الاسم المستعار) داخل هذا السيرفر")
    @app_commands.describe(new_nickname="الاسم الجديد الذي تريده (اتركه فارغاً لإزالة اللقب)")
    async def nickme(self, interaction: discord.Interaction, new_nickname: str = None):
        try:
            # محاولة تغيير لقب الشخص الذي استخدم الأمر
            await interaction.user.edit(nick=new_nickname)
            
            if new_nickname:
                await interaction.response.send_message(f"✅ تم تغيير لقبك بنجاح إلى: **{new_nickname}**", ephemeral=True)
            else:
                await interaction.response.send_message(f"✅ تم إعادة ضبط اسمك إلى الأصلي بنجاح.", ephemeral=True)
                
        except discord.Forbidden:
            # هذا الخطأ يظهر إذا كان رتبة البوت أقل من رتبة الشخص أو لا يملك صلاحيات
            await interaction.response.send_message("❌ لا أملك صلاحية لتغيير اسمك. تأكد أن رتبتي أعلى من رتبتك!", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"⚠️ حدث خطأ غير متوقع: {e}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(NicknameCog(bot))
