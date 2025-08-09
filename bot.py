import discord 
from discord import app_commands
from discord.ext import commands
import json
import os

DATA_FILE = "statystyki.json"
GUILD_ID = 1403555463345471490  # ID Twojego serwera

ROLE_ID_SYTUACJA = 1403555463458590785  # ID roli z dostępem do /sytuacja
ROLE_ID_STATYSTYKI = 1403555463458590789  # ID roli z dostępem do /statystyki

ALLOWED_CHANNEL_ID = 1403555465354412092  # ID kanału, na którym mogą działać komendy

KATEGORIE = [
    "🚓 Patrol",
    "🔒 Aresztowanie",
    "🎯 Reakcja na marka (np. C0)",
    "🌴 Cayo / Zancudo",
    "🕵️ Przesłuchanie",
    "📂 Teczka na frakcję kryminalną",
    "🛒 Sklep",
    "📄 Teczka z napadu",
    "🏦 Bank    10 000",
    "📡 Złapanie opaski GPS + wzięcie na cele",
    "🎁 Dropy / Eventy",
    "📦 Magazyny / Dealerzy",
    "❓ Inne"
]

if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        stats = json.load(f)
else:
    stats = {}

def save_stats():
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(stats, f, ensure_ascii=False, indent=4)

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    await bot.tree.sync(guild=discord.Object(id=GUILD_ID))
    print(f"✅ Zalogowano jako {bot.user}")

@bot.tree.command(name="sytuacja", description="Opisz sytuację, wybierz kategorię i dodaj zdjęcie")
@app_commands.describe(
    kategoria="Wybierz kategorię",
    opis="Wpisz opis sytuacji",
    zdjecie="Dodaj zdjęcie (wymagane)"
)
@app_commands.choices(kategoria=[app_commands.Choice(name=k, value=k) for k in KATEGORIE])
@app_commands.guilds(discord.Object(id=GUILD_ID))
async def sytuacja(interaction: discord.Interaction, kategoria: app_commands.Choice[str], opis: str, zdjecie: discord.Attachment):
    if interaction.channel_id != ALLOWED_CHANNEL_ID:
        await interaction.response.send_message(f"❌ Komenda działa tylko na kanale <#{ALLOWED_CHANNEL_ID}>.", ephemeral=True)
        return

    if ROLE_ID_SYTUACJA not in [role.id for role in interaction.user.roles]:
        await interaction.response.send_message("❌ Nie masz uprawnień do tej komendy.", ephemeral=True)
        return

    user_id = str(interaction.user.id)
    if user_id not in stats or not isinstance(stats[user_id], dict):
        stats[user_id] = {k: 0 for k in KATEGORIE}

    stats[user_id][kategoria.value] += 1
    save_stats()
    total_count = sum(stats[user_id].values())

    embed = discord.Embed(
        title="📜 Nowa sytuacja",
        description=f"**Od:** {interaction.user.mention}\n**Kategoria:** {kategoria.name}\n**Opis:** {opis}",
        color=discord.Color.blue()
    )
    embed.set_footer(text=f"To Twoje {total_count} poprawne użycie tej komendy!")
    embed.set_image(url=zdjecie.url)

    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="statystyki", description="Pokaż statystyki użycia komendy /sytuacja (z podziałem na kategorie)")
@app_commands.guilds(discord.Object(id=GUILD_ID))
async def statystyki(interaction: discord.Interaction):
    if interaction.channel_id != ALLOWED_CHANNEL_ID:
        await interaction.response.send_message(f"❌ Komenda działa tylko na kanale <#{ALLOWED_CHANNEL_ID}>.", ephemeral=True)
        return

    if ROLE_ID_STATYSTYKI not in [role.id for role in interaction.user.roles]:
        await interaction.response.send_message("❌ Nie masz uprawnień do tej komendy.", ephemeral=True)
        return

    if not stats:
        await interaction.response.send_message("📊 Brak zapisanych statystyk.", ephemeral=True)
        return

    await interaction.response.defer(ephemeral=True)
    embed = discord.Embed(title="📊 Statystyki użycia komendy /sytuacja", color=discord.Color.green())

    for user_id, categories in stats.items():
        if isinstance(categories, int):
            categories = {k: 0 for k in KATEGORIE}
            stats[user_id] = categories
            save_stats()

        user = bot.get_user(int(user_id))
        username = user.name if user else f"Użytkownik {user_id}"

        total = sum(categories.values())
        details = "\n".join([f"{cat}: {count}" for cat, count in categories.items() if count > 0])
        embed.add_field(name=f"{username} – {total} razy", value=details or "Brak danych", inline=False)

    await interaction.followup.send(embed=embed, ephemeral=True)

bimport os
bot.run(os.getenv("DISCORD_TOKEN"))
