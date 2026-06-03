"""
Plan Management System
======================
Owner-only CRUD via Telegram inline keyboard.
Welcome Plan for non-premium users on /start.
Formatting preserved via entity→HTML conversion.
Variable substitution engine built-in.
"""
import asyncio
import logging
import html as _html_mod
from datetime import datetime
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto
from pyrogram import enums

# ── Lazy imports to avoid circular deps ──────────────────────────────────────
def _get_db():
    from db import db
    return db

def _get_vars():
    from vars import OWNER, OWNER_ID, OWNER_ID2, ADMINS, BOT_TOKEN
    return OWNER, OWNER_ID, OWNER_ID2, ADMINS, BOT_TOKEN

def _get_listen():
    from main import _LISTEN_FUTURES, bot
    return _LISTEN_FUTURES, bot


# ═══════════════════════════════════════════════════════════════════════════════
# ENTITY → HTML CONVERTER
# Preserves all Telegram formatting: bold, italic, spoiler, blockquote, etc.
# Uses UTF-16 offsets exactly as Telegram Bot API specifies.
# ═══════════════════════════════════════════════════════════════════════════════

def ents_to_html(text: str, entities: list) -> str:
    """
    Convert Telegram message text + entities list into an HTML string.
    100% formatting-safe: handles UTF-16 offsets, nested entities, all types.
    """
    if not text:
        return ""
    if not entities:
        return _html_mod.escape(text)

    # Telegram Bot API uses UTF-16 code unit offsets
    utf16 = text.encode("utf-16-le")

    # Build open/close events: (utf16_position, priority, tag_string)
    # priority 0 = close first (at same position closes happen before opens)
    events = []
    for ent in entities:
        off = ent.get("offset", 0)
        lng = ent.get("length", 0)
        end = off + lng
        etype = ent.get("type", "")

        if etype == "bold":
            o, c = "<b>", "</b>"
        elif etype == "italic":
            o, c = "<i>", "</i>"
        elif etype == "underline":
            o, c = "<u>", "</u>"
        elif etype == "strikethrough":
            o, c = "<s>", "</s>"
        elif etype == "spoiler":
            o, c = "<tg-spoiler>", "</tg-spoiler>"
        elif etype == "code":
            o, c = "<code>", "</code>"
        elif etype == "pre":
            lang = ent.get("language", "")
            o = f'<pre><code class="language-{lang}">' if lang else "<pre>"
            c = "</code></pre>" if lang else "</pre>"
        elif etype == "text_link":
            url = _html_mod.escape(ent.get("url", "#"), quote=True)
            o, c = f'<a href="{url}">', "</a>"
        elif etype == "blockquote":
            o, c = "<blockquote>", "</blockquote>"
        elif etype == "expandable_blockquote":
            o, c = "<blockquote expandable>", "</blockquote>"
        else:
            continue

        events.append((off, 1, o))   # 1 → opens after closes at same pos
        events.append((end, 0, c))   # 0 → closes before opens at same pos

    events.sort(key=lambda x: (x[0], x[1]))

    result = []
    last = 0  # UTF-16 units consumed
    for pos, _, tag in events:
        chunk = utf16[last * 2 : pos * 2].decode("utf-16-le")
        result.append(_html_mod.escape(chunk))
        result.append(tag)
        last = pos

    # Remaining text after all tags
    tail = utf16[last * 2 :].decode("utf-16-le")
    result.append(_html_mod.escape(tail))
    return "".join(result)


def msg_to_html(msg_dict: dict) -> str:
    """
    Convert a raw HTTP API message dict to HTML-preserved string.
    Captures text + entities or caption + caption_entities.
    """
    text = msg_dict.get("text") or msg_dict.get("caption") or ""
    entities = (
        msg_dict.get("entities")
        or msg_dict.get("caption_entities")
        or []
    )
    return ents_to_html(text, entities)


# ═══════════════════════════════════════════════════════════════════════════════
# VARIABLE SUBSTITUTION ENGINE
# ═══════════════════════════════════════════════════════════════════════════════

