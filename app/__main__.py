import asyncio

from tortoise import Tortoise

from app import config, dp, bot


async def main():
    await Tortoise.init(
        config=config.TORTOISE_ORM,
    )
    try:
        await dp.start_polling()
    finally:
        await (await bot.get_session()).close()
        await Tortoise.close_connections()


asyncio.run(main())
