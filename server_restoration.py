import discord
from discord.ext import commands
import asyncio
import json
import os

intents = discord.Intents.default()
intents.guilds = True
intents.guild_messages = True
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

ROLE_NAMES = [
    "Founder", "Owner", "Override", "Co-Owner", "Server Manager", "Staff Manager", "Technical Manager",
    "Community Manager", "━━━━━━━━━━━━━━━━", "Artificial Intelligence",
    "━━━━━━━━━━━━━━━━", "Senior Moderator", "Moderator",
    "Trial Moderator", "Server Staff", "Leave of Absence", "━━━━━━━━━━━━━━━━",
    "Notable Member", "Affiliate", "Partner", "Designer of The Week", "━━━━━━━━━━━━━━━━", 
    "DOTW Cooldown", "DOTW Banned", "Hiring Banned", "Report Banned", "Ticket Banned",
    "━━━━━━━━━━━━━━━━",  "Former Staff", "Community Member", "Staff Blacklist",
    "━━━━━━━━━━━━━━━━", "Unverified", "Archive Access", 
]

WHITE_ROLES = ["━━━━━━━━━━━━━━━━", "Artificial Intelligence"]
WHITE = discord.Color(0xfffffe)

PERMISSION_PRESETS = {
    "Administrator": discord.Permissions(administrator=True),
    
    "Manager": discord.Permissions(
        view_channel=True,
        send_messages=True,
        use_application_commands=True,
        read_message_history=True,
        connect=True,
        speak=True,
        kick_members=True,
        change_nickname=True,
        manage_nicknames=True,
        attach_files=True,
        manage_messages=True,
        mute_members=True,
        move_members=True,
        ban_members=True
    ),
    
    "Server Staff": discord.Permissions(
        view_channel=True,
        send_messages=True,
        use_application_commands=True,
        read_message_history=True,
        connect=True,
        speak=True,
        kick_members=True,
        change_nickname=True,
        manage_nicknames=True,
        attach_files=True,
        manage_messages=True,
        mute_members=True,
        move_members=True
    ),
    
    "Community Member": discord.Permissions(
        view_channel=True,
        send_messages=True,
        use_application_commands=True,
        read_message_history=True,
        connect=True,
        speak=True
    ),
    
    "STAFF": discord.Permissions(
        view_channel=True,
        send_messages=True,
        manage_messages=True,
        kick_members=True,
        ban_members=True
    ),
    
    "Cosmetic": discord.Permissions.none(),
    "None": discord.Permissions.none(),
    "Neutral": discord.Permissions.none(),
    "Unverified": discord.Permissions.none(),
}

ROLE_PERMISSION_MAP = {
    "Founder": "Administrator",
    "Owner": "Administrator",
    "Override": "Administrator",
    "Co-Owner": "Administrator",
    
    "Server Manager": "Manager",
    "Staff Manager": "Manager",
    "Technical Manager": "Manager",
    "Community Manager": "Manager",

    "━━━━━━━━━━━━━━━━": "Neutral",

    "Artificial Intelligence": "Administrator",

    "Senior Moderator": "Server Staff",
    "Moderator": "Server Staff",
    "Trial Moderator": "Server Staff",
    "Server Staff": "Server Staff",

    "Leave of Absence": "Server Staff",

    "Notable Member": "Community Member",
    "Affiliate": "Community Member",
    "Partner": "Community Member",
    "Designer of The Week": "Community Member",

    "DOTW Cooldown": "Neutral",
    "DOTW Banned": "Neutral",
    "Hiring Banned": "Neutral",
    "Report Banned": "Neutral",
    "Ticket Banned": "Neutral",

    "Former Staff": "Community Member",  

    "Community Member": "Community Member",

    "Staff Blacklist": "Neutral",

    "Unverified": "Neutral",
    "Archive Access": "Community Member",
}

HOISTED_ROLES = [
    "Owner",
    "Co-Owner",
    "Server Manager",
    "Server Staff",
    "Notable Member",
    "Affiliate",
    "Partner",
    "Designer of The Week",
    "Community Member"
]

