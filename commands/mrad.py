import discord
from discord import app_commands
from discord.ext import commands
import random

class EconomyCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.developer_id = 1371432836946726934  # الآيدي الخاص بك

    @app_commands.command(name="mrad", description="عرض أو تحويل رصيد مراد")
    @app_commands.describe(user="العضو المراد التحويل له", amount="المبلغ المراد تحويله")
    async def mrad(self, interaction: discord.Interaction, user: discord.Member = None, amount: int = None):
        # استيراد الوظائف من العقل المدبر (main.py)
        from main import get_stats, create_captcha_image
        
        # الحالة 1: عرض الرصيد فقط
        if amount is None:
            target = user or interaction.user
            stats = get_stats(target.id)
            embed = discord.Embed(
                description=f"💰 رصيد **{target.mention}** هو: `{stats['mrad']}` مراد", 
                color=0xff0000
            )
            return await interaction.response.send_message(embed=embed)

        # الحالة 2: التحويل
        sender_id = interaction.user.id
        receiver_id = user.id
        sender_stats = get_stats(sender_id)
        receiver_stats = get_stats(receiver_id, interaction.guild.id)

        # التحقق من القوانين
        if sender_id == receiver_id:
            if sender_id == self.developer_id: # المطور يشحن لنفسه
                receiver_stats["mrad"] += amount
                self.bot.save_data()
                return await interaction.response.send_message(f"✅ تم إضافة `{amount}` لرصيدك يا مطور!")
            return await interaction.response.send_message("❌ لا يمكنك التحويل لنفسك!", ephemeral=True)

        if sender_id != self.developer_id and sender_stats["mrad"] < amount:
            return await interaction.response.send_message("❌ رصيدك لا يكفي!", ephemeral=True)

        if amount <= 0:
            return await interaction.response.send_message("❌ المبلغ غير صالح!", ephemeral=True)

        # نظام الكابتشا (التحقق من البشر)
        captcha_text = str(random.randint(1111, 9999))
        captcha_buffer = create_captcha_image(captcha_text)
        captcha_file = discord.File(captcha_buffer, filename="captcha.png")

        embed_v = discord.Embed(title="🛡️ تأكيد التحويل", description=f"اكتب الرقم الظاهر لتحويل `{amount}` إلى {user.mention}", color=0xff0000)
        embed_v.set_image(url="attachment://captcha.png")

        await interaction.response.send_message(file=captcha_file, embed=embed_v)

        # انتظار الرد
        def check(m): return m.author == interaction.user and m.channel == interaction.channel
        
        try:
            msg = await self.bot.wait_for('message', check=check, timeout=30.0)
            if msg.content == captcha_text:
                await msg.delete()
                # الخصم والإضافة
                if sender_id != self.developer_id:
                    sender_stats["mrad"] -= amount
                receiver_stats["mrad"] += amount
                self.bot.save_data()
                await interaction.followup.send(f"✅ تم تحويل `{amount}` إلى {user.mention} بنجاح!")
            else:
                await interaction.followup.send("❌ رقم الكابتشا خاطئ.")
        except:
            await interaction.followup.send("⏳ انتهى وقت التحقق.")

# ربط الملف بالعقل
async def setup(bot):
    await bot.add_cog(EconomyCog(bot))