def render_plan_content(content: str, user_data: dict) -> str:
    """
    Replace all {variable} placeholders in plan content with real values.
    Input content is HTML (already entity-converted). Variables inside
    HTML-escaped text need special handling.

    user_data keys: first_name, last_name, username, user_id, role,
                    plan_name, expiry_date, days_left, mention
    """
    first = user_data.get("first_name", "")
    last  = user_data.get("last_name", "") or ""
    uname = user_data.get("username", "") or ""
    uid   = str(user_data.get("user_id", ""))

    # Override mention if explicitly provided (already HTML)
    _mention_override = user_data.get("mention")
    if _mention_override and _mention_override.startswith("<a "):
        _mention_val = _mention_override
    else:
        _mention_val = f'<a href="tg://user?id={uid}">{_html_mod.escape(first or uid)}</a>'

    variables = {
        "{first_name}":  _html_mod.escape(first),
        "{last_name}":   _html_mod.escape(last),
        "{full_name}":   _html_mod.escape((first + " " + last).strip()),
        "{username}":    _html_mod.escape(("@" + uname) if uname else ""),
        "{user_id}":     uid,
        "{mention}":     _mention_val,
        "{role}":        _html_mod.escape(user_data.get("role", "User")),
        "{plan_name}":   _html_mod.escape(user_data.get("plan_name", "")),
        "{expiry_date}": _html_mod.escape(str(user_data.get("expiry_date", ""))),
        "{days_left}":   _html_mod.escape(str(user_data.get("days_left", ""))),
        "{credit}":      user_data.get("credit", ""),
        "{credit_link}": user_data.get("credit_link", ""),
    }

    for var, val in variables.items():
        content = content.replace(var, val)
    return content


# ═══════════════════════════════════════════════════════════════════════════════
# OWNER CHECK
# ═══════════════════════════════════════════════════════════════════════════════

def _is_plan_owner(user_id: int) -> bool:
    OWNER, OWNER_ID, OWNER_ID2, ADMINS, _ = _get_vars()
    return user_id in {OWNER, OWNER_ID, OWNER_ID2}


# ═══════════════════════════════════════════════════════════════════════════════
# KEYBOARDS
# ═══════════════════════════════════════════════════════════════════════════════

def _main_menu_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ Add Plan",        callback_data="pm_add")],
        [InlineKeyboardButton("✏️ Edit Plan",       callback_data="pm_edit_list"),
         InlineKeyboardButton("🗑 Delete Plan",      callback_data="pm_del_list")],
        [InlineKeyboardButton("👀 View Plans",       callback_data="pm_view_list")],
        [InlineKeyboardButton("📢 Set Welcome Plan", callback_data="pm_welcome_list")],
        [InlineKeyboardButton("❌ Close",            callback_data="pm_close")],
    ])


def _plan_list_kb(plans: list, action_prefix: str, back_cb: str = "pm_main") -> InlineKeyboardMarkup:
    rows = []
    for p in plans:
        name = p["plan_name"]
        label = f"{name}"
        if p.get("status") == "disabled":
            label = f"⛔ {name}"
        rows.append([InlineKeyboardButton(label, callback_data=f"{action_prefix}:{name[:30]}")])
    rows.append([InlineKeyboardButton("🔙 Back", callback_data=back_cb)])
    return InlineKeyboardMarkup(rows)


def _edit_fields_kb(plan_name: str) -> InlineKeyboardMarkup:
    n = plan_name[:25]
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📝 Name",        callback_data=f"pm_ef:name:{n}"),
         InlineKeyboardButton("📅 Duration",    callback_data=f"pm_ef:duration:{n}")],
        [InlineKeyboardButton("💰 Price",       callback_data=f"pm_ef:price:{n}"),
         InlineKeyboardButton("📄 Description", callback_data=f"pm_ef:description:{n}")],
        [InlineKeyboardButton("🖊 Content",     callback_data=f"pm_ef:content:{n}")],
        [InlineKeyboardButton("🔄 Toggle Status", callback_data=f"pm_ef:toggle:{n}")],
        [InlineKeyboardButton("🔙 Back",        callback_data="pm_edit_list")],
    ])