BLUE_SHADES = [
    0x0068FF, 0x1E90FF, 0x4169E1, 0x6392d9, 0x6495ED, 0x6495ED, 0x4682B4, 0x87CEFA, 0x87CEEB,
    0x00BFFF, 0xADD8E6, 0xB0C4DE, 0x7B68EE, 0x6A5ACD, 0x708090, 0x778899, 0x1E3F66,
    0x274472, 0x3B5998, 0x4A6EB1, 0x2B65EC, 0x38ACEC, 0x56A5EC, 0x6D9BF1, 0x7EC8E3,
    0x82CAFA, 0x6593F5, 0x367588, 0x4F97A3, 0x5082B2, 0x34568B, 0x2F5A78, 0x123456,
    0x0A2342, 0x3A4D63, 0x41627E, 0x1A2B3C, 0x2C3E50, 0x3D5A80, 0x4E729E, 0x5A9BD5,
    0x3E8EDE, 0x225EAA, 0x2D4C88, 0x204D92, 0x2962FF, 0x3366CC, 0x3A75C4, 0x4B89AC
]

MOD_CHANNELS_TO_SKIP = [1400654884822454314, 1400654884210212924]
                        
@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")

BACKUP_FILE = "backup.json"

def serialize_overwrites(overwrites):
    serialized = {}
    for target, perms in overwrites.items():
        if isinstance(target, discord.Role):
            allow, deny = perms.pair()
            serialized[str(target.id)] = [allow.value, deny.value]
    return serialized

def deserialize_overwrites(serialized, guild):
    overwrites = {}
    for role_id, (allow_val, deny_val) in serialized.items():
        role = guild.get_role(int(role_id))
        if role:
            allow = discord.Permissions(allow_val)
            deny = discord.Permissions(deny_val)
            overwrites[role] = discord.PermissionOverwrite.from_pair(allow, deny)
    return overwrites

@bot.command()
@commands.has_permissions(administrator=True)
async def backup_server(ctx):
    guild = ctx.guild
    backup_data = {"categories": [], "channels": []}

    for category in sorted(guild.categories, key=lambda c: c.position):
        backup_data["categories"].append({
            "name": category.name,
            "position": category.position,
            "permissions": serialize_overwrites(category.overwrites)
        })

    for channel in sorted(guild.channels, key=lambda c: c.position):
        if isinstance(channel, discord.CategoryChannel):
            continue
        if channel.id in MOD_CHANNELS_TO_SKIP:
            continue
        backup_data["channels"].append({
            "id": channel.id,
            "name": channel.name,
            "type": str(channel.type),
            "position": channel.position,
            "category": channel.category.name if channel.category else None,
            "permissions": serialize_overwrites(channel.overwrites)
        })

    try:
        with open(BACKUP_FILE, "w", encoding="utf-8") as f:
            json.dump(backup_data, f, indent=4)
        await ctx.send("📦 Server structure has been backed up to `backup.json`.")
    except Exception as e:
        await ctx.send(f"❌ Failed to write backup file: `{e}`")

