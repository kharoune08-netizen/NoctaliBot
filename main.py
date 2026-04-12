import discord
from discord.ext import commands, tasks
import random
import os
import json
from datetime import datetime, timedelta

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

ROLES_LOL = ["Top", "Jungle", "Mid", "ADC", "Support"]
PERM_ROLE = "Noctali Bot Perm"
CASINO_CHANNEL_ID = 1492499084412583956
GAME_CHANNEL_ID = 1492844673041956905

DEVINETTES = [
    {"question": "J'ai des villes, mais pas de maisons. Des forêts, mais pas d'arbres. De l'eau, mais pas de poissons. Qu'est-ce que je suis ?", "reponse": "une carte"},
    {"question": "Plus je sèche, plus je suis mouillée. Qu'est-ce que je suis ?", "reponse": "une serviette"},
    {"question": "Je parle sans bouche et j'entends sans oreilles. Qu'est-ce que je suis ?", "reponse": "un echo"},
    {"question": "Plus tu m'enlèves, plus je grandis. Qu'est-ce que je suis ?", "reponse": "un trou"},
    {"question": "Je suis léger comme une plume mais même l'homme le plus fort ne peut me tenir plus d'une minute. Qu'est-ce que je suis ?", "reponse": "le souffle"},
    {"question": "Je n'ai pas de jambes mais je cours partout. Qu'est-ce que je suis ?", "reponse": "l eau"},
    {"question": "Quel est le comble pour un électricien ?", "reponse": "de ne pas etre au courant"},
    {"question": "Qu'est-ce qu'un canif ?", "reponse": "le petit du canif"},
    {"question": "Plus je suis grande, moins on me voit. Qu'est-ce que je suis ?", "reponse": "l obscurite"},
    {"question": "J'ai une tête mais pas de corps, une queue mais pas de pattes. Qu'est-ce que je suis ?", "reponse": "une piece de monnaie"},
]

devinette_active = {}

# ===== PARTICIPANTS =====

def load_participants():
    try:
        with open("participants.json", "r") as f:
            return json.load(f)
    except:
        return []

def save_participants(data):
    with open("participants.json", "w") as f:
        json.dump(data, f)

# ===== ÉCONOMIE =====

def load_economy():
    try:
        with open("economy.json", "r") as f:
            return json.load(f)
    except:
        return {}

def save_economy(data):
    with open("economy.json", "w") as f:
        json.dump(data, f)

def get_balance(user_id):
    data = load_economy()
    return data.get(str(user_id), {}).get("balance", 500)

def set_balance(user_id, amount):
    data = load_economy()
    if str(user_id) not in data:
        data[str(user_id)] = {}
    data[str(user_id)]["balance"] = max(0, amount)
    save_economy(data)

def get_last_daily(user_id):
    data = load_economy()
    return data.get(str(user_id), {}).get("last_daily", None)

def set_last_daily(user_id, date):
    data = load_economy()
    if str(user_id) not in data:
        data[str(user_id)] = {}
    data[str(user_id)]["last_daily"] = date
    save_economy(data)

def has_perm(user):
    return discord.utils.get(user.roles, name=PERM_ROLE) is not None

# ===== RAPPELS AUTOMATIQUES =====

@tasks.loop(hours=2)
async def rappel_casino():
    channel = bot.get_channel(CASINO_CHANNEL_ID)
    if channel:
        embed = discord.Embed(
            title="🎰 Rappel des commandes Casino !",
            description=(
                "**Jeux :**\n"
                "`!coinflip <mise>` → Pile ou Face\n"
                "`!slots <mise>` → Machine à sous\n\n"
                "**Économie :**\n"
                "`!daily` → Bonus de 500 💰 par jour\n"
                "`!solde` → Voir tes pièces\n"
                "`!voler @membre` → Tenter de voler (40%)\n"
                "`!classement` → Top 10 des plus riches\n\n"
                "🎰 Bonne chance !"
            ),
            color=discord.Color.gold()
        )
        await channel.send(embed=embed)

