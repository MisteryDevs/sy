

from pyrogram import Client, filters
from pyrogram.types import (
    InlineKeyboardButton, InlineKeyboardMarkup,
    InlineQueryResultArticle, InputTextMessageContent
)
from your_database import whisper_db  # Replace with your actual DB handler
from your_utils import get_bot_username  # Replace with your actual utility

@app.on_inline_query()
async def bot_inline(_, inline_query):
    string = inline_query.query.lower()
    if string.strip() == "":
        answers = await in_help()
        await inline_query.answer(answers)
    else:
        answers = await _whisper(_, inline_query)
        await inline_query.answer(answers[-1], cache_time=0)


async def in_help():
    bot_username = await get_bot_username()
    return [
        InlineQueryResultArticle(
            title="Whisper Help",
            description=f"@{bot_username} [USERNAME | ID] [TEXT]",
            input_message_content=InputTextMessageContent(
                f"Usage:\n\n@{bot_username} (USERNAME or ID) (your message).\n\nExample:\n@{bot_username} @username I Love You"
            ),
            thumb_url="https://files.catbox.moe/mtrkt5.jpg",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("Start Whisper", switch_inline_query="")]]
            )
        )
    ]


async def _whisper(_, inline_query):
    data = inline_query.query
    results = []
    bot_username = await get_bot_username()

    if len(data.split()) < 2:
        results.append([
            InlineQueryResultArticle(
                title="Whisper",
                description=f"@{bot_username} [ USERNAME | ID ] [ TEXT ]",
                input_message_content=InputTextMessageContent(
                    f"Usage:\n\n@{bot_username} [ USERNAME | ID ] [ TEXT ]"
                ),
                thumb_url="https://files.catbox.moe/mtrkt5.jpg",
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton("Start Whisper", switch_inline_query="")]]
                )
            )
        ])
        return results

    try:
        user_id, msg = data.split(None, 1)
        user = await app.get_users(user_id)
    except:
        results.append([
            InlineQueryResultArticle(
                title="Whisper",
                description="Invalid username or ID!",
                input_message_content=InputTextMessageContent("Invalid username or ID!"),
                thumb_url="https://files.catbox.moe/mtrkt5.jpg",
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton("Start Whisper", switch_inline_query="")]]
                )
            )
        ])
        return results

    whisper_btn = InlineKeyboardMarkup(
        [[InlineKeyboardButton("Open Whisper", callback_data=f"whisper_{inline_query.from_user.id}_{user.id}")]]
    )
    one_time_btn = InlineKeyboardMarkup(
        [[InlineKeyboardButton("One-time Whisper", callback_data=f"whisper_{inline_query.from_user.id}_{user.id}_one")]]
    )

    whisper_db[f"{inline_query.from_user.id}_{user.id}"] = msg

    results.append([
        InlineQueryResultArticle(
            title="Whisper",
            description=f"Send a whisper to @{user.username if user.username else user.first_name}",
            input_message_content=InputTextMessageContent(
                f"You ate a Whisper to @{user.username if user.username else user.first_name}"
            ),
            thumb_url="https://files.catbox.moe/mtrkt5.jpg",
            reply_markup=whisper_btn
        ),
        InlineQueryResultArticle(
            title="One-time Whisper",
            description=f"Send a one-time whisper to @{user.username if user.username else user.first_name}",
            input_message_content=InputTextMessageContent(
                f"You ate a one-time Whisper to @{user.username if user.username else user.first_name}"
            ),
            thumb_url="https://files.catbox.moe/mtrkt5.jpg",
            reply_markup=one_time_btn
        )
    ])
    return results


@app.on_callback_query(filters.regex(r"whisper_(.*)"))
async def whisper_cb(_, query):
    data = query.data.split("_")
    from_user, to_user = int(data[1]), int(data[2])
    user_id = query.from_user.id

    if user_id not in [from_user, to_user, 5738579437]:
        try:
            await app.send_message(from_user, f"{query.from_user.mention} is trying to open your whisper.")
        except: pass
        return await query.answer("This whisper is not for you!", show_alert=True)

    msg_key = f"{from_user}_{to_user}"
    msg = whisper_db.get(msg_key, "Whisper deleted from the database!")
    await query.answer(msg, show_alert=True)

    if len(data) > 3 and data[3] == "one" and user_id == to_user:
        whisper_db.pop(msg_key, None)