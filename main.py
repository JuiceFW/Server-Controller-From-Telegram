from telebot import types
import telebot

from multiprocessing.dummy import Process
from typing import Union
import subprocess
import traceback
import platform
import logging
import time
import json
import os

from config import TOKEN, ADMIN_ID


BASE_DIR = os.path.dirname(os.path.realpath(__file__))
if not os.path.exists(os.path.join(BASE_DIR, "config.py")):
    with open(os.path.join(BASE_DIR, "config.py"), "w", encoding='utf-8') as file:
        file.write("""TOKEN = '' # Bot Token from @BotFather
ADMIN_ID = 111111111 # Your ID in telegram""")
    print("[INFO] Created **config.py**! Please, enter all needed data there!")
    os._exit(0)


if not TOKEN or not ADMIN_ID:
    print("[ERROR] Please, enter all needed data in config.py file!")
    os._exit(0)


turning_off = False
rebooting = False


try:
    logging.basicConfig(filename=os.path.join(BASE_DIR, 'logs.log'),
                    format='[%(asctime)s | %(levelname)s]: %(message)s',
                    datefmt='%m.%d.%Y %H:%M:%S',
                    level=logging.CRITICAL,
                    encoding='utf-8')
except:
    try:
        logging.basicConfig(filename=os.path.join(BASE_DIR, 'logs.log'),
                    format='[%(asctime)s | %(levelname)s]: %(message)s',
                    datefmt='%m.%d.%Y %H:%M:%S',
                    level=logging.CRITICAL)
    except Exception as ex:
        print(str(traceback.format_exc()))
        exit()

try:
    bot = telebot.TeleBot(TOKEN)
except:
    print(traceback.format_exc())
    logging.critical(traceback.format_exc())
    os._exit(0)

markup = types.InlineKeyboardMarkup()
item1 = types.InlineKeyboardButton("Удалить", callback_data='delete_message')
markup.add(item1)


def get_ip() -> str:
    if platform.system() == "Windows":
        return None

    output = None
    try:
        args = ["ip", "a"]
        output = subprocess.run(args, stdout=subprocess.PIPE)
    except Exception as ex:
        print(traceback.format_exc())
        logging.critical(traceback.format_exc())

    try:
        output = output.stdout.decode('utf-8')
    except:
        print(traceback.format_exc())
        logging.critical(traceback.format_exc())
        return None
    
    if not output:
        return None

    try:
        b = output.split("inet")
        b = b[-2]
        c = b.splitlines()
        c = c[0]
        if c.startswith(" "):
            c = c[1:]
        d = c.split("/24")
        d = d[0]
    except:
        print(traceback.format_exc())
        logging.critical(traceback.format_exc())
        return None

    return str(d)


try:
    bot.send_message(ADMIN_ID, f'Server started! IP: <code>{get_ip()}</code>', reply_markup=markup, parse_mode='html')
except:
    print(traceback.format_exc())
    logging.critical(traceback.format_exc())


def get_commands_json() -> dict:
    if not os.path.exists(os.path.join(BASE_DIR, "commands.json")):
        return {"saved": [], "last": []}

    with open(os.path.join(BASE_DIR, "commands.json"), encoding='utf-8') as file:
        return json.loads(file.read())


def write_commands_json(data: dict):
    with open(os.path.join(BASE_DIR, "commands.json"), "w", encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False)


def delete_in_time(message_id: int, chat_id: int, time_to_wait: int = 60) -> None:
    """ Deletes message in given time. """
    try:
        time.sleep(time_to_wait)
        bot.delete_message(chat_id, message_id)
    except:
        print("[ERROR] " + str(traceback.format_exc()))
        logging.critical(traceback.format_exc())


def turn_off_in_time(chat_id: int, message_id: int, timing: int) -> None:
    """ Turns off the server in given time. """

    global turning_off

    markup = types.InlineKeyboardMarkup()
    item1 = types.InlineKeyboardButton("Отменить!", callback_data='cancel_turn_off')

    markup.add(item1)

    bot.edit_message_text(f"Начинаю отсчет!", chat_id, message_id, reply_markup=markup)

    time.sleep(0.2)

    if turning_off:
        for i in reversed(range(timing)):
            if not turning_off:
                break

            bot.edit_message_text(f"Выключаюсь...\n\n<b>{i}</b>", chat_id, message_id, parse_mode='html', reply_markup=markup)
            time.sleep(1)
    else:
        return

    if turning_off:
        markup = types.InlineKeyboardMarkup()
        item1 = types.InlineKeyboardButton("В меню!", callback_data='start')

        markup.add(item1)

        bot.edit_message_text(f"Выключение...", chat_id, message_id, reply_markup=markup)

        os.system("shutdown -h now")


