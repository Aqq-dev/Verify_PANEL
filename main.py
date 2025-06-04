import discord
from discord import app_commands
from discord.ext import commands
import os
from keep_alive import keep_alive
from discord.ui import Select, View

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

class VerifyButton(discord.ui.Button):
    def __init__(self, role_id: int):
        super().__init__(style=discord.ButtonStyle.success, label="✅ 認証/Verify", custom_id=f"verify_{role_id}")
        self.role_id = role_id

    async def callback(self, interaction: discord.Interaction):
        guild = interaction.guild
        member = interaction.user
        role = guild.get_role(self.role_id)

        if not role:
            await interaction.response.send_message("<:questionmark:1379625207773528154> ロールが見つかりません。", ephemeral=True)
            return

        if role in member.roles:
            await interaction.response.send_message("<:cross:1379625074658644031> あなたはすでに認証しています。", ephemeral=True)
        else:
            await member.add_roles(role)
            await interaction.response.send_message("<:check:1379625033370046625> 認証が完了しました！", ephemeral=True)

class VerifyView(discord.ui.View):
    def __init__(self, role_id: int):
        super().__init__(timeout=None)
        self.add_item(VerifyButton(role_id))

@bot.tree.command(name="verify-button", description="認証パネルを作成します")
@app_commands.describe(role="付与するロール", description="認証パネルの説明", image_url="埋め込む画像URL")
async def verify(interaction: discord.Interaction, role: discord.Role, description: str, image_url: str = None):
    embed = discord.Embed(title="認証パネル", description=description, color=discord.Color.green())
    if image_url:
        embed.set_image(url=image_url)

    view = VerifyView(role.id)
    await interaction.response.send_message(embed=embed, view=view)
    bot.add_view(view)

class VerifyModal(discord.ui.Modal, title="認証テスト"):
    def __init__(self, answer: int, role: discord.Role):
        super().__init__()
        self.answer = answer
        self.role = role

        self.answer_input = discord.ui.TextInput(
            label="計算式の答えを入力してください",
            placeholder="数字のみ入力",
            required=True
        )
        self.add_item(self.answer_input)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            user_answer = int(self.answer_input.value)
        except ValueError:
            await interaction.response.send_message("<:cross:1379625074658644031> 数字を入力してください。", ephemeral=True)
            return

        if user_answer == self.answer:
            if self.role in interaction.user.roles:
                await interaction.response.send_message("<:cross:1379625074658644031> あなたはすでに認証しています。", ephemeral=True)
            else:
                await interaction.user.add_roles(self.role)
                await interaction.response.send_message("<:check:1379625033370046625> 認証が完了しました！", ephemeral=True)
        else:
            await interaction.response.send_message("<:cross:1379625074658644031> 不正解です。もう一度お試しください。", ephemeral=True)


class VerifyButton(discord.ui.Button):
    def __init__(self, role_id: int):
        super().__init__(style=discord.ButtonStyle.success, label="✅ 認証/Verify", custom_id=f"verify_{role_id}")
        self.role_id = role_id

    async def callback(self, interaction: discord.Interaction):
        guild = interaction.guild
        member = interaction.user
        role = guild.get_role(self.role_id)

        if not role:
            await interaction.response.send_message("<:questionmark:1379625207773528154> ロールが見つかりません。", ephemeral=True)
            return

        numbers = [random.randint(1, 10) for _ in range(10)]
        operators = [random.choice(["+", "-", "*"]) for _ in range(9)]

        expression = ""
        for i in range(9):
            expression += f"{numbers[i]} {operators[i]} "
        expression += f"{numbers[9]}"

        try:
            answer = eval(expression)
        except:
            await interaction.response.send_message("計算エラーが発生しました。", ephemeral=True)
            return

        modal = VerifyModal(answer, role)
        modal.title = f"この式を解いてください: {expression}"
        await interaction.response.send_modal(modal)


class VerifyView(discord.ui.View):
    def __init__(self, role_id: int):
        super().__init__(timeout=None)
        self.add_item(VerifyButton(role_id))


@bot.tree.command(name="verify-calculation", description="認証パネルを作成します (計算)")
@app_commands.describe(role="付与するロール", description="認証パネルの説明", image_url="埋め込む画像URL")
async def verify(interaction: discord.Interaction, role: discord.Role, description: str, image_url: str = None):
    embed = discord.Embed(title="認証パネル", description=description, color=discord.Color.green())
    if image_url:
        embed.set_image(url=image_url)

    view = VerifyView(role.id)
    await interaction.response.send_message(embed=embed, view=view)
    bot.add_view(view)

class RoleSelect(discord.ui.Select):
    def __init__(self, roles):
        options = [discord.SelectOption(label=role.name, value=str(role.id)) for role in roles]
        super().__init__(placeholder="ロールを選択", options=options, min_values=1, max_values=1, custom_id="role_select")
        self.roles = roles

    async def callback(self, interaction: discord.Interaction):
        role_id = int(self.values[0])
        role = discord.utils.get(interaction.guild.roles, id=role_id)
        if not role:
            await interaction.response.send_message("ロールが見つかりません。", ephemeral=True)
            return

        member = interaction.user
        if role in member.roles:
            await member.remove_roles(role)
            await interaction.response.send_message(f"<:delete:1379626208521883739> {role.name} を削除しました。", ephemeral=True)
        else:
            await member.add_roles(role)
            await interaction.response.send_message(f"<:check:1379625033370046625> {role.name} を付与しました。", ephemeral=True)

class RoleSelectView(discord.ui.View):
    def __init__(self, roles):
        super().__init__(timeout=None)
        self.add_item(RoleSelect(roles))

@bot.tree.command(name="role_panel", description="ロール選択パネルを作成")
@app_commands.describe()
async def role_panel(interaction: discord.Interaction, role: discord.Role):
    guild_roles = [role]

    embed = discord.Embed(title="ロール付与", description="以下のロールを選択できます。", color=discord.Color.blue())
    embed.add_field(name="付与されるロール", value="\n".join([role.mention for role in guild_roles]))

    view = RoleSelectView(guild_roles)
    await interaction.response.send_message(embed=embed, view=view)

@bot.event
async def on_ready():
    activity = discord.Activity(type=discord.ActivityType.watching, name="Created by @freak074495")
    await bot.change_presence(activity=activity)
    print(f'{bot.user} がログインしました！')
    await bot.tree.sync()
    for guild in bot.guilds:
        for role in guild.roles:
            bot.add_view(VerifyView(role.id))
            bot.add_view(VerifyCalcView(role.id))
    bot.add_view(RoleSelectView([]))

DISCORD_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
if DISCORD_TOKEN is None:
    print("DISCORD_BOT_TOKEN が設定されていません。")
else:
    print("Botが正常に起動しました。")

keep_alive()
bot.run(DISCORD_TOKEN)
