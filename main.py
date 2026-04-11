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

from discord.ext import tasks

MUDAE_CHANNEL_ID = 1492299644321923152  

@tasks.loop(hours=1)
async def rappel_mudae():
    channel = bot.get_channel(MUDAE_CHANNEL_ID)
    if channel:
        embed = discord.Embed(
            title="🎮 C'est l'heure de Mudae !",
            description=(
                "**Commandes pour invoquer :**\n"
                "`$w` → Invoquer une waifu\n"
                "`$h` → Invoquer un husbando\n"
                "`$wa` → Invoquer 4 waifus\n"
                "`$ha` → Invoquer 4 husbandos\n\n"
                "**Commandes utiles :**\n"
                "`$tu` → Voir ton délai restant\n"
                "`$marry` → Voir tes personnages\n"
                "`$dk` → Voir tes dés disponibles\n"
                "`$rt` → Reset ton délai (si dispo)\n\n"
                "⏰ Rappel toutes les heures !"
            ),
            color=discord.Color.purple()
        )
        await channel.send(embed=embed)

@bot.event
async def on_ready():
    print(f"✅ {bot.user} est en ligne !")
    rappel_mudae.start()

import random

ROLES_LOL = ["Top", "Jungle", "Mid", "ADC", "Support"]

participants = []

class ParticipantModal(discord.ui.Modal, title="Rejoindre la partie"):
    pseudo = discord.ui.TextInput(
        label="Ton pseudo League of Legends",
        placeholder="Ex: Noctali123",
        required=True
    )

    async def on_submit(self, interaction: discord.Interaction):
        global participants
        pseudo = self.pseudo.value

        # Vérifie si déjà inscrit
        if any(p["pseudo"] == pseudo for p in participants):
            await interaction.response.send_message(
                f"❌ **{pseudo}** est déjà inscrit !", ephemeral=True
            )
            return

        participants.append({"user": interaction.user, "pseudo": pseudo})
        await interaction.response.send_message(
            f"✅ **{pseudo}** a rejoint la partie ! ({len(participants)}/10)",
            ephemeral=True
        )

        if len(participants) == 10:
            await lancer_partie(interaction)

async def lancer_partie(interaction: discord.Interaction):
    global participants
    random.shuffle(participants)

    equipe1 = participants[:5]
    equipe2 = participants[5:]
    roles = ROLES_LOL.copy()

    def format_equipe(equipe):
        random.shuffle(roles)
        return "\n".join(
            f"**{roles[i]}** → {p['pseudo']}"
            for i, p in enumerate(equipe)
        )

    embed = discord.Embed(
        title="⚔️ Partie Personnalisée — Les équipes sont prêtes !",
        color=discord.Color.gold()
    )
    embed.add_field(
        name="🔵 Équipe 1",
        value=format_equipe(equipe1),
        inline=True
    )
    embed.add_field(
        name="🔴 Équipe 2",
        value=format_equipe(equipe2),
        inline=True
    )

    view = RerollView(equipe1, equipe2)
    await interaction.channel.send(embed=embed, view=view)
    participants = []


class RerollView(discord.ui.View):
    def __init__(self, equipe1, equipe2):
        super().__init__(timeout=None)
        self.equipe1 = equipe1
        self.equipe2 = equipe2

    @discord.ui.button(label="🎲 Reroll les rôles", style=discord.ButtonStyle.blurple)
    async def reroll(self, interaction: discord.Interaction, button: discord.ui.Button):
        roles = ROLES_LOL.copy()

        def format_equipe(equipe):
            random.shuffle(roles)
            return "\n".join(
                f"**{roles[i]}** → {p['pseudo']}"
                for i, p in enumerate(equipe)
            )

        embed = discord.Embed(
            title="⚔️ Partie Personnalisée — Rôles rerollés !",
            color=discord.Color.gold()
        )
        embed.add_field(
            name="🔵 Équipe 1",
            value=format_equipe(self.equipe1),
            inline=True
        )
        embed.add_field(
            name="🔴 Équipe 2",
            value=format_equipe(self.equipe2),
            inline=True
        )
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="🔄 Reroll les équipes", style=discord.ButtonStyle.red)
    async def reroll_equipes(self, interaction: discord.Interaction, button: discord.ui.Button):
        tous = self.equipe1 + self.equipe2
        random.shuffle(tous)
        self.equipe1 = tous[:5]
        self.equipe2 = tous[5:]
        roles = ROLES_LOL.copy()

        def format_equipe(equipe):
            random.shuffle(roles)
            return "\n".join(
                f"**{roles[i]}** → {p['pseudo']}"
                for i, p in enumerate(equipe)
            )

        embed = discord.Embed(
            title="⚔️ Partie Personnalisée — Équipes rerollées !",
            color=discord.Color.gold()
        )
        embed.add_field(
            name="🔵 Équipe 1",
            value=format_equipe(self.equipe1),
            inline=True
        )
        embed.add_field(
            name="🔴 Équipe 2",
            value=format_equipe(self.equipe2),
            inline=True
        )
        await interaction.response.edit_message(embed=embed, view=self)


class JoindreView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="⚔️ Je veux participer !", style=discord.ButtonStyle.green)
    async def rejoindre(self, interaction: discord.Interaction, button: discord.ui.Button):
        if len(participants) >= 10:
            await interaction.response.send_message(
                "❌ La partie est déjà complète !", ephemeral=True
            )
            return
        await interaction.response.send_modal(ParticipantModal())


@bot.command()
@commands.has_permissions(administrator=True)
async def partiepersso(ctx):
    global participants
    participants = []
    embed = discord.Embed(
        title="🎮 Partie Personnalisée League of Legends",
        description=(
            "Une partie personnalisée est en cours d'organisation !\n\n"
            "Clique sur le bouton ci-dessous pour participer et entre ton pseudo LoL.\n\n"
            "👥 **0/10** joueurs inscrits"
        ),
        color=discord.Color.blue()
    )
    await ctx.send(embed=embed, view=JoindreView())
    await ctx.message.delete()


@bot.event
async def on_ready():
    print(f"✅ {bot.user} est en ligne !")

import os
bot.run(os.environ.get("TOKEN"))

