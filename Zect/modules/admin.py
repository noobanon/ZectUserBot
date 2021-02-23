import time
import asyncio
from pyrogram import filters
from pyrogram.types import Message, ChatPermissions

from pyrogram.errors import UserAdminInvalid
from pyrogram.methods.chats.get_chat_members import Filters as ChatMemberFilters

from Zect import app, CMD_HELP
from Zect.helpers.pyrohelper import get_arg
from Zect.helpers.adminhelpers import CheckAdmin
from config import PREFIX

CMD_HELP.update(
    {
        "Admin Tools": """
『 **Admin Tools** 』
  `ban` -> Bans user indefinitely.
  `unban` -> Unbans the user.
  `mute` -> Mutes user indefinitely.
  `unmute` -> Unmutes the user.
  `kick` -> Kicks the user out of the group.
  `gmute` -> Doesn't lets a user speak(even admins).
  `ungmute` -> Inverse of what gmute does.
  `pin` -> pins a message.
  `del` -> delete a message.
  `purge` -> purge message(s)
"""
    }
)

@app.on_message(filters.command("promote", PREFIX) & filters.me)
async def promote(_, message: Message):
    if message.chat.type in ['group', 'supergroup']:
        cmd = message.command
        can_promo = await admin_check(message)
        if can_promo:
            try:
                if message.reply_to_message:
                    user_id = message.reply_to_message.from_user.id
                    custom_rank = get_emoji_regexp().sub('', ' '.join(cmd[1:]))
                else:
                    usr = await client.get_users(cmd[1])
                    custom_rank = get_emoji_regexp().sub('', ' '.join(cmd[2:]))
                    user_id = usr.id
            except IndexError:
                await message.delete()
                return

            if user_id:
                try:
                    await client.promote_chat_member(
                        message.chat.id,
                        user_id,
                        can_change_info=True,
                        can_delete_messages=True,
                        can_restrict_members=True,
                        can_invite_users=True,
                        can_pin_messages=True,
                    )

                    await asyncio.sleep(2)
                    await client.set_administrator_title(
                        message.chat.id, user_id, custom_rank,
                    )
                    await message.delete()
                except UsernameInvalid:
                    await edit_or_reply("None User Found")
                    await asyncio.sleep(5)
                    await message.delete()
                    return
                except PeerIdInvalid:
                    await edit_or_reply("invalid User Or Chat")
                    await asyncio.sleep(5)
                    await message.delete()
                    return
                except UserIdInvalid:
                    await edit_or_reply("User id is invalid")
                    await asyncio.sleep(5)
                    await message.delete()
                    return

                except ChatAdminRequired:
                    await edit_or_reply("You don't have permission to do this")
                    await asyncio.sleep(5)
                    await message.delete()
                    return

        else:
            await edit_or_reply("You don't have permission to do this")
            await asyncio.sleep(5)
            await message.delete()
    else:
        await message.delete()

@app.on_message(filters.command("ban", PREFIX) & filters.me)
async def ban_hammer(_, message: Message):
    if await CheckAdmin(message) is True:
        reply = message.reply_to_message
        if reply:
            user = reply.from_user["id"]
        else:
            user = get_arg(message)
            if not user:
                await message.edit("**Whome should I ban?**")
                return
        try:
            get_user = await app.get_users(user)
            await app.kick_chat_member(
                chat_id=message.chat.id,
                user_id=get_user.id,
            )
            await message.edit(f"{get_user.first_name} has been banned.")
        except:
            await message.edit("I can't ban this user.")


@app.on_message(filters.command("unban", PREFIX) & filters.me)
async def unban(_, message: Message):
    if await CheckAdmin(message) is True:
        reply = message.reply_to_message
        if reply:
            user = reply.from_user["id"]
        else:
            user = get_arg(message)
            if not user:
                await message.edit("**Whome should I unban?**")
                return
        try:
            get_user = await app.get_users(user)
            await app.unban_chat_member(chat_id=message.chat.id, user_id=get_user.id)
            await message.edit(f"{get_user.first_name} was unbanned.")
        except:
            await message.edit("I can't unban this user.")


