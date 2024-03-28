# Copyright (C) 2019 The Raphielscape Company LLC.
#
# Licensed under the Raphielscape Public License, Version 1.c (the "License");
# you may not use this file except in compliance with the License.
#
# Recode by @mrismanaziz
# FROM Man-Userbot <https://github.com/mrismanaziz/Man-Userbot>
# t.me/SharingUserbot & t.me/Lunatic0de

import logging
from asyncio import sleep
from traceback import format_exc

from telethon.errors import (
    BadRequestError,
    ImageProcessFailedError,
    PhotoCropSizeSmallError,
)
from telethon.errors.rpcerrorlist import (
    ChatAdminRequiredError,
    UserAdminInvalidError,
    UserIdInvalidError,
)
from telethon.tl.functions.channels import (
    EditAdminRequest,
    EditBannedRequest,
    EditPhotoRequest,
)
from telethon.tl.functions.users import GetFullUserRequest
from telethon.tl.types import (
    ChannelParticipantsAdmins,
    ChatAdminRights,
    ChatBannedRights,
    InputChatPhotoEmpty,
    MessageMediaPhoto,
)

from Rewe import CMD_HELP
from Rewe.events import register
from Rewe.ewe import (
    ReweChanger,
    _format,
    eod,
    eor,
    get_user_from_event,
    rewe_cmd,
    rewe_handler,
    media_type,
)
from Rewe.database.muted import (
    add_mute,
    add_gmute,
    cek_mute,
    cek_gmute,
    del_mute,
    del_gmute
)

from . import DEVS, cmd, var

BANNED_RIGHTS = ChatBannedRights(
    until_date=None,
    view_messages=True,
    send_messages=True,
    send_media=True,
    send_stickers=True,
    send_gifs=True,
    send_games=True,
    send_inline=True,
    embed_links=True,
)

UNBAN_RIGHTS = ChatBannedRights(
    until_date=None,
    send_messages=None,
    send_media=None,
    send_stickers=None,
    send_gifs=None,
    send_games=None,
    send_inline=None,
    embed_links=None,
)


LOGS = logging.getLogger(__name__)
MUTE_RIGHTS = ChatBannedRights(until_date=None, send_messages=True)
UNMUTE_RIGHTS = ChatBannedRights(until_date=None, send_messages=False)
# ================================================


@rewe_cmd(pattern="setgpic( -s| -d)$", group_only=True)
@register(pattern=r"^\.csetgpic( -s| -d)$", sudo=True)
async def set_group_photo(event):
    "For changing Group dp"
    flag = (event.pattern_match.group(1)).strip()
    if flag == "-s":
        replymsg = await event.get_reply_message()
        photo = None
        if replymsg and replymsg.media:
            if isinstance(replymsg.media, MessageMediaPhoto):
                photo = await event.client.download_media(message=replymsg.photo)
            elif "image" in replymsg.media.document.mime_type.split("/"):
                photo = await event.client.download_file(replymsg.media.document)
            else:
                return await eor(event, "**Media Tidak Valid**", time=10)
        if photo:
            try:
                await event.client(
                    EditPhotoRequest(
                        event.chat_id, await event.client.upload_file(photo)
                    )
                )
                await eor(event, "**Berhasil Mengubah Profil Grup**", time=10)
            except PhotoCropSizeSmallError:
                return await eor(
                    event,
                    "**Gambar Terlalu Kecil**",
                    time=10
                )
            except ImageProcessFailedError:
                return await eor(event, "**Saya memerlukan hak admin untuk melakukan tindakan ini!**", time=10)
            except Exception as e:
                return await eor(event, "**KESALAHAN : **`{}`".format(e))
    else:
        try:
            await event.client(EditPhotoRequest(event.chat_id, InputChatPhotoEmpty()))
        except Exception as e:
            return await eor(event, "**KESALAHAN : **`{}`".format(e))
        await eor(event, "**Foto Profil Grup Berhasil dihapus.**", time=30)


