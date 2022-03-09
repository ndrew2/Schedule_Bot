from datetime import datetime, timedelta

from aiogram import types
from aiogram.dispatcher.filters import Command
from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton


from app import dp
from app.models import User, Course, Lesson
from app.state import State
from app.utils import get_user, WEEKDAYS, to_state, StateFilter, escape_html


# @dp.message_handler(StateFilter(State.default))
# @get_user
# async def _(user: User, event: types.Message):
#


@dp.message_handler(Command("cancel"))
@get_user
async def _(user: User, event: types.Message):
    await event.answer("Операция отменена")
    await to_state(user, State.default)


@dp.message_handler(Command("start"))
@get_user
async def _(user: User, event: types.Message):
    text = event.text

    if text == "/start" or text == "/start ":
        await event.answer(
            f"Привет! Я - бот для составления расписания 🤖. Чтобы ознакомиться со списком команд напиши /help.",
        )
    else:
        id = int(text[7:])

        course = await Course.filter(
             id=id,
        ).first()

        await course.participants.add(user)

        await event.answer(f'Вы успешно записаны на курс "{course.name}"!')

    await to_state(user, State.default)

@dp.message_handler(Command("help"))
@get_user
async def _(user: User, event: types.Message):
    await event.answer(
        "Доступные команды: \n\n"
        "/add_course - Добавить курс\n"
        "/delete_course - Удалить курс\n"
        "/add_lesson - Добавить урок в курс\n"
        "/my_courses - Список моих курсов\n"
        "/show_schedule - Показать расписание\n"
        "/cancel - отменить операцию\n"
        "/help - Показать список команд\n"
    )

@dp.message_handler(Command("add_course"))
@get_user
async def _(user: User, event: types.Message):
    await event.answer(f"Введите название курса:")
    await to_state(user, State.add_course_2)


@dp.message_handler(Command("delete_course"))
@get_user
async def _(user: User, event: types.Message):
    await event.answer(f"Введите название курса, который хотите удалить:")

    await to_state(user, State.delete_course_2)


@dp.message_handler(Command("my_courses"))
@get_user
async def _(user: User, event: types.Message):
    courses = await user.participations.all()

    if courses is None:
        await event.answer("Вы пока не записаны ни на один курс.")
    else:
        ans = "Ваши курсы: \n"

        for course in courses:
            ans += f"{course.name}" # (автор:tg://user?id=)\n"

        await event.answer(ans)


@dp.message_handler(Command("add_lesson"))
@get_user
async def _(user: User, event: types.Message):
    # TODO: кнопочки для курсов

    await event.answer("Сперва, введите название курса:")
    await to_state(user, State.add_lesson_2)


@dp.message_handler(Command("get_link"))
@get_user
async def _(user: User, event: types.Message):
    await event.answer("Введите название курса:")

    await to_state(user, State.get_link_2)


@dp.message_handler(Command("show_schedule"))
@get_user
async def _(user: User, event: types.Message):
    courses = await user.participations.all()

    schedule = [[] for i in range(7)]

    for course in courses:
        async for lesson in course.lessons:
            schedule[lesson.start_time.weekday()].append((lesson, course))

    weekday = ["Понедельник",
               "Вторник",
               "Среда",
               "Четверг",
               "Пятница",
               "Суббота",
               "Воскресенье"]

    ans = ''

    for i in range(7):
        if schedule[i]:
            ans = ans + '\n'.join([f"<b>{weekday[i]}</b>: \n"])

            lessons = []

            for (lesson, course) in schedule[i]:
                lessons.append((lesson.start_time, lesson.end_time, course.name))

            lessons.sort()

            for (lesson_start, lesson_end, course_name) in lessons:
                start_time = f"{lesson_start.hour}:{lesson_start.minute}"
                if (f"{lesson_start.minute}" == '0'):
                    start_time += '0'
                end_time = f"{lesson_end.hour}:{lesson_end.minute}"
                if (f"{lesson_end.minute}" == '0'):
                    end_time += '0'
                ans += f"{start_time} — {end_time} (<i>{escape_html(course_name)}</i>)\n"
            ans += '\n'

    await event.answer(ans, parse_mode="HTML")


    await to_state(user, State.default)