@tasks.loop(hours=2)
async def rappel_game():
    channel = bot.get_channel(GAME_CHANNEL_ID)
    if channel:
        embed = discord.Embed(
            title="🎮 Rappel des commandes Game !",
            description=(
                "**Pierre Feuille Ciseaux :**\n"
                "`!pfc pierre` → Jouer pierre\n"
                "`!pfc feuille` → Jouer feuille\n"
                "`!pfc ciseaux` → Jouer ciseaux\n\n"
                "**Quiz / Devinettes :**\n"
                "`!devinette` → Nouvelle devinette\n\n"
                "🎮 Amuse-toi bien !"
            ),
            color=discord.Color.blue()
        )
        await channel.send(embed=embed)

# ===== PIERRE FEUILLE CISEAUX =====

@bot.command()
async def pfc(ctx, choix: str = None):
    if choix is None or choix.lower() not in ["pierre", "feuille", "ciseaux"]:
        await ctx.send("❌ Usage : `!pfc <pierre/feuille/ciseaux>`")
        return

    choix = choix.lower()
    bot_choix = random.choice(["pierre", "feuille", "ciseaux"])
    emojis = {"pierre": "🪨", "feuille": "📄", "ciseaux": "✂️"}

    if choix == bot_choix:
        resultat = "🤝 Égalité !"
        color = discord.Color.yellow()
    elif (choix == "pierre" and bot_choix == "ciseaux") or \
         (choix == "feuille" and bot_choix == "pierre") or \
         (choix == "ciseaux" and bot_choix == "feuille"):
        resultat = "🎉 Tu as gagné !"
        color = discord.Color.green()
    else:
        resultat = "😈 J'ai gagné !"
        color = discord.Color.red()

    embed = discord.Embed(
        title="🪨📄✂️ Pierre Feuille Ciseaux",
        description=(
            f"Tu as choisi : {emojis[choix]} **{choix}**\n"
            f"J'ai choisi : {emojis[bot_choix]} **{bot_choix}**\n\n"
            f"**{resultat}**"
        ),
        color=color
    )
    await ctx.send(embed=embed)

# ===== DEVINETTES =====

@bot.command()
async def devinette(ctx):
    question = random.choice(DEVINETTES)
    devinette_active[ctx.channel.id] = question["reponse"].lower()

    embed = discord.Embed(
        title="🧠 Devinette !",
        description=f"{question['question']}\n\n*Réponds dans le chat !*",
        color=discord.Color.purple()
    )
    embed.set_footer(text="Tu as 30 secondes pour répondre !")
    await ctx.send(embed=embed)

    def check(m):
        return m.channel == ctx.channel and not m.author.bot

    try:
        msg = await bot.wait_for("message", timeout=30.0, check=check)
        if msg.content.lower() == devinette_active.get(ctx.channel.id):
            await msg.reply(f"✅ Bravo **{msg.author.display_name}** ! C'était bien **{question['reponse']}** ! 🎉")
        else:
            await msg.reply(f"❌ Raté ! La réponse était **{question['reponse']}** !")
    except:
        await ctx.send(f"⏰ Temps écoulé ! La réponse était **{question['reponse']}** !")

    devinette_active.pop(ctx.channel.id, None)

# ===== MODÉRATION =====

@bot.command()
@commands.has_permissions(moderate_members=True)
async def timeout(ctx, membre: discord.Member = None, duree: int = 10, *, raison: str = "Aucune raison"):
    if membre is None:
        await ctx.send("❌ Usage : `!timeout @membre <durée en minutes> <raison>`")
        return
    until = discord.utils.utcnow() + timedelta(minutes=duree)
    await membre.timeout(until, reason=raison)
    embed = discord.Embed(title="⏰ Timeout", description=f"**{membre.display_name}** a été mis en timeout pour **{duree} minutes**\n📝 Raison : {raison}", color=discord.Color.orange())
    await ctx.send(embed=embed)
    await ctx.message.delete()

@bot.command()
@commands.has_permissions(moderate_members=True)
async def unmute(ctx, membre: discord.Member = None):
    if membre is None:
        await ctx.send("❌ Usage : `!unmute @membre`")
        return
    await membre.timeout(None)
    embed = discord.Embed(title="🔊 Unmute", description=f"**{membre.display_name}** a été démute !", color=discord.Color.green())
    await ctx.send(embed=embed)
    await ctx.message.delete()

@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, membre: discord.Member = None, *, raison: str = "Aucune raison"):
    if membre is None:
        await ctx.send("❌ Usage : `!kick @membre <raison>`")
        return
    await membre.kick(reason=raison)
    embed = discord.Embed(title="👢 Kick", description=f"**{membre.display_name}** a été kick !\n📝 Raison : {raison}", color=discord.Color.red())
    await ctx.send(embed=embed)
    await ctx.message.delete()