@rewe_cmd(pattern="promote(?:\\s|$)([\\s\\S]*)", group_only=True)
@register(pattern=r"^\.cpromote(?:\s|$)([\s\S]*)", sudo=True)
async def promote(event):
    new_rights = ChatAdminRights(
        add_admins=False,
        change_info=True,
        invite_users=True,
        ban_users=True,
        delete_messages=True,
        pin_messages=True,
        manage_call=True,
    )
    user, rank = await get_user_from_event(event)
    if not rank:
        rank = "admin"
    if not user:
        return
    await eor(event, "`Mempromosikan...`")
    try:
        await event.client(EditAdminRequest(event.chat_id, user.id, new_rights, rank))
    except BadRequestError:
        return await eod(event, "**Tidak Mempunyai Izin!**")
    await eor(event, "`Berhasil Dipromosikan!`", time=30)


@rewe_cmd(pattern="demote(?:\\s|$)([\\s\\S]*)", group_only=True)
@register(pattern=r"^\.cdemote(?:\s|$)([\s\S]*)", sudo=True)
async def demote(event):
    "To demote a person in group"
    user, _ = await get_user_from_event(event)
    if not user:
        return
    await eor(event, "`Menurunkan...`")
    newrights = ChatAdminRights(
        add_admins=None,
        invite_users=None,
        change_info=None,
        ban_users=None,
        delete_messages=None,
        pin_messages=None,
        manage_call=None,
    )
    rank = "admin"
    try:
        await event.client(EditAdminRequest(event.chat_id, user.id, newrights, rank))
    except BadRequestError:
        return await eor(event, "**Tidak Mempunyai Izin!**")
    await eor(event, "`Berhasil Diturunkan!`", time=30)


@rewe_cmd(pattern="ban(?:\\s|$)([\\s\\S]*)", group_only=True)
@register(pattern=r"^\.cban(?:\s|$)([\s\S]*)", sudo=True)
async def ban(bon):
    me = await bon.client.get_me()
    chat = await bon.get_chat()
    admin = chat.admin_rights
    creator = chat.creator
    if not admin and not creator:
        return await eor(bon, "**Gagal Dikarenakan Bukan Admin :)**")

    user, reason = await get_user_from_event(bon)
    if not user:
        return
    uputt = await eor(bon, "`Pemrosesan Larangan...`")
    try:
        await bon.client(EditBannedRequest(bon.chat_id, user.id, BANNED_RIGHTS))
    except BadRequestError:
        return await eor(bon, "**Tidak Mempunyai Izin!**")
    if reason:
        await rewe.edit(
            f"""
\\**#𝘽𝙖𝙣𝙣𝙚𝙙_𝙐𝙨𝙚𝙧**//

**𝙁𝙞𝙧𝙨𝙩 𝙉𝙖𝙢𝙚 :** [{user.first_name}](tg://user?id={user.id})
**𝙐𝙨𝙚𝙧 𝙄𝘿 :** `{str(user.id)}`
**𝘼𝙘𝙩𝙞𝙤𝙣 :** `𝘽𝙖𝙣𝙣𝙚𝙙 𝙐𝙨𝙚𝙧`
**𝙍𝙚𝙖𝙨𝙤𝙣 :** `{reason}`
**𝘽𝙖𝙣𝙣𝙚𝙙 𝘽𝙮 :** `{me.first_name}`
**𝙋𝙤𝙬𝙚𝙧𝙚𝙙 𝘽𝙮 : ✧ ᴇᴡᴇ-ᴜsᴇʀʙᴏᴛ ✧**
"""
        )
    else:
        await rewe.edit(
            f"""
\\**#𝘽𝙖𝙣𝙣𝙚𝙙_𝙐𝙨𝙚𝙧**//

**𝙁𝙞𝙧𝙨𝙩 𝙉𝙖𝙢𝙚 :** [{user.first_name}](tg://user?id={user.id})
**𝙐𝙨𝙚𝙧 𝙄𝘿 :** `{str(user.id)}`
**𝘼𝙘𝙩𝙞𝙤𝙣 :** `𝘽𝙖𝙣𝙣𝙚𝙙 𝙐𝙨𝙚𝙧`
**𝘽𝙖𝙣𝙣𝙚𝙙 𝘽𝙮 :** `{me.first_name}`
**𝙋𝙤𝙬𝙚𝙧𝙚𝙙 𝘽𝙮 : ✧ ᴇᴡᴇ-ᴜsᴇʀʙᴏᴛ ✧**
"""
        )


