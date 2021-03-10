#!/usr/bin/python
from __future__ import print_function

import telebot
import db
import user_repository
import lab_repository
import question_repository
import answer_option_repository
import progress_repository
import answer_repository
import api
import util
from telebot import types

bot = telebot.TeleBot("TOKEN")
spreadsheetApi = api.init_google_spreadsheet_api()
driveApi = api.init_google_drive_api()
db = db.init_database_connection()


def pass_lab(message):
    if lab_repository.is_user_has_unfinished_labs(message.from_user.id):
        bot.send_message(message.chat.id, 'Чтобу начать новую лаборотную работу сначало завершите текущию')
    else:
        markup = types.ReplyKeyboardRemove(selective=False)
        bot.send_message(message.chat.id, "ID лабороторной работы", reply_markup=markup)
        bot.register_next_step_handler(message, process_pass_lab_step)


def process_pass_lab_step(message):
    if not lab_repository.is_lab_exist(message.text):
        bot.send_message(message.chat.id, "Лабороторная работа не существует")
        bot.register_next_step_handler(message, pass_lab)
        return
    if lab_repository.is_user_finished_lab(message.from_user.id, message.text):
        bot.send_message(message.chat.id, "Вы уже проходили эту работу")
        bot.register_next_step_handler(message, pass_lab)
    else:
        lab_repository.create_new_lab_for_user(message.from_user.id, message.text)
        current_question_id = progress_repository.get_current_question(message.from_user.id)[0]
        question = question_repository.get_question(current_question_id)
        if question[0][1] == 1:
            markup = types.ReplyKeyboardMarkup()
            for i in range(0, len(question[1])):
                markup.add(types.KeyboardButton(question[1][i][0]))
            bot.send_message(message.chat.id, 'Выберите ответ', reply_markup=markup)
        else:
            bot.send_message(message.chat.id, question[0][0])


def answer(message):
    if lab_repository.is_user_has_unfinished_labs(message.from_user.id):
        current_question = progress_repository.get_current_question(message.from_user.id)
        answer_repository.create_answer(message.from_user.id, current_question[1], message.text)

        if progress_repository.set_next_question(message.from_user.id, current_question[1], current_question[0]):
            markup = types.ReplyKeyboardMarkup()
            markup.add(types.KeyboardButton("Создать лабораторную работу"))
            markup.add(types.KeyboardButton("Пройти лабораторную работу"))
            bot.send_message(message.chat.id, 'Лабораторная работа завершена', reply_markup=markup)

            spreadsheet_link = lab_repository.get_answer_spreadsheet_link(current_question[1])
            answers = answer_repository.get_answers(message.from_user.id, current_question[1])
            full_name = user_repository.get_user_full_name(message.from_user.id)
            print(spreadsheet_link)
            print(answers)

            sheet_info = spreadsheetApi.spreadsheets().get(spreadsheetId=spreadsheet_link).execute()["sheets"][0][
                "properties"]
            values = [
                [
                ],
            ]
            values[0].append(full_name)
            for i in range(0, len(answers)):
                values[0].append(answers[i][0])
            body = {
                'values': values
            }
            print(values)
            try:
                result = spreadsheetApi.spreadsheets().values().append(
                    spreadsheetId=spreadsheet_link, range=sheet_info["title"],
                    valueInputOption="RAW", body=body).execute()
            except Exception as e:
                print(e)
        else:
            current_question_id = progress_repository.get_current_question(message.from_user.id)[0]
            question = question_repository.get_question(current_question_id)
            if question[0][1] == 1:
                markup = types.ReplyKeyboardMarkup()
                for i in range(0, len(question[1])):
                    markup.add(types.KeyboardButton(question[1][i][0]))
                bot.send_message(message.chat.id, 'Выберите ответ', reply_markup=markup)
            else:
                markup = types.ReplyKeyboardRemove(selective=False)
                bot.send_message(message.chat.id, question[0][0], reply_markup=markup)


class Lab:
    def __init__(self, lab_id):
        self.lab_id = lab_id


labs = {}


def create_lab(message):
    markup = types.ReplyKeyboardRemove(selective=False)
    bot.send_message(message.chat.id,
                     'Ссылка на Google таблица с вопросами. Таблица должна быть доступна для всех у кого есть ссылка. '
                     'Ссылка вида: '
                     'https://docs.google.com/spreadsheets/d/1QmmRlZcEP_9ul_0iEXkivNYeGDjeZDXbPTC5G_Kjcf8/edit?usp'
                     '=sharing',
                     reply_markup=markup)
    bot.register_next_step_handler(message, process_question_spreadsheet_link_step)


