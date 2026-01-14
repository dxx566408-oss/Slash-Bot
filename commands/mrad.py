import discord
from discord import app_commands
from discord.ext import commands
from utils.database_utils import get_stats
from utils.settings_logic import load_settings, DEVELOPER_ID
from utils.formatters import format_number
from utils.captcha import generate_captcha
import math
import asyncio

class MradCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="mrad", description="نظام عملة مراد: الرصيد، التحويل، وقائمة المتصدرين")
    @app_commands.describe(
        member="اختر عضواً لرؤية رصيده أو التحويل له",
        amount="أدخل المبلغ للتحويل لهذا العضو",
        top="اختر True لعرض قائمة أغنياء السيرفر",
        rank="أدخل رقم مركز معين (مثلاً: 7) لعرض صاحبه"
    )
    async def mrad(self, interaction: discord.Interaction, 
                   member: discord.Member = None, 
                   amount: int = None, 
                   top: bool = False, 
                   rank: int = None):
        
        gid = str(interaction.guild.id)
        settings = load_settings()
        
        # --- 1. خيار القائمة (Top) والمركز (#) ---
        if top or rank is not None:
            # تجميع المستخدمين الذين لديهم رصيد أكبر من 0
            all_users = []
            for uid, servers in self.bot.users_data.items():
                balance = servers.get(gid, {}).get("mrad", 0)
                if balance > 0:
                    all_users.append({"id": uid, "balance": balance})
            
            # ترتيب تنازلي حسب الرصيد
            all_users.sort(key=lambda x: x["balance"], reverse=True)

            # منطق حساب المراكز مع التساوي
            ranked_groups = {}
            current_rank = 0
            last_balance = -1
            for user in all_users:
                if user["balance"] != last_balance:
                    current_rank += 1
                last_balance = user["balance"]
                if current_rank not in ranked_groups:
                    ranked_groups[current_rank] = []
                ranked_groups[current_rank].append(user)

            # حالة طلب مركز معين (#)
            if rank is not None:
                if rank not in ranked_groups:
                    return await interaction.response.send_message(f"⚠️ لا يوجد أحد في المركز #{rank} حالياً.", ephemeral=True)
                
                users_in_rank = ranked_groups[rank]
                mentions = [f"<@{u['id']}>" for u in users_in_rank]
                bal_display = format_number(users_in_rank[0]["balance"])
                
                embed = discord.Embed(title=f"🏆 المركز #{rank}", color=0xffd700)
                embed.description = f"الأعضاء في هذا المركز:\n" + "\n".join(mentions) + f"\n\n**الرصيد:** `{bal_display}` مراد"
                return await interaction.response.send_message(embed=embed)

            # حالة عرض القائمة (Top)
            if top:
                return await self.send_top_page(interaction, 1, all_users)

        # --- 2. خيار العضو (Member) والتحويل (Amount) ---
        target = member or interaction.user
        
        # إذا تم إدخال مبلغ (عملية تحويل)
        if amount is not None:
            if not member:
                return await interaction.response.send_message("❌ يجب اختيار عضو للتحويل له.", ephemeral=True)
            
            # استثناء المطور (أنت)
            if interaction.user.id == DEVELOPER_ID:
                receiver_stats = get_stats(self.bot.users_data, member.id, gid)
                receiver_stats["mrad"] = receiver_stats.get("mrad", 0) + amount
                self.bot.save_data()
                return await interaction.response.send_message(f"✅ (أمر المطور) تم منح `{format_number(amount)}` مراد إلى {member.mention}")

            # قيود الأعضاء العاديين
            if member.bot:
                return await interaction.response.send_message("❌ لا يمكنك التحويل للبوتات.", ephemeral=True)
            if member.id == interaction.user.id:
                return await interaction.response.send_message("❌ لا يمكنك التحويل لنفسك.", ephemeral=True)
            
            sender_stats = get_stats(self.bot.users_data, interaction.user.id, gid)
            if sender_stats.get("mrad", 0) < amount:
                return await interaction.response.send_message("❌ ليس لديك رصيد كافٍ.", ephemeral=True)

            # نظام الكابتشا للعاديين
            captcha_text, captcha_file = generate_captcha()
            embed = discord.Embed(title="🛡️ تحقق أمان", description="اكتب الأرقام التي تراها في الصورة لإتمام التحويل:", color=0x2b2d31)
            embed.set_image(url="attachment://captcha.png")
            await interaction.response.send_message(embed=embed, file=captcha_file, ephemeral=True)

            def check(m):
                return m.author == interaction.user and m.channel == interaction.channel

            try:
                msg = await self.bot.wait_for('message', check=check, timeout=40.0)
                if msg.content == captcha_text:
                    receiver_stats = get_stats(self.bot.users_data, member.id, gid)
                    sender_stats["mrad"] -= amount
                    receiver_stats["mrad"] = receiver_stats.get("mrad", 0) + amount
                    self.bot.save_data()
                    try: await msg.delete() 
                    except: pass
                    return await interaction.followup.send(f"✅ تم تحويل `{format_number(amount)}` مراد إلى {member.mention} بنجاح!", ephemeral=True)
                else:
                    return await interaction.followup.send("❌ الكود خاطئ. تم إلغاء العملية.", ephemeral=True)
            except asyncio.TimeoutError:
                return await interaction.followup.send("⏳ انتهى الوقت. حاول مجدداً.", ephemeral=True)

        # حالة عرض الرصيد الافتراضية
        stats = get_stats(self.bot.users_data, target.id, gid)
        bal = format_number(stats.get("mrad", 0))
        msg = f"**ـ {target.name}, رصيد حسابك هو `${bal}`.** | :bank:" if target == interaction.user else f"** رصيد {target.name} هو `${bal}`.** :credit_card:"
        await interaction.response.send_message(content=msg)

    # دالة تقليب الصفحات
    async def send_top_page(self, interaction, page, all_users):
        total_pages = math.ceil(len(all_users) / 10)
        start = (page - 1) * 10
        current_list = all_users[start:start+10]

        embed = discord.Embed(title="💰 قائمة أغنياء السيرفر", color=0xff0000)
        desc = ""
        for i, user in enumerate(current_list, start=start+1):
            desc += f"#{i} | <@{user['id']}> — `{format_number(user['balance'])}` مراد\n"
        
        embed.description = desc or "القائمة فارغة."
        embed.set_footer(text=f"صفحة {page} من {total_pages}")

        view = TopView(self, page, total_pages, all_users) if total_pages > 1 else None
        
        if interaction.response.is_done():
            await interaction.edit_original_response(embed=embed, view=view)
        else:
            await interaction.response.send_message(embed=embed, view=view)

class TopView(discord.ui.View):
    def __init__(self, cog, current_page, total_pages, all_users):
        super().__init__(timeout=60)
        self.cog, self.current_page, self.total_pages, self.all_users = cog, current_page, total_pages, all_users

    @discord.ui.button(label="الصفحة التالية 🟢", style=discord.ButtonStyle.success)
    async def next_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        next_pg = 1 if self.current_page >= self.total_pages else self.current_page + 1
        await self.cog.send_top_page(interaction, next_pg, self.all_users)

async def setup(bot):
    await bot.add_cog(MradCog(bot))
