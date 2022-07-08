"""Бот, который предложит вам лучше понять свои желания и потребности
в отношении еды."""

import logging
import os
import time
from random import choice

from telegram import (
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    Update,
)
from telegram.ext import (
    Updater,
    Filters,
    MessageHandler,
    CommandHandler,
    ConversationHandler,
)
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv('TOKEN')
CLARIFYING, CHOICES, RESULT, EMOTIONAL_HELP = range(4)
# Глобальная переменная для записи вариантов вкусов при физиологическом голоде:
taste_wish = ''
# Глобальная переменная для записи задачи, которую должна решить еда прямо сейчас:
result = ''
GIF = (
    'ApprovingCat',
    'GoldFish',
    'WinkingCat',
    'Daisy',
    'LovingMooming',
    'DreamingMoomin',
    'ApprovingEgg',
    'DancingMintZebra',
)


def get_logger():
    """Setting logger."""
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    form = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(form)
    logger.addHandler(handler)
    return logger


logger = get_logger()


def reply_handler(text: str, func_name):
    """MessageHandler set for conversation."""
    return MessageHandler(Filters.regex(f'^({text})$'), func_name)


def reaction_questioned(
    update: Update,
    keyboard: list,
    question_text: str
):
    """Set for questionned reaction in conversation."""
    user = update.message.from_user
    logger.info('%s %s', user.first_name, update.message.text)
    keyboard = keyboard
    update.message.reply_text(
        question_text,
        reply_markup=ReplyKeyboardMarkup(
            keyboard,
            resize_keyboard=True,
            one_time_keyboard=True
        )
    )


def just_react(update: Update, answer_text: str):
    """Set for  text reaction, without keyboard and further answering."""
    user = update.message.from_user
    logger.info('%s %s', user.first_name, update.message.text)
    update.message.reply_text(
        answer_text,
        reply_markup=ReplyKeyboardRemove()
    )


def start(update: Update, _):
    """Start the session."""
    name = update.message.chat.first_name
    update.message.reply_text(
        f'Привет, {name}! Хочешь съесть что-нибудь?'
    )
    time.sleep(1)
    reaction_questioned(
        update,
        [['Да', 'Нет']],
        'А может быть ты хочешь пить?',
    )
    return CLARIFYING


def is_thirsty(update: Update, _):
    """Processing thirsty answer."""
    if update.message.text == 'Да':
        just_react(
            update,
            'Здорово что смогла это отследить! Стакан воды всегда хороший выбор!'
        )
        update.message.reply_sticker(
            open(f'./static/{choice(GIF)}.tgs', 'rb')
        )
        return ConversationHandler.END
    if update.message.text == 'Нет':
        update.message.reply_text(
            'Напоминалка:) Физиологический голод обычно ощущается в теле в области живота, а эмоциональный от груди и выше.'
        )
        time.sleep(3)
        reaction_questioned(
            update,
            [
                ['Физиологический'],
                ['Эмоциональный']
            ],
            'Как ты определишь свой голод?'
        )
        return CLARIFYING


def physiological(update: Update, _):
    """Processsing physiological answer."""
    global taste_wish
    if update.message.text == 'Физиологический':
        reaction_questioned(
            update,
            [
                ['Сладкое', 'Cоленое'],
                ['Кислое', 'Острое']
            ],
            'Какого вкуса тебе сейчас хочется?'
        )
        return CHOICES
    elif update.message.text in ('Сладкое', 'Cоленое', 'Кислое', 'Острое'):
        taste_wish += update.message.text
        reaction_questioned(
            update,
            [['Горячее', 'Тёплое', 'Холодное']],
            'Какой температуры?'
        )
        return CHOICES
    elif update.message.text in ('Горячее', 'Тёплое', 'Холодное'):
        taste_wish += (', ' + update.message.text)
        reaction_questioned(
            update,
            [
                ['Густое', 'Жидкое'],
                ['Твёрдое', 'Мягкое', 'Хрустящее']
            ],
            'Какой консистенции?'
        )
        return CHOICES
    elif update.message.text in (
        'Густое', 'Жидкое', 'Твёрдое', 'Мягкое', 'Хрустящее'
    ):
        taste_wish += (', ' + update.message.text)
        update.message.reply_text(
            f'Твой выбор: {taste_wish}'
        )
        taste_wish = ''
        time.sleep(1)
        reaction_questioned(
            update,
            [['Да', 'Нет']],
            'Можешь сейчас сделать небольшую медитацию?'
        )
        return RESULT