# Mute Permissions
mute_permission = ChatPermissions(
    can_send_messages=False,
    can_send_media_messages=False,
    can_send_stickers=False,
    can_send_animations=False,
    can_send_games=False,
    can_use_inline_bots=False,
    can_add_web_page_previews=False,
    can_send_polls=False,
    can_change_info=False,
    can_invite_users=True,
    can_pin_messages=False,
)


@app.on_message(filters.command("mute", PREFIX) & filters.me)
async def mute_hammer(_, message: Message):
    if await CheckAdmin(message) is True:
        reply = message.reply_to_message
        if reply:
            user = reply.from_user["id"]
        else:
            user = get_arg(message)
            if not user:
                await message.edit("**Whome should I mute?**")
                return
        try:
            get_user = await app.get_users(user)
            await app.restrict_chat_member(
                chat_id=message.chat.id,
                user_id=get_user.id,
                permissions=mute_permission,
            )
            await message.edit(f"{get_user.first_name} has been muted.")
        except:
            await message.edit("I can't mute this user.")


# Unmute permissions
unmute_permissions = ChatPermissions(
    can_send_messages=True,
    can_send_media_messages=True,
    can_send_stickers=True,
    can_send_animations=True,
    can_send_games=True,
    can_use_inline_bots=True,
    can_add_web_page_previews=True,
    can_send_polls=True,
    can_change_info=False,
    can_invite_users=True,
    can_pin_messages=False,
)


@app.on_message(filters.command("unmute", PREFIX) & filters.me)
async def unmute(_, message: Message):
    if await CheckAdmin(message) is True:
        reply = message.reply_to_message
        if reply:
            user = reply.from_user["id"]
        else:
            user = get_arg(message)
            if not user:
                await message.edit("**Whome should I unmute?**")
                return
        try:
            get_user = await app.get_users(user)
            await app.restrict_chat_member(
                chat_id=message.chat.id,
                user_id=get_user.id,
                permissions=unmute_permissions,
            )
            await message.edit(f"{get_user.first_name} was unmuted.")
        except:
            await message.edit("I can't unmute this user.")


@app.on_message(filters.command("kick", PREFIX) & filters.me)
async def kick_user(_, message: Message):
    if await CheckAdmin(message) is True:
        reply = message.reply_to_message
        if reply:
            user = reply.from_user["id"]
        else:
            user = get_arg(message)
            if not user:
                await message.edit("**Whome should I kick?**")
                return
        try:
            get_user = await app.get_users(user)
            await app.kick_chat_member(
                chat_id=message.chat.id,
                user_id=get_user.id,
            )
            await message.edit(f"{get_user.first_name} was kicked.")
        except:
            await message.edit("I can't kick this user.")


@app.on_message(filters.command("pin", PREFIX) & filters.me)
async def pin_message(_, message: Message):
    # First of all check if its a group or not
    if message.chat.type in ["group", "supergroup"]:
        # Here lies the sanity checks
        admins = await app.get_chat_members(
            message.chat.id, filter=ChatMemberFilters.ADMINISTRATORS
        )
        admin_ids = [user.user.id for user in admins]
        me = await app.get_me()

        # If you are an admin
        if me.id in admin_ids:
            # If you replied to a message so that we can pin it.
            if message.reply_to_message:
                disable_notification = True

                # Let me see if you want to notify everyone. People are gonna hate you for this...
                if len(message.command) >= 2 and message.command[1] in [
                    "alert",
                    "notify",
                    "loud",
                ]:
                    disable_notification = False

                # Pin the fucking message.
                await app.pin_chat_message(
                    message.chat.id,
                    message.reply_to_message.message_id,
                    disable_notification=disable_notification,
                )
                await message.edit("`Pinned message!`")
            else:
                # You didn't reply to a message and we can't pin anything. ffs
                await message.edit(
                    "`Reply to a message so that I can pin the god damned thing...`"
                )
        else:
            # You have no business running this command.
            await message.edit("`I am not an admin here lmao. What am I doing?`")
    else:
        # Are you fucking dumb this is not a group ffs.
        await message.edit("`This is not a place where I can pin shit.`")

    # And of course delete your lame attempt at changing the group picture.
    # RIP you.
    # You're probably gonna get ridiculed by everyone in the group for your failed attempt.
    # RIP.
    await asyncio.sleep(3)
    await message.delete()