def _confirm_del_kb(plan_name: str) -> InlineKeyboardMarkup:
    n = plan_name[:25]
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ Yes, Delete", callback_data=f"pm_del_confirm:{n}"),
         InlineKeyboardButton("❌ Cancel",      callback_data="pm_del_list")],
    ])


# ═══════════════════════════════════════════════════════════════════════════════
# HELPER: listen with timeout
# ═══════════════════════════════════════════════════════════════════════════════

async def _listen(bot, chat_id: int, timeout: int = 180):
    """Wait for next message from user. Returns _Msg or None on timeout."""
    try:
        return await bot.listen(chat_id, timeout=timeout)
    except (asyncio.TimeoutError, TimeoutError):
        return None


# ═══════════════════════════════════════════════════════════════════════════════
# SHOW PLAN PREVIEW
# ═══════════════════════════════════════════════════════════════════════════════

def _format_plan_preview(p: dict) -> str:
    status = "✅ Active" if p.get("status", "active") == "active" else "⛔ Disabled"
    lines = [
        f"📌 <b>Plan: {_html_mod.escape(p.get('plan_name', ''))}</b>",
        f"📅 Duration: <b>{p.get('duration_days', '—')} days</b>",
        f"💰 Price: <b>{_html_mod.escape(p.get('price', '—'))}</b>",
        f"🔘 Status: {status}",
    ]
    if p.get("description"):
        lines.append(f"📝 Description:\n<i>{_html_mod.escape(p['description'])}</i>")
    if p.get("content"):
        lines.append(f"\n📄 <b>Content Preview:</b>\n{p['content'][:300]}{'...' if len(p.get('content','')) > 300 else ''}")
    return "\n".join(lines)


# ═══════════════════════════════════════════════════════════════════════════════
# HANDLER FUNCTIONS — called by _wire_plan_handlers()
# ═══════════════════════════════════════════════════════════════════════════════

async def handle_pm_main(bot, cq):
    uid = cq.from_user.id
    if not _is_plan_owner(uid):
        await cq.answer("❌ Owner only.", show_alert=True)
        return
    await cq.answer()
    await cq.message.edit_text(
        "📋 <b>Plan Manager</b>\n\nSelect an action:",
        reply_markup=_main_menu_kb()
    )


async def handle_pm_close(bot, cq):
    await cq.answer()
    try:
        await bot.delete_messages(cq.chat_id, cq.message_id)
    except Exception:
        await cq.message.edit_text("✅ Closed.")