@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, membre: discord.Member = None, *, raison: str = "Aucune raison"):
    if membre is None:
        await ctx.send("❌ Usage : `!ban @membre <raison>`")
        return
    await membre.ban(reason=raison)
    embed = discord.Embed(title="🔨 Ban", description=f"**{membre.display_name}** a été banni !\n📝 Raison : {raison}", color=discord.Color.dark_red())
    await ctx.send(embed=embed)
    await ctx.message.delete()

@bot.command()
@commands.has_permissions(ban_members=True)
async def unban(ctx, *, nom: str = None):
    if nom is None:
        await ctx.send("❌ Usage : `!unban <nom#0000>`")
        return
    banned = [entry async for entry in ctx.guild.bans()]
    for ban_entry in banned:
        if str(ban_entry.user) == nom:
            await ctx.guild.unban(ban_entry.user)
            embed = discord.Embed(title="✅ Unban", description=f"**{ban_entry.user}** a été débanni !", color=discord.Color.green())
            await ctx.send(embed=embed)
            return
    await ctx.send(f"❌ Utilisateur **{nom}** introuvable dans les bans.")

@bot.command()
@commands.has_permissions(manage_messages=True)
async def clear(ctx, nombre: int = None):
    if nombre is None or nombre <= 0:
        await ctx.send("❌ Usage : `!clear <nombre>`")
        return
    await ctx.channel.purge(limit=nombre + 1)
    msg = await ctx.send(f"🧹 **{nombre}** messages supprimés !")
    await msg.delete(delay=3)

@bot.command()
@commands.has_permissions(manage_messages=True)
async def slowmode(ctx, secondes: int = 0):
    await ctx.channel.edit(slowmode_delay=secondes)
    if secondes == 0:
        await ctx.send("✅ Slowmode désactivé !")
    else:
        await ctx.send(f"✅ Slowmode mis à **{secondes} secondes** !")
    await ctx.message.delete()

@bot.command()
@commands.has_permissions(manage_roles=True)
async def addrole(ctx, membre: discord.Member = None, *, role_name: str = None):
    if membre is None or role_name is None:
        await ctx.send("❌ Usage : `!addrole @membre <nom du rôle>`")
        return
    role = discord.utils.get(ctx.guild.roles, name=role_name)
    if not role:
        await ctx.send(f"❌ Le rôle **{role_name}** n'existe pas !")
        return
    await membre.add_roles(role)
    embed = discord.Embed(title="✅ Rôle ajouté", description=f"Le rôle **{role_name}** a été ajouté à **{membre.display_name}** !", color=discord.Color.green())
    await ctx.send(embed=embed)
    await ctx.message.delete()

@bot.command()
@commands.has_permissions(manage_roles=True)
async def removerole(ctx, membre: discord.Member = None, *, role_name: str = None):
    if membre is None or role_name is None:
        await ctx.send("❌ Usage : `!removerole @membre <nom du rôle>`")
        return
    role = discord.utils.get(ctx.guild.roles, name=role_name)
    if not role:
        await ctx.send(f"❌ Le rôle **{role_name}** n'existe pas !")
        return
    await membre.remove_roles(role)
    embed = discord.Embed(title="✅ Rôle retiré", description=f"Le rôle **{role_name}** a été retiré à **{membre.display_name}** !", color=discord.Color.orange())
    await ctx.send(embed=embed)
    await ctx.message.delete()

# ===== MENUS ROLES =====

class GenreSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Homme", emoji="♂️"),
            discord.SelectOption(label="Femme", emoji="♀️"),
            discord.SelectOption(label="Autre", emoji="🏳️‍🌈"),
        ]
        super().__init__(placeholder="Fais un choix...", options=options, custom_id="genre_select")

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
        super().__init__(placeholder="Fais un choix...", options=options, custom_id="age_select")

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
        super().__init__(placeholder="Fais un choix...", options=options, custom_id="situation_select")

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
        description=("Sélectionne tes rôles ci-dessous pour personnaliser ton profil.\n\n♂️ → **Genre**\n🎂 → **Âge**\n💍 → **Situation amoureuse**"),
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
            "**1️⃣ Respectez tout le monde**\nAucune insulte, discrimination ou harcèlement ne sera toléré.\n\n"
            "**2️⃣ Pas de spam**\nÉvitez les messages répétitifs ou les mentions abusives.\n\n"
            "**3️⃣ Pas de pub**\nAucun lien ou invitation Discord sans autorisation d'un admin.\n\n"
            "**4️⃣ Contenu approprié**\nPas de contenu NSFW en dehors des salons prévus.\n\n"
            "**5️⃣ Respectez les salons**\nChaque salon a un sujet, restez dans le thème.\n\n"
            "En restant sur ce serveur vous acceptez ces règles. ✅"
        ),
        color=discord.Color.purple()
    )
    await ctx.send(embed=embed)
    await ctx.message.delete()

# ===== PARTIE PERSO LOL =====

def build_embed():
    participants = load_participants()
    liste = "\n".join(f"**{i+1}.** {p['pseudo']}" for i, p in enumerate(participants)) if participants else "*Aucun participant pour l'instant*"
    embed = discord.Embed(
        title="✨ Partie Personnalisée League of Legends",
        description=(
            f"Une partie personnalisée est en cours d'organisation !\n\n"
            f"Clique sur **Je veux participer** pour rejoindre et entre ton pseudo LoL.\n\n"
            f"👥 **{len(participants)}/10** joueurs inscrits\n\n"
            f"**Liste des participants :**\n{liste}"
        ),
        color=discord.Color.blue()
    )
    return embed

class ParticipantModal(discord.ui.Modal, title="Rejoindre la partie"):
    pseudo = discord.ui.TextInput(label="Ton pseudo League of Legends", placeholder="Ex: Noctali123", required=True)

    async def on_submit(self, interaction: discord.Interaction):
        participants = load_participants()
        pseudo = self.pseudo.value
        if any(p["pseudo"].lower() == pseudo.lower() for p in participants):
            await interaction.response.send_message(f"❌ **{pseudo}** est déjà inscrit !", ephemeral=True)
            return
        if len(participants) >= 10:
            await interaction.response.send_message("❌ La partie est déjà complète !", ephemeral=True)
            return
        participants.append({"user_id": interaction.user.id, "pseudo": pseudo})
        save_participants(participants)
        await interaction.response.send_message(f"✅ **{pseudo}** a rejoint la partie !", ephemeral=True)
        try:
            channel = bot.get_channel(interaction.channel_id)
            async for msg in channel.history(limit=20):
                if msg.author == bot.user and msg.embeds and "Partie Personnalisée" in msg.embeds[0].title:
                    await msg.edit(embed=build_embed(), view=JoindreView())
                    break
        except:
            pass
        if len(load_participants()) == 10:
            await lancer_partie(interaction)

class RetirerSelect(discord.ui.Select):
    def __init__(self):
        participants = load_participants()
        options = [discord.SelectOption(label=p["pseudo"], value=p["pseudo"]) for p in participants]
        super().__init__(placeholder="Choisir un joueur à retirer...", options=options)

    async def callback(self, interaction: discord.Interaction):
        if not has_perm(interaction.user):
            await interaction.response.send_message("❌ T'as pas la permission !", ephemeral=True)
            return
        participants = load_participants()
        pseudo = self.values[0]
        participants = [p for p in participants if p["pseudo"] != pseudo]
        save_participants(participants)
        await interaction.response.send_message(f"🗑️ **{pseudo}** a été retiré !", ephemeral=True)
        try:
            channel = bot.get_channel(interaction.channel_id)
            async for msg in channel.history(limit=20):
                if msg.author == bot.user and msg.embeds and "Partie Personnalisée" in msg.embeds[0].title:
                    await msg.edit(embed=build_embed(), view=JoindreView())
                    break
        except:
            pass

class RetirerView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=60)
        self.add_item(RetirerSelect())

async def lancer_partie(interaction: discord.Interaction):
    participants = load_participants()
    random.shuffle(participants)
    equipe1 = participants[:5]
    equipe2 = participants[5:]

    def format_equipe(equipe):
        roles = ROLES_LOL.copy()
        random.shuffle(roles)
        return "\n".join(f"**{roles[i]}** → {p['pseudo']}" for i, p in enumerate(equipe))

    embed = discord.Embed(title="⚔️ Les équipes sont prêtes !", color=discord.Color.gold())
    embed.add_field(name="🔵 Équipe 1", value=format_equipe(equipe1), inline=True)
    embed.add_field(name="🔴 Équipe 2", value=format_equipe(equipe2), inline=True)
    await interaction.channel.send(embed=embed, view=RerollView(equipe1, equipe2))
    save_participants([])

