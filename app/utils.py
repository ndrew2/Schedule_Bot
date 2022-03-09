from functools import wraps
import html
from typing import TYPE_CHECKING

from aiogram import types
from aiogram.dispatcher.filters import Filter

from app.models import User

if TYPE_CHECKING:
    from app.state import State


class StateFilter(Filter):
    def __init__(self, state: 'State'):
        self.state = state

    async def check(self, message: types.Message):
        return bool(
            await User.get_or_none(
                id=message.from_user.id,
                state=self.state.value,
            )
        )


async def to_state(user: User, state: 'State', data: dict = None):
    if data is None:
        data = {}

    user.state = state.value
    user.state_data = data
    await user.save()


def get_user(f):
    @wraps(f)
    async def inner(event: types.Message, *args, **kwargs):
        user, _ = await User.get_or_create(
            id=event.from_user.id,
        )
        await f(user, event, *args, **kwargs)

    return inner


def mention_user(user: User):
    user_full_name = "пользователь"
    return f'<a href="tg://user?id={user.id}">{user_full_name}</a>'


def escape_html(text: str) -> str:
    return html.escape(text, quote=False)


WEEKDAYS = {
    "понедельник": 0,
    "вторник": 1,
    "среда": 2,
    "четверг": 3,
    "пятница": 4,
    "суббота": 5,
    "воскресенье": 6,
}