async def handle_pm_add(bot, cq):
    uid = cq.from_user.id
    if not _is_plan_owner(uid):
        await cq.answer("❌ Owner only.", show_alert=True)
        return
    await cq.answer()
    chat_id = cq.chat_id

    async def _ask(prompt: str) -> str | None:
        await bot.send_message(chat_id, prompt, parse_mode=enums.ParseMode.HTML)
        msg = await _listen(bot, chat_id, timeout=180)
        if msg is None:
            await bot.send_message(chat_id, "⏰ Timed out. Plan creation cancelled.")
            return None
        return msg.text.strip() if msg.text else ""

    async def _ask_rich(prompt: str):
        """Ask and capture with formatting (returns raw _Msg)."""
        await bot.send_message(chat_id, prompt, parse_mode=enums.ParseMode.HTML)
        msg = await _listen(bot, chat_id, timeout=300)
        if msg is None:
            await bot.send_message(chat_id, "⏰ Timed out. Plan creation cancelled.")
        return msg

    await cq.message.edit_text("📝 Starting plan creation...\n\n<i>Send /cancel at any time to abort.</i>")

    # Step 1: Plan name
    name = await _ask("1️⃣ <b>Send the plan name:</b>\n<i>Example: Monthly, Lifetime, Student</i>")
    if not name or name == "/cancel":
        return

    # Step 2: Duration
    days_str = await _ask("2️⃣ <b>Send duration in days:</b>\n<i>Example: 30 / 90 / 365 / 0 (for lifetime)</i>")
    if not days_str or days_str == "/cancel":
        return
    try:
        days = int(days_str)
    except ValueError:
        await bot.send_message(chat_id, "❌ Invalid number. Plan creation cancelled.")
        return

    # Step 3: Price
    price = await _ask("3️⃣ <b>Send the price:</b>\n<i>Example: ₹199 / Free / $9.99</i>")
    if not price or price == "/cancel":
        return

    # Step 4: Short description (plain text)
    desc = await _ask("4️⃣ <b>Send a short description (one line):</b>\n<i>Example: Basic access to all features</i>\n\nSend /skip to leave empty.")
    if desc is None or desc == "/cancel":
        return
    if desc == "/skip":
        desc = ""

    # Step 5: Content (rich text — send as Telegram message with formatting)
    content_msg = await _ask_rich(
        "5️⃣ <b>Send the full plan content:</b>\n\n"
        "✅ Use Telegram formatting (bold, italic, etc.)\n"
        "✅ Supported variables: <code>{first_name}</code> <code>{username}</code> "
        "<code>{plan_name}</code> <code>{expiry_date}</code> <code>{days_left}</code>\n\n"
        "<i>Send the message exactly as you want users to see it.</i>"
    )
    if content_msg is None or content_msg.text == "/cancel":
        return

    # Convert to HTML preserving formatting
    content_html = msg_to_html(content_msg._msg if hasattr(content_msg, "_msg") else {})

    db = _get_db()
    ok = db.add_plan(name, days, price, desc, content_html)
    if ok:
        await bot.send_message(
            chat_id,
            f"✅ <b>Plan created successfully!</b>\n\n"
            f"📌 Name: <b>{_html_mod.escape(name)}</b>\n"
            f"📅 Duration: <b>{days} days</b>\n"
            f"💰 Price: <b>{_html_mod.escape(price)}</b>\n"
            f"📝 Description: <i>{_html_mod.escape(desc) or '—'}</i>\n\n"
            f"📄 Content preview:\n{content_html[:300]}",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Plan Manager", callback_data="pm_main")]]),
            parse_mode=enums.ParseMode.HTML,
        )
    else:
        await bot.send_message(chat_id, "❌ DB error while saving plan.")


async def handle_pm_view_list(bot, cq):
    uid = cq.from_user.id
    if not _is_plan_owner(uid):
        await cq.answer("❌ Owner only.", show_alert=True)
        return
    await cq.answer()
    db = _get_db()
    plans = db.get_all_plans()
    if not plans:
        await cq.message.edit_text(
            "📭 No plans yet.\n\nUse ➕ Add Plan to create one.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="pm_main")]]),
        )
        return
    await cq.message.edit_text(
        "👀 <b>Select a plan to view:</b>",
        reply_markup=_plan_list_kb(plans, "pm_view", "pm_main"),
    )


async def handle_pm_view_plan(bot, cq, plan_name: str):
    uid = cq.from_user.id
    if not _is_plan_owner(uid):
        await cq.answer("❌ Owner only.", show_alert=True)
        return
    await cq.answer()
    db = _get_db()
    p = db.get_plan(plan_name)
    if not p:
        await cq.message.edit_text("❌ Plan not found.")
        return
    preview = _format_plan_preview(p)
    await cq.message.edit_text(
        preview,
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="pm_view_list")]]),
        parse_mode=enums.ParseMode.HTML,
    )


async def handle_pm_edit_list(bot, cq):
    uid = cq.from_user.id
    if not _is_plan_owner(uid):
        await cq.answer("❌ Owner only.", show_alert=True)
        return
    await cq.answer()
    db = _get_db()
    plans = db.get_all_plans()
    if not plans:
        await cq.message.edit_text(
            "📭 No plans to edit.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="pm_main")]]),
        )
        return
    await cq.message.edit_text(
        "✏️ <b>Select a plan to edit:</b>",
        reply_markup=_plan_list_kb(plans, "pm_edit", "pm_main"),
    )