@rewe_cmd(pattern="unban(?:\\s|$)([\\s\\S]*)", group_only=True)
@register(pattern=r"^\.cunban(?:\s|$)([\s\S]*)", sudo=True)
async def nothanos(unbon):
    chat = await unbon.get_chat()
    admin = chat.admin_rights
    creator = chat.creator
    if not admin and not creator:
        return await eor(unbon, "**Gagal Dikarenakan Bukan Admin :)**")
    await eor(unbon, '**Memproses...**')
    user = await get_user_from_event(unbon)
    user = user[0]
    if not user:
        return
    try:
        await unbon.client(EditBannedRequest(unbon.chat_id, user.id, UNBAN_RIGHTS))
        await eor(unbon, "`Membatalkan Larangan Berhasil Dilakukan!`", time=10)
    except UserIdInvalidError:
        await eor(unbon, "`Sepertinya Terjadi KESALAHAN!`", time=10)


@rewe_cmd(pattern="mute(?: |$)(.*)", group_only=True)
@register(pattern=r"^\.cmute(?: |$)(.*)", sudo=True)
async def spider(spdr):
    chat = await spdr.get_chat()
    admin = chat.admin_rights
    creator = chat.creator
    if not admin and not creator:
        return await eor(spdr, "**Gagal Dikarenakan Bukan Admin :)**")
    user, reason = await get_user_from_event(spdr)
    if not user:
        return
    self_user = await spdr.client.get_me()
    if user.id == self_user.id:
        return await eor(spdr, "**Tidak Bisa Membisukan Diri Sendiri..（>﹏<）**")
    if user.id in DEVS:
        return await eor(spdr, "**Gagal Membisukan, Karna dia adalah Pembuat Saya 🤪**")
    await eor(
        spdr,
        "**Membisukan Pengguna...**"
    )
    muting = ReweChanger(cek_mute(self_user.id))
    if user.id in muting:
        return await eor(spdr, "**KESALAHAN!** `Pengguna Sudah Dibisukan.`")
    try:
        await spdr.client(EditBannedRequest(spdr.chat_id, user.id, MUTE_RIGHTS))
        add_mute(self_user.id, user.id)
        if reason:
            await eor(
                spdr,
                f"""
\\**#𝙈𝙪𝙩𝙚𝙙_𝙐𝙨𝙚𝙧**//

**𝙁𝙞𝙧𝙨𝙩 𝙉𝙖𝙢𝙚 :** [{user.first_name}](tg://user?id={user.id})
**𝙐𝙨𝙚𝙧 𝙄𝘿 :** `{user.id}`
**𝙍𝙚𝙖𝙨𝙤𝙣 :** `{reason}`
**𝙈𝙪𝙩𝙚𝙙 𝘽𝙮 :** `{self_user.first_name}`
**𝙋𝙤𝙬𝙚𝙧𝙚𝙙 𝘽𝙮 : ✧ ᴇᴡᴇ-ᴜsᴇʀʙᴏᴛ ✧**
"""
            )
        else:
            await eor(
                spdr,
                f'''
\\**#𝙈𝙪𝙩𝙚𝙙_𝙐𝙨𝙚𝙧**//

**𝙁𝙞𝙧𝙨𝙩 𝙉𝙖𝙢𝙚 :** [{user.first_name}](tg://user?id={user.id})
**𝙐𝙨𝙚𝙧 𝙄𝘿 :** `{user.id}`
**𝘼𝙘𝙩𝙞𝙤𝙣 :** `𝙈𝙪𝙩𝙚𝙙 𝙐𝙨𝙚𝙧`
**𝙈𝙪𝙩𝙚𝙙 𝘽𝙮 :** `{self_user.first_name}`
**𝙋𝙤𝙬𝙚𝙧𝙚𝙙 𝘽𝙮 : ✧ ᴇᴡᴇ-ᴜsᴇʀʙᴏᴛ ✧**
'''
            )
    except UserIdInvalidError:
        return await eor(spdr, "**Terjadi KESALAHAN!**", time=10)


