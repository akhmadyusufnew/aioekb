from aiogram import Router, F, Bot
from aiogram.types import ChatMemberUpdated

from core.telegram import handle_exception
from core.config import settings
from core.db.database import get_session
from core.db.repository import log_telegram_event


router = Router()

@router.chat_member(F.chat.id == settings.GROUP_SUPPORT_TOKO)
async def welcome_new_member(update: ChatMemberUpdated, bot: Bot):
    try:
        if update.new_chat_member.status == "member" and \
           update.old_chat_member.status not in ["member", "administrator", "creator"]:

            new_user = update.new_chat_member.user
            adder = update.from_user
            chat_id = update.chat.id

            async with get_session() as session_db:
                await log_telegram_event(session_db, update)

                if adder and new_user.id != adder.id:
                    msg = (
                        f"<i>Terimakasih Bapak/Ibu</i> <a href='tg://user?id={adder.id}'>{adder.full_name}</a>.\n"
                        f"\n"
                        f"<i>Selamat datang di group</i>\n<b>{update.chat.title}</b>\n"
                        f"Bapak/Ibu <a href='tg://user?id={new_user.id}'>{new_user.full_name}</a>.\n"
                        f"\n"
                        f"<i>Mohon konfirmasi perkenalan dengan format berikut</i>\n"
                        f"<pre>"
                        f"Perkenalan\n"
                        f"\n"
                        f"Nama Lengkap : \n"
                        f"Jabatan : AS/AM\n"
                        f"Cabang : \n"
                        f"</pre>"
                        f"\n"
                        f"\n"
                        f"<i>😊 Ceria Melayani.....🙏🏻 Semangat berprestasi ..💪🏻</i>"
                    )
                else:
                    msg = (
                        f"<i>Selamat datang di group</i>\n<b>{update.chat.title}</b>\n"
                        f"Bapak/Ibu <a href='tg://user?id={new_user.id}'>{new_user.full_name}</a>.\n"
                        f"\n"
                        f"<i>Mohon konfirmasi perkenalan dengan format berikut</i>\n"
                        f"<pre>"
                        f"Perkenalan\n"
                        f"\n"
                        f"Nama Lengkap : \n"
                        f"Jabatan : AS/AM\n"
                        f"Cabang : \n"
                        f"</pre>"
                        f"\n"
                        f"\n"
                        f"<i>😊 Ceria Melayani.....🙏🏻 Semangat berprestasi ..💪🏻</i>"
                    )

                msg = await bot.send_message(chat_id, msg, parse_mode="HTML")
                await log_telegram_event(session_db, msg)

    except Exception as e:
        await handle_exception(update, bot, e)
