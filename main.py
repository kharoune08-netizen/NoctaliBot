import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# ===== MENUS =====

class GenreSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Homme", emoji="♂️"),
            discord.SelectOption(label="Femme", emoji="♀️"),
            discord.SelectOption(label="Autre", emoji="🏳️‍🌈"),
        ]
        super().__init__(placeholder="Fais un choix...", options=options)

    async def callback(self, interaction: discord.Interaction):
        role = discord.utils.get(interaction.guild.roles, name=self.values[0])
        if role:
            await interaction.user.add_roles(role)
            await interaction.response.send_message(
                f"✅ Rôle **{self.values[0]}** attribué !", ephemeral=True
            )
        else:
            await interaction.response.send_message(
                f"❌ Le rôle **{self.values[0]}** n'existe pas sur le serveur.", ephemeral=True
            )


class AgeSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Moins de 15 ans", emoji="🧒"),
            discord.SelectOption(label="15-17 ans", emoji="🧑"),
            discord.SelectOption(label="18-25 ans", emoji="👤"),
            discord.SelectOption(label="25 ans et +", emoji="🧓"),
        ]
        super().__init__(placeholder="Fais un choix...", options=options)

    async def callback(self, interaction: discord.Interaction):
        role = discord.utils.get(interaction.guild.roles, name=self.values[0])
        if role:
            await interaction.user.add_roles(role)
            await interaction.response.send_message(
                f"✅ Rôle **{self.values[0]}** attribué !", ephemeral=True
            )
        else:
            await interaction.response.send_message(
                f"❌ Le rôle **{self.values[0]}** n'existe pas.", ephemeral=True
            )


class SituationSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Célibataire", emoji="💔"),
            discord.SelectOption(label="En couple", emoji="❤️"),
            discord.SelectOption(label="Compliqué", emoji="💫"),
        ]
        super().__init__(placeholder="Fais un choix...", options=options)

    async def callback(self, interaction: discord.Interaction):
        role = discord.utils.get(interaction.guild.roles, name=self.values[0])
        if role:
            await interaction.user.add_roles(role)
            await interaction.response.send_message(
                f"✅ Rôle **{self.values[0]}** attribué !", ephemeral=True
            )
        else:
            await interaction.response.send_message(
                f"❌ Le rôle **{self.values[0]}** n'existe pas.", ephemeral=True
            )


class SetupView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(GenreSelect())
        self.add_item(AgeSelect())
        self.add_item(SituationSelect())


# ===== COMMANDE =====

@bot.command()
@commands.has_permissions(administrator=True)
async def setup(ctx):
    embed = discord.Embed(
        title="🌙 Bienvenue sur le serveur !",
        description=(
            "Sélectionne tes rôles ci-dessous pour personnaliser ton profil.\n\n"
            "♂️ → **Genre**\n"
            "🎂 → **Âge**\n"
            "💍 → **Situation amoureuse**"
        ),
        color=discord.Color.purple()
    )
    await ctx.send(embed=embed, view=SetupView())

@bot.command()
@commands.has_permissions(administrator=True)
async def reglement(ctx):
    embed = discord.Embed(
        title="📖 Règlement du serveur",
        description=(
            "Bienvenue sur le serveur ! Merci de respecter les règles suivantes :\n\n"
            "**1️⃣ Respectez tout le monde**\n"
            "Aucune insulte, discrimination ou harcèlement ne sera toléré.\n\n"
            "**2️⃣ Pas de spam**\n"
            "Évitez les messages répétitifs ou les mentions abusives.\n\n"
            "**3️⃣ Pas de pub**\n"
            "Aucun lien ou invitation Discord sans autorisation d'un admin.\n\n"
            "**4️⃣ Contenu approprié**\n"
            "Pas de contenu NSFW en dehors des salons prévus.\n\n"
            "**5️⃣ Respectez les salons**\n"
            "Chaque salon a un sujet, restez dans le thème.\n\n"
            "En restant sur ce serveur vous acceptez ces règles. ✅"
        ),
        color=discord.Color.purple()
    )
    await ctx.send(embed=embed)
    await ctx.message.delete()


@bot.event
async def on_ready():
    print(f"✅ {bot.user} est en ligne !")

import os
bot.run(os.environ.get("TOKEN"))

