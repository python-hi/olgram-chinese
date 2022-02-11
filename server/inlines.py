from aiocache import cached
import hashlib
from aiogram.types import InlineQuery, InputTextMessageContent, InlineQueryResultArticle

from olgram.models.models import Bot, DefaultAnswer
import typing as ty


@cached(ttl=1)
async def get_phrases(bot: Bot) -> ty.List:
    objects = await bot.answers
    return [obj.text for obj in objects]


async def inline_handler(inline_query: InlineQuery, bot: Bot):
    # Check permissions at first
    # user_id = inline_query.from_user.id
    # if bot.super_chat_id() != user_id:
    #    return await inline_query.answer([], cache_time=1)  # forbidden

    all_phrases = await get_phrases(bot)
    print(f"All phrases {all_phrases}")
    phrases = [phrase for phrase in all_phrases if inline_query.query.lower() in phrase.lower()]
    print(f"phrases {phrases}")
    items = []
    for phrase in phrases:

        input_content = InputTextMessageContent(phrase)
        result_id: str = hashlib.md5(phrase.encode()).hexdigest()
        item = InlineQueryResultArticle(
            id=result_id,
            title=phrase,
            input_message_content=input_content,
        )
        items.append(item)

    await inline_query.answer(results=items, cache_time=1)