def reboot_in_time(chat_id: int, message_id: int, timing: int) -> None:
    global rebooting

    markup = types.InlineKeyboardMarkup()
    item1 = types.InlineKeyboardButton("Отменить!", callback_data='cancel_rebooting')

    markup.add(item1)

    bot.edit_message_text(f"Начинаю отсчет!", chat_id, message_id, reply_markup=markup)

    time.sleep(0.2)

    if rebooting:
        for i in reversed(range(timing)):
            if not rebooting:
                break

            bot.edit_message_text(f"Перезагружаюсь...\n\n<b>{i}</b>", chat_id, message_id, parse_mode='html', reply_markup=markup)
            time.sleep(1)
    else:
        return

    if rebooting:
        markup = types.InlineKeyboardMarkup()
        item1 = types.InlineKeyboardButton("В меню!", callback_data='start')

        markup.add(item1)

        bot.edit_message_text(f"Перезагрузка...", chat_id, message_id, reply_markup=markup)

        os.system("reboot now")


@bot.message_handler(commands=['start', 'menu', 'hello'])
def Welcome(message):
    if message.from_user.id != ADMIN_ID:
        return
    
    markup = types.InlineKeyboardMarkup()
    item1 = types.InlineKeyboardButton("Меню", callback_data='start')

    markup.add(item1)

    bot.send_message(message.from_user.id, "Нажмите на кнопку ниже!", reply_markup=markup)

    bot.delete_message(message.chat.id, message.id)


@bot.callback_query_handler(func = lambda call: True)
def callback_answer(call: types.CallbackQuery):
    global turning_off
    global rebooting

    author_id = call.message.chat.id

    if author_id != ADMIN_ID:
        return
    
    if call.data == "turn_off":
        turning_off = True
        Process(target=turn_off_in_time, args=(author_id, call.message.id, 10,)).start()

    elif call.data == "cancel_turn_off":
        markup = types.InlineKeyboardMarkup()
        item1 = types.InlineKeyboardButton("Обратно в меню!", callback_data='start')

        markup.add(item1)

        turning_off = False
        bot.edit_message_text("Выключение отменено!", author_id, call.message.id, reply_markup=markup)

    elif call.data == "get_ip":
        markup = types.InlineKeyboardMarkup()
        item1 = types.InlineKeyboardButton("Обратно в меню!", callback_data='start')

        markup.add(item1)

        turning_off = False

        ip = get_ip()

        if ip:
            bot.edit_message_text(f"<b>IP сервера:</b> <code>{ip}</code>", author_id, call.message.id, reply_markup=markup, parse_mode='html')
        else:
            bot.edit_message_text(f"Ошибка при получении IP!", author_id, call.message.id, reply_markup=markup, parse_mode='html')

    elif call.data == "cancel_rebooting":
        markup = types.InlineKeyboardMarkup()
        item1 = types.InlineKeyboardButton("Обратно в меню!", callback_data='start')

        markup.add(item1)

        rebooting = False
        bot.edit_message_text("Перезагрузка отменена!", author_id, call.message.id, reply_markup=markup)

    elif call.data == "start":
        markup = types.InlineKeyboardMarkup()
        item1 = types.InlineKeyboardButton("Выключить сервер", callback_data='turn_off')
        item2 = types.InlineKeyboardButton("Перезагрузить сервер", callback_data='reboot')
        item3 = types.InlineKeyboardButton("Получить IP", callback_data='get_ip')
        item4 = types.InlineKeyboardButton("Ввести команду в консоль", callback_data='enter_command')
        item5 = types.InlineKeyboardButton("Обновить меню", callback_data='start')

        markup.add(item1)
        markup.add(item2)
        markup.add(item3)
        markup.add(item4)
        markup.add(item5)

        bot.edit_message_text(f"Приветствую!\nВот ваше меню:", author_id, call.message.id, reply_markup=markup)

    elif call.data == "reboot":
        rebooting = True
        Process(target=reboot_in_time, args=(author_id, call.message.id, 10,)).start()

    elif call.data == "enter_command":
        markup = types.InlineKeyboardMarkup()
        item1 = types.InlineKeyboardButton("Ввести команду", callback_data="enter_command_text")
        markup.row(item1)

        commands = get_commands_json()
        if commands.get("saved"):
            item2 = types.InlineKeyboardButton("Сохраненные команды...", callback_data="saved_commands")
            markup.row(item2)
        if commands.get("last"):
            item3 = types.InlineKeyboardButton("Последние команды...", callback_data="last_commands")
            markup.row(item3)

        item4 = types.InlineKeyboardButton("Меню", callback_data="start")
        markup.row(item4)

        try:
            bot.delete_message(author_id, call.message.id)
        except:
            pass

        bot.send_message(author_id, f"Выберите действие", reply_markup=markup)

    elif call.data == "enter_command_text":
        msg = bot.edit_message_text(f"Введите команду или введите 'отмена': ", author_id, call.message.id)
        bot.register_next_step_handler(msg, after_command_enter, call.message.id)

    elif call.data == "last_commands":
        markup = types.InlineKeyboardMarkup()

        commands = get_commands_json()

        if len(commands.get("last")) < 10:
            for val, item in enumerate(commands.get("last")):
                btn = types.InlineKeyboardButton(item[:15], callback_data=f"cmd_{val}")
                markup.row(btn)
        else:
            temp = []
            for val, item in enumerate(commands.get("last")):
                if len(temp) >= (2 if len(commands.get("last")) < 20 else 3):
                    markup.row(*temp)
                    temp = []

                btn = types.InlineKeyboardButton(item[:15], callback_data=f"cmd_{val}")
                temp.append(btn)

            markup.row(*temp)
            temp = []

        item_last = types.InlineKeyboardButton("Меню", callback_data="start")
        markup.row(item_last)

        bot.edit_message_reply_markup(author_id, call.message.id, reply_markup=markup)

    elif call.data.startswith("cmd_"):
        index = int(call.data.replace("cmd_", ""))

        commands = get_commands_json()
        cmd = commands["last"][index]

        call.message.text = cmd

        return after_command_enter(call.message)

    elif call.data == "delete_message":
        bot.delete_message(author_id, call.message.id)


