import discord
from discord.ext import commands
import random
import os
import json
from datetime import datetime, timedelta

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

ROLES_LOL = ["Top", "Jungle", "Mid", "ADC", "Support"]

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
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ Réservé aux admins !", ephemeral=True)
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
    msg = await ctx.send(embed=build_embed(), view=JoindreView())
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
    print(f"✅ {bot.user} est en ligne !")

bot.run(os.environ.get("TOKEN"))
