@bot.tree.command(name="name", description="عرض جميع أسماء العضو بالتفصيل")
@app_commands.describe(member="العضو المراد فحص أسمائه")
async def name_info(interaction: discord.Interaction, member: discord.Member = None):
    target = member or interaction.user
    
    # 1. اليوزر نيم الأصلي (الفريد)
    user_name = target.name
    
    # 2. الاسم العالمي (Global Name) - الاسم الذي يظهر في الملف الشخصي العام
    global_name = target.global_name if target.global_name else "لا يوجد"
    
    # 3. النيك نيم (Server Nickname) - اللقب داخل هذا السيرفر فقط
    server_nick = target.nick if target.nick else "لا يوجد لقب"

    embed = discord.Embed(
        title="🏷️ قائمة الأسماء", 
        description=f"تفاصيل الأسماء لـ: {target.mention}", 
        color=0xff0000
    )
    
    # إضافة الحقول بشكل منفصل وواضح
    embed.add_field(name="Username (الأصلي)", value=f"`{user_name}`", inline=False)
    embed.add_field(name="Display Name (العالمي)", value=f"`{global_name}`", inline=False)
    embed.add_field(name="Server Nickname (اللقب)", value=f"`{server_nick}`", inline=False)
    
    # وضع صورة العضو المصغرة
    embed.set_author(name=target.name, icon_url=target.display_avatar.url)
    
    await interaction.response.send_message(embed=embed)
