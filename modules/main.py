import os
import re
import sys
import time
import asyncio
import json
import pytz
import requests
# Add root directory to path to allow imports from root modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import m3u8
import subprocess
import urllib
import urllib.parse
import yt_dlp
import tgcrypto
import cloudscraper
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
from base64 import b64encode, b64decode
from logs import logging
from bs4 import BeautifulSoup
import saini as helper
from html_handler import html_handler
from drm_handler import drm_handler
import globals
# Import database and auth modules
from db import db
import auth
from broadcast import broadcast_handler, broadusers_handler
from text_handler import text_to_txt
from youtube_handler import ytm_handler, y2t_handler, getcookies_handler, cookies_handler
from utils import progress_bar
from vars import api_url, api_token, token_cp, adda_token, photologo, photoyt, photocp, photozip
from vars import API_ID, API_HASH, BOT_TOKEN, OWNER, CREDIT, CREDIT_LINK, OWNER_ID, OWNER_ID2, ADMINS, AUTH_MESSAGES, UPGRADE_TEXT, cookies_file_path
import plan_manager as _pm
from aiohttp import ClientSession

# ── Default plan content (shown to all users; saved to DB on first boot) ───────
_DEFAULT_PLAN_CONTENT = (
    "💎 <b>𝐏𝐥𝐚𝐧𝐬 𝐟𝐨𝐫</b> {mention}\n\n"
    "🎉 ᴡᴇʟᴄᴏᴍᴇ {first_name} ᴛᴏ ꜱᴜɢᴀʀ ᴅᴀᴅᴅʏ ᴅʀᴍ ʙᴏᴛ! 🎉\n\n"
    "🔐 ʏᴏᴜ ᴄᴀɴ ᴀᴄᴄᴇꜱꜱ ᴀʟʟ ɴᴏɴ-ᴅʀᴍ + ᴀᴇꜱ ᴇɴᴄʀʏᴘᴛᴇᴅ ᴜʀʟꜱ\n"
    "━━━━━━━━━━━━━━\n"
    "🍁 <b>𝐋𝐨𝐠𝐢𝐧 𝐑𝐞𝐪𝐮𝐢𝐫𝐞𝐝</b>\n"
    "• 📚 ᴀᴘᴘx ᴢɪᴘ + ᴇɴᴄʀʏᴘᴛᴇᴅ ᴜᴘᴛᴏ 𝟺 ᴜʜꜱ\n"
    "• 🎓 ᴄʟᴀꜱꜱᴘʟᴜꜱ ᴅʀᴍ + ɴᴅʀᴍ\n"
    "• 📚 ᴄᴀʀᴇᴇʀᴡɪʟʟ + ᴘᴅꜰ\n"
    "• 🎓 ᴋʜᴀɴ ɢꜱ\n"
    "• 🎓 ᴀʟʟᴇɴ\n"
    "• 🎓 ᴋᴅ ᴄᴀᴍᴘᴜꜱ\n"
    "• 🎓 ꜱᴛᴜᴅʏ ɪǫ ᴅʀᴍ\n"
    "• 🚀 ᴀᴘᴘx + ᴀᴘᴘx ᴇɴᴄ ᴘᴅꜰ\n"
    "• 🎓 ᴠɪᴍᴇᴏ ᴘʀᴏᴛᴇᴄᴛɪᴏɴ\n"
    "• 🎓 ʙʀɪɢʜᴛᴄᴏᴠᴇ ᴘʀᴏᴛᴇᴄᴛɪᴏɴ\n"
    "• 🎓 ᴠɪꜱɪᴏɴɪᴀꜱ ᴘʀᴏᴛᴇᴄᴛɪᴏɴ\n"
    "• 🎓 ᴢᴏᴏᴍ ᴠɪᴅᴇᴏ\n"
    "• 🎓 ᴜᴛᴋᴀʀꜱʜ ᴘʀᴏᴛᴇᴄᴛɪᴏɴ (ᴠɪᴅᴇᴏ + ᴘᴅꜰ)\n"
    "• 🎓 ᴀʟʟ ɴᴏɴ-ᴅʀᴍ + ᴀᴇꜱ ᴇɴᴄʀʏᴘᴛᴇᴅ ᴜʀʟꜱ\n"
    "• 🎓 ᴍᴘᴅ ᴜʀʟꜱ ɪꜰ ᴛʜᴇ ᴋᴇʏ ɪꜱ ᴋɴᴏᴡɴ\n"
    "━━━━━━━━━━━━━━\n"
    "🌷 <b>𝐖𝐢𝐭𝐡𝐨𝐮𝐭 𝐋𝐨𝐠𝐢𝐧</b> 🌷\n"
    "• 🎓 ꜱᴛᴜᴅʏ ɪǫ\n"
    "• 🎓 ᴘʜʏꜱɪᴄꜱᴡᴀʟʟᴀʜ\n"
    "• 🎓 ᴜɴᴀᴄᴀᴅᴇᴍʏ\n"
    "• 🎓 ᴋɢꜱ (ᴋʜᴀɴ ꜱɪʀ)\n"
    "• 🎓 ɪꜰᴀꜱ ᴏɴʟɪɴᴇ\n"
    "• 🎓 ꜱᴇʟᴇᴄᴛɪᴏɴᴡᴀʏ\n"
    "• 🎓 ᴜᴛᴋᴀʀꜱʜ\n"
    "• 🎓 ᴊʀꜰ ᴀᴅᴅᴀ\n"
    "• 🎓 12ᴍɪɴ ᴛᴏ ᴄʟᴀᴛ\n"
    "• 🎓 ʟᴇɢᴀʟ ᴇᴅɢᴇ\n"
    "• 🎓 ʟᴀᴡ ᴘʀᴇᴘ ᴛᴜᴛᴏʀɪᴀʟ\n"
    "• 🎓 ᴡᴇ ʟᴇᴀʀɴ\n"
    "• 🎓 ʟᴇɢᴀʟ ᴀᴅᴅᴀ\n"
    "• 🎓 ᴀᴅᴅᴀ247\n"
    "━━━━━━━━━━━━━━\n"
    "💰 <b>𝐏𝐫𝐢𝐜𝐞:</b> ₹𝟸,𝟻𝟶𝟶 (30 ᴅᴀʏꜱ)\n\n"
    "📩 <b>𝐂𝐨𝐧𝐭𝐚𝐜𝐭:</b> ➥ 🌷 <a href='{credit_link}'>{credit}</a> 🌷"
)
from subprocess import getstatusoutput
from pytube import YouTube
from aiohttp import web
import random
from pyrogram import Client, filters, idle, StopPropagation, enums
from pyrogram.types import Message, InputMediaPhoto
from pyrogram.errors import FloodWait, PeerIdInvalid, UserIsBlocked, InputUserDeactivated
from pyrogram.errors.exceptions.bad_request_400 import StickerEmojiInvalid
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import aiohttp
import aiofiles
import zipfile
import shutil
import ffmpeg

# Patch pyrogram Message to add .edit() as alias for .edit_text()
try:
    from pyrogram.types import Message as _PyroMsg
    if not hasattr(_PyroMsg, "edit"):
        _PyroMsg.edit = _PyroMsg.edit_text
except Exception:
    pass

# Initialize the bot
bot = Client(
    "bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    max_concurrent_transmissions=10,
)

# ── HTTP-based listen() — works with our HTTP polling engine ──────────────────
# Maps chat_id → asyncio.Future waiting for next message from that chat
_LISTEN_FUTURES: dict = {}

async def _bot_listen(chat_id: int, timeout: int = 120, filters=None):
    """Wait for next message from chat_id via HTTP polling futures."""
    loop = asyncio.get_event_loop()
    fut: asyncio.Future = loop.create_future()
    _LISTEN_FUTURES[chat_id] = fut
    try:
        return await asyncio.wait_for(asyncio.shield(fut), timeout=timeout)
    except (asyncio.TimeoutError, TimeoutError):
        # Re-raise as asyncio.TimeoutError so drm_handler catches it properly
        raise asyncio.TimeoutError(f"⏰ No response within {timeout}s")
    finally:
        _LISTEN_FUTURES.pop(chat_id, None)

bot.listen = _bot_listen


# ═══════════════════════════════════════════════════════════════════════════════
# HTTP getUpdates polling engine
# Pyrogram's MTProto push doesn't deliver updates reliably on Heroku/Python 3.12
# This runs alongside pyrogram and dispatches all incoming commands/messages
# ═══════════════════════════════════════════════════════════════════════════════

class _Msg:
    """Minimal pyrogram-compatible Message wrapper built from HTTP API dict."""
    __slots__ = (
        "_client", "message_id", "id", "text", "chat", "from_user", "_msg",
        "document", "caption", "reply_to_message",
        "photo", "video", "audio", "sticker", "voice", "animation",
        "entities", "caption_entities",
    )

    def __init__(self, d: dict, client):
        self._client    = client
        self._msg       = d
        self.message_id = d.get("message_id", 0)
        self.id         = self.message_id  # pyrogram convention
        self.text       = d.get("text") or d.get("caption") or ""
        self.caption    = d.get("caption", "")
        # Media types — set to None if not present
        self.photo     = d.get("photo")      # list of PhotoSize dicts or None
        self.video     = d.get("video")
        self.audio     = d.get("audio")
        self.sticker   = d.get("sticker")
        self.voice     = d.get("voice")
        self.animation = d.get("animation")
        self.entities          = d.get("entities", [])
        self.caption_entities  = d.get("caption_entities", [])

        _c = d.get("chat", {})
        self.chat = type("_C", (), {
            "id":   _c.get("id", 0),
            "type": _c.get("type", "private"),
        })()

        _u = d.get("from", {})
        if not _u:
            # Channel post — use sender_chat/chat as pseudo-user so handlers don't crash
            _sc = d.get("sender_chat") or d.get("chat", {})
            _u = {
                "id":         _sc.get("id", 0),
                "first_name": _sc.get("title", "Channel"),
                "username":   _sc.get("username"),
                "last_name":  None,
            }
        _uid = _u.get("id", 0)
        _uname = _u.get("username")
        _fname = _u.get("first_name", "User")
        self.from_user = type("_U", (), {
            "id":         _uid,
            "first_name": _fname,
            "last_name":  _u.get("last_name"),
            "username":   _uname,
            "mention":    f"@{_uname}" if _uname else f"[{_fname}](tg://user?id={_uid})",
        })()

        # Document support — needed by drm_handler
        _doc = d.get("document")
        if _doc:
            self.document = type("_Doc", (), {
                "file_id":   _doc.get("file_id", ""),
                "file_name": _doc.get("file_name", "file"),
                "mime_type": _doc.get("mime_type", ""),
                "file_size": _doc.get("file_size", 0),
            })()
        else:
            self.document = None

        # reply_to_message — needed by broadcast_handler
        _rp = d.get("reply_to_message")
        if _rp:
            self.reply_to_message = _Msg(_rp, client)
        else:
            self.reply_to_message = None

    async def reply_text(self, text, reply_markup=None, parse_mode=None,
                         disable_web_page_preview=False, **kw):
        from pyrogram.enums import ParseMode as _PM
        kwargs = {"disable_web_page_preview": disable_web_page_preview}
        if reply_markup:
            kwargs["reply_markup"] = reply_markup
        if parse_mode:
            _pm_map = {"html": _PM.HTML, "markdown": _PM.MARKDOWN, "disabled": _PM.DISABLED}
            kwargs["parse_mode"] = _pm_map.get(str(parse_mode).lower(), _PM.HTML)
        return await self._client.send_message(self.chat.id, text, **kwargs)

    async def reply_document(self, document, caption="", **kw):
        try:
            return await self._client.send_document(self.chat.id, document,
                                                     caption=caption, **kw)
        except Exception as e:
            logging.warning(f"[_Msg] reply_document: {e}")

    async def download(self, file_name=None):
        """Download file using pyrogram (works with file_id from HTTP API)."""
        try:
            if self.document:
                return await self._client.download_media(
                    self.document.file_id,
                    file_name=file_name or self.document.file_name,
                )
        except Exception as e:
            logging.warning(f"[_Msg] download failed: {e}")
        return None

    async def delete(self, revoke=True):
        try:
            await self._client.delete_messages(self.chat.id, self.message_id, revoke=revoke)
        except Exception:
            pass

    def _fix_pm(self, kw):
        from pyrogram.enums import ParseMode as _PM
        if "parse_mode" in kw and isinstance(kw["parse_mode"], str):
            _pm_map = {"html": _PM.HTML, "markdown": _PM.MARKDOWN, "disabled": _PM.DISABLED}
            kw["parse_mode"] = _pm_map.get(kw["parse_mode"].lower(), _PM.HTML)
        return kw

    async def edit_text(self, text, **kw):
        try:
            await self._client.edit_message_text(self.chat.id, self.message_id, text,
                                                  **self._fix_pm(kw))
        except Exception:
            pass

    async def edit_caption(self, caption, **kw):
        try:
            await self._client.edit_message_caption(self.chat.id, self.message_id,
                                                     caption, **self._fix_pm(kw))
        except Exception:
            pass


