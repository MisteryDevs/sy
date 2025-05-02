from pyrogram.types import InlineKeyboardButton

import config
from AviaxMusic import app

OWNER_SID = 7943643606

def start_panel(_):
    buttons = [
        [
            InlineKeyboardButton(
                text=_["S_B_1"], url=f"https://t.me/{app.username}?startgroup=true"
            ),
            InlineKeyboardButton(text=_["S_B_2"], url=config.SUPPORT_GROUP),
        ],
    ]
    return buttons


def private_panel(_):
    buttons = [
        [
            InlineKeyboardButton(
                text=_["S_B_3"],
                url=f"https://t.me/{app.username}?startgroup=true",
            )
        ],
        [InlineKeyboardButton(text=_["S_B_4"], callback_data="settings_back_helper")],
        [
            InlineKeyboardButton(text=_["S_B_6"], url="https://t.me/+MyfM9r6eK9hiNTRl"),
            InlineKeyboardButton(text=_["S_B_2"], url="https://t.me/+3br0vt5M4wQwODhl"),
        ],
        [
           InlineKeyboardButton(text=_["S_B_5"], user_id=OWNER_SID),
        ],
    ]
    return buttons