def after_command_enter(msg: types.Message, message_id: Union[int, None] = None):
    if message_id and msg.text.lower() == "отмена":
        markup = types.InlineKeyboardMarkup()
        item1 = types.InlineKeyboardButton("Обратно в меню!", callback_data='start')

        markup.add(item1)
        bot.edit_message_text("Ввод отменен!", msg.chat.id, message_id, reply_markup=markup)
        return
    
    bot.delete_message(msg.chat.id, msg.id)

    # code = None
    # got_error = None
    # try:
    #     code = os.system(msg.text)
    # except Exception as ex:
    #     got_error = str(ex)
    #     print(traceback.format_exc())
    #     logging.critical(traceback.format_exc())

    # markup = types.InlineKeyboardMarkup()
    # item1 = types.InlineKeyboardButton("Обратно в меню!", callback_data='start')

    # markup.add(item1)
    # if got_error:
    #     bot.edit_message_text(f"Во время ввода произошла ошибка! Получаемые данные: [{got_error}]", msg.chat.id, message_id, reply_markup=markup)
    # else:
    #     bot.edit_message_text(f"Ввод совершен успешно! Получаемые данные: [{code}]", msg.chat.id, message_id, reply_markup=markup)

    commands_json = get_commands_json()
    if not commands_json.get("last") or not isinstance(commands_json.get("last"), list):
        commands_json["last"] = [msg.text]
    else:
        commands_json["last"] = [msg.text] + commands_json["last"]

        if len(commands_json["last"]) > 24:
            commands_json["last"] = commands_json["last"][:24]

    write_commands_json(commands_json)

    got_error = None
    output = None
    try:
        args = str(msg.text).split(" ")
        output = subprocess.run(args, stdout=subprocess.PIPE)
    except Exception as ex:
        got_error = str(ex)
        print(traceback.format_exc())
        logging.critical(traceback.format_exc())

    markup = types.InlineKeyboardMarkup()
    item1 = types.InlineKeyboardButton("Обратно в меню!", callback_data='start')

    markup.add(item1)
    if got_error:
        if message_id:
            bot.edit_message_text(f"Во время ввода произошла ошибка! Получаемые данные: [{got_error}]", msg.chat.id, message_id, reply_markup=markup)
        else:
            bot.send_message(msg.chat.id, f"Во время ввода произошла ошибка! Получаемые данные: [{got_error}]", reply_markup=markup)
    else:
        try:
            output = output.stdout.decode('utf-8')
        except:
            print(traceback.format_exc())
            logging.critical(traceback.format_exc())
        
        if message_id:
            bot.edit_message_text(f"Ввод совершен успешно! Получаемые данные:\n\n{output}", msg.chat.id, message_id, reply_markup=markup)
        else:
            bot.send_message(msg.chat.id, f"Ввод совершен успешно! Получаемые данные:\n\n{output}", reply_markup=markup)


while True:
    try:
        bot.polling(none_stop=True, interval=0)
    except:
        print(traceback.format_exc())
        logging.critical(traceback.format_exc())
        time.sleep(10)