async def handle_pm_edit_plan(bot, cq, plan_name: str):
    uid = cq.from_user.id
    if not _is_plan_owner(uid):
        await cq.answer("❌ Owner only.", show_alert=True)
        return
    await cq.answer()
    db = _get_db()
    p = db.get_plan(plan_name)
    if not p:
        await cq.message.edit_text("❌ Plan not found.")
        return
    await cq.message.edit_text(
        f"✏️ <b>Editing: {_html_mod.escape(plan_name)}</b>\n\nChoose field to edit:",
        reply_markup=_edit_fields_kb(plan_name),
        parse_mode=enums.ParseMode.HTML,
    )


async def handle_pm_edit_field(bot, cq, field: str, plan_name: str):
    uid = cq.from_user.id
    if not _is_plan_owner(uid):
        await cq.answer("❌ Owner only.", show_alert=True)
        return
    await cq.answer()
    chat_id = cq.chat_id
    db = _get_db()
    p = db.get_plan(plan_name)
    if not p:
        await cq.message.edit_text("❌ Plan not found.")
        return

    if field == "toggle":
        new_status = "disabled" if p.get("status", "active") == "active" else "active"
        db.update_plan_field(plan_name, "status", new_status)
        icon = "⛔" if new_status == "disabled" else "✅"
        await cq.message.edit_text(
            f"{icon} Plan <b>{_html_mod.escape(plan_name)}</b> is now <b>{new_status}</b>.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data=f"pm_edit:{plan_name[:25]}")]]),
            parse_mode=enums.ParseMode.HTML,
        )
        return

    prompts = {
        "name":        "Send the new plan name:",
        "duration":    "Send new duration in days (number):",
        "price":       "Send new price (e.g. ₹299):",
        "description": "Send new short description (or /skip):",
        "content":     (
            "Send the new full content:\n\n"
            "✅ Use Telegram formatting\n"
            "✅ Variables: {first_name} {plan_name} {expiry_date} etc.\n\n"
            "Send the message exactly as you want users to see it."
        ),
    }
    prompt = prompts.get(field, f"Send new value for {field}:")

    await bot.send_message(chat_id, f"✏️ <b>Editing {field} of «{_html_mod.escape(plan_name)}»</b>\n\n{prompt}",
                           parse_mode=enums.ParseMode.HTML)
    msg = await _listen(bot, chat_id, timeout=300)
    if msg is None or (msg.text and msg.text.strip() == "/cancel"):
        await bot.send_message(chat_id, "❌ Cancelled.")
        return

    if field == "content":
        new_value = msg_to_html(msg._msg if hasattr(msg, "_msg") else {})
    elif field == "duration":
        try:
            new_value = int(msg.text.strip())
        except ValueError:
            await bot.send_message(chat_id, "❌ Must be a number.")
            return
    else:
        new_value = msg.text.strip() if msg.text else ""
        if field == "description" and new_value == "/skip":
            new_value = ""

    # If renaming, handle specially
    if field == "name":
        db.rename_plan(plan_name, new_value)
        await bot.send_message(chat_id,
            f"✅ Plan renamed to <b>{_html_mod.escape(new_value)}</b>.",
            parse_mode=enums.ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Plan Manager", callback_data="pm_main")]]))
    else:
        db_field = "duration_days" if field == "duration" else field
        db.update_plan_field(plan_name, db_field, new_value)
        await bot.send_message(chat_id,
            f"✅ <b>{field.title()}</b> updated for plan <b>{_html_mod.escape(plan_name)}</b>.",
            parse_mode=enums.ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Plan Manager", callback_data="pm_main")]]))


async def handle_pm_del_list(bot, cq):
    uid = cq.from_user.id
    if not _is_plan_owner(uid):
        await cq.answer("❌ Owner only.", show_alert=True)
        return
    await cq.answer()
    db = _get_db()
    plans = db.get_all_plans()
    if not plans:
        await cq.message.edit_text(
            "📭 No plans to delete.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="pm_main")]]),
        )
        return
    await cq.message.edit_text(
        "🗑 <b>Select a plan to delete:</b>",
        reply_markup=_plan_list_kb(plans, "pm_del", "pm_main"),
    )


async def handle_pm_del_plan(bot, cq, plan_name: str):
    uid = cq.from_user.id
    if not _is_plan_owner(uid):
        await cq.answer("❌ Owner only.", show_alert=True)
        return
    await cq.answer()
    await cq.message.edit_text(
        f"⚠️ <b>Delete plan «{_html_mod.escape(plan_name)}»?</b>\n\nThis cannot be undone.",
        reply_markup=_confirm_del_kb(plan_name),
        parse_mode=enums.ParseMode.HTML,
    )


async def handle_pm_del_confirm(bot, cq, plan_name: str):
    uid = cq.from_user.id
    if not _is_plan_owner(uid):
        await cq.answer("❌ Owner only.", show_alert=True)
        return
    await cq.answer("Deleting...")
    db = _get_db()
    ok = db.delete_plan(plan_name)
    if ok:
        await cq.message.edit_text(
            f"✅ Plan <b>{_html_mod.escape(plan_name)}</b> deleted.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Plan Manager", callback_data="pm_main")]]),
            parse_mode=enums.ParseMode.HTML,
        )
    else:
        await cq.message.edit_text("❌ Plan not found or already deleted.")