@bot.command()
@commands.has_permissions(administrator=True)
async def restore_server(ctx):
    if not os.path.exists(BACKUP_FILE):
        await ctx.send("⚠️ No `backup.json` file found. Run `!backup_server` first.")
        return

    confirm_msg = await ctx.send("⚠️ Are you **sure** you want to restore the server structure? This will delete all current channels.\nReact with ✅ to confirm within 30 seconds.")
    await confirm_msg.add_reaction("✅")

    def check(reaction, user):
        return user == ctx.author and str(reaction.emoji) == "✅" and reaction.message.id == confirm_msg.id

    try:
        await bot.wait_for("reaction_add", timeout=30.0, check=check)
    except asyncio.TimeoutError:
        await ctx.send("❌ Restore cancelled.")
        return

    try:
        with open(BACKUP_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        await ctx.send(f"❌ Failed to read backup file: `{e}`")
        return

    for channel in ctx.guild.channels:
        try:
            await channel.delete()
            await asyncio.sleep(2)
        except Exception as e:
            print(f"❌ Could not delete {channel.name}: {e}")

    category_map = {}

    for cat_data in sorted(data["categories"], key=lambda x: x["position"]):
        overwrites = deserialize_overwrites(cat_data["permissions"], ctx.guild)
        new_cat = await ctx.guild.create_category(
            name=cat_data["name"],
            overwrites=overwrites
        )
        await asyncio.sleep(2)
        await new_cat.edit(position=cat_data["position"])
        category_map[cat_data["name"]] = new_cat

    for ch_data in sorted(data["channels"], key=lambda x: x["position"]):
        if int(ch_data.get("id", 0)) in MOD_CHANNELS_TO_SKIP:
            continue
        overwrites = deserialize_overwrites(ch_data["permissions"], ctx.guild)
        category = category_map.get(ch_data["category"])
        ch_type = ch_data["type"]

        try:
            if ch_type == "text":
                new_ch = await ctx.guild.create_text_channel(
                    name=ch_data["name"],
                    overwrites=overwrites,
                    category=category
                )
            elif ch_type == "voice":
                new_ch = await ctx.guild.create_voice_channel(
                    name=ch_data["name"],
                    overwrites=overwrites,
                    category=category
                )
            elif ch_type == "forum":
                new_ch = await ctx.guild.create_forum_channel(
                    name=ch_data["name"],
                    overwrites=overwrites,
                    category=category
                )
            else:
                continue
                
            await new_ch.edit(position=ch_data["position"])
            await asyncio.sleep(2)
        except Exception as e:
            print(f"⚠️ Failed to create channel `{ch_data['name']}`: {e}")

    try:
        await ctx.author.send("✅ Server structure has been restored from `backup.json`.")
    except discord.Forbidden:
        print("⚠️ Could not DM the user after restoration.")


@bot.command()
@commands.has_permissions(manage_roles=True)
async def create_roles(ctx):
    if not ctx.guild:
        await ctx.send("❌ This command must be used in a server.")
        return

    await ctx.defer()

    guild = ctx.guild
    bot_member = guild.me
    bot_top_role = bot_member.top_role

    # Step 1: Delete roles
    deleted = 0
    for role in guild.roles:
        if role.name != "@everyone" and role < bot_top_role:
            try:
                await role.delete()
                print(f"✅ Deleted role: `{role.name}`")
                await ctx.send(f"")
                deleted += 1
            except discord.Forbidden:
                await ctx.send(f"❌ Cannot delete role `{role.name}`")
            except discord.HTTPException:
                pass

    print(f"🧹 Deleted all roles.")
    await ctx.send(f"🧹 Deleted {deleted} roles.")

    # Step 2: Create new roles
    created = 0
    blue_index = 0
    for role_name in ROLE_NAMES:
        preset_key = ROLE_PERMISSION_MAP.get(role_name, "Neutral")
        permissions = PERMISSION_PRESETS[preset_key]
        color = WHITE if role_name in WHITE_ROLES else discord.Color(BLUE_SHADES[blue_index % len(BLUE_SHADES)])
        
        if role_name not in WHITE_ROLES:
            blue_index += 1

        hoist = role_name in HOISTED_ROLES
    
        try:
            await guild.create_role(name=role_name, color=color, permissions=permissions, hoist=hoist)
            print(f"✅ Created role: `{role_name}` with preset `{preset_key}`")
            created += 1
        except Exception as e:
            print(f"⚠️ Failed to create `{role_name}`: {e}")

    await ctx.send(f"✅ Created {created} roles.")
    print(f"✅ Created {created} roles.")

    # Step 3: Assign AI role to all bots
    ai_role = discord.utils.get(guild.roles, name="Artificial Intelligence")
    if ai_role:
        assigned = 0
        for member in guild.members:
            if member.bot:
                try:
                    await member.add_roles(ai_role)
                    assigned += 1
                except:
                    pass
        await ctx.send(f"🤖 Assigned 'Artificial Intelligence' role to {assigned} bots.")
    else:
        await ctx.send("❗ 'Artificial Intelligence' role not found after creation.")
    
        
    # Step 4: Assign Community Member role to all human members
    community_role = discord.utils.get(guild.roles, name="Community Member")
    if community_role:
        assigned = 0
        for member in guild.members:
            if not member.bot:
                try:
                    await member.add_roles(community_role)
                    assigned += 1
                except:
                    pass
        await ctx.send(f"👤 Assigned 'Community Member' role to {assigned} members.")
    else:
        await ctx.send("❗ 'Community Member' role not found after creation.")

bot.run("MTQwMTc0MzY4NTAxMTM3ODMyNg.GRWkOu.GGuUNTq3l3vygpEF1m5qcNVPytLkXZQehGHlCA")
