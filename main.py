import discord
from discord.ext import commands
import asyncio
import random
import os

# -------- BOT SETUP --------

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

# -------- GIVEAWAYS --------

@bot.command()
@commands.has_permissions(administrator=True)
async def gstart(ctx, minutes: int, *, prize: str):
    embed = discord.Embed(
        title="🎉 GIVEAWAY 🎉",
        description=f"**Prize:** {prize}\n\nReact with 🎉 to enter!",
        color=discord.Color.purple()
    )
    embed.set_footer(text=f"Ends in {minutes} minutes")

    msg = await ctx.send(embed=embed)
    await msg.add_reaction("🎉")

    await asyncio.sleep(minutes * 60)

    msg = await ctx.channel.fetch_message(msg.id)
    reaction = discord.utils.get(msg.reactions, emoji="🎉")

    if reaction is None:
        await ctx.send("No one entered 😔")
        return

    users = [u async for u in reaction.users() if not u.bot]

    if not users:
        await ctx.send("No valid entries 😔")
        return

    winner = random.choice(users)
    await ctx.send(f"🎉 Congrats {winner.mention}! You won **{prize}**")

# -------- TICKETS --------

@bot.command()
@commands.has_permissions(administrator=True)
async def ticketpanel(ctx):
    embed = discord.Embed(
        title="🎫 Support Tickets",
        description="React with 🎫 to open a ticket",
        color=discord.Color.blue()
    )
    msg = await ctx.send(embed=embed)
    await msg.add_reaction("🎫")

@bot.event
async def on_reaction_add(reaction, user):
    if user.bot:
        return

    if reaction.emoji != "🎫":
        return

    guild = reaction.message.guild

    category = discord.utils.get(guild.categories, name="Tickets")
    if category is None:
        category = await guild.create_category("Tickets")

    # Prevent duplicate tickets
    existing = discord.utils.get(
        guild.text_channels,
        name=f"ticket-{user.name.lower()}"
    )
    if existing:
        return

    channel = await guild.create_text_channel(
        name=f"ticket-{user.name}",
        category=category
    )

    await channel.set_permissions(guild.default_role, view_channel=False)
    await channel.set_permissions(user, view_channel=True, send_messages=True)

    await channel.send(
        f"{user.mention} 🎫 Ticket created!\n"
        "Please explain your issue. A staff member will help you soon."
    )

# -------- RUN BOT --------

TOKEN = os.getenv("DISCORD_TOKEN")
bot.run(TOKEN)