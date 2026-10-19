import os
import requests
import discord
from discord import app_commands
from discord.ext import commands
from flask import Flask
from threading import Thread

# ── Render Keep-Alive ──
app = Flask('')

@app.route('/')
def home():
    return "Bot is running 24/7!"

def run():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()

# ── Bot Configuration ──
TOKEN = os.getenv("DISCORD_TOKEN")

# Sirf ye 3 Users bot use kar payenge
ALLOWED_USER_IDS = [
    1525179499602509977,  # Main Admin (PERSISTX)
    1306569043402031116,
    1421363542912929852
]

API_URL    = "https://auth.terminalx999.online/api_admin.php"
API_KEY    = "TX999_API_0cd981c565dcd81963149ffe8f72b322"
APP_ID     = "9f087d585fbd666572fc24b7"
APP_SECRET = "4ac5c8b945cbf8c75e15d771704616356c15edc051cbad6c12c92376da1dced7"

# Target Package for UID Bypass
PACKAGE_ID   = "cb921031dc43197e8ccb6828"
PACKAGE_NAME = "UID BYPASS"

DENIED_MESSAGE = "⛔ Access Denied: For use contact Super Admin PERSISTX !"

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

# ── Only User Security Check (Channel / Server Check Removed) ──
def is_authorized(interaction: discord.Interaction) -> bool:
    if interaction.user.id not in ALLOWED_USER_IDS:
        return False
    return True

# ── Auto Sync Commands Globally & All Joined Guilds ──
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name} (ID: {bot.user.id})")
    try:
        # Har server par commands instant sync hongi
        for guild in bot.guilds:
            bot.tree.copy_global_to(guild=guild)
            synced = await bot.tree.sync(guild=guild)
            print(f"Synced {len(synced)} commands to server: {guild.name} ({guild.id})")
        
        # Global sync fallback
        await bot.tree.sync()
        print("Global command sync completed!")
    except Exception as e:
        print(f"Failed to sync commands: {e}")

# ── Helper for Key Action Requests ──
def request_key_action(action: str, key: str):
    payload = {
        "api_key": API_KEY,
        "action": action,
        "key": key.strip(),
        "app_id": APP_ID,
        "app_secret": APP_SECRET
    }
    resp = requests.post(API_URL, json=payload, timeout=10)
    return resp.json()

# ── Persistent Action Buttons View Class ──
class KeyManagementView(discord.ui.View):
    def __init__(self, key: str):
        super().__init__(timeout=None)
        self.key = key

    @discord.ui.button(label="Reset HWID", style=discord.ButtonStyle.primary, emoji="🔄")
    async def reset_hwid_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not is_authorized(interaction):
            await interaction.response.send_message(DENIED_MESSAGE, ephemeral=True)
            return

        await interaction.response.defer(ephemeral=True)
        try:
            res = request_key_action("reset_hwid", self.key)
            if res.get("success"):
                await interaction.followup.send(f"✓ **HWID Reset Done** for key: `{self.key}`", ephemeral=True)
            else:
                await interaction.followup.send(f"❌ Failed: {res.get('message', 'Unknown error')}", ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"⚠️ Error: {str(e)}", ephemeral=True)

    @discord.ui.button(label="Ban", style=discord.ButtonStyle.danger, emoji="🚫")
    async def ban_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not is_authorized(interaction):
            await interaction.response.send_message(DENIED_MESSAGE, ephemeral=True)
            return

        await interaction.response.defer(ephemeral=True)
        try:
            res = request_key_action("ban_key", self.key)
            if res.get("success"):
                await interaction.followup.send(f"🚫 **Key Banned**: `{self.key}`", ephemeral=True)
            else:
                await interaction.followup.send(f"❌ Failed: {res.get('message', 'Unknown error')}", ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"⚠️ Error: {str(e)}", ephemeral=True)

    @discord.ui.button(label="Unban", style=discord.ButtonStyle.success, emoji="✅")
    async def unban_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not is_authorized(interaction):
            await interaction.response.send_message(DENIED_MESSAGE, ephemeral=True)
            return

        await interaction.response.defer(ephemeral=True)
        try:
            res = request_key_action("unban_key", self.key)
            if res.get("success"):
                await interaction.followup.send(f"✅ **Key Unbanned**: `{self.key}`", ephemeral=True)
            else:
                await interaction.followup.send(f"❌ Failed: {res.get('message', 'Unknown error')}", ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"⚠️ Error: {str(e)}", ephemeral=True)

    @discord.ui.button(label="Delete", style=discord.ButtonStyle.secondary, emoji="🗑️")
    async def delete_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not is_authorized(interaction):
            await interaction.response.send_message(DENIED_MESSAGE, ephemeral=True)
            return

        await interaction.response.defer(ephemeral=True)
        try:
            res = request_key_action("delete_key", self.key)
            if res.get("success"):
                await interaction.followup.send(f"🗑️ **Key Deleted**: `{self.key}`", ephemeral=True)
            else:
                await interaction.followup.send(f"❌ Failed: {res.get('message', 'Unknown error')}", ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"⚠️ Error: {str(e)}", ephemeral=True)