async def _http_poll_loop():
    """Long-poll getUpdates via HTTP Bot API and dispatch to handlers."""
    offset = None
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
    logging.warning("[POLL] HTTP polling loop started")
    async with aiohttp.ClientSession() as sess:
        while True:
            try:
                params = {
                    "timeout": 20,
                    "limit":   100,
                    "allowed_updates": '["message","callback_query","channel_post","edited_channel_post"]',
                }
                if offset is not None:
                    params["offset"] = offset
                async with sess.get(
                    url, params=params,
                    timeout=aiohttp.ClientTimeout(total=25)
                ) as resp:
                    data = await resp.json()

                if not data.get("ok"):
                    logging.warning(f"[POLL] error response: {data}")
                    await asyncio.sleep(3)
                    continue

                for upd in data["result"]:
                    offset = upd["update_id"] + 1
                    asyncio.create_task(_dispatch_http(upd))

            except asyncio.CancelledError:
                break
            except Exception as e:
                logging.warning(f"[POLL] exception: {e}")
                await asyncio.sleep(5)


class _CQ:
    """Minimal pyrogram-compatible CallbackQuery wrapper from HTTP API dict."""
    def __init__(self, d: dict, client):
        self._client = client
        self._d = d
        self.id = d.get("id", "")
        self.data = d.get("data", "")
        msg = d.get("message", {})
        self.message_id = msg.get("message_id", 0)
        _c = msg.get("chat", {})
        self.chat_id = _c.get("id", 0)
        _u = d.get("from", {})
        self.from_user = type("_U", (), {
            "id":         _u.get("id", 0),
            "first_name": _u.get("first_name", "User"),
            "username":   _u.get("username"),
        })()
        # Full message proxy — handlers call cq.message.edit_* methods
        _cq_self = self
        class _MsgProxy:
            id   = _cq_self.message_id
            chat = type("_C", (), {"id": _cq_self.chat_id})()
            def _fix_pm(self, kw):
                from pyrogram.enums import ParseMode as _PM
                if "parse_mode" in kw and isinstance(kw.get("parse_mode"), str):
                    kw["parse_mode"] = {"html": _PM.HTML, "markdown": _PM.MARKDOWN}.get(
                        kw["parse_mode"].lower(), _PM.HTML)
                return kw
            async def _do_edit(self, text, **kw):
                try:
                    await client.edit_message_text(_cq_self.chat_id, _cq_self.message_id, text, **self._fix_pm(kw))
                except Exception as e:
                    logging.warning(f"[CQ.msg] edit: {e}")
                return self  # return self so editable.edit() also works
            async def edit(self, text, **kw):
                return await self._do_edit(text, **kw)
            async def edit_text(self, text, **kw):
                return await self._do_edit(text, **kw)
            async def edit_caption(self, caption, **kw):
                try: await client.edit_message_caption(_cq_self.chat_id, _cq_self.message_id, caption, **self._fix_pm(kw))
                except Exception as e: logging.warning(f"[CQ.msg] edit_caption: {e}")
                return self
            async def edit_reply_markup(self, reply_markup=None):
                try: await client.edit_message_reply_markup(_cq_self.chat_id, _cq_self.message_id, reply_markup=reply_markup)
                except Exception as e: logging.warning(f"[CQ.msg] edit_reply_markup: {e}")
                return self
            async def edit_media(self, media, **kw):
                try: await client.edit_message_media(_cq_self.chat_id, _cq_self.message_id, media, **kw)
                except Exception as e: logging.warning(f"[CQ.msg] edit_media: {e}")
                return self
            async def reply_text(self, text, **kw):
                try: return await client.send_message(_cq_self.chat_id, text, **self._fix_pm(kw))
                except Exception as e: logging.warning(f"[CQ.msg] reply_text: {e}")
            async def delete(self):
                try: await client.delete_messages(_cq_self.chat_id, _cq_self.message_id)
                except Exception: pass
        self.message = _MsgProxy()

    def _fix_pm(self, kw):
        from pyrogram.enums import ParseMode as _PM
        if "parse_mode" in kw and isinstance(kw["parse_mode"], str):
            _pm_map = {"html": _PM.HTML, "markdown": _PM.MARKDOWN}
            kw["parse_mode"] = _pm_map.get(kw["parse_mode"].lower(), _PM.HTML)
        return kw

    async def answer(self, text="", show_alert=False):
        try:
            async with aiohttp.ClientSession() as s:
                await s.post(
                    f"https://api.telegram.org/bot{BOT_TOKEN}/answerCallbackQuery",
                    json={"callback_query_id": self.id, "text": text, "show_alert": show_alert},
                )
        except Exception:
            pass

    async def edit_message_text(self, text, **kw):
        try:
            await self._client.edit_message_text(self.chat_id, self.message_id,
                                                  text, **self._fix_pm(kw))
        except Exception as e:
            logging.warning(f"[CQ] edit_message_text: {e}")

    async def edit_message_caption(self, caption, **kw):
        try:
            await self._client.edit_message_caption(self.chat_id, self.message_id,
                                                     caption, **self._fix_pm(kw))
        except Exception as e:
            logging.warning(f"[CQ] edit_message_caption: {e}")

    async def edit_message_reply_markup(self, reply_markup=None):
        try:
            await self._client.edit_message_reply_markup(self.chat_id, self.message_id,
                                                          reply_markup=reply_markup)
        except Exception as e:
            logging.warning(f"[CQ] edit_message_reply_markup: {e}")


# Map callback_data patterns → handler functions (filled after handlers are defined)
_CB_HANDLERS: list[tuple] = []  # list of (regex_pattern, async_fn)


def _register_cb(pattern: str, fn):
    import re as _re
    _CB_HANDLERS.append((_re.compile(pattern), fn))


async def _dispatch_http(upd: dict):
    """Route a single HTTP update to the right handler."""
    # ── callback_query ────────────────────────────────────────────────────────
    cq_dict = upd.get("callback_query")
    if cq_dict:
        cq = _CQ(cq_dict, bot)
        data = cq.data
        logging.warning(f"[POLL] callback_query data={data!r} from={cq.from_user.id}")
        for pattern, fn in _CB_HANDLERS:
            if pattern.search(data):
                try:
                    await fn(bot, cq)
                except Exception as e:
                    logging.exception(f"[POLL] cb handler crash {data!r}: {e}")
                break
        return

    # ── message ───────────────────────────────────────────────────────────────
    msg_dict = (upd.get("message") or upd.get("edited_message")
                or upd.get("channel_post") or upd.get("edited_channel_post"))
    if not msg_dict:
        return

    text = msg_dict.get("text", "") or ""
    chat_id = msg_dict.get("chat", {}).get("id", 0)
    logging.warning(f"[POLL] from={chat_id} text={text!r}")

    m = _Msg(msg_dict, bot)

    # ── resolve pending bot.listen() futures first (text-only) ──────────────
    # Documents go to drm_handler, not to settings listen dialogs
    if chat_id in _LISTEN_FUTURES and not _LISTEN_FUTURES[chat_id].done():
        if not m.document:  # only resolve for text replies
            _LISTEN_FUTURES[chat_id].set_result(m)
            return

    if text.startswith("/"):
        cmd_part = text.split()[0].split("@")[0].lstrip("/").lower()
    else:
        cmd_part = ""

    try:
        if cmd_part == "start":
            await start(bot, m)
        elif cmd_part == "whoami":
            _uid2 = (m.from_user.id if m.from_user else None) or m.chat.id
            await m.reply_text(f"🆔 Your ID: `{_uid2}`\nOWNER={OWNER} OWNER_ID={OWNER_ID} OWNER_ID2={OWNER_ID2}")
        elif cmd_part == "ping":
            await ping(bot, m)
        elif cmd_part == "add":
            await auth.add_user_cmd(bot, m)
        elif cmd_part == "remove":
            await auth.remove_user_cmd(bot, m)
        elif cmd_part == "users":
            await auth.list_users_cmd(bot, m)
        elif cmd_part == "plan":
            _uid3 = (m.from_user.id if m.from_user else None) or m.chat.id
            if _uid3 in {OWNER, OWNER_ID, OWNER_ID2}:
                await _pm.plan_command(bot, m)
            else:
                try:
                    _bu = (await bot.get_me()).username
                except Exception:
                    _bu = "bot"
                await show_plan_for_user_msg(bot, m, _bu)
        elif cmd_part == "id":
            await id_command(bot, m)
        elif cmd_part == "info":
            await info(bot, m)
        elif cmd_part == "status":
            await status_command(bot, m)
        elif cmd_part == "clean":
            await clean_command(bot, m)
        elif cmd_part == "logs":
            await send_logs(bot, m)
        elif cmd_part == "reset":
            await restart_handler(bot, m)
        elif cmd_part == "stop":
            await cancel_handler(bot, m)
        elif cmd_part == "y2t":
            await call_y2t_handler(bot, m)
        elif cmd_part == "ytm":
            await call_ytm_handler(bot, m)
        elif cmd_part == "t2t":
            await call_text_to_txt(bot, m)
        elif cmd_part == "t2h":
            await call_html_handler(bot, m)
        elif cmd_part == "cookies":
            await call_cookies_handler(bot, m)
        elif cmd_part == "getcookies":
            await call_getcookies_handler(bot, m)
        elif cmd_part == "broadcast":
            await call_broadcast_handler(bot, m)
        elif cmd_part == "broadusers":
            await call_broadusers_handler(bot, m)
        elif cmd_part == "addplan":
            await admin_addplan(bot, m)
        elif cmd_part == "delplan":
            await admin_delplan(bot, m)
        elif cmd_part == "clearplans":
            await admin_clearplans(bot, m)
        elif cmd_part == "plans":
            await admin_listplans(bot, m)
        elif not cmd_part and (m.document or (m.text and "://" in m.text) or m.text):
            # plain text / URL / document — main upload handler
            await call_drm_handler(bot, m)
    except Exception as e:
        logging.exception(f"[POLL] handler crash for {cmd_part!r}: {e}")
        try:
            await m.reply_text(f"❌ Error: {e}")
        except Exception:
            pass


# ── Register authentication command handlers ──────────────────────────────────
from pyrogram.handlers import MessageHandler
bot.add_handler(MessageHandler(auth.add_user_cmd, filters.command("add") & filters.private))
bot.add_handler(MessageHandler(auth.remove_user_cmd, filters.command("remove") & filters.private))
bot.add_handler(MessageHandler(auth.list_users_cmd, filters.command("users") & filters.private))
bot.add_handler(MessageHandler(auth.my_plan_cmd, filters.command("plan") & filters.private))

# ── Raw update hook — fires for EVERY TL update before any filtering ─────────
@bot.on_raw_update()
async def _dbg_raw(client, update, users, chats):
    logging.warning(f"[RAW] {type(update).__name__}")

# ── Catch-all diagnostic — logs every incoming message ───────────────────────
@bot.on_message(group=1)
async def _dbg_all(client, m: Message):
    logging.warning(f"[DBG] update from {m.chat.id} text={m.text!r}")

# .....,.....,.......,...,.......,....., .....,.....,.......,...,.......,.....,
@bot.on_message(filters.command("ping"))
async def ping(client, m: Message):
    await m.reply_text("🏓 Pong! Bot is alive.")