@rewe_cmd(pattern="unmute(?: |$)(.*)", group_only=True)
@register(pattern=r"^\.cunmute(?: |$)(.*)", sudo=True)
async def unmoot(unmot):
    self_user = await unmot.client.get_me()
    chat = await unmot.get_chat()
    admin = chat.admin_rights
    creator = chat.creator
    if not admin and not creator:
        return await eor(unmot, "**Gagal Dikarenakan Bukan Admin :)**", time=10)
    xx = await eor(unmot, '**Memproses...**')
    user = await get_user_from_event(unmot)
    user = user[0]
    if not user:
        return xx.edit("Not User")
    muted = cek_mute(self_user.id)
    if muted:
        muting = eval(muted)
    else:
        muting = muted
    if user.id not in muting:
        return await xx.edit("**KESALAHAN! Pengguna Sudah Tidak Dibisukan.**")
    try:
        await unmot.client(EditBannedRequest(unmot.chat_id, user.id, UNBAN_RIGHTS))
        await xx.edit("**Berhasil Melakukan Unmute!**")
        del_mute(self_user.id, user.id)
    except UserIdInvalidError:
        return await eod(xx, "**Terjadi KESALAHAN!**")


@rewe_handler()
async def muter(moot):
    me = await moot.client.get_me()
    muted = cek_mute(me.id)
    gmuted = cek_gmute(me.id)
    rights = ChatBannedRights(
        until_date=None,
        send_messages=True,
        send_media=True,
        send_stickers=True,
        send_gifs=True,
        send_games=True,
        send_inline=True,
        embed_links=True,
    )
    if muted:
        for i in eval(muted):
            if str(i) == str(moot.sender_id):
                await moot.delete()
                await moot.client(
                    EditBannedRequest(moot.chat_id, moot.sender_id, rights)
                )
    elif gmuted:
        for i in eval(gmuted):
            if str(i) == str(moot.sender_id):
                await moot.delete()


@rewe_cmd(pattern="ungmute(?: |$)(.*)", group_only=True)
@register(pattern=r"^\.cungmute(?: |$)(.*)", sudo=True)
async def ungmoot(un_gmute):
    me = await un_gmute.client.get_me()
    chat = await un_gmute.get_chat()
    admin = chat.admin_rights
    creator = chat.creator
    if not admin and not creator:
        return await eor(un_gmute, "**Gagal Dikarenakan Bukan Admin :)**", time=10)
    uputt = await eor(un_gmute, '**Memproses...**')
    user = await get_user_from_event(un_gmute)
    user = user[0]
    if not user:
        return
    await rewe.edit("**Membuka Global Mute Pengguna...**")
    ungmuting = ReweChanger(cek_gmute(me.id))
    if user.id in ungmuting:
        await rewe.edit("**KESALAHAN!** Pengguna Sudah Tidak Di Bisukan Global...")
        del_gmute(me.id, user.id)
        return
    else:
        await rewe.edit("**BERHASIL! Pengguna Sudah Tidak Dibisukan**", time=10)