class RerollView(discord.ui.View):
    def __init__(self, equipe1, equipe2):
        super().__init__(timeout=None)
        self.equipe1 = equipe1
        self.equipe2 = equipe2

    @discord.ui.button(label="🎲 Reroll les rôles", style=discord.ButtonStyle.blurple)
    async def reroll_roles(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not has_perm(interaction.user):
            await interaction.response.send_message("❌ T'as pas la permission !", ephemeral=True)
            return
        def format_equipe(equipe):
            roles = ROLES_LOL.copy()
            random.shuffle(roles)
            return "\n".join(f"**{roles[i]}** → {p['pseudo']}" for i, p in enumerate(equipe))
        embed = discord.Embed(title="⚔️ Rôles rerollés !", color=discord.Color.gold())
        embed.add_field(name="🔵 Équipe 1", value=format_equipe(self.equipe1), inline=True)
        embed.add_field(name="🔴 Équipe 2", value=format_equipe(self.equipe2), inline=True)
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="🔄 Reroll les équipes", style=discord.ButtonStyle.red)
    async def reroll_equipes(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not has_perm(interaction.user):
            await interaction.response.send_message("❌ T'as pas la permission !", ephemeral=True)
            return
        tous = self.equipe1 + self.equipe2
        random.shuffle(tous)
        self.equipe1 = tous[:5]
        self.equipe2 = tous[5:]
        def format_equipe(equipe):
            roles = ROLES_LOL.copy()
            random.shuffle(roles)
            return "\n".join(f"**{roles[i]}** → {p['pseudo']}" for i, p in enumerate(equipe))
        embed = discord.Embed(title="⚔️ Équipes rerollées !", color=discord.Color.gold())
        embed.add_field(name="🔵 Équipe 1", value=format_equipe(self.equipe1), inline=True)
        embed.add_field(name="🔴 Équipe 2", value=format_equipe(self.equipe2), inline=True)
        await interaction.response.edit_message(embed=embed, view=self)

class JoindreView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="⚔️ Je veux participer !", style=discord.ButtonStyle.green)
    async def rejoindre(self, interaction: discord.Interaction, button: discord.ui.Button):
        if len(load_participants()) >= 10:
            await interaction.response.send_message("❌ La partie est déjà complète !", ephemeral=True)
            return
        await interaction.response.send_modal(ParticipantModal())

    @discord.ui.button(label="🚪 Se désinscrire", style=discord.ButtonStyle.grey)
    async def desinscrire(self, interaction: discord.Interaction, button: discord.ui.Button):
        participants = load_participants()
        if not any(p["user_id"] == interaction.user.id for p in participants):
            await interaction.response.send_message("❌ Tu n'es pas inscrit !", ephemeral=True)
            return
        participants = [p for p in participants if p["user_id"] != interaction.user.id]
        save_participants(participants)
        await interaction.response.send_message("✅ Tu as été désinscrit !", ephemeral=True)
        try:
            channel = bot.get_channel(interaction.channel_id)
            async for msg in channel.history(limit=20):
                if msg.author == bot.user and msg.embeds and "Partie Personnalisée" in msg.embeds[0].title:
                    await msg.edit(embed=build_embed(), view=JoindreView())
                    break
        except:
            pass

    @discord.ui.button(label="🗑️ Reset la liste", style=discord.ButtonStyle.red)
    async def reset_liste(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not has_perm(interaction.user):
            await interaction.response.send_message("❌ T'as pas la permission !", ephemeral=True)
            return
        save_participants([])
        await interaction.response.send_message("✅ Liste réinitialisée !", ephemeral=True)
        try:
            channel = bot.get_channel(interaction.channel_id)
            async for msg in channel.history(limit=20):
                if msg.author == bot.user and msg.embeds and "Partie Personnalisée" in msg.embeds[0].title:
                    await msg.edit(embed=build_embed(), view=JoindreView())
                    break
        except:
            pass

@bot.command()
@commands.has_permissions(administrator=True)
async def partiepersso(ctx):
    save_participants([])
    await ctx.send(embed=build_embed(), view=JoindreView())
    await ctx.message.delete()

@bot.command()
@commands.has_permissions(administrator=True)
async def retirer(ctx):
    participants = load_participants()
    if not participants:
        await ctx.send("❌ Aucun participant à retirer !")
        return
    await ctx.send("🗑️ Quel joueur veux-tu retirer ?", view=RetirerView())
    await ctx.message.delete()

# ===== COINFLIP =====

class CoinflipView(discord.ui.View):
    def __init__(self, user, mise):
        super().__init__(timeout=30)
        self.user = user
        self.mise = mise

    @discord.ui.button(label="🪙 Pile", style=discord.ButtonStyle.blurple)
    async def pile(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user.id:
            await interaction.response.send_message("❌ C'est pas ton jeu !", ephemeral=True)
            return
        await self.jouer(interaction, "pile")

    @discord.ui.button(label="🪙 Face", style=discord.ButtonStyle.blurple)
    async def face(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user.id:
            await interaction.response.send_message("❌ C'est pas ton jeu !", ephemeral=True)
            return
        await self.jouer(interaction, "face")

    async def jouer(self, interaction, choix):
        resultat = random.choice(["pile", "face"])
        balance = get_balance(interaction.user.id)
        if choix == resultat:
            balance += self.mise
            set_balance(interaction.user.id, balance)
            embed = discord.Embed(title="🪙 Coinflip — Gagné !", description=f"C'était **{resultat}** !\n✅ Tu gagnes **{self.mise}** 💰\nSolde : **{balance}** 💰", color=discord.Color.green())
        else:
            balance -= self.mise
            set_balance(interaction.user.id, balance)
            embed = discord.Embed(title="🪙 Coinflip — Perdu !", description=f"C'était **{resultat}** !\n❌ Tu perds **{self.mise}** 💰\nSolde : **{balance}** 💰", color=discord.Color.red())
        await interaction.response.edit_message(embed=embed, view=None)

@bot.command()
async def coinflip(ctx, mise: int = None):
    if mise is None or mise <= 0:
        await ctx.send("❌ Usage : `!coinflip <mise>`")
        return
    balance = get_balance(ctx.author.id)
    if mise > balance:
        await ctx.send(f"❌ T'as pas assez de pièces ! Solde : **{balance}** 💰")
        return
    embed = discord.Embed(title="🪙 Coinflip", description=f"Mise : **{mise}** 💰\nChoisis **Pile** ou **Face** !", color=discord.Color.gold())
    await ctx.send(embed=embed, view=CoinflipView(ctx.author, mise))

# ===== SLOTS =====

SYMBOLES = ["🍒", "🍋", "🍊", "⭐", "💎", "7️⃣"]
MULTIPLICATEURS = {"🍒": 2, "🍋": 2, "🍊": 3, "⭐": 5, "💎": 10, "7️⃣": 20}

@bot.command()
async def slots(ctx, mise: int = None):
    if mise is None or mise <= 0:
        await ctx.send("❌ Usage : `!slots <mise>`")
        return
    balance = get_balance(ctx.author.id)
    if mise > balance:
        await ctx.send(f"❌ T'as pas assez de pièces ! Solde : **{balance}** 💰")
        return
    rouleaux = [random.choice(SYMBOLES) for _ in range(3)]
    s1, s2, s3 = rouleaux
    if s1 == s2 == s3:
        gain = mise * MULTIPLICATEURS[s1]
        balance += gain
        resultat = f"🎉 JACKPOT ! Tu gagnes **{gain}** 💰 (x{MULTIPLICATEURS[s1]})"
        color = discord.Color.gold()
    elif s1 == s2 or s2 == s3 or s1 == s3:
        gain = mise
        balance += gain
        resultat = f"✅ Deux identiques ! Tu gagnes **{gain}** 💰"
        color = discord.Color.green()
    else:
        balance -= mise
        resultat = f"❌ Perdu ! Tu perds **{mise}** 💰"
        color = discord.Color.red()
    set_balance(ctx.author.id, balance)
    embed = discord.Embed(title="🎰 Slots", description=f"[ {s1} | {s2} | {s3} ]\n\n{resultat}\nSolde : **{balance}** 💰", color=color)
    await ctx.send(embed=embed)

# ===== DAILY =====

@bot.command()
async def daily(ctx):
    last = get_last_daily(ctx.author.id)
    now = datetime.now()
    if last:
        last_date = datetime.fromisoformat(last)
        if now - last_date < timedelta(hours=24):
            reste = timedelta(hours=24) - (now - last_date)
            heures = int(reste.seconds // 3600)
            minutes = int((reste.seconds % 3600) // 60)
            await ctx.send(f"⏰ T'as déjà pris ton bonus ! Reviens dans **{heures}h {minutes}min**")
            return
    bonus = 500
    balance = get_balance(ctx.author.id) + bonus
    set_balance(ctx.author.id, balance)
    set_last_daily(ctx.author.id, now.isoformat())
    embed = discord.Embed(title="🎁 Bonus quotidien !", description=f"Tu reçois **{bonus}** 💰 !\nSolde : **{balance}** 💰", color=discord.Color.green())
    await ctx.send(embed=embed)

# ===== SOLDE =====

@bot.command()
async def solde(ctx):
    balance = get_balance(ctx.author.id)
    embed = discord.Embed(title=f"💰 Solde de {ctx.author.display_name}", description=f"**{balance}** 💰", color=discord.Color.gold())
    await ctx.send(embed=embed)

# ===== VOLER =====

@bot.command()
async def voler(ctx, membre: discord.Member = None):
    if membre is None:
        await ctx.send("❌ Usage : `!voler @membre`")
        return
    if membre.id == ctx.author.id:
        await ctx.send("❌ Tu peux pas te voler toi-même !")
        return
    victime_balance = get_balance(membre.id)
    if victime_balance < 100:
        await ctx.send(f"❌ **{membre.display_name}** est trop pauvre !")
        return
    succes = random.random() < 0.4
    if succes:
        vol = random.randint(50, min(300, victime_balance))
        set_balance(membre.id, victime_balance - vol)
        set_balance(ctx.author.id, get_balance(ctx.author.id) + vol)
        embed = discord.Embed(title="💸 Vol réussi !", description=f"Tu as volé **{vol}** 💰 à **{membre.display_name}** !", color=discord.Color.green())
    else:
        amende = random.randint(50, 200)
        set_balance(ctx.author.id, max(0, get_balance(ctx.author.id) - amende))
        embed = discord.Embed(title="🚨 Vol raté !", description=f"Tu t'es fait attraper ! Tu paies **{amende}** 💰 d'amende", color=discord.Color.red())
    await ctx.send(embed=embed)

# ===== CLASSEMENT =====

@bot.command()
async def classement(ctx):
    data = load_economy()
    if not data:
        await ctx.send("❌ Personne n'a encore de pièces !")
        return
    sorted_data = sorted(data.items(), key=lambda x: x[1].get("balance", 0), reverse=True)[:10]
    medals = ["🥇", "🥈", "🥉"] + ["🏅"] * 7
    description = ""
    for i, (user_id, info) in enumerate(sorted_data):
        try:
            user = await bot.fetch_user(int(user_id))
            name = user.display_name
        except:
            name = "Utilisateur inconnu"
        description += f"{medals[i]} **{name}** — {info.get('balance', 0)} 💰\n"
    embed = discord.Embed(title="🏆 Classement des richesses", description=description, color=discord.Color.gold())
    await ctx.send(embed=embed)

# ===== LANCEMENT =====

@bot.event
async def on_ready():
    bot.add_view(SetupView())
    bot.add_view(JoindreView())
    rappel_casino.start()
    rappel_game.start()
    print(f"✅ {bot.user} est en ligne !")

WELCOME_CHANNEL_ID = 1490028436805259344

@bot.event
async def on_member_join(member):
    channel = bot.get_channel(WELCOME_CHANNEL_ID)
    if channel:
        embed = discord.Embed(
            title="🎉 Nouveau membre !",
            description=f"**{member.name}** a rejoint le serveur !\n\ncc {member.mention} ça va ?",
            color=discord.Color.green()
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        await channel.send(embed=embed)

@rappel_casino.before_loop

@rappel_casino.before_loop
async def before_casino():
    await bot.wait_until_ready()

@rappel_game.before_loop
async def before_game():
    await bot.wait_until_ready()

bot.run(os.environ.get("TOKEN"))
