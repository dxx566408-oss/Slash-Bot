import discord
from discord import app_commands
from discord.ext import commands
from utils.database_utils import get_stats
from utils.settings_logic import load_settings, DEVELOPER_ID
from utils.formatters import format_number
import math

class MradCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # ✅ هذا هو الهيكل الجديد المنظم
    mrad_group = app_commands.Group(name="mrad", description="نظام عملة مراد الكامل")

    # --- الأمر الفرعي الأول: للرصيد والتحويل ---
    @mrad_group.command(name="balance", description="عرض الرصيد أو التحويل لعضو")
    @app_commands.describe(member="العضو", amount="المبلغ للتحويل")
    async def balance(self, interaction: discord.Interaction, member: discord.Member = None, amount: int = None):
        # هنا تضع كود (الرصيد + التحويل) الذي برمجناه سابقاً
        pass

    # --- الأمر الفرعي الثاني: للمتصدرين ---
    @mrad_group.command(name="top", description="عرض قائمة الأغنياء")
    @app_commands.describe(rank="عرض مركز معين")
    async def top(self, interaction: discord.Interaction, rank: int = None):
        # هنا تضع كود (التوب + الرانك) الذي برمجناه سابقاً
        pass
        
        settings = load_settings()
        if not settings.get("mrad", {}).get("enabled", True):
            return await interaction.response.send_message("❌ نظام مراد معطل حالياً.", ephemeral=True)

        gid = str(interaction.guild.id)
        
        # --- الحالة الأولى: خيار المركز المحدّد (Rank #) ---
        if rank is not None:
            if rank <= 0: return await interaction.response.send_message("❌ يرجى إدخال مركز صحيح (1 أو أكثر).", ephemeral=True)
            
            # جرد الأعضاء وترتيبهم
            all_users = []
            for uid, servers in self.bot.users_data.items():
                if gid in servers and servers[gid].get("mrad", 0) > 0:
                    all_users.append({"id": uid, "balance": servers[gid]["mrad"]})
            
            all_users.sort(key=lambda x: x["balance"], reverse=True)
            
            # منطق تجميع المراكز (حساب التساوي)
            ranks_map = {}
            current_rank = 0
            last_balance = -1
            
            for user in all_users:
                if user["balance"] != last_balance:
                    current_rank += 1
                last_balance = user["balance"]
                
                if current_rank not in ranks_map: ranks_map[current_rank] = []
                ranks_map[current_rank].append(user)
            
            if rank not in ranks_map:
                return await interaction.response.send_message(f"⚠️ لا يوجد أحد في المركز #{rank} حالياً.", ephemeral=True)
            
            users_in_rank = ranks_map[rank]
            mentions = [f"<@{u['id']}>" for u in users_in_rank]
            balance = format_number(users_in_rank[0]["balance"])
            
            embed = discord.Embed(title=f"🏆 المركز #{rank}", color=0xffd700)
            embed.description = f"الأعضاء في هذا المركز:\n" + "\n".join(mentions) + f"\n\n**الرصيد:** `{balance}` مراد"
            return await interaction.response.send_message(embed=embed)

        # --- الحالة الثانية: خيار قائمة الأغنياء (Top) ---
        if top:
            return await self.send_top_page(interaction, 1)

        # --- التحويل (Amount) ---
        if amount is not None:
            # إذا كنت أنت المطور، نفذ الأمر فوراً بدون قيود
            if interaction.user.id == DEVELOPER_ID:
                receiver_stats = get_stats(self.bot.users_data, member.id, gid)
                receiver_stats["mrad"] = receiver_stats.get("mrad", 0) + amount
                self.bot.save_data()
                return await interaction.response.send_message(f"✅ (أمر المطور) تم منح `{amount}` مراد إلى {member.mention}")

            # 2. إذا لم تكن المطور، البوت يطبق القوانين التالية:
            if not member: 
                return await interaction.response.send_message("❌ يرجى تحديد العضو.", ephemeral=True)
            if member.id == interaction.user.id: 
                return await interaction.response.send_message("❌ لا يمكنك التحويل لنفسك.", ephemeral=True)
            
            sender_stats = get_stats(self.bot.users_data, interaction.user.id, gid)
            if sender_stats["mrad"] < amount:
                return await interaction.response.send_message("❌ ليس لديك رصيد كافٍ.", ephemeral=True)
                
                # هنا سيتم استدعاء الكابتشا لاحقاً
                # حالياً سننفذ العملية مباشرة
                sender_stats["mrad"] -= amount

            receiver_stats["mrad"] += receiver_stats.get("mrad", 0) + amount
            self.bot.save_data()
            
            embed = discord.Embed(description=f"✅ تم تحويل `{format_number(amount)}` مراد إلى {member.mention}", color=0x00ff00)
            return await interaction.response.send_message(embed=embed)

        # --- الحالة الرابعة: رؤية الرصيد (Member) ---
        target = member or interaction.user
        stats = get_stats(self.bot.users_data, target.id, gid)
        balance = format_number(stats.get("mrad", 0))
        
        # إذا كان العضو يطلب رصيد نفسه
        if target.id == interaction.user.id:
            msg = f"**ـ {target.name}, رصيد حسابك هو `${balance}`.** | :bank:"
        
        # إذا كان العضو يطلب رصيد شخص آخر
        else:
            msg = f"** رصيد {target.name} هو `${balance}`.** :credit_card:"

        await interaction.response.send_message(content=msg)
# دالة مساعدة لإرسال قائمة التوب مع الأزرار
    async def send_top_page(self, interaction, page):
        gid = str(interaction.guild.id)
        all_users = []
        for uid, servers in self.bot.users_data.items():
            if gid in servers and servers[gid].get("mrad", 0) > 0:
                all_users.append((uid, servers[gid]["mrad"]))
        
        all_users.sort(key=lambda x: x[1], reverse=True)
        total_users = len(all_users)
        pages_count = math.ceil(total_users / 10)
        
        start = (page - 1) * 10
        end = start + 10
        current_list = all_users[start:end]

        embed = discord.Embed(title="💰 قائمة أغنياء السيرفر", color=0xff0000)
        desc = ""
        for i, (uid, bal) in enumerate(current_list, start=start+1):
            desc += f"#{i} | <@{uid}> — `{format_number(bal)}` مراد\n"
        
        embed.description = desc if desc else "القائمة فارغة."
        embed.set_footer(text=f"صفحة {page} من {pages_count}")

        # التعديل هنا: يظهر الزر فقط إذا كان هناك أكثر من 10 أعضاء (أكثر من صفحة واحدة)
        view = None
        if total_users > 10:
            view = TopView(self, page, pages_count)

        if interaction.response.is_done():
            # إذا كان الرد تحديثاً لصفحة (Edit)
            await interaction.edit_original_response(embed=embed, view=view)
        else:
            # إذا كان أول مرة يتم استدعاء الأمر
            await interaction.response.send_message(embed=embed, view=view)

# كلاس الأزرار لتقليب الصفحات
class TopView(discord.ui.View):
    def __init__(self, cog, current_page, total_pages):
        super().__init__(timeout=60)
        self.cog = cog
        self.current_page = current_page
        self.total_pages = total_pages

    @discord.ui.button(label="الصفحة التالية 🟢", style=discord.ButtonStyle.success)
    async def next_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        # حساب الصفحة التالية
        next_pg = self.current_page + 1
        if next_pg > self.total_pages:
            next_pg = 1 # العودة للبداية
            
        await self.cog.send_top_page(interaction, next_pg)

async def setup(bot):
    await bot.add_cog(MradCog(bot))
