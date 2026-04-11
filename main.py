import discord
from discord.ext import commands
import random
import os

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

ROLES_LOL = ["Top", "Jungle", "Mid", "ADC", "Support"]
participants = []
partie_message = None

# ===== MENUS ROLES =====

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
            await interaction.response.send_message(f"✅ Rôle **{self.values[0]}** attribué !", ephemeral=True)
        else:
            await interaction.response.send_message(f"❌ Le rôle **{self.values[0]}** n'existe pas sur le serveur.", ephemeral=True)

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
            await interaction.response.send_message(f"✅ Rôle **{self.values[0]}** attribué !", ephemeral=True)
        else:
            await interaction.response.send_message(f"❌ Le rôle **{self.values[0]}** n'existe pas.", ephemeral=True)

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
            await interaction.response.send_message(f"✅ Rôle **{self.values[0]}** attribué !", ephemeral=True)
        else:
            await interaction.response.send_message(f"❌ Le rôle **{self.values[0]}** n'existe pas.", ephemeral=True)

class SetupView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(GenreSelect())
        self.add_item(AgeSelect())
        self.add_item(SituationSelect())

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

# ===== REGLEMENT =====

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

# ===== PARTIE PERSO LOL =====

def build_embed():
    liste = "\n".join(f"**{i+1}.** {p['pseudo']}" for i, p in enumerate(participants)) if participants else "*Aucun participant pour l'instant*"
    embed = discord.Embed(
        title="🎮 Partie Personnalisée League of Legends",
        description=(
            "Une partie personnalisée est en cours d'organisation !\n\n"
            "Clique sur **Je veux participer** pour rejoindre et entre ton pseudo LoL.\n\n"
            f"👥 **{len(participants)}/10** joueurs inscrits\n\n"
            f"**Liste des participants :**\n{liste}"
        ),
        color=discord.Color.blue()
    )
    return embed

class ParticipantModal(discord.ui.Modal, title="Rejoindre la partie"):
    pseudo = discord.ui.TextInput(
        label="Ton pseudo League of Legends",
        placeholder="Ex: Noctali123",
        required=True
    )

    async def on_submit(self, interaction: discord.Interaction):
        global participants, partie_message
        pseudo = self.pseudo.value

        if any(p["pseudo"].lower() == pseudo.lower() for p in participants):
            await interaction.response.send_message(f"❌ **{pseudo}** est déjà inscrit !", ephemeral=True)
            return

        if len(participants) >= 10:
            await interaction.response.send_message("❌ La partie est déjà complète !", ephemeral=True)
            return

        participants.append({"user": interaction.user, "pseudo": pseudo})
        await interaction.response.send_message(f"✅ **{pseudo}** a rejoint la partie !", ephemeral=True)

        if partie_message:
            await partie_message.edit(embed=build_embed(), view=JoindreView())

        if len(participants) == 10:
            await lancer_partie(interaction)

class RetirerSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label=p["pseudo"], value=p["pseudo"])
            for p in participants
        ]
        super().__init__(placeholder="Choisir un joueur à retirer...", options=options)

    async def callback(self, interaction: discord.Interaction):
        global participants, partie_message
        pseudo = self.values[0]
        participants = [p for p in participants if p["pseudo"] != pseudo]
        await interaction.response.send_message(f"🗑️ **{pseudo}** a été retiré de la liste !", ephemeral=True)
        if partie_message:
            await partie_message.edit(embed=build_embed(), view=JoindreView())

class RetirerView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=60)
        self.add_item(RetirerSelect())

async def lancer_partie(interaction: discord.Interaction):
    global participants
    random.shuffle(participants)
    equipe1 = participants[:5]
    equipe2 = participants[5:]

    def format_equipe(equipe):
        roles = ROLES_LOL.copy()
        random.shuffle(roles)
        return "\n".join(f"**{roles[i]}** → {p['pseudo']}" for i, p in enumerate(equipe))

    embed = discord.Embed(
        title="⚔️ Partie Personnalisée — Les équipes sont prêtes !",
        color=discord.Color.gold()
    )
    embed.add_field(name="🔵 Équipe 1", value=format_equipe(equipe1), inline=True)
    embed.add_field(name="🔴 Équipe 2", value=format_equipe(equipe2), inline=True)

    view = RerollView(equipe1, equipe2)
    await interaction.channel.send(embed=embed, view=view)
    participants = []

