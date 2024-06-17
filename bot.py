from aiogram import Bot, Dispatcher, Router
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove
from aiogram.utils.keyboard import ReplyKeyboardBuilder
import logging

from business import *

load_dotenv()
logger = logging.getLogger(__name__)
IS_DEBUG = True if os.getenv('IS_DEBUG') == "True" else False
AUTHENTICATION_TOKEN = os.getenv('DEBUG_AUTHENTICATION_TOKEN') if IS_DEBUG else os.getenv('AUTHENTICATION_TOKEN')


class BotConfig:
    home_button = KeyboardButton(text='Головна')

    week_days_button_list = [
        [InlineKeyboardButton(text="Понеділок", callback_data="monday")],
        [InlineKeyboardButton(text="Вівторок", callback_data="tuesday")],
        [InlineKeyboardButton(text="Середа", callback_data="wednesday")],
        [InlineKeyboardButton(text="Четверг", callback_data="thursday")],
        [InlineKeyboardButton(text="П'ятниця", callback_data="friday")],
        [InlineKeyboardButton(text="Субота", callback_data="saturday")],
        [InlineKeyboardButton(text="Неділя", callback_data="sunday")],
    ]

    next_week_days_button_list = [
        [InlineKeyboardButton(text="Понеділок", callback_data="next_monday")],
        [InlineKeyboardButton(text="Вівторок", callback_data="next_tuesday")],
        [InlineKeyboardButton(text="Середа", callback_data="next_wednesday")],
        [InlineKeyboardButton(text="Четверг", callback_data="next_thursday")],
        [InlineKeyboardButton(text="П'ятниця", callback_data="next_friday")],
        [InlineKeyboardButton(text="Субота", callback_data="next_saturday")],
        [InlineKeyboardButton(text="Неділя", callback_data="next_sunday")],
    ]

    week_day_keyboard_inline = InlineKeyboardMarkup(inline_keyboard=week_days_button_list)
    next_week_day_keyboard_inline = InlineKeyboardMarkup(inline_keyboard=next_week_days_button_list)
    back_builder = ReplyKeyboardBuilder()
    home_builder = ReplyKeyboardBuilder()
    admin_builder = ReplyKeyboardBuilder()
    cabinet_builder = ReplyKeyboardBuilder()
    exchange_builder = ReplyKeyboardBuilder()

    back_builder.row(
        home_button,
    )

    home_builder.row(
    )

    def __init__(self, database):
        self.dp = Dispatcher()
        self.bot = Bot(AUTHENTICATION_TOKEN)
        self.database = database
        self.router = Router()
        self.dp.include_router(self.router)

        @self.dp.message(CommandStart())
        async def command_start_handle(message):
            await self._command_start_handle(message)

        @self.dp.message()
        async def on_user_shared(message):
            await self._on_button_click(message)

        @self.router.callback_query()
        async def callback(callback_query):
            await self._callback(callback_query)

    async def start(self):
        await self.dp.start_polling(self.bot)

    async def _callback(self, callback_query):
        logger.info(f'user send callback id:{callback_query.message.chat.id} '
                    f'data:{callback_query.data} {datetime.datetime.now()}')
        user_action = {
            # 'monday': lambda: self.send_week_schedule(callback_query, 1),
        }

        if callback_query.data in user_action:
            await user_action[callback_query.data]()

    async def _on_button_click(self, message):
        user_id = message.from_user.id
        user = self.database.get_user(user_id)
        logger.info(f'user send callback id:{user_id} '
                    f'data:{message.text} {datetime.datetime.now()}')

        user_action = {
            # 'Головна': lambda: self.change_gr(message),
            '/change_room_code': lambda: self.change_room_code(message),
            'change_room_code': lambda: self.change_room_code_state(message),
        }

        admin_action = {
            # 'Адмінка': lambda: self.bot.send_message(message.chat.id, 'Ви в адмінці',
            #                                         reply_markup=self.admin_builder.as_markup(resize_keyboard=True)),
        }

        if user:
            if message.text in user_action:
                await user_action[message.text]()
            elif user[1] in user_action:
                await user_action[user[1]]()
            elif user[2] == 'admin':
                user = self.database.get_user(user_id)
                user = user[0]
                if message.text in admin_action:
                    await admin_action[message.text]()
                elif user[1] in admin_action:
                    await admin_action[user[1]]()
            elif not user[3] in [None, 'None', 'none', '', 'NULL', 'null']:
                users_list = self.database.get_users_by_room_code(user[3])
                users_list.remove(user)
                for user_ in users_list:
                    await self.bot.send_message(user_[0], f'||Хтось: {message.text}||',
                                                parse_mode=ParseMode.MARKDOWN_V2)
            elif user[3] in [None, 'None', 'none', '', 'NULL', 'null']:
                await self.bot.send_message(message.chat.id, f'Чудік, введи нормальний код кімнати')
        else:
            await self.bot.send_message(message.from_user.id, 'Потрібно пройти реєстрацію. Натисніть /start')

    async def _command_start_handle(self, message):
        user_id = message.from_user.id
        user = self.database.get_user(user_id)
        await self.bot.send_message(user_id, f'Цей текст чисто для того аби ти розумів, що бот працює. '
                                    f'Щоб змінити кімнату введи /change_room_code', reply_markup=ReplyKeyboardRemove())
        if user:
            await self.bot.send_message(user_id, f'Ти вже зареєстрований. Введи /change_room_code щоб змінить '
                                                 f'кімнату або ж просто пиши повідомлення якщо ти вже в кімнаті')
            return

        self.database.add_new_user(user_id)

    async def home(self, message):
        self.database.changer_user_state('default')
        await self.bot.send_message(message.chat.id, 'Ти на головній')

    async def change_room_code(self, message):
        await self.bot.send_message(message.chat.id, 'Введи сюди код кімнати, у якій ти хочеш спілкуватись. '
                                                     'Назва None, NULL тощо недопустима (пиняй на себе)')
        self.database.changer_user_state(message.chat.id, 'change_room_code')

    async def change_room_code_state(self, message):
        await self.bot.send_message(message.chat.id, f'Тепер ти спілкуєшся у кімнаті з кодом: {message.text}\n'
                                                     f'Тепер просто пиши повідомлення і вони надійдуть усім учасникам '
                                                     f'кімнати. Також ти будеш отримувати відразу всі повідомлення усіх'
                                                     f'учасників. Приємного спілкування!')
        self.database.changer_user_state(message.chat.id, 'default')
        self.database.changer_user_room_code(message.chat.id, message.text)
        user_id = message.from_user.id
        user = self.database.get_user(user_id)
        users_list = self.database.get_users_by_room_code(user[3])
        users_list.remove(user)
        for user_ in users_list:
            await self.bot.send_message(user_[0], f'||БОТ: у нас нова людина||',
                                        parse_mode=ParseMode.MARKDOWN_V2)