@rewe_cmd(pattern="gmute(?: |$)(.*)", group_only=True)
@register(pattern=r"^\.cgmute(?: |$)(.*)", sudo=True)
async def gspider(gspdr):
    try:
        chat = await gspdr.get_chat()
        admin = chat.admin_rights
        creator = chat.creator
        if not admin and not creator:
            return await eor(gspdr, "**Gagal Dikarenakan Bukan Admin :)**", time=10)
        rewe = await eor(gspdr, '**Memproses...**')
        user, reason = await get_user_from_event(gspdr)
        if not user:
            return
        self_user = await gspdr.client.get_me()
        if user.id == self_user.id:
            return await rewe.edit("**Tidak Bisa Membisukan Diri Sendiri..（>﹏<）**")
        if user.id in DEVS:
            return await rewe.edit("**Gagal Membisukan Global, Karna dia adalah Pembuat Saya 🤪**")
        await rewe.edit("**Berhasil Membisukan Pengguna!**")
        gmuted = ReweChanger(cek_gmute(self_user.id))
        if user.id in gmuted:
            await eor(gspdr, "**KESALAHAN! Pengguna Sudah Dibisukan.**")
            return
        else:
            add_gmute(self_user.id, user.id)
            if reason:
                await rewe.edit(
                    f'''
\\**#𝙂𝙈𝙪𝙩𝙚𝙙_𝙐𝙨𝙚𝙧**//

**𝙁𝙞𝙧𝙨𝙩 𝙉𝙖𝙢𝙚 :** [{user.first_name}](tg://user?id={user.id})
**𝙐𝙨𝙚𝙧 𝙄𝘿 :** `{user.id}`
**𝙍𝙚𝙖𝙨𝙤𝙣 :** `{reason}`
**𝙂𝙢𝙪𝙩𝙚𝙙 𝘽𝙮 :** `{self_user.first_name}`
**𝙋𝙤𝙬𝙚𝙧𝙚𝙙 𝘽𝙮 : ✧ ᴇᴡᴇ-ᴜsᴇʀʙᴏᴛ ✧**
'''
                )
            else:
                await rewe.edit(
                    f'''
\\**#𝙂𝙢𝙪𝙩𝙚𝙙_𝙐𝙨𝙚𝙧**//

**𝙁𝙞𝙧𝙨𝙩 𝙉𝙖𝙢𝙚 :** [{user.first_name}](tg://user?id={user.id})
**𝙐𝙨𝙚𝙧 𝙄𝘿:** `{user.id}`
**𝘼𝙘𝙩𝙞𝙤𝙣 :** `𝙂𝙡𝙤𝙗𝙖𝙡 𝙈𝙪𝙩𝙚𝙙`
**𝙂𝙢𝙪𝙩𝙚𝙙 𝘽𝙮 :** `{self_user.first_name}`
**𝙋𝙤𝙬𝙚𝙧𝙚𝙙 𝘽𝙮 : ✧ ᴇᴡᴇ-ᴜsᴇʀʙᴏᴛ ✧**
'''
                )
    except BaseException:
        await eor(rewe, f'{format_exc()}')


@rewe_cmd(pattern="zombies(?: |$)(.*)", group_only=True)
async def rm_deletedacc(show):
    con = show.pattern_match.group(1).lower()
    del_u = 0
    del_status = "**Grup Bersih, Tidak Menemukan Akun Terhapus.**"
    if con != "clean":
        await eor(show, "`Mencari Akun Depresi...`")
        async for user in show.client.iter_participants(show.chat_id):
            if user.deleted:
                del_u += 1
                await sleep(1)
        if del_u > 0:
            del_status = f"**Menemukan** `{del_u}` **Akun Depresi/Terhapus/Zombie Dalam Grup Ini,**\n**Bersihkan Itu Menggunakan Perintah** `{cmd}zombies clean`"
        return await show.edit(del_status)
    chat = await show.get_chat()
    admin = chat.admin_rights
    creator = chat.creator
    if not admin and not creator:
        return await eor(show, "**Maaf Kamu Bukan Admin!**")
    await eor(show, "`Menghapus Akun Depresi...`")
    del_u = 0
    del_a = 0
    async for user in show.client.iter_participants(show.chat_id):
        if user.deleted:
            try:
                await show.client(
                    EditBannedRequest(show.chat_id, user.id, BANNED_RIGHTS)
                )
            except ChatAdminRequiredError:
                return await eor(show, "`Tidak Memiliki Izin Banned Dalam Grup Ini`")
            except UserAdminInvalidError:
                del_u -= 1
                del_a += 1
            await show.client(EditBannedRequest(show.chat_id, user.id, UNBAN_RIGHTS))
            del_u += 1
    if del_u > 0:
        del_status = f"**Membersihkan** `{del_u}` **Akun Terhapus**"
    if del_a > 0:
        del_status = f"**Membersihkan** `{del_u}` **Akun Terhapus**\n`{del_a}` **Akun Admin Yang Terhapus Tidak Dihapus.**"
    await show.edit(del_status)
    await sleep(2)
    await show.delete()
    if var.BOTLOG_CHATID:
        await show.client.send_message(
            var.BOTLOG_CHATID, 
            f"**#ZOMBIES**\n**Membersihkan** `{del_u}` **Akun Terhapus!**\n**GRUP:** {show.chat.title}(`{show.chat_id}`)"
        )


