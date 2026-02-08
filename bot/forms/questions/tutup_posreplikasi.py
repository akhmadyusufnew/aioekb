from aiogram.types import Message

from ._base import BaseFormQuestion

class TutupPOSReplikasiFormQuestion(BaseFormQuestion):

    async def q_status(self, message: Message):
        cmd = self.command_text()
        keyboard_buttons = [
            [
                KeyboardButton(text="✅ Berhasil")
            ],
            [
                KeyboardButton(text="Kendala")
            ],
        ]
        await self.ask(
            message,
            f"Status Penutupan:"
            f"\n\n"
            f"{cmd}"
            f"\n\n"
            f"/kendala /berhasil",
            reply_markup=ReplyKeyboardMarkup(
                keyboard=keyboard_buttons,
                resize_keyboard=True,
                one_time_keyboard=True,
            )
        )    