# .....,.....,.......,...,.......,....., .....,.....,.......,...,.......,.....,
@bot.on_message(filters.command("start"))
async def start(client, m: Message):
  try:
    user_id = m.chat.id
    first_name = (m.from_user.first_name if m.from_user else None) or "User"
    is_admin = user_id in {OWNER, OWNER_ID, OWNER_ID2} or user_id in ADMINS

    # ── Step 1: guaranteed immediate reply — nothing can block this ───────────
    ack = await m.reply_text("⏳ Loading...")

    # ── Step 2: send photo (replace ack) ─────────────────────────────────────
    has_photo = False
    start_msg = ack
    try:
        start_msg = await client.send_photo(
            chat_id=user_id,
            photo="https://i.ibb.co/zTPJFct8/photo-2025-04-25-12-55-01-7497233558289776672.jpg",
            caption=f'🌟 Welcome <a href="tg://user?id={user_id}">{first_name}</a>! 🌟',
            parse_mode=enums.ParseMode.HTML,
        )
        has_photo = True
        await ack.delete()
    except Exception:
        pass  # ack stays as fallback message

    async def edit_msg(text, reply_markup=None):
        try:
            if has_photo:
                await start_msg.edit_caption(text, reply_markup=reply_markup, parse_mode=enums.ParseMode.HTML)
            else:
                await start_msg.edit_text(text, reply_markup=reply_markup, parse_mode=enums.ParseMode.HTML,
                                          disable_web_page_preview=True)
        except Exception as _e:
            logging.warning(f"[/start] edit: {_e}")

    # ── Step 3: progress animation ────────────────────────────────────────────
    import html as _html_safe
    steps = [
        ("Initializing Uploader bot... 🤖", "[⬜️⬜️⬜️⬜️⬜️⬜️⬜️⬜️⬜️⬜️] 0%"),
        ("Loading features... ⏳",          "[🟥🟥🟥⬜️⬜️⬜️⬜️⬜️⬜️⬜️] 25%"),
        ("Almost ready... 😊",              "[🟧🟧🟧🟧🟧⬜️⬜️⬜️⬜️⬜️] 50%"),
        ("Checking subscription... 🔍",     "[🟨🟨🟨🟨🟨🟨🟨🟨⬜️⬜️] 75%"),
    ]
    for desc, prog in steps:
        await asyncio.sleep(1)
        await edit_msg(f'🌟 Welcome <a href="tg://user?id={user_id}">{_html_safe.escape(first_name)}</a>! 🌟\n\n{desc}\n\nProgress: {prog}\n\n')

    await asyncio.sleep(1)

    # ── Step 4: auth check ────────────────────────────────────────────────────
    try:
        _me = await client.get_me()
        bot_username = _me.username
    except Exception:
        bot_username = "bot"

    try:
        is_authorized = is_admin or db.is_user_authorized(user_id, bot_username)
    except Exception:
        is_authorized = is_admin

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("✨ Commands", callback_data="cmd_command")],
        [InlineKeyboardButton("💎 Features", callback_data="feat_command"),
         InlineKeyboardButton("⚙️ Settings", callback_data="setttings")],
        [InlineKeyboardButton("💳 Plans", callback_data="upgrade_command")],
        [InlineKeyboardButton("📞 Contact", url=f"tg://openmessage?user_id={OWNER}"),
         InlineKeyboardButton("🦅 Join", url="https://t.me/+2y45kqIrSg5iYTI1")],
    ])

    # ── Step 5: final message ─────────────────────────────────────────────────
    _fn_safe = _html_safe.escape(first_name)
    _mention = f'<a href="tg://user?id={user_id}">{_fn_safe}</a>'
    _username = (m.from_user.username if m.from_user else "") or ""

    # Plan shown to everyone; premium users get a badge on top
    _plan_text = _render_plan(first_name, user_id, _username)
    _badge = ""
    if is_authorized:
        _badge = "✅ <b>You are a Premium Member!</b>\n"
        try:
            _info = db.get_user_expiry_info(user_id, bot_username)
            if _info and not is_admin:
                _badge += (
                    f"<blockquote>📅 Expiry: <b>{_info['expiry_date']}</b>\n"
                    f"⏳ Remaining: <b>{_info['days_left']} days</b></blockquote>\n"
                )
        except Exception:
            pass
        _badge += "\n"

    await edit_msg(
        f"🌟 <b>Welcome, {_mention}!</b> 🌟\n\n"
        f"{_badge}"
        f"{_plan_text}\n\n"
        f"<b>✨ Tap the buttons below</b> to get started.",
        reply_markup=keyboard,
    )
  except Exception as _e:
    logging.exception(f"[/start] crash: {_e}")
    try:
        await m.reply_text(f"❌ Start error: {_e}")
    except Exception:
        pass

# .....,.....,.......,...,.......,....., .....,.....,.......,...,.......,.....,
# .....,.....,.......,...,.......,....., .....,.....,.......,...,.......,.....,
@bot.on_callback_query(filters.regex("back_to_main_menu"))
async def back_to_main_menu(client, callback_query):
    user_id = callback_query.from_user.id
    first_name = callback_query.from_user.first_name
    caption = f'✨ <b>Welcome back, <a href="tg://user?id={user_id}">{first_name}</a>!</b>'
    keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("✨ Commands", callback_data="cmd_command")],
            [InlineKeyboardButton("💎 Features", callback_data="feat_command"), InlineKeyboardButton("⚙️ Settings", callback_data="setttings")],
            [InlineKeyboardButton("💳 Plans", callback_data="upgrade_command")],
            [InlineKeyboardButton(text="📞 Contact", url=f"tg://openmessage?user_id={OWNER}"), InlineKeyboardButton(text="🦅 Join", url="https://t.me/+2y45kqIrSg5iYTI1")],
        ])
    
    await callback_query.message.edit_media(
      InputMediaPhoto(
        parse_mode=enums.ParseMode.HTML,
        media="https://i.ibb.co/zTPJFct8/photo-2025-04-25-12-55-01-7497233558289776672.jpg",
        caption=caption
      ),
      reply_markup=keyboard
    )
    await callback_query.answer()  

# .....,.....,.......,...,.......,....., .....,.....,.......,...,.......,.....,
# .....,.....,.......,...,.......,....., .....,.....,.......,...,.......,.....,
@bot.on_callback_query(filters.regex("cmd_command"))
async def cmd(client, callback_query):
    user_id = callback_query.from_user.id
    first_name = callback_query.from_user.first_name
    caption = f'✨ <b>Hey <a href="tg://user?id={user_id}">{first_name}</a>!</b>\nChoose a section to explore commands.'
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🚻 User", callback_data="user_command"), InlineKeyboardButton("🚹 Owner", callback_data="owner_command")],
        [InlineKeyboardButton("🔙 Back to Main Menu", callback_data="back_to_main_menu")]
    ])
    await callback_query.message.edit_media(
    InputMediaPhoto(
      parse_mode=enums.ParseMode.HTML,
      media="https://i.ibb.co/zTPJFct8/photo-2025-04-25-12-55-01-7497233558289776672.jpg",
      caption=caption
    ),
    reply_markup=keyboard
    )
# .....,.....,.......,...,.......,....., .....,.....,.......,...,.......,.....,
@bot.on_callback_query(filters.regex("user_command"))
async def help_button(client, callback_query):
  user_id = callback_query.from_user.id
  first_name = callback_query.from_user.first_name
  keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back to Commands", callback_data="cmd_command")]])
  caption = (
        f"💥 𝐁𝐎𝐓𝐒 𝐂𝐎𝐌𝐌𝐀𝐍𝐃𝐒\n"
        f"▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰\n" 
        f"📌 𝗠𝗮𝗶𝗻 𝗙𝗲𝗮𝘁𝘂𝗿𝗲𝘀:\n\n"  
        f"➥ /start – Bot Status Check\n"
        f"➥ /y2t – YouTube → .txt Converter\n"  
        f"➥ /ytm – YouTube → .mp3 downloader\n"  
        f"➥ /t2t – Text → .txt Generator\n"
        f"➥ /t2h – .txt → .html Converter\n" 
        f"➥ /stop – Cancel Running Task\n"
        f"▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰ \n" 
        f"⚙️ 𝗧𝗼𝗼𝗹𝘀 & 𝗦𝗲𝘁𝘁𝗶𝗻𝗴𝘀: \n\n" 
        f"➥ /cookies – Update YT Cookies\n" 
        f"➥ /id – Get Chat/User ID\n"  
        f"➥ /info – User Details\n"  
        f"➥ /logs – View Bot Activity\n"
        f"▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰\n"
        f"💡 𝗡𝗼𝘁𝗲:\n\n"  
        f"• Send any link for auto-extraction\n"
        f"• Send direct .txt file for auto-extraction\n"
        f"• Supports batch processing\n\n"  
        f"╭────────⊰◆⊱────────╮\n"   
        f" ➠ 𝐌𝐚𝐝𝐞 𝐁𝐲 : {CREDIT} 💻\n"
        f"╰────────⊰◆⊱────────╯\n"
  )
    
  await callback_query.message.edit_media(
    InputMediaPhoto(
      parse_mode=enums.ParseMode.HTML,
      media="https://i.ibb.co/zTPJFct8/photo-2025-04-25-12-55-01-7497233558289776672.jpg",
      caption=caption
    ),
    reply_markup=keyboard
    )
# .....,.....,.......,...,.......,....., .....,.....,.......,...,.......,.....,
@bot.on_callback_query(filters.regex("owner_command"))
async def help_button_owner(client, callback_query):
  user_id = callback_query.from_user.id
  first_name = callback_query.from_user.first_name
  keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back to Commands", callback_data="cmd_command")]])
  caption = (
        f"👤 𝐁𝐨𝐭 𝐎𝐰𝐧𝐞𝐫 𝐂𝐨𝐦𝐦𝐚𝐧𝐝𝐬\n\n" 
        f"➥ /add xxxx – Add User ID\n" 
        f"➥ /remove xxxx – Remove User ID\n"  
        f"➥ /users – Total User List\n"  
        f"➥ /broadcast – For Broadcasting\n"  
        f"➥ /broadusers – All Broadcasting Users\n"  
        f"➥ /reset – Reset Bot\n"
        f"▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰\n"  
        f"╭────────⊰◆⊱────────╮\n"   
        f" ➠ 𝐌𝐚𝐝𝐞 𝐁𝐲 : {CREDIT} 💻\n"
        f"╰────────⊰◆⊱────────╯\n"
  )
    
  await callback_query.message.edit_media(
    InputMediaPhoto(
      parse_mode=enums.ParseMode.HTML,
      media="https://i.ibb.co/zTPJFct8/photo-2025-04-25-12-55-01-7497233558289776672.jpg",
      caption=caption
    ),
    reply_markup=keyboard
  )

# .....,.....,.......,...,.......,....., .....,.....,.......,...,.......,.....,
# .....,.....,.......,...,.......,....., .....,.....,.......,...,.......,.....,
@bot.on_callback_query(filters.regex("upgrade_command"))
async def upgrade_button(client, callback_query):
    await _show_plan_for_user_cq(client, callback_query)

# ── Shared plan display logic ─────────────────────────────────────────────────

def _render_plan(first_name: str, user_id: int, username: str = "") -> str:
    """Render the saved plan (or default) with user variables substituted."""
    import html as _h
    _fn_safe = _h.escape(first_name)
    _mention = f'<a href="tg://user?id={user_id}">{_fn_safe}</a>'
    raw = db.get_setting("default_plan_content") or _DEFAULT_PLAN_CONTENT
    return _pm.render_plan_content(raw, {
        "first_name": _fn_safe,
        "last_name": "",
        "username": username,
        "user_id": user_id,
        "mention": _mention,
        "role": "User",
        "plan_name": "",
        "expiry_date": "",
        "days_left": "",
        "credit": CREDIT,
        "credit_link": CREDIT_LINK,
    })

async def _show_plan_for_user_cq(client, cq):
    """Show plan + membership badge when user taps 💳 Plans button."""
    user_id    = cq.from_user.id
    first_name = cq.from_user.first_name
    username   = cq.from_user.username or ""
    keyboard   = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="back_to_main_menu")]])
    _is_owner_flag = user_id in {OWNER, OWNER_ID, OWNER_ID2}

    try:
        bot_username = (await client.get_me()).username
    except Exception:
        bot_username = "bot"

    is_premium = _is_owner_flag or db.is_user_authorized(user_id, bot_username)
    plan_text = _render_plan(first_name, user_id, username)

    # Premium badge shown above the plan
    badge = "✅ <b>You are a Premium Member!</b>\n\n" if is_premium else ""
    text = badge + plan_text

    await cq.answer()
    try:
        await cq.message.edit_text(text, reply_markup=keyboard, parse_mode=enums.ParseMode.HTML,
                                   disable_web_page_preview=True)
    except Exception:
        await client.send_message(cq.chat_id, text, reply_markup=keyboard,
                                  parse_mode=enums.ParseMode.HTML,
                                  disable_web_page_preview=True)