# ── 1. License Key Generation Command (/genuid) ──
@bot.tree.command(name="genuid", description="Generate UID Bypass license keys.")
@app_commands.describe(
    days="Number of validity days (0 = lifetime)",
    count="Number of keys to generate (max 100)"
)
async def genuid(interaction: discord.Interaction, days: int = 30, count: int = 1):
    if not is_authorized(interaction):
        await interaction.response.send_message(DENIED_MESSAGE, ephemeral=True)
        return

    await interaction.response.defer(ephemeral=False)
    
    if count < 1:
        count = 1

    payload = {
        "api_key": API_KEY, 
        "action": "generate_key", 
        "app_id": APP_ID,
        "app_secret": APP_SECRET,
        "package_id": PACKAGE_ID, 
        "days": days,
        "amount": count,
        "count": count
    }
    
    try:
        resp = requests.post(API_URL, json=payload, timeout=10)
        data = resp.json()
        
        keys = []
        if isinstance(data.get("data"), dict):
            keys = data.get("data", {}).get("keys", [])
        elif isinstance(data.get("keys"), list):
            keys = data.get("keys")
        elif isinstance(data.get("key"), str):
            keys = [data.get("key")]
            
        if data.get("success") or len(keys) > 0:
            if len(keys) == 0:
                msg = data.get("message", "Panel returned 0 keys.")
                await interaction.followup.send(f"❌ Key generation failed: {msg}", ephemeral=True)
                return

            dur = "Lifetime" if days == 0 else f"{days} Days"
            
            embed = discord.Embed(
                title="🔑 UID Bypass License Key Generated", 
                color=0x22c55e
            )
            embed.add_field(name="Package Name", value=f"**{PACKAGE_NAME}**", inline=True)
            embed.add_field(name="Duration", value=dur, inline=True)
            embed.add_field(name="Count", value=str(len(keys)), inline=True)
            embed.add_field(name="Keys", value="\n".join([f"`{k}`" for k in keys]), inline=False)
            embed.set_footer(text="Manage key actions using buttons below or dedicated slash commands.")
            
            if len(keys) == 1:
                view = KeyManagementView(key=keys[0])
                await interaction.followup.send(embed=embed, view=view)
            else:
                await interaction.followup.send(embed=embed)
        else:
            msg = data.get("message", "Key generation failed.")
            await interaction.followup.send(f"❌ {msg}", ephemeral=True)
    except Exception as e:
        await interaction.followup.send(f"⚠️ Error: {str(e)}", ephemeral=True)

# ── Standalone Slash Commands for Key Management ──

@bot.tree.command(name="resethwid", description="Reset HWID binding for any license key.")
@app_commands.describe(key="Enter the full license key to reset HWID")
async def resethwid(interaction: discord.Interaction, key: str):
    if not is_authorized(interaction):
        await interaction.response.send_message(DENIED_MESSAGE, ephemeral=True)
        return

    await interaction.response.defer(ephemeral=True)
    try:
        res = request_key_action("reset_hwid", key)
        if res.get("success"):
            await interaction.followup.send(f"🔄 **HWID Reset Done** for key: `{key.strip()}`", ephemeral=True)
        else:
            await interaction.followup.send(f"❌ Failed: {res.get('message', 'Action failed')}", ephemeral=True)
    except Exception as e:
        await interaction.followup.send(f"⚠️ Error: {str(e)}", ephemeral=True)

@bot.tree.command(name="bankey", description="Ban a specific license key.")
@app_commands.describe(key="Enter the full license key to ban")
async def bankey(interaction: discord.Interaction, key: str):
    if not is_authorized(interaction):
        await interaction.response.send_message(DENIED_MESSAGE, ephemeral=True)
        return

    await interaction.response.defer(ephemeral=True)
    try:
        res = request_key_action("ban_key", key)
        if res.get("success"):
            await interaction.followup.send(f"🚫 **Key Banned Successfully**: `{key.strip()}`", ephemeral=True)
        else:
            await interaction.followup.send(f"❌ Failed: {res.get('message', 'Action failed')}", ephemeral=True)
    except Exception as e:
        await interaction.followup.send(f"⚠️ Error: {str(e)}", ephemeral=True)

@bot.tree.command(name="unbankey", description="Unban a previously banned license key.")
@app_commands.describe(key="Enter the full license key to unban")
async def unbankey(interaction: discord.Interaction, key: str):
    if not is_authorized(interaction):
        await interaction.response.send_message(DENIED_MESSAGE, ephemeral=True)
        return

    await interaction.response.defer(ephemeral=True)
    try:
        res = request_key_action("unban_key", key)
        if res.get("success"):
            await interaction.followup.send(f"✅ **Key Unbanned Successfully**: `{key.strip()}`", ephemeral=True)
        else:
            await interaction.followup.send(f"❌ Failed: {res.get('message', 'Action failed')}", ephemeral=True)
    except Exception as e:
        await interaction.followup.send(f"⚠️ Error: {str(e)}", ephemeral=True)