async def handle_pm_welcome_list(bot, cq):
    uid = cq.from_user.id
    if not _is_plan_owner(uid):
        await cq.answer("❌ Owner only.", show_alert=True)
        return
    await cq.answer()
    db = _get_db()
    plans = db.get_all_plans()
    current = db.get_setting("welcome_plan")

    rows = []
    for p in plans:
        name = p["plan_name"]
        tick = "✅ " if name == current else ""
        rows.append([InlineKeyboardButton(f"{tick}{name}", callback_data=f"pm_setwelcome:{name[:30]}")])

    rows.append([InlineKeyboardButton("✏️ Write Custom Welcome", callback_data="pm_setwelcome_custom")])
    rows.append([InlineKeyboardButton("🔙 Back", callback_data="pm_main")])

    current_note = f"\n\n<i>Current welcome plan: <b>{_html_mod.escape(current or 'None')}</b></i>" if current else ""
    await cq.message.edit_text(
        f"📢 <b>Set Welcome Plan</b>{current_note}\n\nSelect a plan to show non-premium users on /start:",
        reply_markup=InlineKeyboardMarkup(rows),
        parse_mode=enums.ParseMode.HTML,
    )


async def handle_pm_setwelcome(bot, cq, plan_name: str):
    uid = cq.from_user.id
    if not _is_plan_owner(uid):
        await cq.answer("❌ Owner only.", show_alert=True)
        return
    await cq.answer()
    db = _get_db()
    db.set_setting("welcome_plan", plan_name)
    await cq.message.edit_text(
        f"✅ Welcome plan set to <b>{_html_mod.escape(plan_name)}</b>.\n\n"
        f"Non-premium users will see this plan content on /start.",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Plan Manager", callback_data="pm_main")]]),
        parse_mode=enums.ParseMode.HTML,
    )


async def handle_pm_setwelcome_custom(bot, cq):
    uid = cq.from_user.id
    if not _is_plan_owner(uid):
        await cq.answer("❌ Owner only.", show_alert=True)
        return
    await cq.answer()
    chat_id = cq.chat_id

    await cq.message.edit_text(
        "✏️ <b>Send your custom welcome message:</b>\n\n"
        "✅ Use Telegram formatting (bold, italic, blockquote, etc.)\n"
        "✅ Supported variables:\n"
        "<code>{first_name}</code> <code>{username}</code> <code>{user_id}</code> <code>{mention}</code>",
        parse_mode=enums.ParseMode.HTML,
    )
    msg = await _listen(bot, chat_id, timeout=300)
    if msg is None or (msg.text and msg.text.strip() == "/cancel"):
        await bot.send_message(chat_id, "❌ Cancelled.")
        return

    content_html = msg_to_html(msg._msg)
    db = _get_db()
    db.set_setting("welcome_plan_custom", content_html)
    db.set_setting("welcome_plan", "__custom__")
    await bot.send_message(
        chat_id,
        "✅ <b>Custom welcome message saved!</b>\n\n"
        f"Preview:\n{content_html[:400]}",
        parse_mode=enums.ParseMode.HTML,
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Plan Manager", callback_data="pm_main")]]),
    )


