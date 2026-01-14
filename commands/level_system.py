import discord
from discord import app_commands
from discord.ext import commands
from utils.database_utils import get_stats

class LevelSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # دالة الحسبة الرياضية بناءً على القواعد التي وضعتها
    def calculate_logic(self, ms, vs):
        # 1. حسبة الكتابي (Text)
        vm_from_vs = vs // 60 # تحويل الثواني لدقائق للحسبة الصوتية
        
        t_xp = ms // 25
        t_ms_prog = ms - (t_xp * 25)
        t_lvl = t_xp // 20
        t_xp_prog = t_xp - (t_lvl * 20)

        # 2. حسبة الصوتي (Voice) بناءً على الدقائق vm
        v_vm = vm_from_vs
        v_xp = v_vm // 5
        v_vm_prog = v_vm - (v_xp * 5)
        v_lvl = v_xp // 20
        v_xp_prog = v_xp - (v_lvl * 20)

        # 3. الحسبة العامة (General Level)
        total_xp = t_xp + v_xp
        gen_lvl = total_xp // 20
        gen_xp_prog = total_xp - (gen_lvl * 20)

        return {
            "text": {"lvl": t_lvl, "xp_0_20": t_xp_prog, "xp": t_xp, "ms_0_25": t_ms_prog, "ms": ms},
            "voice": {"lvl": v_lvl, "xp_0_20": v_xp_prog, "xp": v_xp, "vm_0_5": v_vm_prog, "vm": v_vm},
            "gen": {"lvl": gen_lvl, "xp_0_20": gen_xp_prog, "xp": total_xp}
        }

    @app_commands.command(name="level", description="عرض مستوياتك في هذا السيرفر")
    @app_commands.choices(type=[
        app_commands.Choice(name="level text", value="text"),
        app_commands.Choice(name="level voice", value="voice"),
        app_commands.Choice(name="level (general)", value="general")
    ])
    async def level(self, interaction: discord.Interaction, type: str = "general", member: discord.Member = None):
        target = member or interaction.user
        gid = str(interaction.guild.id)
        
        # جلب البيانات المحلية للسيرفر
        stats = get_stats(self.bot.users_data, target.id, gid)
        data = self.calculate_logic(stats.get("ms", 0), stats.get("vs", 0))

        embed = discord.Embed(color=0x2b2d31)
        embed.set_author(name=f"مستوى {target.display_name}", icon_url=target.display_avatar.url)

        if type == "text":
            d = data["text"]
            embed.title = "📝 Level Text"
            embed.description = (f"**lvl:** `{d['lvl']}`\n**xp:** `{d['xp_0_20']}/20`\n"
                                 f"**xp total:** `{d['xp']}`\n**ms:** `{d['ms_0_25']}/25`\n**ms total:** `{d['ms']}`")
        elif type == "voice":
            d = data["voice"]
            embed.title = "🎙️ Level Voice"
            embed.description = (f"**lvl:** `{d['lvl']}`\n**xp:** `{d['xp_0_20']}/20`\n"
                                 f"**xp total:** `{d['xp']}`\n**vm:** `{d['vm_0_5']}/5`\n**vm total:** `{d['vm']}`")
        else:
            d = data["gen"]
            embed.title = "🌟 Level General"
            embed.description = f"**lvl:** `{d['lvl']}`\n**xp:** `{d['xp_0_20']}/20`\n**xp total:** `{d['xp']}`"

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="level_global", description="عرض مستوياتك التراكمية في كل السيرفرات")
    async def level_global(self, interaction: discord.Interaction, member: discord.Member = None):
        target = member or interaction.user
        uid = str(target.id)
        
        # جمع البيانات من كل السيرفرات المخزنة لهذا المستخدم
        total_ms = 0
        total_vs = 0
        
        if uid in self.bot.users_data:
            for gid in self.bot.users_data[uid]:
                server_data = self.bot.users_data[uid][gid]
                total_ms += server_data.get("ms", 0)
                total_vs += server_data.get("vs", 0)

        data = self.calculate_logic(total_ms, total_vs)
        gen = data["gen"]

        embed = discord.Embed(title=f"🌎 Global Level: {target.display_name}", color=0xffd700)
        embed.add_field(name="المستوى العالمي", value=f"**lvl:** `{gen['lvl']}`\n**xp:** `{gen['xp_0_20']}/20`\n**Total XP:** `{gen['xp']}`")
        embed.set_footer(text="إجمالي النشاط من كافة السيرفرات المشتركة")
        
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(LevelSystem(bot))