async def show_plan_for_user_msg(bot_client, m, bot_username: str):
    """Show plan + membership badge as a new message (/plan command)."""
    user_id    = (m.from_user.id if m.from_user else None) or m.chat.id
    first_name = (m.from_user.first_name if m.from_user else None) or "User"
    username   = (m.from_user.username if m.from_user else None) or ""
    _is_owner_flag = user_id in {OWNER, OWNER_ID, OWNER_ID2}
    is_premium = _is_owner_flag or db.is_user_authorized(user_id, bot_username)

    plan_text = _render_plan(first_name, user_id, username)
    badge = "✅ <b>You are a Premium Member!</b>\n\n" if is_premium else ""
    text = badge + plan_text

    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("📞 Contact Owner", url=f"tg://openmessage?user_id={OWNER}")]])
    await m.reply_text(text, reply_markup=keyboard, parse_mode=enums.ParseMode.HTML,
                       disable_web_page_preview=True)
# .....,.....,.......,...,.......,....., .....,.....,.......,...,.......,.....,
# .....,.....,.......,...,.......,....., .....,.....,.......,...,.......,.....,
@bot.on_callback_query(filters.regex("setttings"))
async def settings_button(client, callback_query):
    caption = "⚙️ <b>Bot Settings</b>\n\nCustomize your upload experience below."
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📝 Caption Style", callback_data="caption_style_command"), InlineKeyboardButton("🖋️ File Name", callback_data="file_name_command")],
        [InlineKeyboardButton("🌅 Thumbnail", callback_data="thummbnail_command")],
        [InlineKeyboardButton("✍️ Add Credit", callback_data="add_credit_command"), InlineKeyboardButton("🔏 Set Token", callback_data="set_token_command")],
        [InlineKeyboardButton("📽️ Video Quality", callback_data="quality_command"), InlineKeyboardButton("🏷️ Topic", callback_data="topic_command")],
        [InlineKeyboardButton("🔄 Reset", callback_data="resset_command")],
        [InlineKeyboardButton("🔙 Back to Main Menu", callback_data="back_to_main_menu")]
    ])

    await callback_query.message.edit_media(
    InputMediaPhoto(
      parse_mode=enums.ParseMode.HTML,
      media="https://i.ibb.co/zTPJFct8/photo-2025-04-25-12-55-01-7497233558289776672.jpg",
      caption=caption
    ),
    reply_markup=keyboard
    )
# .....,.....,.......,...,.......,....., .....,.....,.......,...,.......,.....,
@bot.on_callback_query(filters.regex("thummbnail_command"))
async def handle_thumbnail_command(client, callback_query):
    user_id = callback_query.from_user.id
    first_name = callback_query.from_user.first_name
    caption = f'✨ <b>Hey <a href="tg://user?id={user_id}">{first_name}</a>!</b>\nChoose a thumbnail option below.'
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🎥 Video", callback_data="viideo_thumbnail_command"), InlineKeyboardButton("📑 PDF", callback_data="pddf_thumbnail_command")],
        [InlineKeyboardButton("🔙 Back to Settings", callback_data="setttings")]
    ])
    await callback_query.message.edit_media(
    InputMediaPhoto(
      parse_mode=enums.ParseMode.HTML,
      media="https://i.ibb.co/zTPJFct8/photo-2025-04-25-12-55-01-7497233558289776672.jpg",
      caption=caption
    ),
    reply_markup=keyboard
    )
# .....,.....,.......,...,.......,....., .....,.....,.......,...,.......,.....,
@bot.on_callback_query(filters.regex("wattermark_command"))
async def handle_watermark_menu(client, callback_query):
    user_id = callback_query.from_user.id
    first_name = callback_query.from_user.first_name
    caption = f'✨ <b>Hey <a href="tg://user?id={user_id}">{first_name}</a>!</b>\nChoose a watermark option below.'
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🎥 Video", callback_data="video_watermark_command"), InlineKeyboardButton("📑 PDF", callback_data="pdf_watermark_command")],
        [InlineKeyboardButton("🔙 Back to Settings", callback_data="setttings")]
    ])
    await callback_query.message.edit_media(
    InputMediaPhoto(
      parse_mode=enums.ParseMode.HTML,
      media="https://i.ibb.co/zTPJFct8/photo-2025-04-25-12-55-01-7497233558289776672.jpg",
      caption=caption
    ),
    reply_markup=keyboard
    )
# .....,.....,.......,...,.......,....., .....,.....,.......,...,.......,.....,
@bot.on_callback_query(filters.regex("set_token_command"))
async def handle_token_menu(client, callback_query):
    user_id = callback_query.from_user.id
    first_name = callback_query.from_user.first_name
    caption = f'✨ <b>Hey <a href="tg://user?id={user_id}">{first_name}</a>!</b>\nChoose a platform to set the token.'
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Classplus", callback_data="cp_token_command")],
        [InlineKeyboardButton("Physics Wallah", callback_data="pw_token_command"), InlineKeyboardButton("Carrerwill", callback_data="cw_token_command")],
        [InlineKeyboardButton("🔙 Back to Settings", callback_data="setttings")]
    ])
    await callback_query.message.edit_media(
    InputMediaPhoto(
      parse_mode=enums.ParseMode.HTML,
      media="https://i.ibb.co/zTPJFct8/photo-2025-04-25-12-55-01-7497233558289776672.jpg",
      caption=caption
    ),
    reply_markup=keyboard
    )
# .....,.....,.......,...,.......,....., .....,.....,.......,...,.......,.....,
@bot.on_callback_query(filters.regex("caption_style_command"))
async def handle_caption(client, callback_query):
    user_id = callback_query.from_user.id
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back to Settings", callback_data="setttings")]])
    editable = await callback_query.message.edit(
        "**Caption Style 1**\n"
        "<blockquote expandable><b>[🎥]Vid Id</b> : {str(count).zfill(3)}\n"
        "**Video Title :** `{name1} [{res}p].{ext}`\n"
        "<blockquote><b>Batch Name :</b> {b_name}</blockquote>\n\n"
        "**Extracted by➤**{CR}</blockquote>\n\n"
        "**Caption Style 2**\n"
        "<blockquote expandable>**——— ✦ {str(count).zfill(3)} ✦ ———**\n\n"
        "🎞️ **Title** : `{name1}`\n"
        "**├── Extention :  {extension}.{ext}**\n"
        "**├── Resolution : [{res}]**\n"
        "📚 **Course : {b_name}**\n\n"
        "🌟 **Extracted By : {credit}**</blockquote>\n\n"
        "**Caption Style 3**\n"
        "<blockquote expandable>**{str(count).zfill(3)}.** {name1} [{res}p].{ext}</blockquote>\n\n"
        "**Send Your Caption Style eg. /cc1 or /cc2 or /cc3**", reply_markup=keyboard)
    input_msg = await bot.listen(editable.chat.id)
    try:
        if input_msg.text.lower() == "/cc1":
            globals.caption = '/cc1'
            await editable.edit(f"✅ Caption Style 1 Updated!", reply_markup=keyboard)
        elif input_msg.text.lower() == "/cc2":
            globals.caption = '/cc2'
            await editable.edit(f"✅ Caption Style 2 Updated!", reply_markup=keyboard)
        else:
            globals.caption = input_msg.text
            await editable.edit(f"✅ Caption Style 3 Updated!", reply_markup=keyboard)
            
    except Exception as e:
        await editable.edit(f"<b>❌ Failed to set Caption Style:</b>\n<blockquote expandable>{str(e)}</blockquote>", reply_markup=keyboard)
    finally:
        await input_msg.delete()
# .....,.....,.......,...,.......,....., .....,.....,.......,...,.......,.....,
@bot.on_callback_query(filters.regex("file_name_command"))
async def handle_file_name(client, callback_query):
    user_id = callback_query.from_user.id
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back to Settings", callback_data="setttings")]])
    editable = await callback_query.message.edit("**Send End File Name or Send /d**", reply_markup=keyboard)
    input_msg = await bot.listen(editable.chat.id)
    try:
        if input_msg.text.lower() == "/d":
            globals.endfilename = '/d'
            await editable.edit(f"✅ End File Name Disabled !", reply_markup=keyboard)
        else:
            globals.endfilename = input_msg.text
            await editable.edit(f"✅ End File Name `{globals.endfilename}` is enabled!", reply_markup=keyboard)
            
    except Exception as e:
        await editable.edit(f"<b>❌ Failed to set End File Name:</b>\n<blockquote expandable>{str(e)}</blockquote>", reply_markup=keyboard)
    finally:
        await input_msg.delete()
# .....,.....,.......,...,.......,....., .....,.....,.......,...,.......,.....,
@bot.on_callback_query(filters.regex("viideo_thumbnail_command"))
async def video_thumbnail(client, callback_query):
    user_id = callback_query.from_user.id
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back to Settings", callback_data="thummbnail_command")]])
    editable = await callback_query.message.edit(f"Send the Video Thumb URL or Send /d \n<blockquote><b>Note </b>- For document format send : No</blockquote>", reply_markup=keyboard)
    input_msg = await bot.listen(editable.chat.id)

    try:
        if input_msg.text.startswith("http://") or input_msg.text.startswith("https://"):
            globals.thumb = input_msg.text
            await editable.edit(f"✅ Thumbnail set successfully from the URL !", reply_markup=keyboard)

        elif input_msg.text.lower() == "/d":
            globals.thumb = "/d"
            await editable.edit(f"✅ Thumbnail set to default !", reply_markup=keyboard)

        else:
            globals.thumb = input_msg.text
            await editable.edit(f"✅ Video in Document Format is enabled !", reply_markup=keyboard)

    except Exception as e:
        await editable.edit(f"<b>❌ Failed to set thumbnail:</b>\n<blockquote expandable>{str(e)}</blockquote>", reply_markup=keyboard)
    finally:
        await input_msg.delete()
# .....,.....,.......,...,.......,....., .....,.....,.......,...,.......,.....,
@bot.on_callback_query(filters.regex("pddf_thumbnail_command"))
async def pdf_thumbnail_button(client, callback_query):
  keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back to Settings", callback_data="thummbnail_command")]])
  caption = ("<b>⋅ This Feature is Not Working Yet ⋅</b>")
  await callback_query.message.edit_media(
    InputMediaPhoto(
        parse_mode=enums.ParseMode.HTML,
        media="https://i.ibb.co/zTPJFct8/photo-2025-04-25-12-55-01-7497233558289776672.jpg",
        caption=caption
    ),
    reply_markup=keyboard
  )
# .....,.....,.......,...,.......,....., .....,.....,.......,...,.......,.....,
@bot.on_callback_query(filters.regex("add_credit_command"))
async def credit(client, callback_query):
    user_id = callback_query.from_user.id
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back to Settings", callback_data="setttings")]])
    current_credit = globals.CR
    current_link = globals.CR_LINK
    editable = await callback_query.message.edit(
        f"**✍️ Set Credit**\n\n"
        f"**Current Credit:** `{current_credit}`\n"
        f"**Current Link:** `{current_link}`\n\n"
        f"**Send in format:** `CreditName*@username`\n"
        f"**Example:** `👨‍💻Rick Johnson*@rick007contactbot`\n\n"
        f"Or send just `CreditName` to set only the name.\n"
        f"Send /d to reset to default.", reply_markup=keyboard)
    input_msg = await bot.listen(editable.chat.id)

    try:
        if input_msg.text.lower() == "/d":
            globals.CR = f"{CREDIT}"
            globals.CR_LINK = f"{CREDIT_LINK}"
            await editable.edit(f"✅ Credit reset to default!\n\n**Credit:** `{globals.CR}`\n**Link:** `{globals.CR_LINK}`", reply_markup=keyboard)

        elif "*" in input_msg.text:
            parts = input_msg.text.split("*", 1)
            credit_name = parts[0].strip()
            username = parts[1].strip()
            
            # Convert @username to https://t.me/username link
            if username.startswith("@"):
                credit_link = f"https://t.me/{username[1:]}"
            elif username.startswith("https://") or username.startswith("http://"):
                credit_link = username
            else:
                credit_link = f"https://t.me/{username}"
            
            globals.CR = credit_name
            globals.CR_LINK = credit_link
            await editable.edit(f"✅ Credit updated!\n\n**Credit:** `{globals.CR}`\n**Link:** `{globals.CR_LINK}`", reply_markup=keyboard)

        else:
            globals.CR = input_msg.text.strip()
            await editable.edit(f"✅ Credit name set as `{globals.CR}`!\n**Link:** `{globals.CR_LINK}` (unchanged)", reply_markup=keyboard)

    except Exception as e:
        await editable.edit(f"<b>❌ Failed to set Credit:</b>\n<blockquote expandable>{str(e)}</blockquote>", reply_markup=keyboard)
    finally:
        await input_msg.delete()