# ═══════════════════════════════════════════════════════════════════════════════
# /plan COMMAND — show Plan Manager
# ═══════════════════════════════════════════════════════════════════════════════

async def plan_command(bot, m):
    uid = (m.from_user.id if m.from_user else None) or m.chat.id
    if not _is_plan_owner(uid):
        await m.reply_text("❌ This command is Owner only.")
        return
    await m.reply_text(
        "📋 <b>Plan Manager</b>\n\nSelect an action:",
        reply_markup=_main_menu_kb(),
        parse_mode=enums.ParseMode.HTML,
    )


# ═══════════════════════════════════════════════════════════════════════════════
# WELCOME PLAN — get content for non-premium users
# ═══════════════════════════════════════════════════════════════════════════════

def get_welcome_content(user_data: dict) -> tuple[str, None]:
    """
    Get the welcome plan content for a non-premium user.
    Returns (html_text, None) or (None, None) if no welcome plan set.
    """
    db = _get_db()
    welcome_id = db.get_setting("welcome_plan")
    if not welcome_id:
        return None, None

    if welcome_id == "__custom__":
        raw = db.get_setting("welcome_plan_custom") or ""
    else:
        p = db.get_plan(welcome_id)
        if not p:
            return None, None
        raw = p.get("content", "") or p.get("description", "")

    if not raw:
        return None, None

    rendered = render_plan_content(raw, user_data)
    return rendered, None  # (html_text, parse_mode hint — always HTML)


# ═══════════════════════════════════════════════════════════════════════════════
# CALLBACK ROUTER — wire all pm_* patterns into _CB_HANDLERS
# ═══════════════════════════════════════════════════════════════════════════════

def wire_plan_callbacks(register_cb):
    """
    Register all plan manager callback handlers.
    Call this after _wire_cb_handlers() in main.py.
    register_cb(pattern_str, async_fn)
    """
    import re

    async def _router(bot, cq):
        data = cq.data
        if data == "pm_main":
            await handle_pm_main(bot, cq)
        elif data == "pm_close":
            await handle_pm_close(bot, cq)
        elif data == "pm_add":
            await handle_pm_add(bot, cq)
        elif data == "pm_view_list":
            await handle_pm_view_list(bot, cq)
        elif data.startswith("pm_view:"):
            await handle_pm_view_plan(bot, cq, data[8:])
        elif data == "pm_edit_list":
            await handle_pm_edit_list(bot, cq)
        elif data.startswith("pm_edit:"):
            await handle_pm_edit_plan(bot, cq, data[8:])
        elif data.startswith("pm_ef:"):
            parts = data.split(":", 3)  # pm_ef:field:name
            if len(parts) >= 3:
                _, field, pname = parts[0], parts[1], parts[2]
                await handle_pm_edit_field(bot, cq, field, pname)
        elif data == "pm_del_list":
            await handle_pm_del_list(bot, cq)
        elif data.startswith("pm_del:"):
            await handle_pm_del_plan(bot, cq, data[7:])
        elif data.startswith("pm_del_confirm:"):
            await handle_pm_del_confirm(bot, cq, data[15:])
        elif data == "pm_welcome_list":
            await handle_pm_welcome_list(bot, cq)
        elif data.startswith("pm_setwelcome:"):
            await handle_pm_setwelcome(bot, cq, data[14:])
        elif data == "pm_setwelcome_custom":
            await handle_pm_setwelcome_custom(bot, cq)

    register_cb(r"^pm_", _router)
