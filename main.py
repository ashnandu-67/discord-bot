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
# 🎫 TICKET SYSTEM
# =========================
@bot.tree.command(name="ticket", description="Create a support ticket")
async def ticket(interaction: discord.Interaction):
    guild = interaction.guild

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

    await channel.send(f"🎫 Ticket created for {interaction.user.mention}")
    await interaction.response.send_message(
        f"✅ Your ticket has been created: {channel.mention}",
        ephemeral=True
    )

# =========================
# ---- RUN BOT (IMPORTANT)
# =========================
TOKEN = os.getenv("TOKEN")

if TOKEN is None:
    raise RuntimeError("TOKEN environment variable not set")

bot.run(TOKEN)