def meditation(update: Update, _):
    """Processing if meditation could be produced."""
    if update.message.text == 'Да':
        just_react(
            update,
            'Отлично!'
        )
        time.sleep(2)
        update.message.reply_text(
            'Приятного аппетита!'
        )
        time.sleep(2)
        update.message.reply_text(
            'Надеюсь то, что у тебя в тарелке соответствует твоему выбору!'
        )
        update.message.reply_sticker(
            open(f'./static/{choice(GIF)}.tgs', 'rb')
        )
    elif update.message.text == 'Нет':
        just_react(
            update,
            'Тогда постарайся немного замедлиться'
        )
        time.sleep(1)
        update.message.reply_text(
            'Cделай несколько глубоких вдохов-выдохов'
        )
        time.sleep(2)
        update.message.reply_text(
            'Ну и приятного аппетита! Надеюсь то, что у тебя в тарелке соответствует твоему выбору!'
        )
        update.message.reply_sticker(
            open(f'./static/{choice(GIF)}.tgs', 'rb')
        )
    return ConversationHandler.END


def emotional(update: Update, _):
    """Processing emotional eating."""
    reaction_questioned(
        update,
        [
            ['Устала', 'Раздражена'],
            ['Грустно', 'Тревожно'],
            ['Спать хочу']
        ],
        'Как ты сейчас себя чувствуешь?'
    )
    return CHOICES


def emotional_choises(update: Update, _):
    """Processing reasons for willingness to have food."""
    global result
    if update.message.text in ('Устала', 'Раздражена', 'Грустно', 'Тревожно', 'Спать хочу'):
        reaction_questioned(
            update,
            [
                ['Убрать эмоциональное напряжение'],
                ['Справиться с усталостью'],
                ['Получить удовольствие'],
                ['Расслабиться', 'Отдохнуть'],
                ['Переключиться']
            ],
            'Какая функция у еды, что хочется получить?'
        )
        return CHOICES
    if update.message.text in (
        'Убрать эмоциональное напряжение', 'Расслабиться',
    ):
        result = update.message.text
        reaction_questioned(
            update,
            [
                ['Да, попробую'],
                ['Нет возможности']
            ],
            'Может можешь пойти прогуляться или немного размяться?'
        )
        return EMOTIONAL_HELP
    elif update.message.text in (
        'Справиться с усталостью', 'Отдохнуть'
    ):
        result += update.message.text
        reaction_questioned(
            update,
            [
                ['Да, попробую'],
                ['Нет возможности']
            ],
            'Может быть полежать? Размяться? Сделать небольшой самомассаж?'
        )
        return EMOTIONAL_HELP
    elif update.message.text in (
        'Получить удовольствие', 'Переключиться'
    ):
        result = update.message.text

        reaction_questioned(
            update,
            [
                ['Да, попробую другие способы'],
                ['Прямо сейчас только еда!']
            ],
            'Что приятное доступно тебе прямо сейчас? Если у тебя есть список простых приятных вещей, самое время им воспользоаваться! Или написать такой.'
        )
        return EMOTIONAL_HELP


def algorithm_extra_eating(update: Update, _):
    """Perform algorythm during emotional reason to have food."""
    update.message.reply_text(
        'OK! Давай вместе просто последуем схеме!'
    )
    time.sleep(2)
    update.message.reply_text(
        'Итак, представь заранее, что уже съела то, что собираешься'
    )
    time.sleep(5)
    update.message.reply_text(
        'Какие ощущения будут во время еды? Какие после?'
    )
    time.sleep(4)
    update.message.reply_text(
        'Будет ли там чувство тяжести? Чувство вины или удовольствие?'
    )
    time.sleep(4)
    update.message.reply_text(
        'Вспомни о своих целях и ценностях в длительной перспективе, какой выбор будет лучшим прямо сейчас?'
    )
    time.sleep(3)
    reaction_questioned(
        update,
        [
            ['Да, пожалуй попробую без еды, постараюсь себя порадовать как-нибудь ещё'],
            ['Всё представила. Поем!']
        ],
        'Что решила делать?'
    )
    return EMOTIONAL_HELP