@rewe_cmd(pattern="admins$", group_only=True)
async def get_admin(show):
    info = await show.client.get_entity(show.chat_id)
    title = info.title or "Grup Ini"
    mentions = f"<b>♕︎ Daftar Admin Grup {title}:</b> \n"
    try:
        async for user in show.client.iter_participants(
            show.chat_id, filter=ChannelParticipantsAdmins
        ):
            if not user.deleted:
                link = f'<a href="tg://user?id={user.id}">{user.first_name}</a>'
                mentions += f"\n✧ {link}"
            else:
                mentions += f"\n⍟ Akun Terhapus <code>{user.id}</code>"
    except ChatAdminRequiredError as err:
        mentions += f" {str(err)}" + "\n"
    await show.edit(mentions, parse_mode="html")


@rewe_cmd(pattern="pin( loud|$)")
@register(pattern=r"^\.cpin( loud|$)", sudo=True)
async def pin(event):
    to_pin = event.reply_to_msg_id
    if not to_pin:
        return await eor(event, "`Balas Pesan Untuk Melakukan Penyematan.`", time=30)
    options = event.pattern_match.group(1)
    is_silent = bool(options)
    try:
        await event.client.pin_message(event.chat_id, to_pin, notify=is_silent)
    except BadRequestError:
        return await eod(event, "**Tidak Mempunyai Izin!**", time=5)
    except Exception as e:
        return await eod(event, "**KESALAHAN : **`{}`".format(e), time=5)
    await eor(event, "`Pesan berhasil disematkan!`")


@rewe_cmd(pattern="unpin( all|$)")
@register(pattern=r"^\.cunpin( all|$)", sudo=True)
async def pin(event):
    to_unpin = event.reply_to_msg_id
    options = (event.pattern_match.group(1)).strip()
    if not to_unpin and options != "all":
        return await eor(
            event,
            f"**Balas ke Pesan untuk melepas Pin atau Gunakan** `{cmd}unpin all` **Untuk Melepas Semua Pin**",
            time=20,
        )
    try:
        if to_unpin and not options:
            await event.client.unpin_message(event.chat_id, to_unpin)
            await eor(event, "`Berhasil Menghapus Pesan Sematan!`")
        elif options == "all":
            await event.client.unpin_message(event.chat_id)
            await eor(event, "`Berhasil Menghapus Semua Pesan Sematan!`")
        else:
            return await eor(
                event,
                f"**Balas ke Pesan untuk melepas pin atau gunakan** `{cmd}unpin all`",
                time=20,
            )
    except BadRequestError:
        return await eor(event, "**Tidak Mempunyai Izin!**", time=10)
    except Exception as e:
        return await eor(event, "**KESALAHAN : **`{}`".format(e), time=10)


@rewe_cmd(pattern="kick(?: |$)(.*)", group_only=True)
@register(pattern=r"^\.ckick(?: |$)(.*)", sudo=True)
async def kick(usr):
    chat = await usr.get_chat()
    admin = chat.admin_rights
    creator = chat.creator
    if not admin and not creator:
        return await eor(usr, "**Gagal Dikarenakan Bukan Admin :)**")
    user, reason = await get_user_from_event(usr)
    if not user:
        return await eor(usr, "**Tidak Dapat Menemukan Pengguna.**")
    xxnx = await eor(usr, '**Memproses...**')
    try:
        await usr.client.kick_participant(usr.chat_id, user.id)
        await sleep(0.5)
    except Exception as e:
        noperm = "**Tidak Mempunyai Izin!**" + "\n" + e
        return await eod(usr, noperm)
    if reason:
        await xxnx.edit(
            f"[{user.first_name}](tg://user?id={user.id}) **Telah Dikick Dari Grup**\n**Alasan:** `{reason}`"
        )
    else:
        await xxnx.edit(
            f"[{user.first_name}](tg://user?id={user.id}) **Telah Dikick Dari Grup.**"
        )


@rewe_cmd(pattern=r"undlt( -u)?(?: |$)(\d*)?")
async def _iundlt(event):
    catevent = await eor(event, "`Mencari tindakan terbaru...`")
    flag = event.pattern_match.group(1)
    if event.pattern_match.group(2) != "":
        lim = int(event.pattern_match.group(2))
        if lim > 15:
            lim = int(15)
 
