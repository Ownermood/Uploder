from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.handlers import MessageHandler
from datetime import datetime
import asyncio
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from db import db
from vars import *

async def handle_subscription_end(client: Client, user_id: int):
    try:
        await client.send_message(
            user_id,
            "**⚠️ Subscription Ended**\n"
            "Your access has expired. Contact admin to renew."
        )
    except Exception:
        pass

# Command to add a new user
async def add_user_cmd(client: Client, message: Message):
    """Add a new user to the bot"""
    try:
        # Check if sender is admin
        if message.from_user.id not in {OWNER_ID, OWNER_ID2} and not db.is_admin(message.from_user.id):
            await message.reply_text(AUTH_MESSAGES["not_admin"])
            return

        # Parse command arguments
        args = message.text.split()[1:]
        if len(args) != 2:
            await message.reply_text(
                AUTH_MESSAGES["invalid_format"].format(
                    format="/add user_id days\n\nExample:\n/add 123456789 30"
                )
            )
            return

        user_id = int(args[0])
        days = int(args[1])

        # Get bot username
        _me = await client.get_me()
        bot_username = _me.username

        try:
            # Try to get user info from Telegram
            user = await client.get_users(user_id)
            name = user.first_name
            if user.last_name:
                name += f" {user.last_name}"
        except:
            # If can't get user info, use ID as name
            name = f"User {user_id}"

        # Add user to database with bot username
        success, expiry_date = db.add_user(user_id, name, days, bot_username)
        
        if success:
            # Format expiry date
            expiry_str = expiry_date.strftime("%d-%m-%Y %H:%M:%S")
            _mention = f'<a href="tg://user?id={user_id}">{name}</a>'

            # Send success message to admin
            await message.reply_text(
                f"<b>✅ User Added Successfully!</b>\n\n"
                f"<blockquote>"
                f"👤 Name  ›  {_mention}\n"
                f"🆔 ID  ›  <code>{user_id}</code>\n"
                f"📅 Expiry  ›  <b>{expiry_str}</b>"
                f"</blockquote>",
                parse_mode="html",
                disable_web_page_preview=True,
            )

            # Try to notify the user using template
            try:
                await client.send_message(
                    user_id,
                    AUTH_MESSAGES["subscription_active"].format(
                        expiry_date=expiry_str
                    )
                )
            except Exception as e:
                print(f"Failed to notify user {user_id}: {str(e)}")
        else:
            await message.reply_text("❌ Failed to add user. Please try again.")

    except ValueError:
        await message.reply_text("❌ Invalid user ID or days. Please use numbers only.")
    except Exception as e:
        await message.reply_text(f"❌ Error: {str(e)}")

# Command to remove a user
async def remove_user_cmd(client: Client, message: Message):
    """Remove a user from the bot"""
    try:
        # Check if sender is admin
        if message.from_user.id not in {OWNER_ID, OWNER_ID2} and not db.is_admin(message.from_user.id):
            await message.reply_text("❌ Not authorized to remove users.")
            return

        # Parse command arguments
        args = message.text.split()[1:]
        if len(args) != 1:
            await message.reply_text(
                "❌ Invalid format!\n"
                "Use: /remove user_id\n"
                "Example: /remove 123456789"
            )
            return

        user_id = int(args[0])
        
        # Remove user from database
        _me = await client.get_me()
        _mention = f'<a href="tg://user?id={user_id}">{user_id}</a>'
        if db.remove_user(user_id, _me.username):
            await message.reply_text(
                f"<b>✅ User Removed</b>\n\n👤 {_mention} has been removed.",
                parse_mode="html", disable_web_page_preview=True,
            )
        else:
            await message.reply_text(
                f"<b>❌ Not Found</b>\n\n👤 {_mention} was not found.",
                parse_mode="html", disable_web_page_preview=True,
            )

    except ValueError:
        await message.reply_text("❌ Invalid user ID. Use numbers only.")
    except Exception as e:
        await message.reply_text(f"❌ Error: {str(e)}")

# Command to list all users
async def list_users_cmd(client: Client, message: Message):
    """List all users of the bot"""
    try:
        # Check if sender is admin
        if message.from_user.id not in {OWNER_ID, OWNER_ID2} and not db.is_admin(message.from_user.id):
            await message.reply_text("❌ Not authorized to list users.")
            return

        _me = await client.get_me()
        users = db.list_users(_me.username)
        
        if not users:
            await message.reply_text("📝 No users found.")
            return

        # Format user list
        user_list = "<b>📝 Premium Users</b>\n\n"
        for user in users:
            expiry = user['expiry_date']
            if isinstance(expiry, str):
                expiry = datetime.strptime(expiry, "%Y-%m-%d %H:%M:%S")
            days_left = (expiry - datetime.now()).days
            _uid = user['user_id']
            _name = user.get('name', str(_uid))
            _mention = f'<a href="tg://user?id={_uid}">{_name}</a>'
            user_list += (
                f"👤 {_mention}\n"
                f"🆔 <code>{_uid}</code>\n"
                f"⏳ {days_left} days left  |  📅 {expiry.strftime('%d-%m-%Y')}\n"
                f"━━━━━━━━━━━━━━\n"
            )

        await message.reply_text(user_list, parse_mode="html", disable_web_page_preview=True)

    except Exception as e:
        await message.reply_text(f"❌ Error: {str(e)}")

# Command to check user's plan
async def my_plan_cmd(client: Client, message: Message):
    """Show user's current plan details"""
    try:
        _me = await client.get_me()
        user = db.get_user(message.from_user.id, _me.username)
        
        if not user:
            await message.reply_text("❌ No active plan.")
            return

        expiry = user['expiry_date']
        if isinstance(expiry, str):
            expiry = datetime.strptime(expiry, "%Y-%m-%d %H:%M:%S")
        days_left = (expiry - datetime.now()).days

        _uid = message.from_user.id
        _name = user.get('name', str(_uid))
        _mention = f'<a href="tg://user?id={_uid}">{_name}</a>'
        await message.reply_text(
            f"<b>📋 Plan Details</b>\n\n"
            f"👤 {_mention}\n"
            f"⏳ <b>{days_left} days</b> remaining\n"
            f"📅 Expires: <b>{expiry.strftime('%d-%m-%Y')}</b>",
            parse_mode="html",
            disable_web_page_preview=True,
        )

    except Exception as e:
        await message.reply_text(f"❌ Error: {str(e)}")

# Register command handlers
add_user_handler = filters.command("add") & filters.private, add_user_cmd
remove_user_handler = filters.command("remove") & filters.private, remove_user_cmd
list_users_handler = filters.command("users") & filters.private, list_users_cmd
my_plan_handler = filters.command("plan") & filters.private, my_plan_cmd