# .....,.....,.......,...,.......,....., .....,.....,.......,...,.......,.....,
@bot.on_callback_query(filters.regex("cp_token_command"))
async def handle_token(client, callback_query):
    user_id = callback_query.from_user.id
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back to Settings", callback_data="set_token_command")]])
    editable = await callback_query.message.edit("**Send Classplus Token**", reply_markup=keyboard)
    input_msg = await bot.listen(editable.chat.id)
    try:
        globals.cptoken = input_msg.text
        await editable.edit(f"✅ Classplus Token set successfully !\n\n<blockquote expandable>`{globals.cptoken}`</blockquote>", reply_markup=keyboard)
            
    except Exception as e:
        await editable.edit(f"<b>❌ Failed to set Classplus Token:</b>\n<blockquote expandable>{str(e)}</blockquote>", reply_markup=keyboard)
    finally:
        await input_msg.delete()
# .....,.....,.......,...,.......,....., .....,.....,.......,...,.......,.....,
@bot.on_callback_query(filters.regex("pw_token_command"))
async def handle_pw_token(client, callback_query):
    user_id = callback_query.from_user.id
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back to Settings", callback_data="set_token_command")]])
    editable = await callback_query.message.edit("**Send Physics Wallah Same Batch Token**", reply_markup=keyboard)
    input_msg = await bot.listen(editable.chat.id)
    try:
        globals.pwtoken = input_msg.text
        await editable.edit(f"✅ Physics Wallah Token set successfully !\n\n<blockquote expandable>`{globals.pwtoken}`</blockquote>", reply_markup=keyboard)
            
    except Exception as e:
        await editable.edit(f"<b>❌ Failed to set Physics Wallah Token:</b>\n<blockquote expandable>{str(e)}</blockquote>", reply_markup=keyboard)
    finally:
        await input_msg.delete()
# .....,.....,.......,...,.......,....., .....,.....,.......,...,.......,.....,
@bot.on_callback_query(filters.regex("cw_token_command"))
async def handle_cw_token(client, callback_query):
    user_id = callback_query.from_user.id
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back to Settings", callback_data="set_token_command")]])
    editable = await callback_query.message.edit("**Send Carrerwill Token**", reply_markup=keyboard)
    input_msg = await bot.listen(editable.chat.id)
    try:
        if input_msg.text.lower() == "/d":
            globals.cwtoken = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJpYXQiOjE3MjQyMzg3OTEsImNvbiI6eyJpc0FkbWluIjpmYWxzZSwiYXVzZXIiOiJVMFZ6TkdGU2NuQlZjR3h5TkZwV09FYzBURGxOZHowOSIsImlkIjoiZEUxbmNuZFBNblJqVEROVmFWTlFWbXhRTkhoS2R6MDkiLCJmaXJzdF9uYW1lIjoiYVcxV05ITjVSemR6Vm10ak1WUlBSRkF5ZVNzM1VUMDkiLCJlbWFpbCI6Ik5Ga3hNVWhxUXpRNFJ6VlhiR0ppWTJoUk0wMVdNR0pVTlU5clJXSkRWbXRMTTBSU2FHRnhURTFTUlQwPSIsInBob25lIjoiVUhVMFZrOWFTbmQ1ZVcwd1pqUTViRzVSYVc5aGR6MDkiLCJhdmF0YXIiOiJLM1ZzY1M4elMwcDBRbmxrYms4M1JEbHZla05pVVQwOSIsInJlZmVycmFsX2NvZGUiOiJOalZFYzBkM1IyNTBSM3B3VUZWbVRtbHFRVXAwVVQwOSIsImRldmljZV90eXBlIjoiYW5kcm9pZCIsImRldmljZV92ZXJzaW9uIjoiUShBbmRyb2lkIDEwLjApIiwiZGV2aWNlX21vZGVsIjoiU2Ftc3VuZyBTTS1TOTE4QiIsInJlbW90ZV9hZGRyIjoiNTQuMjI2LjI1NS4xNjMsIDU0LjIyNi4yNTUuMTYzIn19.snDdd-PbaoC42OUhn5SJaEGxq0VzfdzO49WTmYgTx8ra_Lz66GySZykpd2SxIZCnrKR6-R10F5sUSrKATv1CDk9ruj_ltCjEkcRq8mAqAytDcEBp72-W0Z7DtGi8LdnY7Vd9Kpaf499P-y3-godolS_7ixClcYOnWxe2nSVD5C9c5HkyisrHTvf6NFAuQC_FD3TzByldbPVKK0ag1UnHRavX8MtttjshnRhv5gJs5DQWj4Ir_dkMcJ4JaVZO3z8j0OxVLjnmuaRBujT-1pavsr1CCzjTbAcBvdjUfvzEhObWfA1-Vl5Y4bUgRHhl1U-0hne4-5fF0aouyu71Y6W0eg'
            await editable.edit(f"✅ Carrerwill Token set successfully as default !", reply_markup=keyboard)

        else:
            globals.cwtoken = input_msg.text
            await editable.edit(f"✅ Carrerwill Token set successfully !\n\n<blockquote expandable>`{globals.cwtoken}`</blockquote>", reply_markup=keyboard)
            
    except Exception as e:
        await editable.edit(f"<b>❌ Failed to set Careerwill Token:</b>\n<blockquote expandable>{str(e)}</blockquote>", reply_markup=keyboard)
    finally:
        await input_msg.delete()
# .....,.....,.......,...,.......,....., .....,.....,.......,...,.......,.....,
@bot.on_callback_query(filters.regex("video_watermark_command"))
async def video_watermark(client, callback_query):
    user_id = callback_query.from_user.id
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back to Settings", callback_data="wattermark_command")]])
    editable = await callback_query.message.edit(f"**Send Video Watermark text or Send /d**", reply_markup=keyboard)
    input_msg = await bot.listen(editable.chat.id)

    try:
        if input_msg.text.lower() == "/d":
            globals.vidwatermark = "/d"
            await editable.edit(f"**Video Watermark Disabled ✅** !", reply_markup=keyboard)

        else:
            globals.vidwatermark = input_msg.text
            await editable.edit(f"Video Watermark `{globals.vidwatermark}` enabled ✅!", reply_markup=keyboard)

    except Exception as e:
        await editable.edit(f"<b>❌ Failed to set Watermark:</b>\n<blockquote expandable>{str(e)}</blockquote>", reply_markup=keyboard)
    finally:
        await input_msg.delete()
# .....,.....,.......,...,.......,....., .....,.....,.......,...,.......,.....,
@bot.on_callback_query(filters.regex("pdf_watermark_command"))
async def pdf_watermark_button(client, callback_query):
  keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back to Settings", callback_data="wattermark_command")]])
  caption = ("<b>⋅ This Feature is Not Working Yet ⋅</b>")
  await callback_query.message.edit_media(
    InputMediaPhoto(
        parse_mode=enums.ParseMode.HTML,
        media="https://i.ibb.co/zTPJFct8/photo-2025-04-25-12-55-01-7497233558289776672.jpg",
        caption=caption
    ),
    reply_markup=keyboard
  )
# .....,.....,.......,...,.......,....., .....,.....,.......,...,.......,.....,
@bot.on_callback_query(filters.regex("quality_command"))
async def handle_quality(client, callback_query):
    user_id = callback_query.from_user.id
    caption = "**📽️ Select Video Quality:**\n\n__Choose your preferred video quality for downloads__"
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📱 144p", callback_data="quality_144"), InlineKeyboardButton("📱 240p", callback_data="quality_240")],
        [InlineKeyboardButton("💻 360p", callback_data="quality_360"), InlineKeyboardButton("💻 480p", callback_data="quality_480")],
        [InlineKeyboardButton("🖥️ 720p (HD)", callback_data="quality_720"), InlineKeyboardButton("🖥️ 1080p (Full HD)", callback_data="quality_1080")],
        [InlineKeyboardButton("🔙 Back to Settings", callback_data="setttings")]
    ])
    await callback_query.message.edit(caption, reply_markup=keyboard)

# Quality selection handlers
@bot.on_callback_query(filters.regex("quality_144"))
async def set_quality_144(client, callback_query):
    globals.raw_text2 = '144'
    globals.quality = '144p'
    globals.res = '256x144'
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back to Settings", callback_data="setttings")]])
    await callback_query.message.edit(f"✅ Video Quality set to **144p** !", reply_markup=keyboard)

@bot.on_callback_query(filters.regex("quality_240"))
async def set_quality_240(client, callback_query):
    globals.raw_text2 = '240'
    globals.quality = '240p'
    globals.res = '426x240'
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back to Settings", callback_data="setttings")]])
    await callback_query.message.edit(f"✅ Video Quality set to **240p** !", reply_markup=keyboard)

@bot.on_callback_query(filters.regex("quality_360"))
async def set_quality_360(client, callback_query):
    globals.raw_text2 = '360'
    globals.quality = '360p'
    globals.res = '640x360'
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back to Settings", callback_data="setttings")]])
    await callback_query.message.edit(f"✅ Video Quality set to **360p** !", reply_markup=keyboard)

@bot.on_callback_query(filters.regex("quality_480"))
async def set_quality_480(client, callback_query):
    globals.raw_text2 = '480'
    globals.quality = '480p'
    globals.res = '854x480'
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back to Settings", callback_data="setttings")]])
    await callback_query.message.edit(f"✅ Video Quality set to **480p** !", reply_markup=keyboard)

@bot.on_callback_query(filters.regex("quality_720"))
async def set_quality_720(client, callback_query):
    globals.raw_text2 = '720'
    globals.quality = '720p'
    globals.res = '1280x720'
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back to Settings", callback_data="setttings")]])
    await callback_query.message.edit(f"✅ Video Quality set to **720p (HD)** !", reply_markup=keyboard)

@bot.on_callback_query(filters.regex("quality_1080"))
async def set_quality_1080(client, callback_query):
    globals.raw_text2 = '1080'
    globals.quality = '1080p'
    globals.res = '1920x1080'
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back to Settings", callback_data="setttings")]])
    await callback_query.message.edit(f"✅ Video Quality set to **1080p (Full HD)** !", reply_markup=keyboard)
# .....,.....,.......,...,.......,....., .....,.....,.......,...,.......,.....,
@bot.on_callback_query(filters.regex("topic_command"))
async def handle_topic_command(client, callback_query):
    user_id = callback_query.from_user.id
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back to Settings", callback_data="setttings")]])
    editable = await callback_query.message.edit(f"**If you want to enable topic in caption: send /yes or send /d**\n\n<blockquote><b>Topic fetch from (bracket) in title</b></blockquote>", reply_markup=keyboard)
    input_msg = await bot.listen(editable.chat.id)

    try:
        if input_msg.text.lower() == "/yes":
            globals.topic = "/yes"
            await editable.edit(f"**Topic enabled in Caption ✅** !", reply_markup=keyboard)

        else:
            globals.topic = input_msg.text
            await editable.edit(f"Topic disabled in Caption ✅!", reply_markup=keyboard)

    except Exception as e:
        await editable.edit(f"<b>❌ Failed to set Topic in Caption:</b>\n<blockquote expandable>{str(e)}</blockquote>", reply_markup=keyboard)
    finally:
        await input_msg.delete()