class RerollView(discord.ui.View):
    def __init__(self, equipe1, equipe2):
        super().__init__(timeout=None)
        self.equipe1 = equipe1
        self.equipe2 = equipe2

    @discord.ui.button(label="🎲 Reroll les rôles", style=discord.ButtonStyle.blurple)
    async def reroll_roles(self, interaction: discord.Interaction, button: discord.ui.Button):
        def format_equipe(equipe):
            roles = ROLES_LOL.copy()
            random.shuffle(roles)
            return "\n".join(f"**{roles[i]}** → {p['pseudo']}" for i, p in enumerate(equipe))

        embed = discord.Embed(title="⚔️ Partie Personnalisée — Rôles rerollés !", color=discord.Color.gold())
        embed.add_field(name="🔵 Équipe 1", value=format_equipe(self.equipe1), inline=True)
        embed.add_field(name="🔴 Équipe 2", value=format_equipe(self.equipe2), inline=True)
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="🔄 Reroll les équipes", style=discord.ButtonStyle.red)
    async def reroll_equipes(self, interaction: discord.Interaction, button: discord.ui.Button):
        tous = self.equipe1 + self.equipe2
        random.shuffle(tous)
        self.equipe1 = tous[:5]
        self.equipe2 = tous[5:]

        def format_equipe(equipe):
            roles = ROLES_LOL.copy()
            random.shuffle(roles)
            return "\n".join(f"**{roles[i]}** → {p['pseudo']}" for i, p in enumerate(equipe))

        embed = discord.Embed(title="⚔️ Partie Personnalisée — Équipes rerollées !", color=discord.Color.gold())
        embed.add_field(name="🔵 Équipe 1", value=format_equipe(self.equipe1), inline=True)
        embed.add_field(name="🔴 Équipe 2", value=format_equipe(self.equipe2), inline=True)
        await interaction.response.edit_message(embed=embed, view=self)

class JoindreView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="⚔️ Je veux participer !", style=discord.ButtonStyle.green)
    async def rejoindre(self, interaction: discord.Interaction, button: discord.ui.Button):
        if len(participants) >= 10:
            await interaction.response.send_message("❌ La partie est déjà complète !", ephemeral=True)
            return
        await interaction.response.send_modal(ParticipantModal())

    @discord.ui.button(label="🚪 Se désinscrire", style=discord.ButtonStyle.grey)
    async def desinscrire(self, interaction: discord.Interaction, button: discord.ui.Button):
        global participants, partie_message
        pseudo_user = [p for p in participants if p["user"].id == interaction.user.id]
        if not pseudo_user:
            await interaction.response.send_message("❌ Tu n'es pas inscrit !", ephemeral=True)
            return
        participants = [p for p in participants if p["user"].id != interaction.user.id]
        await interaction.response.send_message(f"✅ Tu as été désinscrit !", ephemeral=True)
        if partie_message:
            await partie_message.edit(embed=build_embed(), view=JoindreView())

@bot.command()
@commands.has_permissions(administrator=True)
async def partiepersso(ctx):
    global participants, partie_message
    participants = []
    msg = await ctx.send(embed=build_embed(), view=JoindreView())
    partie_message = msg
    await ctx.message.delete()

@bot.command()
@commands.has_permissions(administrator=True)
async def retirer(ctx):
    if not participants:
        await ctx.send("❌ Aucun participant à retirer !", ephemeral=True)
        return
    await ctx.send("🗑️ Quel joueur veux-tu retirer ?", view=RetirerView(), ephemeral=True)
    await ctx.message.delete()

# ===== LANCEMENT =====

@bot.event
async def on_ready():
    print(f"✅ {bot.user} est en ligne !")

bot.run(os.environ.get("TOKEN"))
