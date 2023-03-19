# Импорт всех необходимых библиотек
import speech_recognition  # Работа со звуком
import webbrowser  # Работа с браузером
import wikipedia  # Поиск статьи в википедии
import keyboard  # Отслеживание клавиш
import winsound  # Воспроизведение звуков
import pyttsx3  # Синтез речи
import json  # Работа с Json-файлами
import os  # Работа с операционной системой
import openai  # Искуственный интеллект
import subprocess  # Открытие файлов в операционной системе
from telegram_assistant import my_answer_send  # Команда для отправки запроса


# Главный код
# Получение токена OpenAI
with open("Resources/Files/OpenAI_token", "r") as file:
    openai.api_key = file.read()

# Функции для сохранения ответа от ассистента
def save_to_file_answer(info, file):
    # Запись текста в файл
    if file == "text":
        # Создание текстового файла
        with open("Resources/Files/Answer.txt", "w+", encoding="utf-8") as file:
            file.write(info)


# Класс голосового ассистента
class VoiceAssistant():
    # Начальные настройки
    def __init__(self):

        '''Настройка синтезатора'''
        # Инициализация синтезатора
        self.engine = pyttsx3.init()

        # Изменение голосовой модели
        id_voice = 0
        for i, string in enumerate(self.engine.getProperty("voices")):
            if "Anna" in str(string):
                id_voice = i

        self.engine.setProperty('voice', (self.engine.getProperty("voices"))[id_voice].id)

        # Переменная для того, чтобы не повторять туториал диалога
        self.tutor = 0

        # Открытие файла для синхронизации информации
        with open("Resources/Files/Name.txt", "r", encoding="utf-8") as file:
            # Получение имени пользователя
            self.name = str(file.read())

        # Настройка языка для Википедии
        wikipedia.set_lang("ru")

        '''Настройка инструментов для работы с голосом'''
        # Распознаватель голоса
        self.recognizer = speech_recognition.Recognizer()
        # Подключение к микрофону
        self.microphone = speech_recognition.Microphone()

        # Настройка шума для микрофона
        with self.microphone:
            self.recognizer.adjust_for_ambient_noise(self.microphone, duration=2)

    # Распознавание речи
    def get_text(self):
        # Подключение к микрофону
        with self.microphone:

            # Будущий текст
            text = ""

            '''Формирование ответа и обработка ошибок'''
            try: # Попытка записи звука

                # Звук начала записи звука
                winsound.PlaySound("Resources/Sound/start_rec.wav", winsound.SND_FILENAME)
                # Настройка и запись аудио-дорожки
                audio = self.recognizer.listen(self.microphone, 5, 10)

            except speech_recognition.WaitTimeoutError: # Ошибка: Голос не распознан
                # Информирование пользователя
                self.speak_text("Попробуйте спросить ещё раз.")
                # Вывод ничего
                return

            try: # Попытка распознавания голоса через Google

                # Логи для консоли
                print("Начинаю распознавание речи через Google...")
                # Распознанный текст
                text = self.recognizer.recognize_google(audio, language="ru")

            except speech_recognition.UnknownValueError: # Ошибка: вход подана запись без слов
                # Информирование пользователя
                self.speak_text("Попробуйте спросить ещё раз.")

            except speech_recognition.RequestError: # Ошибка: Нет интернета
                # Информирование пользователя
                self.speak_text("Отсутствует подключение к интернету.")

            '''Отправка текста на верификацию запроса'''
            return text

    # Функция отвечающая за голос ассистента
    def speak_text(self, text):
        # Подготовка текста для озвучка
        self.engine.say(text=text)
        # Воспроизведение текста
        self.engine.runAndWait()

    # Обработка запроса
    def request_verification(self, data):
        # Изменение текста в список слов
        data = data.lower().split()

        '''Проверка на команды'''
        if len(data) >= 2:

            # Блок команд с ключевым словом - скажи
            if data[0] == "скажи":
                self.speak_text(" ".join(data[1:]))

            # Блок команд с ключевым словом - включи
            elif data[0] == "включи":
                pass

            # Создание файла со статьёй
            elif data[0] == "сохрани" or data[0] == "запиши":

                # Сохранение предыдущей информации
                if data[1] == "это":
                    # Сохранение пути
                    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
                    # Имя файла
                    file_name = "Запрос.txt"
                    file_path = os.path.join(desktop_path, file_name)

                    with open(file_path, "w") as file1:
                        with open("Resources/Files/Answer.txt", "r") as file2:
                            file1.write(file2.read())

                    # Написать текст
                    self.speak_text(f"Файл был создан на вашем рабочем столе")

                if data[1] == "информацию" and data[2] == "про":
                    # Сохранение пути
                    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
                    # Имя файла
                    file_name = "запрос.txt"
                    # Путь к файлу
                    file_path = os.path.join(desktop_path, file_name)
                    # Название статьи
                    data = " ".join(data[3:])
                    text = wikipedia.summary(data, sentences=10)
                    # Создание файла
                    with open(file_path, "w+", encoding="utf-8") as file:
                        # Запись в файл статьи
                        file.write(str(text))
                    # Информирование пользователя
                    self.speak_text("файл создан")
                    # Сохранение последнего запроса
                    with open("Resources/Files/Answer.txt", "w+", encoding="utf-8") as file:
                        file.write(str(text))


            # Блок команд с ключевым словом создай
            elif data[0] == "создай":

                # Создание папки
                if data[1] == "папку":

                    # Имя папки
                    name = " ".join(data[2:]).replace("с именем", "").lower()

                    # Путь к рабочему столу
                    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")

                    # Путь к папке
                    folder_path = os.path.join(desktop_path, name)

                    # Папка содаётся в случае отсутствия такой же на рабочем столе
                    if not os.path.exists(folder_path):
                        os.mkdir(folder_path)
                        self.speak_text(f"Папка {name} была создана на рабочем столе")
                    else:
                        self.speak_text(f"Папка {name} уже существует на рабочем столе")

            # Поиск статьи про слово
            elif data[0] == "информация" and data[1] == "на" and data[2] == "тему":
                try:
                    data = " ".join(data[3:])
                    text = wikipedia.summary(data, sentences=3)
                    with open("Resources/Files/Answer.txt", "w+", encoding="utf-8") as file:
                        file.write(str(text))
                    self.speak_text(str(text))
                except:
                    self.speak_text("Произошла ошибка при поиске статьи, попробуйте ещё раз")

            # Поиск видео
            elif data[0] == "видео" and data[1] == "на" and data[2] == "тему":
                self.youtube_search(" ".join(data[3:]))


            # Блок команд с ключевым словом удали
            elif data[0] == "удали":

                # Удаление папки
                if data[1] == "папку":
                    # Имя папки
                    name = " ".join(data[2:]).replace("с именем", "").lower()

                    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")

                    folder_path = os.path.join(desktop_path, name)

                    if os.path.exists(folder_path):
                        os.rmdir(folder_path)
                        self.speak_text(f"Папка {name} была удалена с рабочего стола")
                    else:
                        self.speak_text(f"Папка {name} не существует на рабочем столе")

            # Блок кода с ключевым словом открой
            elif data[0] == "открой":

                # Открытие папки
                if data[1] == "папку":
                    # Имя папки
                    name = " ".join(data[2:]).replace("с именем", "").lower()

                    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")

                    folder_path = os.path.join(desktop_path, name)

                    if os.path.exists(folder_path):
                        subprocess.Popen(["explorer.exe", folder_path])
                        self.speak_text(f"Папка {name} была успешно открыта")
                    else:
                        self.speak_text(f"Папка {name} не существует на рабочем столе")


            # Запуск диалога
            elif data[0] == "давай" and data[1] == "поговорим":
                self.dialog_assistant(mode=0)

        # Инструкции с одним словом
        elif len(data) == 1:

            # Запуск диалога одним словом
            if data[0] == "диалог":
                self.dialog_assistant(mode=0)

            if data[0] == "отмена":
                pass

            if data[0] == "выключение":
                winsound.PlaySound("Resources/Sound/bye_rec.wav", winsound.SND_FILENAME)
                # Информирование пользователя
                self.speak_text("Выключение.")
                # Конечный выход
                exit()


            # Старт
            if data[0] == "старт":

                self.speak_text("Открываю презентацию")

                desktop_path = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
                file_path = os.path.join(desktop_path, 'ГолосовойАссистент.pptx')

                os.startfile(file_path)

                from time import sleep
                sleep(10)
                self.speak_text("Тема проекта - голосовой ассистент на пайтон")

            # Конец
            if data[0] == "конец":
                winsound.PlaySound("Resources/Sound/bye_rec.wav", winsound.SND_FILENAME)
                self.speak_text("Спасибо за внимание!")
                exit()

    # Поиск видео
    def youtube_search(self, search):
        # Формирование ссылки
        url = "https://www.youtube.com/results?search_query=" + search
        # Открытие ссылки в браузере
        webbrowser.get().open(url)
        # Информирование пользователя
        self.speak_text(f"{self.name}, вот какие видео мне удалось найти по запросу {search}")

    def yandex_search(self, search):
        # Формирование ссылки
        url = "https://yandex.ru/search/?clid=2456107&text=" + search.replace(" ", "+")
        # Открытие ссылки в браузере
        webbrowser.get().open(url)
        # Информирование пользователя
        self.speak_text(f"{self.name}, вот, что мне удалось найти по запросу {search}")

    # Формирование ответа OpenAI на сообщение
    def generate_text(self, text, code=1):
        # Формирование json-файла с ответом
        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=text,
            temperature=0.5,
            max_tokens=300,
            top_p=1.0,
            frequency_penalty=0.5,
            presence_penalty=0.0
        )
        # Вывод текста
        if code:
            response = response["choices"][0]["text"].replace("\n", " ")
        else:
            return str(response["choices"][0]["text"].replace(" ", "\n"))
        return str(response)

    # Запуск диалога
    def dialog_assistant(self, mode):
        # Информирование о правилах диалога
        if self.tutor == 0:
            self.speak_text("Чтобы спросить нажмите знак минуса")
            self.speak_text("Чтобы выйти из разговора нажмите шифт")
        else:
            self.speak_text("Диалог запущен")
        # Цикл работы
        while True:

            # Нажатие кнопки для совершения запроса
            if keyboard.is_pressed("-"):
                # Получение речи пользователя
                if mode:
                    text = input("Дебаг консоль диалога: ")
                else:
                    text = self.get_text()
                # Продолжение диалога, если в речи есть слова
                if text:

                    # При вопросе будет ставиться знак вопроса
                    if "вопрос" in text:
                        text += "?"
                        # Отправка нейросети речи пользователя
                        answer = self.generate_text(text)
                        # Ответ от нейросети
                        self.speak_text(answer)

                        # Запись ответа от нейросети в файл
                        save_to_file_answer(f"Вы: {text}\n\nИИ:{answer}", "text")

                    # При желании продолжить фразу, точка ставиться не будет
                    elif "продолжи фразу" in text:
                        answer = self.generate_text(text)
                        # Ответ от нейросети
                        self.speak_text(f"{text[14:]} - {answer}")

                        # Запись ответа от нейросети в файл
                        save_to_file_answer(f"Вы: {text}\n\nИИ:{answer}", "text")

                    # Если в задачу входит написание кода, то программа не будет его проговаривать
                    elif "напиши код" in text or "создай код" in text:
                        answer = self.generate_text(text)
                        # Сохранение файла
                        save_to_file_answer(f"Ваш запрос для кода{text}\n\nОтвет:\n{answer}", "text")
                        # Отправка кода в личные сообщения через бота в телеграмм
                        my_answer_send()
                        # Код от нейросети
                        self.speak_text(f"Код был успешно создан и отправлен вам в личные сообщения")

                    # При обычной речи будет ставиться точка
                    else:
                        text += "."
                        # Отправка нейросети речи пользователя
                        answer = self.generate_text(text)
                        # Ответ от нейросети
                        self.speak_text(answer)

                        # Запись ответа от нейросети в файл
                        save_to_file_answer(f"Вы: {text}\n\nИИ:{answer}", "text")

            # Отправка предыдущего ответа
            elif keyboard.is_pressed("0"):
                # Вызов функции для создания бота
                my_answer_send()
                # Информирование пользователя
                start.speak_text("Последний запрос для искусственного интеллекта был успешно отправлен вам")


            # Выход из функции
            elif keyboard.is_pressed("SHIFT"):
                # Информирование пользователя
                self.speak_text("Выход из диалога.")
                if self.tutor == 0:
                    self.tutor += 1
                return



# Запуск пуллинга
if __name__ == "__main__":

    # Создание объекта VoiceAssistant
    start = VoiceAssistant()

    # Вывод лога о старте обработки событий
    print("Главный цикл запущен.")

    # Цикл обработки событий
    while True:

        '''Обработка нажатия кнопок'''

        # Голосовая команда
        if keyboard.is_pressed("+"):
            # Вызов соответствующей функции
            text = start.get_text()
            if text:
                start.request_verification(text)

        # Запуск диалога
        elif keyboard.is_pressed("-"):
            # Вызов функции бесконечного диалога
            start.dialog_assistant(mode=0)

        # Отправка предыдущего ответа
        elif keyboard.is_pressed("0"):
            # Вызов функции для создания бота
            my_answer_send()
            # Информирование пользователя
            start.speak_text("Последний запрос был успешно отправлен вам")

        # Отключение программы
        elif keyboard.is_pressed("SHIFT"):
            # Проигрывание звука выключения
            winsound.PlaySound("Resources/Sound/bye_rec.wav", winsound.SND_FILENAME)
            # Информирование пользователя
            start.speak_text("Выключение.")
            # Конечный выход
            exit()