@bot.tree.command(name="delkey", description="Permanently delete a license key from the database.")
@app_commands.describe(key="Enter the full license key to delete")
async def delkey(interaction: discord.Interaction, key: str):
    if not is_authorized(interaction):
        await interaction.response.send_message(DENIED_MESSAGE, ephemeral=True)
        return

    await interaction.response.defer(ephemeral=True)
    try:
        res = request_key_action("delete_key", key)
        if res.get("success"):
            await interaction.followup.send(f"🗑️ **Key Deleted Successfully**: `{key.strip()}`", ephemeral=True)
        else:
            await interaction.followup.send(f"❌ Failed: {res.get('message', 'Action failed')}", ephemeral=True)
    except Exception as e:
        await interaction.followup.send(f"⚠️ Error: {str(e)}", ephemeral=True)

# ── UID Whitelist Commands ──

@bot.tree.command(name="whitelist_uid", description="Whitelist a Free Fire UID on Emulator Bypass.")
@app_commands.choices(region=[
    app_commands.Choice(name="IN - India", value="IND"),
    app_commands.Choice(name="BD - Bangladesh", value="BD"),
    app_commands.Choice(name="PK - Pakistan", value="PK"),
    app_commands.Choice(name="SG - Singapore", value="SG"),
    app_commands.Choice(name="ID - Indonesia", value="ID"),
    app_commands.Choice(name="BR - Brazil", value="BR"),
    app_commands.Choice(name="US - North America", value="NA")
])
@app_commands.describe(
    uid="Player Free Fire UID",
    region="Select game server region",
    nickname="Player in-game nickname (optional)",
    days="Whitelist duration (0 = Lifetime)",
    note="Buyer reference or note"
)
async def whitelist_uid(
    interaction: discord.Interaction, 
    uid: str, 
    region: app_commands.Choice[str], 
    days: int = 30, 
    nickname: str = "Player", 
    note: str = "Discord Whitelist"
):
    if not is_authorized(interaction):
        await interaction.response.send_message(DENIED_MESSAGE, ephemeral=True)
        return

    await interaction.response.defer(ephemeral=False)
    payload = {
        "api_key": API_KEY,
        "action": "whitelist_uid",
        "app_id": APP_ID,
        "app_secret": APP_SECRET,
        "uid": uid.strip(),
        "region": region.value,
        "nickname": nickname.strip(),
        "days": days,
        "note": note
    }
    try:
        resp = requests.post(API_URL, json=payload, timeout=10)
        data = resp.json()
        if data.get("success"):
            dur = "Lifetime" if days == 0 else f"{days} Days"
            embed = discord.Embed(title="✅ UID Whitelisted Successfully", color=0x22c55e)
            embed.add_field(name="Free Fire UID", value=f"`{uid.strip()}`", inline=True)
            embed.add_field(name="Nickname", value=f"**{nickname}**", inline=True)
            embed.add_field(name="Region", value=f"{region.name}", inline=True)
            embed.add_field(name="Duration", value=dur, inline=True)
            embed.add_field(name="Note", value=note, inline=True)
            await interaction.followup.send(embed=embed)
        else:
            await interaction.followup.send(f"❌ Failed to Whitelist: {data.get('message', 'API returned error')}", ephemeral=True)
    except Exception as e:
        await interaction.followup.send(f"⚠️ Error: {str(e)}", ephemeral=True)

@bot.tree.command(name="del_uid", description="Remove a UID from whitelist.")
@app_commands.describe(uid="Free Fire UID to remove")
async def del_uid(interaction: discord.Interaction, uid: str):
    if not is_authorized(interaction):
        await interaction.response.send_message(DENIED_MESSAGE, ephemeral=True)
        return

    await interaction.response.defer(ephemeral=True)
    try:
        payload = {
            "api_key": API_KEY,
            "action": "delete_uid",
            "app_id": APP_ID,
            "app_secret": APP_SECRET,
            "uid": uid.strip()
        }
        resp = requests.post(API_URL, json=payload, timeout=10)
        data = resp.json()
        if data.get("success"):
            await interaction.followup.send(f"🗑️ UID `{uid.strip()}` has been removed from whitelist.", ephemeral=True)
        else:
            await interaction.followup.send(f"❌ Failed: {data.get('message', 'Action failed')}", ephemeral=True)
    except Exception as e:
        await interaction.followup.send(f"⚠️ Error: {str(e)}", ephemeral=True)

keep_alive()

if TOKEN:
    bot.run(TOKEN)
else:
    print("❌ ERROR: DISCORD_TOKEN Environment Variable missing!")
