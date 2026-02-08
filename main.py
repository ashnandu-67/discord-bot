import os
import discord
from discord.ext import commands
from discord import app_commands
import random

# ---- BOT SETUP ----
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# ---- ON READY ----
@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"Logged in as {bot.user}")

# =========================
# 🎉 GIVEAWAY COMMAND
# =========================
@bot.tree.command(name="giveaway", description="Start a giveaway")
@app_commands.describe(prize="What are you giving away?")
async def giveaway(interaction: discord.Interaction, prize: str):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ Admins only.", ephemeral=True)
        return

    embed = discord.Embed(
        title="🎉 GIVEAWAY 🎉",
        description=f"Prize: **{prize}**\nReact with 🎉 to enter!",
        color=discord.Color.gold()
    )
    embed.set_footer(text="Ends when admin uses /end_giveaway")

    msg = await interaction.channel.send(embed=embed)
    await msg.add_reaction("🎉")

    await interaction.response.send_message("✅ Giveaway started!", ephemeral=True)

# =========================
# 🎉 END GIVEAWAY
# =========================
@bot.tree.command(name="end_giveaway", description="End the giveaway and pick a winner")
async def end_giveaway(interaction: discord.Interaction):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ Admins only.", ephemeral=True)
        return

    async for message in interaction.channel.history(limit=50):
        for reaction in message.reactions:
            if str(reaction.emoji) == "🎉":
                users = [u async for u in reaction.users() if not u.bot]
                if not users:
                    await interaction.response.send_message("❌ No participants.", ephemeral=True)
                    return

                winner = random.choice(users)
                await interaction.channel.send(f"🎉 **Winner:** {winner.mention}!")
                await interaction.response.send_message("✅ Giveaway ended.", ephemeral=True)
                return

    await interaction.response.send_message("❌ No giveaway found.", ephemeral=True)

# =========================
# 🎫 TICKET PANEL SYSTEM
# =========================

class TicketSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(
                label="Designer Application",
                description="Apply to become a designer",
                emoji="🎨"
            ),
            discord.SelectOption(
                label="Support Ticket",
                description="Get help from staff",
                emoji="🛠️"
            ),
        ]

        super().__init__(
            placeholder="Make a selection",
            min_values=1,
            max_values=1,
            options=options
        )

    async def callback(self, interaction: discord.Interaction):
        guild = interaction.guild
        choice = self.values[0]

        category = discord.utils.get(guild.categories, name="Tickets")
        if category is None:
            category = await guild.create_category("Tickets")

        channel = await guild.create_text_channel(
            name=f"ticket-{interaction.user.name}",
            category=category,
            overwrites={
                guild.default_role: discord.PermissionOverwrite(read_messages=False),
                interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
                guild.me: discord.PermissionOverwrite(read_messages=True)
            }
        )

        embed = discord.Embed(
            title="🎫 Ticket Created",
            description=f"Type: **{choice}**\nUser: {interaction.user.mention}",
            color=discord.Color.green()
        )

        await channel.send(embed=embed)
        await interaction.response.send_message(
            f"✅ Your ticket has been created: {channel.mention}",
            ephemeral=True
        )

class TicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(TicketSelect())

# =========================
# 📋 SEND TICKET PANEL
# =========================
@bot.tree.command(name="ticket_panel", description="Send the ticket panel")
async def ticket_panel(interaction: discord.Interaction):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ Admins only.", ephemeral=True)
        return

    embed = discord.Embed(
        title="📋 Designer Application",
        description=(
            "This designer application is for members who are interested in joining our ER:LC Designing Server.\n\n"
            "**By applying, you agree to:**\n"
            "• Work professionally\n"
            "• Follow server guidelines\n"
            "• Meet deadlines\n"
            "• Accept feedback\n\n"
            "Select an option below to continue."
        ),
        color=discord.Color.blurple()
    )

    await interaction.channel.send(embed=embed, view=TicketView())
    await interaction.response.send_message("✅ Ticket panel sent.", ephemeral=True)

# =========================
# ---- RUN BOT ----
# =========================
TOKEN = os.getenv("TOKEN")

if TOKEN is None:
    raise RuntimeError("TOKEN environment variable not set")

bot.run(TOKEN)