# .....,.....,.......,...,.......,....., .....,.....,.......,...,.......,.....,
@bot.on_callback_query(filters.regex("resset_command"))
async def handle_reset_cmd(client, callback_query):
    user_id = callback_query.from_user.id
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back to Settings", callback_data="setttings")]])
    editable = await callback_query.message.edit(f"If you want to reset settings send /yes or Send /no", reply_markup=keyboard)
    input_msg = await bot.listen(editable.chat.id)

    try:
        if input_msg.text.lower() == "/yes":
            globals.caption = '/cc1'
            globals.endfilename = '/d'
            globals.thumb = '/d'
            globals.CR = f"{CREDIT}"
            globals.CR_LINK = f"{CREDIT_LINK}"
            globals.cwtoken = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJpYXQiOjE3MjQyMzg3OTEsImNvbiI6eyJpc0FkbWluIjpmYWxzZSwiYXVzZXIiOiJVMFZ6TkdGU2NuQlZjR3h5TkZwV09FYzBURGxOZHowOSIsImlkIjoiZEUxbmNuZFBNblJqVEROVmFWTlFWbXhRTkhoS2R6MDkiLCJmaXJzdF9uYW1lIjoiYVcxV05ITjVSemR6Vm10ak1WUlBSRkF5ZVNzM1VUMDkiLCJlbWFpbCI6Ik5Ga3hNVWhxUXpRNFJ6VlhiR0ppWTJoUk0wMVdNR0pVTlU5clJXSkRWbXRMTTBSU2FHRnhURTFTUlQwPSIsInBob25lIjoiVUhVMFZrOWFTbmQ1ZVcwd1pqUTViRzVSYVc5aGR6MDkiLCJhdmF0YXIiOiJLM1ZzY1M4elMwcDBRbmxrYms4M1JEbHZla05pVVQwOSIsInJlZmVycmFsX2NvZGUiOiJOalZFYzBkM1IyNTBSM3B3VUZWbVRtbHFRVXAwVVQwOSIsImRldmljZV90eXBlIjoiYW5kcm9pZCIsImRldmljZV92ZXJzaW9uIjoiUShBbmRyb2lkIDEwLjApIiwiZGV2aWNlX21vZGVsIjoiU2Ftc3VuZyBTTS1TOTE4QiIsInJlbW90ZV9hZGRyIjoiNTQuMjI2LjI1NS4xNjMsIDU0LjIyNi4yNTUuMTYzIn19.snDdd-PbaoC42OUhn5SJaEGxq0VzfdzO49WTmYgTx8ra_Lz66GySZykpd2SxIZCnrKR6-R10F5sUSrKATv1CDk9ruj_ltCjEkcRq8mAqAytDcEBp72-W0Z7DtGi8LdnY7Vd9Kpaf499P-y3-godolS_7ixClcYOnWxe2nSVD5C9c5HkyisrHTvf6NFAuQC_FD3TzByldbPVKK0ag1UnHRavX8MtttjshnRhv5gJs5DQWj4Ir_dkMcJ4JaVZO3z8j0OxVLjnmuaRBujT-1pavsr1CCzjTbAcBvdjUfvzEhObWfA1-Vl5Y4bUgRHhl1U-0hne4-5fF0aouyu71Y6W0eg'
            globals.cptoken = "cptoken"
            globals.pwtoken = "pwtoken"
            globals.vidwatermark = '/d'
            globals.raw_text2 = '480'
            globals.quality = '480p'
            globals.res = '854x480'
            globals.topic = '/d'
            await editable.edit(f"✅ Settings reset as default !", reply_markup=keyboard)

        else:
            await editable.edit(f"✅ Settings Not Changed !", reply_markup=keyboard)

    except Exception as e:
        await editable.edit(f"<b>❌ Failed to Change Settings:</b>\n<blockquote expandable>{str(e)}</blockquote>", reply_markup=keyboard)
    finally:
        await input_msg.delete()

# .....,.....,.......,...,.......,....., .....,.....,.......,...,.......,.....,
# .....,.....,.......,...,.......,....., .....,.....,.......,...,.......,.....,
@bot.on_callback_query(filters.regex("feat_command"))
async def feature_button(client, callback_query):
  caption = "💎 <b>Bot Features</b>\n\nExplore everything this bot can do."
  keyboard = InlineKeyboardMarkup([
      [InlineKeyboardButton("📌 Auto Pin Batch Name", callback_data="pin_command")],
      [InlineKeyboardButton("💧 Watermark", callback_data="watermark_command"), InlineKeyboardButton("🔄 Reset", callback_data="reset_command")],
      [InlineKeyboardButton("🖨️ Bot Working Logs", callback_data="logs_command")],
      [InlineKeyboardButton("🖋️ File Name", callback_data="custom_command"), InlineKeyboardButton("🏷️ Title", callback_data="titlle_command")],
      [InlineKeyboardButton("🎥 YouTube", callback_data="yt_command")],
      [InlineKeyboardButton("🌐 HTML", callback_data="html_command")],
      [InlineKeyboardButton("📝 Text File", callback_data="txt_maker_command"), InlineKeyboardButton("📢 Broadcast", callback_data="broadcast_command")],
      [InlineKeyboardButton("🔙 Back to Main Menu", callback_data="back_to_main_menu")]
  ])
  await callback_query.message.edit_media(
    InputMediaPhoto(
      parse_mode=enums.ParseMode.HTML,
      media="https://i.ibb.co/zTPJFct8/photo-2025-04-25-12-55-01-7497233558289776672.jpg",
      caption=caption
    ),
    reply_markup=keyboard
  )
# .....,.....,.......,...,.......,....., .....,.....,.......,...,.......,.....,
@bot.on_callback_query(filters.regex("pin_command"))
async def pin_button(client, callback_query):
  keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back to Feature", callback_data="feat_command")]])
  caption = "📌 <b>Auto Pin Batch Name</b>\n\nAutomatically pins the batch name in your channel or group when processing starts from the first link."
  await callback_query.message.edit_media(
    InputMediaPhoto(
      parse_mode=enums.ParseMode.HTML,
      media="https://i.ibb.co/zTPJFct8/photo-2025-04-25-12-55-01-7497233558289776672.jpg",
      caption=caption
      ),
      reply_markup=keyboard
  )
# .....,.....,.......,...,.......,....., .....,.....,.......,...,.......,.....,
@bot.on_callback_query(filters.regex("watermark_command"))
async def watermark_button(client, callback_query):
  keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back to Feature", callback_data="feat_command")]])
  caption = "💧 <b>Custom Watermark</b>\n\nAdd your own watermark to videos for a personal touch."
  await callback_query.message.edit_media(
    InputMediaPhoto(
      parse_mode=enums.ParseMode.HTML,
      media="https://i.ibb.co/zTPJFct8/photo-2025-04-25-12-55-01-7497233558289776672.jpg",
      caption=caption
      ),
      reply_markup=keyboard
  )
# .....,.....,.......,...,.......,....., .....,.....,.......,...,.......,.....,
@bot.on_callback_query(filters.regex("reset_command"))
async def restart_button(client, callback_query):
  keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back to Feature", callback_data="feat_command")]])
  caption = "🔄 <b>Reset Bot</b>\n\nUse /reset to restart the bot anytime."
  await callback_query.message.edit_media(
    InputMediaPhoto(
      parse_mode=enums.ParseMode.HTML,
      media="https://i.ibb.co/zTPJFct8/photo-2025-04-25-12-55-01-7497233558289776672.jpg",
      caption=caption
      ),
      reply_markup=keyboard
  )
# .....,.....,.......,...,.......,....., .....,.....,.......,...,.......,.....,
@bot.on_callback_query(filters.regex("logs_command"))
async def handle_logs_command(client, callback_query):
  keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back to Feature", callback_data="feat_command")]])
  caption = "🖨️ <b>Bot Logs</b>\n\nUse /logs to receive the bot's activity log as a .txt file."
  await callback_query.message.edit_media(
    InputMediaPhoto(
      parse_mode=enums.ParseMode.HTML,
      media="https://i.ibb.co/zTPJFct8/photo-2025-04-25-12-55-01-7497233558289776672.jpg",
      caption=caption
      ),
      reply_markup=keyboard
    )
# .....,.....,.......,...,.......,....., .....,.....,.......,...,.......,.....,
@bot.on_callback_query(filters.regex("custom_command"))
async def custom_button(client, callback_query):
  keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back to Feature", callback_data="feat_command")]])
  caption = "🖋️ <b>Custom File Name</b>\n\nSet a custom suffix added before the file extension during upload."
  await callback_query.message.edit_media(
    InputMediaPhoto(
      parse_mode=enums.ParseMode.HTML,
      media="https://i.ibb.co/zTPJFct8/photo-2025-04-25-12-55-01-7497233558289776672.jpg",
      caption=caption
      ),
      reply_markup=keyboard
  )
# .....,.....,.......,...,.......,....., .....,.....,.......,...,.......,.....,
@bot.on_callback_query(filters.regex("titlle_command"))
async def titlle_button(client, callback_query):
  keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back to Feature", callback_data="feat_command")]])
  caption = "🏷️ <b>Custom Title</b>\n\nAdd a custom title at the beginning of uploads.\n\n<b>Note:</b> The title must be enclosed in (parentheses). Works best with appx-style .txt files."
  await callback_query.message.edit_media(
    InputMediaPhoto(
      parse_mode=enums.ParseMode.HTML,
      media="https://i.ibb.co/zTPJFct8/photo-2025-04-25-12-55-01-7497233558289776672.jpg",
      caption=caption
      ),
      reply_markup=keyboard
  )
# .....,.....,.......,...,.......,....., .....,.....,.......,...,.......,.....,
@bot.on_callback_query(filters.regex("broadcast_command"))
async def handle_broadcast_command(client, callback_query):
  keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back to Feature", callback_data="feat_command")]])
  caption = "📢 <b>Broadcast</b>\n\n◆ /broadcast — Send a message to all users.\n◆ /broadusers — View all users in the broadcast list."
  await callback_query.message.edit_media(
    InputMediaPhoto(
      parse_mode=enums.ParseMode.HTML,
      media="https://i.ibb.co/zTPJFct8/photo-2025-04-25-12-55-01-7497233558289776672.jpg",
      caption=caption
      ),
      reply_markup=keyboard
  )
# .....,.....,.......,...,.......,....., .....,.....,.......,...,.......,.....,
@bot.on_callback_query(filters.regex("txt_maker_command"))
async def editor_button(client, callback_query):
  keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back to Feature", callback_data="feat_command")]])
  caption = "📝 <b>Text File Creator</b>\n\n◆ /t2t — Convert text to a .txt file."
  await callback_query.message.edit_media(
    InputMediaPhoto(
      parse_mode=enums.ParseMode.HTML,
      media="https://i.ibb.co/zTPJFct8/photo-2025-04-25-12-55-01-7497233558289776672.jpg",
      caption=caption
      ),
      reply_markup=keyboard
  )
# .....,.....,.......,...,.......,....., .....,.....,.......,...,.......,.....,
@bot.on_callback_query(filters.regex("yt_command"))
async def y2t_button(client, callback_query):
  keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back to Feature", callback_data="feat_command")]])
  caption = f"**YouTube Commands:**\n\n◆/y2t - 🔪 YouTube Playlist → .txt Converter\n◆/ytm - 🎶 YouTube → .mp3 downloader\n\n<blockquote><b>◆YouTube → .mp3 downloader\n01. Send YouTube Playlist.txt file\n02. Send single or multiple YouTube links set\neg.\n`https://www.youtube.com/watch?v=xxxxxx\nhttps://www.youtube.com/watch?v=yyyyyy`</b></blockquote>"
  await callback_query.message.edit_media(
    InputMediaPhoto(
      parse_mode=enums.ParseMode.HTML,
      media="https://i.ibb.co/zTPJFct8/photo-2025-04-25-12-55-01-7497233558289776672.jpg",
      caption=caption
      ),
      reply_markup=keyboard
  )

# .....,.....,.......,...,.......,....., .....,.....,.......,...,.......,.....,
@bot.on_callback_query(filters.regex("html_command"))
async def handle_html_command(client, callback_query):
  keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back to Feature", callback_data="feat_command")]])
  caption = "🌐 <b>HTML Converter</b>\n\n◆ /t2h — Convert a .txt file to .html format."
  await callback_query.message.edit_media(
    InputMediaPhoto(
      parse_mode=enums.ParseMode.HTML,
      media="https://i.ibb.co/zTPJFct8/photo-2025-04-25-12-55-01-7497233558289776672.jpg",
      caption=caption
      ),
      reply_markup=keyboard
  )