def algorithm_result(update: Update, _):
    """If desire turned out to be irresistable."""
    global result
    if update.message.text == 'Всё представила. Поем!':
        just_react(
            update,
            'Хорошо, но, пожалуйста, ешь медленно, осознанно и без гаджетов/книжки/ТВ!'
        )
        time.sleep(1)
        update.message.reply_text(
            'Давай сделаем несколько глубоких вдохов и выдохов'
        )
        time.sleep(2)
        update.message.reply_text(
            'Постарайся почувствовать все оттенки вкуса выбранной еды'
        )
        update.message.reply_text(
            'Приятного аппетита!'
        )
        time.sleep(5)
        update.message.reply_text(
            'Как теперь себя чувствуешь?'
        )
        time.sleep(2)
        update.message.reply_text(
            'Появился ли дискомфорт или неприятные эмоции? Какие-то приятные ощущения?'
        )
        time.sleep(2)

        reaction_questioned(
            update,
            [['Скорее да', 'Скорее нет']],
            f'Удалось ли получить желаемый результат? {result}?'
        )
        result = ''
        return EMOTIONAL_HELP
    elif update.message.text == 'Да, пожалуй попробую без еды, постараюсь себя порадовать как-нибудь ещё':
        just_react(
            update,
            'Хороший выбор! Надеюсь удастся почувствовать себя лучше!'
        )
        update.message.reply_sticker(
            open(f'./static/{choice(GIF)}.tgs', 'rb')
        )
        return ConversationHandler.END


def after_eating(update, _):
    if update.message.text == 'Скорее да':
        just_react(
            update,
            'Хорошо! Но старайся использовать и другие варианты!'
        )
    elif update.message.text == 'Скорее нет':
        just_react(
            update,
            'Отрицательный результат тоже результат! Попробуй другие способы помочь себе!'
        )
    update.message.reply_sticker(
            open(f'./static/{choice(GIF)}.tgs', 'rb')
        )
    return ConversationHandler.END


def try_smth_instead_food(update: Update, _):
    """If choice is not food."""
    name = update.message.chat.first_name
    update.message.reply_text(
        f'Отлично, {name}! Надеюсь ты почувствуешь себя лучше!',
        reply_markup=ReplyKeyboardRemove()
    )
    update.message.reply_sticker(
            open(f'./static/{choice(GIF)}.tgs', 'rb')
        )
    return ConversationHandler.END


def main():
    updater = Updater(TOKEN)
    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler('start', start)
        ],
        states={
            CLARIFYING: [
                reply_handler('Да|Нет', is_thirsty),
                reply_handler('Физиологический', physiological),
                reply_handler('Эмоциональный', emotional),
            ],
            CHOICES: [
                reply_handler(
                    'Сладкое|Cоленое|Кислое|Острое|Горячее|Тёплое|Холодное|Густое|Жидкое|Твёрдое|Мягкое|Хрустящее',
                    physiological
                ),
                reply_handler('Устала|Раздражена|Грустно|Тревожно|Спать хочу', emotional_choises),
                reply_handler(
                    'Убрать эмоциональное напряжение|Справиться с усталостью|Получить удовольствие|Расслабиться|Отдохнуть|Переключиться',
                    emotional_choises
                ),
            ],
            RESULT: [
                reply_handler('Да|Нет', meditation),
            ],
            EMOTIONAL_HELP: [
                reply_handler('Нет возможности|Прямо сейчас только еда!', algorithm_extra_eating),
                reply_handler(
                    'Всё представила. Поем!|Да, пожалуй попробую без еды, постараюсь себя порадовать как-нибудь ещё',
                    algorithm_result
                ),
                reply_handler(
                    'Да, попробую|Да, попробую другие способы',
                    try_smth_instead_food
                ),
                reply_handler('Скорее да|Скорее нет', after_eating)
            ],
        },
        fallbacks=[],
        allow_reentry=True,
    )
    updater.dispatcher.add_handler(conv_handler)

    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()
