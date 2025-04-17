from pyrogram import Client, filters
from pyrogram.types import (
    InlineQuery,
    InlineQueryResultArticle,
    InputTextMessageContent,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery
)

from config import OWNER_ID

# In-memory whisper storage
whisper_db = {}

# Get your bot username
async def get_bot_username():
    me = await Client.get_me()
    return me.username

# Whisper help message
async def whisper_help():
    bot_username = await get_bot_username()
    return [
        InlineQueryResultArticle(
            title="Whisper Help",
            description=f"@{bot_username} [USERNAME or ID] [MESSAGE]",
            input_message_content=InputTextMessageContent(
                f"Usage:\n\n@{bot_username} [USERNAME or ID] [YOUR MESSAGE]\n\nExample:\n@{bot_username} @username I love you"
            ),
            thumb_url="https://files.catbox.moe/mtrkt5.jpg",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("Start Whisper", switch_inline_query="")]]
            )
        )
    ]


# Handle inline whisper input
@Client.on_inline_query()
async def inline_whisper(client, inline_query: InlineQuery):
    query = inline_query.query.strip()

    if not query:
        return await inline_query.answer(await whisper_help(), cache_time=0)

    try:
        user_id, text = query.split(None, 1)
        user = await client.get_users(user_id)
    except:
        return await inline_query.answer(await whisper_help(), cache_time=0)

    key = f"{inline_query.from_user.id}_{user.id}"
    whisper_db[key] = text

    btns = InlineKeyboardMarkup(
        [[InlineKeyboardButton("Open Whisper", callback_data=f"whisper_{key}")]]
    )
    one_btns = InlineKeyboardMarkup(
        [[InlineKeyboardButton("One-Time Whisper", callback_data=f"whisper_{key}_one")]]
    )

    results = [
        InlineQueryResultArticle(
            title="Whisper",
            description=f"Send to @{user.username or user.first_name}",
            input_message_content=InputTextMessageContent(
                f"You sent a whisper to @{user.username or user.first_name}"
            ),
            reply_markup=btns,
            thumb_url="https://files.catbox.moe/mtrkt5.jpg"
        ),
        InlineQueryResultArticle(
            title="One-Time Whisper",
            description=f"One-time whisper to @{user.username or user.first_name}",
            input_message_content=InputTextMessageContent(
                f"You sent a one-time whisper to @{user.username or user.first_name}"
            ),
            reply_markup=one_btns,
            thumb_url="https://files.catbox.moe/mtrkt5.jpg"
        )
    ]
    await inline_query.answer(results, cache_time=0)


# Handle whisper button callback
@Client.on_callback_query(filters.regex(r"^whisper_"))
async def whisper_callback(client, query: CallbackQuery):
    parts = query.data.split("_")
    from_id, to_id = int(parts[1]), int(parts[2])
    user_id = query.from_user.id

    if user_id not in [from_id, to_id, OWNER_ID]:
        try:
            await client.send_message(from_id, f"{query.from_user.mention} tried to view your whisper!")
        except:
            pass
        return await query.answer("This whisper is not for you!", show_alert=True)

    key = f"{from_id}_{to_id}"
    message = whisper_db.get(key, "Whisper not found or expired.")

    await query.answer(message, show_alert=True)

    # Delete if one-time whisper
    if len(parts) > 3 and parts[3] == "one" and user_id == to_id:
        whisper_db.pop(key, None)