# .....,.....,.......,...,.......,....., .....,.....,.......,...,.......,.....,


# ── Wire all callback_query handlers into HTTP polling engine ─────────────────
def _wire_cb_handlers():
    import re as _re
    # Extract (pattern, fn) from all @bot.on_callback_query decorators
    from pyrogram.dispatcher import Dispatcher as _D
    try:
        for group in _D.groups if hasattr(_D, 'groups') else []:
            pass
    except Exception:
        pass
    # Manual registration of all known callback patterns → their handler fns
    _cb_map = [
        ("back_to_main_menu",        back_to_main_menu),
        ("cmd_command",              cmd),
        ("user_command",             help_button),
        ("owner_command",            help_button_owner),
        ("upgrade_command",          upgrade_button),
        ("setttings",                settings_button),
        ("thummbnail_command",       handle_thumbnail_command),
        ("wattermark_command",       handle_watermark_menu),
        ("set_token_command",        handle_token_menu),
        ("caption_style_command",    handle_caption),
        ("file_name_command",        handle_file_name),
        ("viideo_thumbnail_command", video_thumbnail),
        ("quality_command",          handle_quality),
        ("quality_144",              set_quality_144),
        ("quality_240",              set_quality_240),
        ("quality_360",              set_quality_360),
        ("quality_480",              set_quality_480),
        ("quality_720",              set_quality_720),
        ("quality_1080",             set_quality_1080),
        ("topic_command",            handle_topic_command),
        ("resset_command",           handle_reset_cmd),
        ("feat_command",             feature_button),
        ("pin_command",              pin_button),
        ("watermark_command",        watermark_button),
        ("reset_command",            restart_button),
        ("logs_command",             handle_logs_command),
        ("custom_command",           custom_button),
        ("titlle_command",           titlle_button),
        ("broadcast_command",        handle_broadcast_command),
        ("txt_maker_command",        editor_button),
        ("yt_command",               y2t_button),
        ("html_command",             handle_html_command),
        ("add_credit_command",       credit),
        ("cp_token_command",         handle_token),
        ("pw_token_command",         handle_pw_token),
        ("cw_token_command",         handle_cw_token),
        ("video_watermark_command",  video_watermark),
        ("pddf_thumbnail_command",   pdf_thumbnail_button),
        ("pdf_watermark_command",    pdf_watermark_button),
    ]
    for pattern, fn in _cb_map:
        try:
            _register_cb(pattern, fn)
        except Exception as _e:
            logging.warning(f"[WIRE] could not register cb {pattern}: {_e}")

    # Register Plan Manager callbacks (pm_* prefix)
    _pm.wire_plan_callbacks(_register_cb)

# called after all handlers defined (at bottom of file before __main__)


# .....,.....,.......,...,.......,....., .....,.....,.......,...,.......,.....,

@bot.on_message(filters.command(["id"]))
async def id_command(client, message: Message):
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton(text="Send to Owner", url=f"tg://openmessage?user_id={OWNER}")]])
    chat_id = message.chat.id
    text = f"<blockquote expandable><b>The ID of this chat id is:</b></blockquote>\n`{chat_id}`"
    
    if str(chat_id).startswith("-100"):
        await message.reply_text(text)
    else:
        await message.reply_text(text, reply_markup=keyboard)

# .....,.....,.......,...,.......,....., .....,.....,.......,...,.......,.....,

@bot.on_message(filters.private & filters.command(["info"]))
async def info(bot: Client, update: Message):
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton(text="📞 Contact", url=f"tg://openmessage?user_id={OWNER}")]])
    text = (
        f"╭────────────────╮\n"
        f"│✨ **Your Telegram Info**✨ \n"
        f"├────────────────\n"
        f"├🔹**Name :** `{update.from_user.first_name} {update.from_user.last_name if update.from_user.last_name else 'None'}`\n"
        f"├🔹**User ID :** @{update.from_user.username}\n"
        f"├🔹**TG ID :** `{update.from_user.id}`\n"
        f"├🔹**Profile :** {update.from_user.mention}\n"
        f"╰────────────────╯"
    )
    
    await update.reply_text(        
        text=text,
        disable_web_page_preview=True,
        reply_markup=keyboard
    )

# .....,.....,.......,...,.......,....., .....,.....,.......,...,.......,.....,
@bot.on_message(filters.command(["logs"]))
async def send_logs(client: Client, m: Message):
    # Admin only check — use from_user.id (falls back to chat.id for private)
    _uid = (m.from_user.id if m.from_user else None) or m.chat.id
    logging.warning(f"[LOGS] admin check uid={_uid} OWNER={OWNER} OWNER_ID={OWNER_ID}")
    if _uid not in {OWNER, OWNER_ID, OWNER_ID2} and not db.is_admin(_uid):
        await m.reply_text("❌ **This command is only available to admins.**")
        return
    
    import glob as _g
    # Find logs.txt — check both CWD and script directory
    _log_paths = ["logs.txt", os.path.join(os.path.dirname(__file__), "logs.txt"),
                  os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs.txt")]
    _log_file = next((p for p in _log_paths if os.path.isfile(p)), None)
    if not _log_file:
        await m.reply_text(f"❌ **logs.txt not found.**\nSearched: {_log_paths}")
        return
    try:
        sent = await m.reply_text("**📤 Sending logs...**")
        await m.reply_document(document=_log_file, caption="📋 Bot Logs")
        await sent.delete()
    except Exception as e:
        logging.exception(f"[LOGS] send failed: {e}")
        await m.reply_text(f"**Error sending logs:**\n<blockquote>{e}</blockquote>")

# ══════════════════════════════════════════════════════════════
# PLAN MANAGEMENT — quick text commands
# /addplan  → 2-step: bot asks for content, owner sends rich message
# /delplan  → /delplan PlanName
# /plans    → list all plans
# ══════════════════════════════════════════════════════════════

def _is_owner(m) -> bool:
    uid = (m.from_user.id if m.from_user else None) or m.chat.id
    return uid in {OWNER, OWNER_ID, OWNER_ID2} or db.is_admin(uid)

# ── /addplan — 2-step: owner sends next message, saved as-is ─────────────────
@bot.on_message(filters.command("addplan"))
async def admin_addplan(client, m):
    if not _is_owner(m):
        await m.reply_text("❌ Owner only.")
        return
    chat_id = m.chat.id
    prompt = await m.reply_text(
        "📩 <b>Send your plan text now.</b>\n\n"
        "Whatever message you send — <b>it will be saved exactly as-is.</b>\n"
        "Bold, italic, emoji, blockquote — all formatting is supported.\n\n"
        "<i>To cancel, send /cancel.</i>",
        parse_mode=enums.ParseMode.HTML,
    )
    try:
        content_msg = await bot.listen(chat_id, timeout=300)
    except (asyncio.TimeoutError, TimeoutError):
        try: await prompt.delete()
        except Exception: pass
        await m.reply_text("⏰ Timed out. Use /addplan again.")
        return
    if content_msg.text and content_msg.text.strip() in ("/cancel", "/stop"):
        await m.reply_text("❌ Cancelled.")
        return
    raw_dict = content_msg._msg if hasattr(content_msg, "_msg") else {}
    content_html = _pm.msg_to_html(raw_dict) if raw_dict else (content_msg.text or "")
    db.set_setting("default_plan_content", content_html)
    logging.warning(f"[PLAN] saved by={chat_id} len={len(content_html)}")
    try: await prompt.delete()
    except Exception: pass
    await m.reply_text("✅ <b>Plan saved successfully!</b>", parse_mode=enums.ParseMode.HTML)

# ── /plans — show the owner their current saved plan ─────────────────────────
@bot.on_message(filters.command("plans"))
async def admin_listplans(client, m):
    if not _is_owner(m):
        await m.reply_text("❌ Owner only.")
        return
    content = db.get_setting("default_plan_content")
    if not content:
        await m.reply_text(
            "❌ <b>No plan saved yet.</b>\n\nUse /addplan to set one.",
            parse_mode=enums.ParseMode.HTML,
        )
        return
    await m.reply_text(
        f"✅ <b>Current saved plan:</b>\n\n{content}",
        parse_mode=enums.ParseMode.HTML,
    )

# ── /clearplans — delete all saved plans from the database ───────────────────
@bot.on_message(filters.command("clearplans"))
async def admin_clearplans(client, m):
    if not _is_owner(m):
        await m.reply_text("❌ Owner only.")
        return
    try:
        db.db["plans"].delete_many({})
        db.set_setting("default_plan_content", "")
        db.set_setting("welcome_plan", "")
        db.set_setting("welcome_plan_custom", "")
        await m.reply_text(
            "🗑 <b>All plans cleared!</b>\n\n"
            "Use /addplan to set a new one.",
            parse_mode=enums.ParseMode.HTML,
        )
    except Exception as e:
        await m.reply_text(f"❌ Error: {e}")

# ── /delplan — specific plan delete (backward compat) ─────────────────────────
@bot.on_message(filters.command("delplan"))
async def admin_delplan(client, m):
    if not _is_owner(m):
        await m.reply_text("❌ Owner only.")
        return
    # If no arg — clear the saved default plan text
    parts = m.text.split(None, 1)
    if len(parts) < 2:
        db.set_setting("default_plan_content", "")
        await m.reply_text("✅ Default plan cleared.")
        return
    name = parts[1].strip()
    ok = db.delete_plan(name)
    if ok:
        await m.reply_text(f"✅ Plan '{name}' deleted.")
    else:
        await m.reply_text(f"❌ '{name}' not found. Use /plans to check.")

# .....,.....,.......,...,.......,....., .....,.....,.......,...,.......,.....,
@bot.on_message(filters.command(["reset"]))
async def restart_handler(_, m):
    _uid = (m.from_user.id if m.from_user else None) or m.chat.id
    if _uid not in {OWNER, OWNER_ID, OWNER_ID2}:
        return
    else:
        await m.reply_text("🔄 Restarting the bot, please wait...")
        os.execl(sys.executable, sys.executable, *sys.argv)

# .....,.....,.......,...,.......,....., .....,.....,.......,...,.......,.....,
@bot.on_message(filters.command("stop") & filters.private)
async def cancel_handler(client: Client, m: Message):
    bot_username = (await client.get_me()).username
    if not db.is_user_authorized(m.chat.id, bot_username):
        print(f"User ID not authorized", m.chat.id)
        await bot.send_message(
            m.chat.id,
            f"<blockquote>⚠️ <b>You are not a Premium Member.</b>\n"
            f"Please contact the owner to get access.\n"
            f"Your User ID: <code>{m.chat.id}</code></blockquote>",
            parse_mode=enums.ParseMode.HTML,
        )
        return
    else:
        if globals.processing_request:
            globals.cancel_requested = True
            await m.delete()
            cancel_message = await m.reply_text("**🚦 Process cancel request received. Stopping after current process...**")
            await asyncio.sleep(30)  # 30 second wait
            await cancel_message.delete()
        else:
            await m.reply_text("**⚡ No active process to cancel.**")
            
# .....,.....,.......,...,.......,....., .....,.....,.......,...,.......,.....,
@bot.on_message(filters.command("broadcast") & filters.private)
async def call_broadcast_handler(client: Client, message: Message):
    await broadcast_handler(client, message)
    
# .....,.....,.......,...,.......,....., .....,.....,.......,...,.......,.....,
@bot.on_message(filters.command("broadusers") & filters.private)
async def call_broadusers_handler(client: Client, message: Message):
    await broadusers_handler(client, message)
    
# .....,.....,.......,...,.......,....., .....,.....,.......,...,.......,.....,
@bot.on_message(filters.command("cookies") & filters.private)
async def call_cookies_handler(client: Client, m: Message):
    await cookies_handler(client, m)

# .....,.....,.......,...,.......,....., .....,.....,.......,...,.......,.....,
@bot.on_message(filters.command(["t2t"]))
async def call_text_to_txt(bot: Client, m: Message):
    await text_to_txt(bot, m)

# .....,.....,.......,...,.......,....., .....,.....,.......,...,.......,.....,
@bot.on_message(filters.command(["y2t"]))
async def call_y2t_handler(bot: Client, m: Message):
    await y2t_handler(bot, m)

# .....,.....,.......,...,.......,....., .....,.....,.......,...,.......,.....,
@bot.on_message(filters.command(["ytm"]))
async def call_ytm_handler(bot: Client, m: Message):
    await ytm_handler(bot, m)

# .....,.....,.......,...,.......,....., .....,.....,.......,...,.......,.....
@bot.on_message(filters.command("getcookies") & filters.private)
async def call_getcookies_handler(client: Client, m: Message):
    # Admin only check — use from_user.id (falls back to chat.id for private)
    _uid = (m.from_user.id if m.from_user else None) or m.chat.id
    logging.warning(f"[GETCOOKIES] admin check uid={_uid} OWNER={OWNER} OWNER_ID={OWNER_ID}")
    if _uid not in {OWNER, OWNER_ID, OWNER_ID2} and not db.is_admin(_uid):
        await m.reply_text("❌ **This command is only available to admins.**")
        return
    await getcookies_handler(client, m)

#...............…........# .....,.....,.......,...,.......,....., .....,.....,.......,...,.......,.....,
@bot.on_message(filters.command(["t2h"]))
async def call_html_handler(bot: Client, message: Message):
    await html_handler(bot, message)
    
# .....,.....,.......,...,.......,....., .....,.....,.......,...,.......,.....,
@bot.on_message(filters.private & (filters.document | filters.text))
async def call_drm_handler(bot: Client, m: Message):
    logging.warning(f"[DRM] called: doc={bool(m.document)} text={repr(m.text)[:50]} chat={m.chat.id}")
    try:
        await drm_handler(bot, m)
    except Exception as _e:
        logging.exception(f"[DRM] crash: {_e}")
        try:
            await m.reply_text(f"❌ Error: {_e}")
        except Exception:
            pass
                          
# .....,.....,.......,...,.......,....., .....,.....,.......,...,.......,.....,


# .....,.....,.......,...,.......,....., .....,.....,.......,...,.......,.....,
# ── Auto disk cleanup (runs every 30 min) ─────────────────────────────────────
import shutil as _shutil
import glob as _glob

async def _auto_cleanup():
    """Delete temp files older than 1 hour every 30 minutes."""
    while True:
        await asyncio.sleep(1800)  # 30 min
        now = time.time()
        cleaned = 0
        for pattern in ["*.mp4", "*.mkv", "*.pdf", "*.jpg", "*.m4a", "*.webm", "*.mp3"]:
            for f in _glob.glob(pattern):
                try:
                    if os.path.isfile(f) and (now - os.path.getmtime(f)) > 3600:
                        os.remove(f)
                        cleaned += 1
                except Exception:
                    pass
        for d in ["downloads", "temp_zip_*"]:
            for folder in _glob.glob(d):
                try:
                    if os.path.isdir(folder) and (now - os.path.getmtime(folder)) > 3600:
                        _shutil.rmtree(folder, ignore_errors=True)
                        cleaned += 1
                except Exception:
                    pass
        if cleaned:
            print(f"🧹 Auto-cleanup: removed {cleaned} stale temp files")

# .....,.....,.......,...,.......,....., .....,.....,.......,...,.......,.....,
@bot.on_message(filters.command(["status", "ping"]) & filters.private)
async def status_command(client: Client, m: Message):
    import psutil, platform
    cpu    = psutil.cpu_percent(interval=0.5)
    ram    = psutil.virtual_memory()
    disk   = psutil.disk_usage("/")
    uptime = time.time() - psutil.boot_time()
    h = int(uptime // 3600); mn = int((uptime % 3600) // 60)

    # Disk usage of downloads folder
    dl_size = sum(
        os.path.getsize(f) for f in _glob.glob("downloads/**/*", recursive=True)
        if os.path.isfile(f)
    ) if os.path.exists("downloads") else 0

    text = (
        f"⚡ **Bot Status** ⚡\n\n"
        f"🖥️ **CPU** : `{cpu:.1f}%`\n"
        f"🧠 **RAM** : `{ram.percent:.1f}%` ({ram.used // 1024**2} MB / {ram.total // 1024**2} MB)\n"
        f"💾 **Disk** : `{disk.percent:.1f}%` free `{disk.free // 1024**3} GB`\n"
        f"📂 **Temp** : `{dl_size // 1024**2} MB` in downloads/\n"
        f"⏱️ **Uptime** : `{h}h {mn}m`\n"
        f"🔄 **Processing** : `{'Yes 🔴' if globals.processing_request else 'No 🟢'}`\n"
    )
    await m.reply_text(text)

# .....,.....,.......,...,.......,....., .....,.....,.......,...,.......,.....,
@bot.on_message(filters.command("clean") & filters.private)
async def clean_command(client: Client, m: Message):
    if not db.is_admin(m.chat.id):
        await m.reply_text("❌ Admin only command.")
        return
    msg = await m.reply_text("🧹 Cleaning temp files...")
    cleaned = 0
    for pattern in ["*.mp4", "*.mkv", "*.pdf", "*.jpg", "*.m4a", "*.webm", "*.mp3"]:
        for f in _glob.glob(pattern):
            try:
                os.remove(f); cleaned += 1
            except Exception:
                pass
    for folder in _glob.glob("downloads") + _glob.glob("temp_zip_*"):
        try:
            _shutil.rmtree(folder, ignore_errors=True); cleaned += 1
        except Exception:
            pass
    await msg.edit(f"✅ Cleaned **{cleaned}** temp files!")


def reset_and_set_commands():
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/setMyCommands"
    requests.post(url, json={"commands": []})
    commands = [
        {"command": "start",       "description": "✅ Check Alive the Bot"},
        {"command": "stop",        "description": "🚫 Stop the ongoing process"},
        {"command": "id",          "description": "🆔 Get Your ID"},
        {"command": "info",        "description": "ℹ️ Check Your Information"},
        {"command": "plan",        "description": "📋 Check Your Plan"},
        {"command": "status",      "description": "⚡ Bot Health & Disk Status"},
        {"command": "clean",       "description": "🧹 Clean Temp Files (Admin)"},
        {"command": "y2t",         "description": "🔪 YouTube → .txt Converter"},
        {"command": "ytm",         "description": "🎶 YouTube → .mp3 downloader"},
        {"command": "t2t",         "description": "📟 Text → .txt Generator"},
        {"command": "t2h",         "description": "🌐 .txt → .html Converter"},
        {"command": "cookies",     "description": "🍪 Upload YT Cookies"},
        {"command": "getcookies",  "description": "🔍 Get Current YT Cookies"},
        {"command": "logs",        "description": "🖨️ View Bot Activity"},
        {"command": "add",         "description": "▶️ Add Authorisation"},
        {"command": "remove",      "description": "⏸️ Remove Authorisation"},
        {"command": "users",       "description": "👥 All Premium Users"},
        {"command": "broadcast",   "description": "📢 Broadcast to All Users"},
        {"command": "broadusers",  "description": "👁️ All Broadcasting Users"},
        {"command": "reset",       "description": "✅ Reset the Bot"},
        {"command": "addplan",     "description": "💳 Add Plan (Admin)"},
        {"command": "delplan",     "description": "🗑️ Delete Plan (Admin)"},
        {"command": "plans",       "description": "📋 View All Plans (Admin)"},
        {"command": "whoami",      "description": "🆔 Debug: Show your Telegram ID"},
        {"command": "clearplans",  "description": "🗑️ Clear All Plans (Admin)"},
    ]
    requests.post(url, json={"commands": commands})


def notify_owner():
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": OWNER,
        "text": "🚀 <b>Bot restarted successfully!</b>\n⚡ All systems are up and running.",
        "parse_mode": "HTML",
    }
    requests.post(url, data=data)


import traceback as _traceback
import logging as _logging

def _handle_unhandled_exception(exc_type, exc_value, exc_tb):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_tb)
        return
    _logging.critical("Unhandled exception caused crash:", exc_info=(exc_type, exc_value, exc_tb))