def process_question_spreadsheet_link_step(message):
    try:
        if not util.is_url(message.text):
            new_message = bot.send_message(message.chat.id, 'Некорректная ссылка')
            bot.register_next_step_handler(new_message, create_lab(new_message))
        else:
            chat_id = message.chat.id
            lab_id = lab_repository.create_lab()
            lab = Lab(lab_id)
            labs[chat_id] = lab
            spreadsheet_id = util.extract_google_spreadsheet_id(message.text)
            sheet_info = spreadsheetApi.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()["sheets"][0][
                "properties"]
            sheet = spreadsheetApi.spreadsheets().values().get(spreadsheetId=spreadsheet_id,
                                                               range=sheet_info["title"]).execute()["values"]
            for i in range(len(sheet)):
                question_id = question_repository.create_question(lab_id, sheet[i][0], len(sheet[i]) != 1)
                for j in range(1, len(sheet[i])):
                    answer_option_repository.create_answer(question_id, sheet[i][j])

            new_message = bot.send_message(message.chat.id,
                                           'Ссылка на Google Disk папку для ответов. Папка должна быть доступна для '
                                           'всех у кого есть ссылка. Ссылка вида: '
                                           'https://drive.google.com/drive/folders/1BqyY_KkwdK2lcxxGKinq5bKYYbJ75klv'
                                           '?usp=sharing')
            bot.register_next_step_handler(new_message, process_answer_spreadsheet_link_step)
    except Exception as e:
        bot.register_next_step_handler(message, create_lab(message))


def process_answer_spreadsheet_link_step(message):
    try:
        if not util.is_url(message.text):
            new_message = bot.send_message(message.chat.id, 'Некорректная ссылка')
            bot.register_next_step_handler(new_message, process_answer_spreadsheet_link_step)
        else:
            chat_id = message.chat.id
            lab = labs[chat_id]
            spreadsheet = {
                'properties': {
                    'title': "Ответы " + str(lab.lab_id)
                }
            }
            new_spreadsheet_id = \
                spreadsheetApi.spreadsheets().create(body=spreadsheet, fields='spreadsheetId').execute()[
                    "spreadsheetId"]

            lab_repository.set_answer_spreadsheet_link(lab.lab_id, new_spreadsheet_id)

            permission = {
                'type': 'anyone',
                'role': 'writer',
            }
            driveApi.permissions().create(fileId=new_spreadsheet_id, body=permission, fields='id').execute()

            folder_id = util.extract_google_disc_folder(message.text)
            file = driveApi.files().get(fileId=new_spreadsheet_id, fields='parents').execute()
            driveApi.files().update(fileId=new_spreadsheet_id, addParents=folder_id,
                                    removeParents=",".join(file.get('parents')), fields='id, parents').execute()
            markup = types.ReplyKeyboardMarkup()
            markup.add(types.KeyboardButton("Создать лабораторную работу"))
            markup.add(types.KeyboardButton("Пройти лабораторную работу"))
            bot.send_message(message.chat.id, "Лабораторная работа создана, ID: " + str(lab.lab_id),
                             reply_markup=markup)
    except Exception as e:
        bot.register_next_step_handler(message, create_lab(message))


@bot.message_handler(commands=['start'])
def start_message(message):
    if not user_repository.is_user_exist(message.from_user.id):
        bot.send_message(message.chat.id, "ФИО")
        bot.register_next_step_handler(message, process_register_link_step)
    markup = types.ReplyKeyboardMarkup()
    markup.add(types.KeyboardButton("Создать лабораторную работу"))
    markup.add(types.KeyboardButton("Пройти лабораторную работу"))
    bot.send_message(message.chat.id, 'Выберите действие', reply_markup=markup)


def process_register_link_step(message):
    try:
        if not user_repository.is_user_exist(message.from_user.id):
            user_repository.create_user(message.from_user.id, message.text)
        markup = types.ReplyKeyboardMarkup()
        markup.add(types.KeyboardButton("Создать лабораторную работу"))
        markup.add(types.KeyboardButton("Пройти лабораторную работу"))
        bot.send_message(message.chat.id, 'Выберите действие', reply_markup=markup)
    except Exception as error:
        bot.register_next_step_handler(message, start_message)


@bot.message_handler(func=lambda m: True)
def new_message(message):
    if message.text == 'Создать лабораторную работу':
        create_lab(message)
        return
    if message.text == 'Пройти лабораторную работу':
        pass_lab(message)
        return
    answer(message)


bot.enable_save_next_step_handlers(delay=2)
bot.load_next_step_handlers()
bot.polling()