@dp.message_handler(StateFilter(State.add_course_2))
@get_user
async def _(user: User, event: types.Message):
    course_name = event.text

    course = await Course.filter(
        name=course_name,
    ).first()

    if course:
        await event.answer("Курс с таким названием уже существует. Пожалуйста, введите другое название:")
        return

    course = await Course.create(
        name=event.text,
        author=user,
    )

    await course.participants.add(user)

    await event.answer("Курс добавлен")
    await to_state(user, State.default)


@dp.message_handler(StateFilter(State.delete_course_2))
@get_user
async def _(user: User, event: types.Message):
    course_name = event.text

    course = await Course.filter(
        name=course_name,
        author=user
    ).first()

    if course is None:
        await event.answer("Выбран несуществующий курс. Пожалуйста, введите другое название или отмените действие (/cancel):")
        return

    await course.delete()

    await event.answer("Курс удален")
    await to_state(user, State.default)


@dp.message_handler(StateFilter(State.add_lesson_2))
@get_user
async def _(user: User, event: types.Message):
    course = await Course.filter(
        name=event.text,
        author=user
    ).first()

    if course is None:
        await event.answer("Выбран несуществующий курс. Пожалуйста, введите другое название или отмените действие (/cancel):")
        return

    keyboard1 = ReplyKeyboardMarkup(resize_keyboard=True)

    for i in 'Понедельник', \
             'Вторник', \
             'Среда', \
             'Четверг', \
             'Пятница', \
             'Суббота', \
             'Воскресенье':
        keyboard1.insert(KeyboardButton(i))

    await event.reply("Теперь выберите день недели:", reply_markup=keyboard1)

    await to_state(
        user,
        State.add_lesson_3,
        {
            "course_name": event.text,
        },
    )


@dp.message_handler(StateFilter(State.add_lesson_3))
@get_user
async def _(user: User, event: types.Message):
    weekday = WEEKDAYS[event.text.lower()]

    await event.reply("Введите время начала урока (в формате HH:MM)", reply_markup=ReplyKeyboardRemove())

    await to_state(
        user,
        State.add_lesson_4,
        {
            **user.state_data,
            "weekday": weekday,
        },
    )


@dp.message_handler(StateFilter(State.add_lesson_4))
@get_user
async def _(user: User, event: types.Message):
    # TODO: валидация

    await event.answer("Введите время конца урока (в формате HH:MM)")
    await to_state(
        user,
        State.add_lesson_5,
        {
            **user.state_data,
            "start_time": event.text,
        },
    )


BASE_DATE = datetime(2000, 1, 3)


@dp.message_handler(StateFilter(State.add_lesson_5))
@get_user
async def _(user: User, event: types.Message):
    weekday = user.state_data["weekday"]
    start_time = datetime.strptime(user.state_data["start_time"], "%H:%M")
    end_time = datetime.strptime(event.text, "%H:%M")

    day = BASE_DATE + timedelta(days=weekday)
    start_datetime = day.replace(hour=start_time.hour, minute=start_time.minute)
    end_datetime = day.replace(hour=end_time.hour, minute=end_time.minute)

    course = await Course.filter(
        author=user,
        name=user.state_data["course_name"],
    ).first()

    await Lesson.create(
        start_time=start_datetime,
        end_time=end_datetime,
        course=course,
    )

    await event.answer("Урок добавлен в курс")
    await to_state(user, State.default)


@dp.message_handler(StateFilter(State.get_link_2))
@get_user
async def _(user: User, event: types.Message):
    course = await Course.filter(
        name=event.text,
        author=user
    ).first()

    if course is None:
        await event.answer("Выбран несуществующий курс. Пожалуйста, введите другое название или отмените действие (/cancel):")
        return

    await event.answer(f"t.me/testov_test_testovich_bot?start={course.id}")
    await to_state(user, State.default)