sys.excepthook = _handle_unhandled_exception


async def _startup():
    """Runs after bot.start() — background tasks + notify + keep-alive via idle()."""
    asyncio.create_task(_auto_cleanup())
    asyncio.create_task(_http_poll_loop())   # ← HTTP fallback polling

    # Seed default plan content if not already set by owner
    try:
        if not db.get_setting("default_plan_content"):
            db.set_setting("default_plan_content", _DEFAULT_PLAN_CONTENT)
            logging.warning("[STARTUP] Default plan content seeded to DB")
    except Exception as _pe:
        logging.warning(f"[STARTUP] Could not seed plan: {_pe}")

    # Webhook check (visible in logs, runs after bot.start)
    try:
        import requests as _req
        _whi = _req.get(
            f"https://api.telegram.org/bot{BOT_TOKEN}/getWebhookInfo", timeout=10
        ).json()
        logging.warning(f"[STARTUP] WebhookInfo: {_whi}")
        _req.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/deleteWebhook",
            data={"drop_pending_updates": "true"}, timeout=10,
        )
        logging.warning("[STARTUP] Webhook cleared")
    except Exception as _we:
        logging.warning(f"[STARTUP] webhook check failed: {_we}")

    try:
        me = await bot.get_me()
        _logging.info(f"[STARTUP] Connected as @{me.username} (id={me.id})")
        try:
            with open("bot_status.json", "w") as _sf:
                json.dump({
                    "connected": True,
                    "username": me.username,
                    "id": me.id,
                    "name": me.first_name,
                    "time": time.strftime("%Y-%m-%d %H:%M:%S"),
                }, _sf)
        except Exception:
            pass
        for _admin in {OWNER, OWNER_ID, *ADMINS}:
            try:
                await bot.send_message(
                    _admin,
                    f"✅ <b>@{me.username} is live!</b>\nSend /start to begin.",
                    parse_mode=enums.ParseMode.HTML,
                )
                break
            except Exception as e:
                _logging.warning(f"[STARTUP] Could not message {_admin}: {e}")
    except Exception as e:
        _logging.critical(f"[STARTUP] get_me() failed: {e}")
        try:
            with open("bot_status.json", "w") as _sf:
                json.dump({"connected": False, "error": str(e),
                           "time": time.strftime("%Y-%m-%d %H:%M:%S")}, _sf)
        except Exception:
            pass


async def _main():
    from pyrogram.errors import FloodWait as _FloodWait
    for _attempt in range(10):
        try:
            await bot.start()
            break
        except _FloodWait as _fw:
            _logging.warning(
                f"[STARTUP] Telegram FloodWait: waiting {_fw.value}s before retry "
                f"(attempt {_attempt+1}/10)..."
            )
            await asyncio.sleep(_fw.value + 5)
        except Exception as _e:
            _logging.critical(f"[STARTUP] bot.start() failed: {_e}")
            raise
    else:
        _logging.critical("[STARTUP] Could not start after 10 FloodWait retries. Exiting.")
        return

    _logging.info("[STARTUP] bot.start() completed — handlers active")

    # Kick-start update delivery for fresh bot MTProto sessions
    try:
        from pyrogram.raw.functions.updates import GetState as _GetState
        _state = await bot.invoke(_GetState())
        _logging.warning(f"[STARTUP] GetState OK pts={_state.pts} date={_state.date}")
    except Exception as _gse:
        _logging.warning(f"[STARTUP] GetState failed (non-fatal): {_gse}")

    await _startup()
    await idle()
    await bot.stop()


_wire_cb_handlers()

if __name__ == "__main__":
    print(r"""
    ╔══════════════════════════════════════════════════════╗
    ║   🦅  G O L D E N   E A G L E   B O T                 ║
    ║        U L T I M A T E   E D I T I O N                ║
    ║   Smooth · Futuristic · DRM + Non-DRM · A-to-Z        ║
    ╚══════════════════════════════════════════════════════╝
    """)
    for _sf in ["bot.session", "bot.session-journal"]:
        try:
            if os.path.exists(_sf):
                os.remove(_sf)
        except Exception:
            pass

    reset_and_set_commands()
    notify_owner()

    # Use a single explicit event loop so pyrogram's internals stay on the same loop
    import asyncio as _asyncio
    _loop = _asyncio.new_event_loop()
    _asyncio.set_event_loop(_loop)
    try:
        _loop.run_until_complete(_main())
    finally:
        _loop.close()
