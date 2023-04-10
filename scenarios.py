import sys
import inspect
from abc import ABC, abstractmethod
from typing import Optional
from random import randint, choice

from helper import Helper
from request import Request
from response_helpers import button

helper = Helper({})
NAME = "\"Математический мозговой тренажёр\""


def init_helper(event):
    global helper
    helper = Helper(event)


class Scenario(ABC):
    """ Abstract class of scenarios """
    @classmethod
    def id(cls):
        return cls.__name__

    """ Scenario response generation """
    @abstractmethod
    def reply(self, request):
        raise NotImplementedError()

    """ Scenario response generation if user needs help """
    @abstractmethod
    def help(self, request):
        raise NotImplementedError

    @abstractmethod
    def handle_local_intents(self, request: Request) -> Optional[str]:
        raise NotImplementedError()

    def fallback(self, request: Request, buttons=None):
        """ Called when the user's intent is not clear """
        excuses = ['Прошу прощения. ', 'Простите меня. ', 'Приношу свои извинения. ', 'Извините. ', '']
        incomprehension = ['Я вас не поняла.', 'Пожалуйста повторите еще раз.',
                           'Пожалуйста, попробуйте переформулировать запрос.']
        return self.make_response(choice(excuses) + choice(incomprehension) + ' Скажите \"Повтори\", чтобы я повторила.'
                                  , buttons=buttons + [
                                      button('Повтори', hide=True),
                                      button('В самое начало', hide=True),
                                      button('Помощь', hide=True),
                                      button('Что умеет навык?', hide=True)
                                  ])

    def make_response(self, text, tts=None, card=None, state=None, buttons=None, directives=None, end_session=None):
        """
        :param text: required property. The text to be shown and spoken to the user.
        :param tts: response in TTS (text-to-speech) format. If tts is empty tts = text
        :param card: posts with image support. If the application is able to display the card to the user,
            the response.text property is not used.
        :param state: an object containing the state of the skill to store.
        :param buttons: array of objects. The buttons to show to the user.
        :param directives: directives. The content depends on the directive type. Possible values:
            audio_player;
            start_account_linking.
        :param end_session: boolean. Required property. Sign of the end of the conversation.
        :return: response to be serialized as JSON.
        """
        if tts is None:
            tts = text
        tts = '<speaker audio=\"dialogs-upload/75986b16-ef4a-48ae-95ce-e95c020ae7a3/661bc281-2f05-4593-9cad-6a6f9caa3e1c.opus\">' + \
              tts + '<speaker audio=\"dialogs-upload/75986b16-ef4a-48ae-95ce-e95c020ae7a3/bdc67ca3-0972-4599-bc26-dedb90f25c45.opus\">'
        response = {
            'text': text,
            'tts': tts,
        }
        if card is not None:
            response['card'] = card
        if buttons is not None:
            response['buttons'] = buttons
        if directives is not None:
            response['directives'] = directives
        webhook_response = {
            'response': response,
            'version': '1.0',
            'session_state': {
                'scenario': self.id(),
            },
        }
        if state is None:
            state = {'showed': helper.showed}
        elif 'showed' not in state:
            state.update({'showed': helper.showed})
        webhook_response['session_state'].update(state)
        if end_session:
            webhook_response['end_session'] = True
        return webhook_response

    @property
    def buttons(self):
        raise NotImplementedError()


class Welcome(Scenario):
    """ Welcome scenario """
    def reply(self, request: Request):
        variants = ['Добро пожаловать в навык ' + NAME + '. Данный навык поможет детям и' 
                    ' школьникам разобраться как в базовых, так и в углублённых арифметических действиях, используя ' 
                    'устный счёт. Например, сложение, вычитание, умножение и так далее. Скажите \"Начнем\", чтобы ' 
                    'начать или \"Что ты умеешь?\", чтобы узнать, что умеет навык.',
                    'Привет, это навык ' + NAME + ' давай посчитаем? Скажите \"Начнем\", чтобы '
                    'начать или \"Что ты умеешь?\", чтобы узнать, что умеет навык.',
                    'Приветствую тебя, данный навык поможет детям и школьникам разобраться как в базовых, так и в '
                    'углублённых арифметических действиях, используя устный счёт. Например, сложение, вычитание, '
                    'умножение и так далее, займемся устным счетом? Скажите \"Начнем\", чтобы начать или \"Что ты '
                    'умеешь?\", чтобы узнать, что умеет навык.',
                    'Добро пожаловать в навык ' + NAME + ', посчитаем? Скажите \"Начнем\", '
                    'чтобы начать или \"Что ты умеешь?\", чтобы узнать, что умеет навык.',
                    'Привет! Вы зашли в навык ' + NAME + '. Давайте оценим твои умения! Если вы'
                    ' хотите узнать, что я умею, так и скажите. Если вы хотите остановить навык, скажите \"Хватит\". '
                    'Вы готовы?']
        text = choice(variants)
        return self.make_response(text, buttons=self.buttons)

    def help(self, request: Request):
        variants = ['Вы оказались в навыке ' + NAME + '! Вы можете узнать, что умеет этот навык'
                    ', сказав \"Что умеет этот навык?\". Или начать игру, сказав \"Начнем\"',
                    'Это навык ' + NAME + '. Чтобы узнать, что умеет навык, нужно сказать \"Что'
                    ' ты умеешь\". Чтобы вернуться назад, так и скажите. Или может просто начнем?']
        text = choice(variants)
        return self.make_response(text, buttons=self.buttons + [
            button('Повторить', hide=True)
        ])

    def handle_local_intents(self, request: Request):
        if 'start_confirm' in request.intents or 'YANDEX.CONFIRM' in request.intents:
            return StartBody()
        elif 'start_reject' in request.intents or 'YANDEX.REJECT' in request.intents:
            return Parting()
        elif 'help' in request.intents:
            return Help()

    @property
    def buttons(self):
        agreements = ['Да', 'Давай', 'С радостью']
        failures = ['Нет', 'В другой раз', 'Не сейчас', 'Как-нибудь потом']
        helps = ['Что умеет этот навык?']
        buttons = [
            button(choice(agreements), hide=True),
            button(choice(failures), hide=True),
            button(choice(helps), hide=True)
        ]
        return buttons


class Parting(Scenario):
    """ Parting scenario """
    def reply(self, request: Request):
        variants = ['Хорошо, до новых встреч!', 'Жаль, а так хотелось посмотреть вас в деле.',
                    'Ну ничего в следующий раз.', 'Ну ничего. Будет скучно - обращайтесь.']
        text = choice(variants)
        return self.make_response(text, end_session=True)

    def help(self, request):
        pass

    def handle_local_intents(self, request: Request):
        pass

    @property
    def buttons(self):
        return []


class Help(Scenario):
    """ This scenario shows what the skill is capable of """
    def reply(self, request):
        variants = ['Навык ' + NAME + ' представляет из себя программу, которая  предлагает'
                    ' выполнить расчёты в уме, используя простейшие арифметические действия, также может рассказать'
                    ' что-нибудь интересное и увлекательное. Скажите \"В начало\", чтобы вернуться в начало навыка.'
                    ' Вы можете попросить повторить последнее сообщение, сказав \"Повтори\". Команда \"Стоп\" нужна для'
                    ' того, чтобы покинуть навык.',
                    '' + NAME + ' - полезный и увлекательный навык, который в игровой форме'
                    ' поможет разобраться с умением счёта в уме. Навык предложит решить вам задания, укажет на ваши'
                    ' ошибки и оценит ваши умения. Скажите \"В начало\", чтобы вернуться в начало навыка. Вы можете'
                    ' попросить повторить последнее сообщение, сказав \"Повтори\". Команда \"Стоп\" нужна для того,'
                    ' чтобы покинуть навык.',
                    'В жтом навыке вы будете выполнять расчёты без ручки и бумаги. Ваша цель ответить на все вопросы'
                    ' используя только устный счёт. А еще навык укажет на ваши ошибки и оценит ваши умения. Скажите '
                    '\"В начало\", чтобы вернуться в начало навыка. Вы можете попросить повторить последнее сообщение, '
                    'сказав \"Повтори\". Команда \"Стоп\" нужна для того, чтобы покинуть навык.',
                    'Этот навык нацелен на работу с простейшими арифметическими действиями: сложение, вычитание, '
                    'умножение, деление, операции с дробями, возведение в степень, вычисление квадратного корня, '
                    'тригонометрические табличные значения. Также навык укажет на ваши ошибки и оценит ваши умения. '
                    'Скажите \"В начало\", чтобы вернуться в начало навыка. Вы можете попросить повторить последнее '
                    'сообщение, сказав \"Повтори\". Команда \"Стоп\" нужна для того, чтобы покинуть навык. Не '
                    'волнуйтесь, по ходу действий вы всё поймёте.']
        text = choice(variants)
        return self.make_response(text + ' Начнём?', buttons=self.buttons)

    def help(self, request: Request):
        variants = ['Если вы хотите вернуться назад, просто скажите \"Назад\".',
                    'Вы узнали, что умеет навык, хотите вернуться назад?',
                    'Не переживайте, вы все поймете, вернемся назад?']
        text = choice(variants)
        return self.make_response(text, buttons=self.buttons + [
            button('Повторить', hide=True),
            button('Назад', hide=True)
        ])

    def handle_local_intents(self, request: Request):
        if 'YANDEX.CONFIRM' in request.intents or 'start_confirm' in request.intents or 'back' in request.intents:
            return StartBody()
        elif 'YANDEX.REJECT' in request.intents:
            return Parting()

    @property
    def buttons(self):
        confirms = ['Давай начнём', 'Погнали', 'Поехали', 'Вперед']
        buttons = [
            button(choice(confirms), hide=True),
        ]
        return buttons


class StartBody(Scenario):
    """ This scenario prompts user to select a task to choose from """
    def __init__(self):
        self._options_text = ['1) сложение, вычитание',
                              '2) умножение, деление',
                              '3) операции с дробями',
                              '4) возведение в степень',
                              '5) вычисление квадратного корня',
                              '6) тригонометрические табличные значения']
        self._options_tts = ['sil <[500]> первое. сложение, вычитание sil <[500]> ',
                             'второе. умножение, деление sil <[500]> ',
                             'третье. операции с дробями sil <[500]> ',
                             'четвертое. возведение в степень sil <[500]> ',
                             'пятое. вычисление квадратного корня sil <[500]> ',
                             'шестое. тригонометрические табличные значения sil <[500]> ']

    def reply(self, request: Request):
        variants = ['С каким типом заданий вы бы хотели поработать?', 'Выберите тип задания.',
                    'Какое задание вам по душе?']
        text = choice(variants)
        tts = text +\
               self._options_tts[0] +\
               self._options_tts[1] +\
               self._options_tts[2] +\
               self._options_tts[3] +\
               self._options_tts[4] +\
               self._options_tts[5]
        return self.make_response(text, tts=tts, buttons=self.buttons)

    def help(self, request: Request):
        variants = ['Сейчас вам нужно выбрать один из типов заданий, которые вы хотите пройти. Если хотите еще раз'
                    ' ознакомиться со списком вариантов скажите \"Повторить\" или просто выберите задание.',
                    'Навык содержит 6 типов заданий, ваша задача выбрать один из типов. Чтобы услышать варианты выбора,'
                    ' скажите \"Повторить\".']
        text = choice(variants)
        return self.make_response(text, buttons=self.buttons + [
            button('Повторить', hide=True)
        ])

    def handle_local_intents(self, request: Request):
        if 'repeat_variant' in request.intents:
            if request.intents['repeat_variant']['slots']['Variant']['value'] > 0 and request.intents['repeat_variant']['slots']['Variant']['value'] < 7:
                text = self._options_text[request.intents['repeat_variant']['slots']['Variant']['value'] - 1] + '. Назовите номер, выбранного задания.'
                tts = self._options_tts[request.intents['repeat_variant']['slots']['Variant']['value'] - 1] + ' Назовите номер, выбранного задания.'
                return self.make_response(text, tts=tts, buttons=self.buttons)
            else:
                return StartBody()

        if 'addition_subtraction' in request.intents:
            return AdditionSubtraction()
        elif 'multiplication_division' in request.intents:
            return MultiplicationDivision()
        elif 'fractions' in request.intents:
            return Fractions()
        elif 'exponentiation' in request.intents:
            return Exponentiation()
        elif 'square_root' in request.intents:
            return SquareRoot()
        elif 'trigonometry' in request.intents:
            return Trigonometry()

        for el in request.entities:
            if el['value'] == 1:
                return AdditionSubtraction()
            elif el['value'] == 2:
                return MultiplicationDivision()
            elif el['value'] == 3:
                return Fractions()
            elif el['value'] == 4:
                return Exponentiation()
            elif el['value'] == 5:
                return SquareRoot()
            elif el['value'] == 6:
                return Trigonometry()

    @property
    def buttons(self):
        buttons = [
            button(self._options_text[0]),
            button(self._options_text[1]),
            button(self._options_text[2]),
            button(self._options_text[3]),
            button(self._options_text[4]),
            button(self._options_text[5]),
        ]
        return buttons


class AdditionSubtraction(Scenario):
    def reply(self, request):
        num1, num2 = randint(-1000, 1000), randint(-1000, 1000)
        text = ''
        tts = ''
        if helper.question_number == 0:
            # Rules
            text = 'Вам поочерёдно представятся 10 примеров, содержащих операции сложения и вычитания, для решения ' \
                   'на время. На каждый из них у вас есть 30 секунд. Удачи!\n'
            tts = text
        else:
            # If answer is correct
            if helper.correct:
                variants = ['Вы ответили верно.\n', 'Ваш ответ правильный.\n', 'Браво, вы правы!\n',
                            'Поздравляю вас, вы дали верный ответ!\n', 'Этот ответ был правильный.\n']
                text = choice(variants)
                tts = text
            # Else show the correct answer
            else:
                variants = ['Верный ответ: ' + str(helper.answer) + '.\n',
                            'Ваш ответ неверный, правильный ответ: ' + str(helper.answer) + '.\n',
                            'Увы, вы ответили неправильно, ответом было ' + str(helper.answer) + '\n',
                            'Вы дали неверный ответ, верным был ' + str(helper.answer) + '\n',
                            'Этот ответ был неправильный. Верный ответ: ' + str(helper.answer) + '\n']
                text = choice(variants)
                tts = text
        answer = 0
        example = ''
        # Randomize the operation. 1 - addition, 2 - subtraction
        if randint(1, 2) == 1:
            text += str(num1) + ' + ' + str(num2) + ' = ?'
            variants = ['сколько будет ' + str(num1) + ' плюс ' + str(num2),
             'реши ' + str(num1) + ' плюс ' + str(num2), 'сумма ' + str(num1) + ' и ' + str(num2) + ' равна',
             str(num1) + ' плюс ' + str(num2) + ' б+уудет', str(num1) + ' плюс ' + str(num2) + ' равн+оо']
            tts += choice(variants)
            example = choice(variants)
            answer = num1+num2
        else:
            text += str(num1) + ' - ' + str(num2) + ' = ?'
            variants = ['сколько будет ' + str(num1) + ' минус ' + str(num2),
             'реши ' + str(num1) + ' минус ' + str(num2), 'разница ' + str(num1) + ' и ' + str(num2) + ' равна',
             str(num1) + ' минус ' + str(num2) + ' б+уудет', str(num1) + ' минус ' + str(num2) + ' равн+оо']
            tts += choice(variants)
            example = choice(variants)
            answer = num1-num2
        tts += '<speaker audio=\"dialogs-upload/75986b16-ef4a-48ae-95ce-e95c020ae7a3/44d33529-856c-42e8-9a0f-f3d60311ef88.opus\">'
        if helper.question_number != 0:
            tts = tts + example
        return self.make_response(text, tts, state={
            'points': helper.points,
            'question_number': helper.question_number,
            'answer': answer
        })

    def help(self, request: Request):
        text = 'Вы попросили помощи во время выполнения задания, продолжить его выполнение вы уже не сможете.'
        if helper.question_number == 0:
            text += ' Вам поочерёдно представляются 10 примеров, содержащих операции сложения и вычитания, для ' \
                    'решения на время. На каждый из них у вас есть 30 секунд. Главное не торопитесь, времени у вас ' \
                    'достаточно.'
        elif helper.points == 0:
            text += ' Вы не смогли дать правильного ответа ни на один из вопросов. Чтобы сложить числа с разными ' \
                    'знаками, нужно из большего модуля вычесть меньший модуль, и перед полученным ответом поставить ' \
                    'знак того числа, модуль которого больше. Чтобы из меньшего числа вычесть большее, нужно из ' \
                    'большего числа вычесть меньшее и перед полученным ответом поставить минус.'
        else:
            text += ' Вы верно ответили на ' + str(helper.points) + ' из ' + str(helper.question_number) + \
                    ' вопросов, правильный ответ на пример ' + str(helper.answer) + '.'
        text += ' Возвращаемся назад.'
        return self.make_response(text, buttons=self.buttons + [
            button('Назад', hide=True)
        ], state={
            'points': -1
        })

    def handle_local_intents(self, request: Request):
        # If user activates help or back intent
        if helper.points == -1 or 'back' in request.intents:
            return StartBody()
        elif 'answer' in request.intents:
            if request.intents['answer']['slots']['Answer']['value'] == helper.answer:
                helper.points += 1
                helper.correct = True
        helper.question_number += 1
        if helper.question_number == 10:
            if helper.points == 10:
                return Congratulations()
            else:
                return EndBody()
        else:
            return AdditionSubtraction()

    @property
    def buttons(self):
        return []


class MultiplicationDivision(Scenario):
    def reply(self, request):
        num1, num2 = randint(-50, 50), randint(-50, 50)
        text = ''
        tts = ''
        if helper.question_number == 0:
            text = 'Вам поочерёдно представятся 10 примеров, содержащих операции умножения и деления, для решения на' \
                   ' время. На каждый из них у вас есть 30 секунд. Удачи!\n'
            tts = text
        else:
            if helper.correct:
                variants = ['Вы ответили верно.\n', 'Ваш ответ правильный.\n', 'Браво, вы правы!\n',
                            'Поздравляю вас, вы дали верный ответ!\n', 'Этот ответ был правильный.\n']
                text = choice(variants)
                tts = text
            else:
                variants = ['Верный ответ: ' + str(helper.answer) + '.\n', 
                            'Ваш ответ неверный, правильный ответ: ' + str(helper.answer) + '.\n', 
                            'Увы, вы ответили неправильно, ответом было ' + str(helper.answer) + '\n',
                            'Вы дали неверный ответ, верным был ' + str(helper.answer) + '\n', 
                            'Этот ответ был неправильный. Верный ответ: ' + str(helper.answer) + '\n']
                text = choice(variants)
                tts = text
        answer = 0
        example = ''
        # Randomize the operation. 1 - multiplication, 2 - division
        if randint(1, 2) == 1:
            text += str(num1) + ' * ' + str(num2) + ' = ?'
            variants = ['сколько будет ' + str(num1) + ' умножить на ' + str(num2), 
                        'реши ' + str(num1) + ' умножить на ' + str(num2),
                        'произведение ' + str(num1) + ' и ' + str(num2) + ' равно',
                        str(num1) + ' умножить на ' + str(num2) + ' б+уудет',
                        str(num1) + ' умноженное на ' + str(num2) + ' равн+оо']
            tts += choice(variants)
            example = choice(variants)
            answer = num1 * num2
        else:
            answer = num1
            num1 = num1 * num2
            text += str(num1) + ' / ' + str(num2) + ' = ?'
            variants = ['сколько будет ' + str(num1) + ' делить на ' + str(num2),
             'реши ' + str(num1) + ' делить на ' + str(num2), 'частное ' + str(num1) + ' и ' + str(num2) + ' равно',
             str(num1) + ' делить на ' + str(num2) + ' б+уудет', str(num1) + ' деленное на ' + str(num2) + ' равн+оо']
            tts += choice(variants)
            example = choice(variants)
        tts += '<speaker audio=\"dialogs-upload/75986b16-ef4a-48ae-95ce-e95c020ae7a3/44d33529-856c-42e8-9a0f-f3d60311ef88.opus\">'
        if helper.question_number != 0:
            tts = tts + example
        return self.make_response(text, tts, state={
            'points': helper.points,
            'question_number': helper.question_number,
            'answer': answer
        })

    def help(self, request: Request):
        text = 'Вы попросили помощи во время выполнения задания, продолжить его выполнение вы уже не сможете.'
        if helper.question_number == 0:
            text += ' Вам поочерёдно представляются 10 примеров, содержащих операции умножения и деления, для решения' \
                    ' на время. На каждый из них у вас есть 30 секунд. Главное не торопитесь, времени у вас достаточно.'
        elif helper.points == 0:
            text += ' Вы не смогли дать правильного ответа ни на один из вопросов. Попробуйте представлять числа в ' \
                    'виде суммы или разности чисел, одно или несколько из которых \"круглое\". На 10, 20, 100, 1000 и' \
                    ' другие круглые числа умножать быстрее, в уме нужно сводить всё к таким простым операциям.'
        else:
            text += ' Вы верно ответили на ' + str(helper.points) + ' из ' + str(helper.question_number) + \
                    ' вопросов, правильный ответ на пример ' + str(helper.answer) + '.'
        text += ' Возвращаемся назад.'
        return self.make_response(text, buttons=self.buttons + [
            button('Назад', hide=True)
        ], state={
            'points': -1
        })

    def handle_local_intents(self, request: Request):
        # If user activates help or back intent
        if helper.points == -1 or 'back' in request.intents:
            return StartBody()
        elif 'answer' in request.intents:
            if request.intents['answer']['slots']['Answer']['value'] == helper.answer:
                helper.points += 1
                helper.correct = True
        helper.question_number += 1
        if helper.question_number == 10:
            if helper.points == 10:
                return Congratulations()
            else:
                return EndBody()
        else:
            return MultiplicationDivision()

    @property
    def buttons(self):
        return []


def find_gcd(a, b):
    while a != 0 and b != 0:
        if a > b:
            a = a % b
        else:
            b = b % a

    return a + b


def find_lcm(a, b):
    return a*b // find_gcd(a, b)


class Fractions(Scenario):
    def reply(self, request):
        operation = randint(1, 4)
        numerator1, denominator1 = 1, 1
        numerator2, denominator2 = 1, 1
        text = ''
        tts = ''
        if helper.question_number == 0:
            text = 'Вам поочерёдно представятся 10 примеров, содержащих операции сложения, вычитания, умножения и ' \
                   'деления над дробями, для решения на время. На каждый из них у вас есть 30 секунд. Удачи!\n'
            tts = text
        else:
            if helper.correct:
                variants = ['Вы ответили верно.\n', 'Ваш ответ правильный.\n', 'Браво, вы правы!\n',
                            'Поздравляю вас, вы дали верный ответ!\n', 'Этот ответ был правильный.\n']
                text = choice(variants)
                tts = text
            else:
                ans = str(helper.answer) + '/' + str(helper.answer_den)
                variants = ['Верный ответ: ' + ans + '.\n', 'Ваш ответ неверный, правильный ответ: ' + ans + '.\n',
                            'Увы, вы ответили неправильно, ответом было ' + ans + '\n',
                            'Вы дали неверный ответ, верным был ' + ans + '\n',
                            'Этот ответ был неправильный. Верный ответ: ' + ans + '\n']
                text = choice(variants)
                tts = text
        answer = 2
        answer_den = 1
        example = ''

        # Randomize the operation. 1 - addition, 2 - subtraction, 3 - multiplication, 4 - division
        if operation == 1:
            numerator1, denominator1 = randint(1, 20), randint(1, 20)
            gcd = find_gcd(numerator1, denominator1)
            numerator1 //= gcd
            denominator1 //= gcd

            numerator2, denominator2 = randint(1, 20), denominator1 * (randint(199, 399) // 100)
            gcd = find_gcd(numerator2, denominator2)
            numerator2 //= gcd
            denominator2 //= gcd

            text += str(numerator1) + '/' + str(denominator1) + ' + ' + str(numerator2) + '/' + str(denominator2) +\
                                                                                                                ' = ?'
            variants = [
                'сколько будет ' + str(numerator1) + ' дробь ' + str(denominator1) + ' плюс ' + str(numerator2) +
                ' дробь ' + str(denominator2),
                'реши ' + str(numerator1) + ' дробь ' + str(denominator1) + ' плюс ' + str(numerator2) + ' дробь ' +
                str(denominator2),
                'сумма двух дробей ' + str(numerator1) + ' дробь ' + str(denominator1) + ' и ' + str(numerator2) +
                ' дробь ' + str(denominator2) + ' равна',
                str(numerator1) + ' дробь ' + str(denominator1) + ' плюс ' + str(numerator2) + ' дробь ' +
                str(denominator2) + ' б+уудет',
                str(numerator1) + ' дробь ' + str(denominator1) + ' плюс ' + str(numerator2) + ' дробь ' +
                str(denominator2) + ' равн+оо']
            tts += choice(variants)
            example = choice(variants)
            lcm = find_lcm(denominator1, denominator2)
            answer = numerator1 * (lcm // denominator1) + numerator2 * (lcm // denominator2)
            answer_den = lcm
        elif operation == 2:
            numerator1, denominator1 = randint(1, 20), randint(1, 20)
            gcd = find_gcd(numerator1, denominator1)
            numerator1 //= gcd
            denominator1 //= gcd

            numerator2, denominator2 = randint(1, 20), denominator1 * (randint(199, 399) // 100)
            gcd = find_gcd(numerator2, denominator2)
            numerator2 //= gcd
            denominator2 //= gcd

            lcm = find_lcm(denominator1, denominator2)
            nnumerator1 = numerator1 * (lcm // denominator1)
            nnumerator2 = numerator2 * (lcm // denominator2)
            answer = max(nnumerator1, nnumerator2) - min(nnumerator1, nnumerator2)
            if nnumerator1 < nnumerator2:
                numerator1, numerator2 = numerator2, numerator1
                denominator1, denominator2 = denominator2, denominator1
            answer_den = lcm

            text += str(numerator1) + '/' + str(denominator1) + ' - ' + str(numerator2) + '/' + str(denominator2) +\
                                                                                                                ' = ?'
            variants = [
                'сколько будет ' + str(numerator1) + ' дробь ' + str(denominator1) + ' минус ' + str(numerator2) +
                ' дробь ' + str(denominator2),
                'реши ' + str(numerator1) + ' дробь ' + str(denominator1) + ' минус ' + str(numerator2) + ' дробь ' +
                str(denominator2),
                'разница двух дробей ' + str(numerator1) + ' дробь ' + str(denominator1) + ' и ' + str(numerator2) +
                ' дробь ' + str(denominator2) + ' равна',
                str(numerator1) + ' дробь ' + str(denominator1) + ' минус ' + str(numerator2) + ' дробь ' +
                str(denominator2) + ' б+уудет',
                str(numerator1) + ' дробь ' + str(denominator1) + ' минус ' + str(numerator2) + ' дробь ' +
                str(denominator2) + ' равн+оо']
            tts += choice(variants)
            example = choice(variants)
        elif operation == 3:
            numerator1, denominator1 = randint(1, 20), randint(1, 20)
            gcd = find_gcd(numerator1, denominator1)
            numerator1 //= gcd
            denominator1 //= gcd

            numerator2, denominator2 = randint(1, 20), randint(1, 20)
            gcd = find_gcd(numerator2, denominator2)
            numerator2 //= gcd
            denominator2 //= gcd

            text += str(numerator1) + '/' + str(denominator1) + ' * ' + str(numerator2) + '/' + str(denominator2) + \
                                                                                                                ' = ?'
            variants = [
                'сколько будет ' + str(numerator1) + ' дробь ' + str(denominator1) + ' умножить на ' + str(numerator2)
                + ' дробь ' + str(denominator2),
                'реши ' + str(numerator1) + ' дробь ' + str(denominator1) + ' умножить на ' + str(numerator2) +
                ' дробь ' + str(denominator2),
                'произведение двух дробей ' + str(numerator1) + ' дробь ' + str(denominator1) + ' и ' + str(numerator2)
                + ' дробь ' + str(denominator2) + ' равно',
                str(numerator1) + ' дробь ' + str(denominator1) + ' умножить на ' + str(numerator2) + ' дробь ' +
                str(denominator2) + ' б+уудет',
                str(numerator1) + ' дробь ' + str(denominator1) + ' умножить на ' + str(numerator2) + ' дробь ' +
                str(denominator2) + ' равн+оо']
            tts += choice(variants)
            example = choice(variants)
            answer = numerator1 * numerator2
            answer_den = denominator1 * denominator2
        else:
            numerator1, denominator1 = randint(1, 20), randint(1, 20)
            gcd = find_gcd(numerator1, denominator1)
            numerator1 //= gcd
            denominator1 //= gcd

            numerator2, denominator2 = randint(1, 20), randint(1, 20)
            gcd = find_gcd(numerator2, denominator2)
            numerator2 //= gcd
            denominator2 //= gcd

            text += str(numerator1) + '/' + str(denominator1) + ' / ' + str(numerator2) + '/' + str(denominator2) + \
                                                                                                                ' = ?'
            variants = [
                'сколько будет ' + str(numerator1) + ' дробь ' + str(denominator1) + ' разделить на ' + str(numerator2)
                + ' дробь ' + str(denominator2),
                'реши ' + str(numerator1) + ' дробь ' + str(denominator1) + ' делить на ' + str(numerator2) + ' дробь '
                + str(denominator2),
                'частное двух дробей ' + str(numerator1) + ' дробь ' + str(denominator1) + ' и ' + str(numerator2) +
                ' дробь ' + str(denominator2) + ' равно',
                str(numerator1) + ' дробь ' + str(denominator1) + ' разделить на ' + str(numerator2) + ' дробь '
                + str(denominator2) + ' б+уудет',
                str(numerator1) + ' дробь ' + str(denominator1) + ' делить на ' + str(numerator2) + ' дробь ' +
                str(denominator2) + ' равн+оо']
            tts += choice(variants)
            example = choice(variants)
            answer = numerator1 * denominator2
            answer_den = denominator1 * numerator2

        tts += '<speaker audio=\"dialogs-upload/75986b16-ef4a-48ae-95ce-e95c020ae7a3/44d33529-856c-42e8-9a0f-f3d60311ef88.opus\">'
        if helper.question_number != 0:
            tts = tts + example

        gcd = find_gcd(answer, answer_den)
        answer //= gcd
        answer_den //= gcd

        return self.make_response(text, tts, state={
            'points': helper.points,
            'question_number': helper.question_number,
            'answer': answer,
            'answer_den': answer_den
        })

    def help(self, request: Request):
        text = 'Вы попросили помощи во время выполнения задания, продолжить его выполнение вы уже не сможете.'
        variants = ['Для того, чтобы сложить две дроби, нужно сначала привести их к общему знаменателю, а затем'
                    ' выполнить сложение.',
                    'Для того, чтобы из одной дроби вычесть другую, нужно сначала привести их к общему знаменателю,'
                    ' а затем выполнить вычитание.',
                    'Для того, чтобы перемножить две дроби, нужно перемножить соответственно их числители и '
                    'знаменатели.',
                    'Для того, чтобы одну дробь разделить на другую, нужно делимое умножить на дробь, обратную '
                    'делителю.']
        if helper.question_number == 0:
            variants += [' Главное не торопитесь, времени у вас достаточно.']
            text += ' Вам поочерёдно представятся 10 примеров, содержащих операции сложения, вычитания, умножения и ' \
                    'деления над дробями, для решения. На каждый из них у вас есть 30 секунд.' + \
                    choice(variants)
        elif helper.points == 0:
            text += ' Вы не смогли дать правильного ответа ни на один из вопросов.' + choice(variants)
        else:
            text += ' Вы верно ответили на ' + str(helper.points) + ' из ' + str(helper.question_number) + \
                    ' вопросов, правильный ответ на пример ' + str(helper.answer) + '.'
        text += ' Возвращаемся назад.'
        return self.make_response(text, buttons=self.buttons + [
            button('Назад', hide=True)
        ], state={
            'points': -1
        })

    def handle_local_intents(self, request: Request):
        # If user activates help or back intent
        if helper.points == -1 or 'back' in request.intents:
            return StartBody()
        elif 'answer' in request.intents:
            numerator = int(request.tokens[request.intents['answer']['slots']['Answer']['tokens']['start']])
            denominator = 1
            if request.intents['answer']['slots']['Answer']['tokens']['start'] + 1 < len(request.tokens):
                denominator = int(request.tokens[request.intents['answer']['slots']['Answer']['tokens']['start'] + 1])
            gcd = find_gcd(numerator, denominator)
            numerator //= gcd
            denominator //= gcd
            if numerator == helper.answer and denominator == helper.answer_den:
                helper.points += 1
                helper.correct = True
        helper.question_number += 1
        if helper.question_number == 10:
            if helper.points == 10:
                return Congratulations()
            else:
                return EndBody()
        else:
            return Fractions()

    @property
    def buttons(self):
        return []


class Exponentiation(Scenario):
    def reply(self, request):
        num1 = randint(999, 30999) // 1000
        num2 = 0
        if num1 < 4:
            num2 = randint(199, 599) // 100
        elif num1 < 11:
            num2 = randint(199, 499) // 100
        elif num1 < 21:
            num2 = randint(199, 399) // 100
        else:
            num2 = 2
        text = ''
        tts = ''
        if helper.question_number == 0:
            text = 'Вам поочерёдно представятся 10 примеров, содержащих операцию возведения в степень, для решения на' \
                   ' время. На каждый из них у вас есть 30 секунд. Удачи!\n'
            tts = text
        else:
            if helper.correct:
                variants = ['Вы ответили верно.\n', 'Ваш ответ правильный.\n', 'Браво, вы правы!\n',
                            'Поздравляю вас, вы дали верный ответ!\n', 'Этот ответ был правильный.\n']
                text = choice(variants)
                tts = text
            else:
                variants = ['Верный ответ: ' + str(helper.answer) + '.\n',
                            'Ваш ответ неверный, правильный ответ: ' + str(helper.answer) + '.\n',
                            'Увы, вы ответили неправильно, ответом было ' + str(helper.answer) + '\n',
                            'Вы дали неверный ответ, верным был ' + str(helper.answer) + '\n',
                            'Этот ответ был неправильный. Верный ответ: ' + str(helper.answer) + '\n']
                text = choice(variants)
                tts = text
        answer = 0
        example = ''
        text = str(num1) + '^' + str(num2) + ' = ?'
        variants = ['сколько будет ' + str(num1) + ' в степени ' + str(num2),
                    'реши ' + str(num1) + ' в степени ' + str(num2),
                    str(num1) + ' в степени ' + str(num2) + ' б+уудет',
                    str(num1) + ' в степени ' + str(num2) + ' равн+оо']
        tts = choice(variants)
        example = choice(variants)
        answer = num1**num2
        tts += '<speaker audio=\"dialogs-upload/75986b16-ef4a-48ae-95ce-e95c020ae7a3/44d33529-856c-42e8-9a0f-f3d60311ef88.opus\">'
        if helper.question_number != 0:
            tts = tts + example
        return self.make_response(text, tts, state={
            'points': helper.points,
            'question_number': helper.question_number,
            'answer': answer
        })

    def help(self, request: Request):
        text = 'Вы попросили помощи во время выполнения задания, продолжить его выполнение вы уже не сможете.'
        if helper.question_number == 0:
            text += ' Вам поочерёдно представляются 10 примеров, содержащих операцию возведения в степень, для ' \
                    'решения на время. На каждый из них у вас есть 30 секунд. Главное не торопитесь, времени у вас ' \
                    'достаточно.'
        elif helper.points == 0:
            text += ' Вы не смогли дать правильного ответа ни на один из вопросов. Сосредоточьтесь на решении и не ' \
                    'переживайте, результаты, кроме вас, никто не увидит. Наша цель научиться.'
        else:
            text += ' Вы верно ответили на ' + str(helper.points) + ' из ' + str(helper.question_number) + ' вопросов' \
                    ', правильный ответ на пример ' + str(helper.answer) + '.'
        text += ' Возвращаемся назад.'
        return self.make_response(text, buttons=self.buttons + [
            button('Назад', hide=True)
        ], state={
            'points': -1
        })

    def handle_local_intents(self, request: Request):
        # If user activates help or back intent
        if helper.points == -1 or 'back' in request.intents:
            return StartBody()
        elif 'answer' in request.intents:
            if request.intents['answer']['slots']['Answer']['value'] == helper.answer:
                helper.points += 1
                helper.correct = True
        helper.question_number += 1
        if helper.question_number == 10:
            if helper.points == 10:
                return Congratulations()
            else:
                return EndBody()
        else:
            return Exponentiation()

    @property
    def buttons(self):
        return []


class SquareRoot(Scenario):
    def reply(self, request):
        num1 = randint(999, 50999) // 1000
        text = ''
        tts = ''
        if helper.question_number == 0:
            text = 'Вам поочерёдно представятся 10 примеров, где вам нужно найти квадратный корень, для решения на ' \
                   'время. На каждый из них у вас есть 30 секунд. Удачи!\n'
            tts = text
        else:
            if helper.correct:
                variants = ['Вы ответили верно.\n', 'Ваш ответ правильный.\n', 'Браво, вы правы!\n',
                            'Поздравляю вас, вы дали верный ответ!\n', 'Этот ответ был правильный.\n']
                text = choice(variants)
                tts = text
            else:
                variants = ['Верный ответ: ' + str(helper.answer) + '.\n',
                            'Ваш ответ неверный, правильный ответ: ' + str(helper.answer) + '.\n',
                            'Увы, вы ответили неправильно, ответом было ' + str(helper.answer) + '\n',
                            'Вы дали неверный ответ, верным был ' + str(helper.answer) + '\n',
                            'Этот ответ был неправильный. Верный ответ: ' + str(helper.answer) + '\n']
                text = choice(variants)
                tts = text
        answer = num1
        num1 = num1**2
        example = ''
        text += '√' + str(num1) + ' = ?'
        variants = ['чему равен квадратный корень из ' + str(num1),
                    'посчитай квадратный корень из ' + str(num1), 'квадратный корень из ' + str(num1) + ' равен',
                    'квадратный корень из ' + str(num1) + ' б+уудет']
        tts += choice(variants)
        example = choice(variants)
        tts += '<speaker audio=\"dialogs-upload/75986b16-ef4a-48ae-95ce-e95c020ae7a3/44d33529-856c-42e8-9a0f-f3d60311ef88.opus\">'
        if helper.question_number != 0:
            tts = tts + example
        return self.make_response(text, tts, state={
            'points': helper.points,
            'question_number': helper.question_number,
            'answer': answer
        })

    def help(self, request: Request):
        text = 'Вы попросили помощи во время выполнения задания, продолжить его выполнение вы уже не сможете.'
        if helper.question_number == 0:
            text += ' Вам поочерёдно представляются 10 примеров, где вам нужно найти квадратный корень, для решения ' \
                    'на время. На каждый из них у вас есть 30 секунд. Главное не торопитесь, времени у вас достаточно.'
        elif helper.points == 0:
            text += ' Вы не смогли дать правильного ответа ни на один из вопросов. Арифметическим квадратным корнем ' \
                    'из неотрицательного числа a называется такое неотрицательное число, квадрат которого равен a.'
        else:
            text += ' Вы верно ответили на ' + str(helper.points) + ' из ' + str(helper.question_number) + \
                    ' вопросов, правильный ответ на пример ' + str(helper.answer) + '.'
        text += ' Возвращаемся назад.'
        return self.make_response(text, buttons=self.buttons + [
            button('Назад', hide=True)
        ], state={
            'points': -1
        })

    def handle_local_intents(self, request: Request):
        # If user activates help or back intent
        if helper.points == -1 or 'back' in request.intents:
            return StartBody()
        elif 'answer' in request.intents:
            if request.intents['answer']['slots']['Answer']['value'] == helper.answer:
                helper.points += 1
                helper.correct = True
        helper.question_number += 1
        if helper.question_number == 10:
            if helper.points == 10:
                return Congratulations()
            else:
                return EndBody()
        else:
            return SquareRoot()

    @property
    def buttons(self):
        return []


class Trigonometry(Scenario):
    def __init__(self):
        self._values = [
            ('sin0° = ?', 'чему равен синус нуля градусов', [0]),
            ('cos0° = ?', 'чему равен косинус нуля градусов', [1]),
            ('tg0° = ?', 'чему равен тангенс нуля градусов', [0]),
            ('sin?° = 1/2', 'синус какого угла равен одной второй', [30, 150]),
            ('cos?° = √3/2', 'косинус какого угла равен корню из трех деленному на два', [30, 330]),
            ('tg?° = 1/√3', 'тангенс какого угла равен единице деленной на корень из трех', [30, 210]),
            ('ctg?° = √3', 'котангенс какого угла равен корню из трех', [30, 210]),
            ('sin?° = √2/2', 'синус какого угла равен корню из двух деленному на два', [45, 135]),
            ('cos?° = √2/2', 'косинус какого угла равен корню из двух деленному на два', [45, 315]),
            ('tg45° = ?', 'чему равен тангенс сорока пяти градусов', [1]),
            ('ctg45° = ?', 'чему равен котангенс сорока пяти градусов', [1]),
            ('cos?° = 1/2', 'косинус какого угла равен одной второй', [60, 300]),
            ('sin?° = √3/2', 'синус какого угла равен корню из трех деленному на два', [60, 120]),
            ('ctg?° = 1/√3', 'котангенс какого угла равен единице деленной на корень из трех', [60, 240]),
            ('tg?° = √3', 'тангенс какого угла равен корню из трех', [60, 240]),
            ('sin90° = ?', 'чему равен синус девяноста градусов', [1]),
            ('cos90° = ?', 'чему равен косинус девяноста градусов', [0]),
            ('ctg90° = ?', 'чему равен котангенс девяноста градусов', [0]),
            ('cos?° = -1/2', 'косинус какого угла равен минус одной второй', [120, 240]),
            ('ctg?° = -1/√3', 'котангенс какого угла равен минус единице деленной на корень из трех', [120, 300]),
            ('tg?° = -√3', 'тангенс какого угла равен минус корню из трех', [120, 300]),
            ('cos?° = -√2/2', 'косинус какого угла равен минус корню из двух деленному на два', [135, 225]),
            ('tg135° = ?', 'чему равен тангенс ста тридцати пяти градусов', [-1]),
            ('ctg135° = ?', 'чему равен котангенс ста тридцати пяти градусов', [-1]),
            ('cos?° = -√3/2', 'косинус какого угла равен минус корню из трех деленному на два', [150, 210]),
            ('tg?° = -1/√3', 'тангенс какого угла равен минус единице деленной на корень из трех', [150, 330]),
            ('ctg?° = -√3', 'котангенс какого угла равен минус корню из трех', [150, 330]),
            ('sin180° = ?', 'чему равен синус ста восьмидесяти градусов', [0]),
            ('cos180° = ?', 'чему равен косинус ста восьмидесяти градусов', [-1]),
            ('tg180° = ?', 'чему равен тангенс ста восьмидесяти градусов', [0]),
            ('sin?° = -1/2', 'синус какого угла равен минус одной второй', [210, 330]),
            ('sin?° = -√2/2', 'синус какого угла равен минус корню из двух деленному на два', [225, 315]),
            ('tg225° = ?', 'чему равен тангенс двухсот двадцати пяти градусов', [1]),
            ('ctg225° = ?', 'чему равен котангенс двухсот двадцати пяти градусов', [1]),
            ('sin?° = -√3/2', 'синус какого угла равен минус корню из трех деленному на два', [240, 300]),
            ('sin270° = ?', 'чему равен синус двухсот семидесяти градусов', [-1]),
            ('cos270° = ?', 'чему равен косинус двухсот семидесяти градусов', [0]),
            ('ctg270° = ?', 'чему равен котангенс двухсот семидесяти градусов', [0]),
            ('sin360° = ?', 'чему равен синус трехсот шестидесяти градусов', [0]),
            ('cos360° = ?', 'чему равен косинус трехсот шестидесяти градусов', [1]),
            ('tg360° = ?', 'чему равен тангенс трехсот шестидесяти градусов', [0]),
        ]

    def reply(self, request):
        if helper.question_number == 0:
            text = 'Вам поочерёдно представятся 10 вопросов о табличных тригонометрических значениях. На каждый из ' \
                   'них у вас есть 30 секунд. Вы должны дать значение угла в градусах. Удачи!\n'
            tts = text
        else:
            if helper.correct:
                variants = ['Вы ответили верно.\n', 'Ваш ответ правильный.\n', 'Браво, вы правы!\n',
                            'Поздравляю вас, вы дали верный ответ!\n', 'Этот ответ был правильный.\n']
                text = choice(variants)
                tts = text
            else:
                variants = ['Верный ответ: ' + str(helper.answer[0]) + '.\n',
                            'Ваш ответ неверный, правильный ответ: ' + str(helper.answer[0]) + '.\n',
                            'Увы, вы ответили неправильно, ответом было ' + str(helper.answer[0]) + '\n',
                            'Вы дали неверный ответ, верным был ' + str(helper.answer[0]) + '\n',
                            'Этот ответ был неправильный. Верный ответ: ' + str(helper.answer[0]) + '\n']
                text = choice(variants)
                tts = text

        variant = randint(0, len(self._values) - 1)
        while variant in helper.asked:
            variant = (variant + 1) % (len(self._values) - 1)
        text += self._values[variant][0]
        tts += self._values[variant][1]

        variants = [
            'и так ваш ответ?',
            'ответом будет?',
            'пол+учится?',
            'ваш ответ?',
            'отвечайте',
            'пришло время ответа',
        ]

        tts += '<speaker audio=\"dialogs-upload/75986b16-ef4a-48ae-95ce-e95c020ae7a3/44d33529-856c-42e8-9a0f-f3d60311ef88.opus\">'
        if helper.question_number != 0:
            tts = tts + choice(variants)
        return self.make_response(text, tts, state={
            'points': helper.points,
            'question_number': helper.question_number,
            'answer': self._values[variant][2],
            'asked': helper.asked + [variant]
        })

    def help(self, request: Request):
        text = 'Вы попросили помощи во время выполнения задания, продолжить его выполнение вы уже не сможете.'
        if helper.question_number == 0:
            text += ' Вам поочерёдно представляются 10 вопросов о табличных тригонометрических значениях. На каждый ' \
                    'из них у вас есть 30 секунд. Главное не торопитесь, времени у вас достаточно.'
        elif helper.points == 0:
            text += ' Вы не смогли дать правильного ответа ни на один из вопросов. Эти значения нужно выучить, а ' \
                    'лучше всего запоминать тригонометрические значения, запоминая их на единичной окружности'
        else:
            text += ' Вы верно ответили на ' + str(helper.points) + ' из ' + str(helper.question_number) + \
                    ' вопросов, правильный ответ на пример ' + str(helper.answer) + '.'
        text += ' Возвращаемся назад.'
        return self.make_response(text, buttons=self.buttons + [
            button('Назад', hide=True)
        ], state={
            'points': -1
        })

    def handle_local_intents(self, request: Request):
        answer = 3
        isIn = False
        # We are looking for an answer among the tokens, because sometimes voice recognition does not work correctly or
        # the user says the whole sentence, and not just the answer
        for el in request.tokens:
            if el.isdigit() and (int(el) % 360) in helper.answer:
                isIn = True
                break
        # If user activates help or back intent
        if helper.points == -1 or 'back' in request.intents:
            return StartBody()
        elif 'answer' in request.intents:
            answer = request.intents['answer']['slots']['Answer']['value']
            answer %= 360
        if answer in helper.answer or isIn:
            helper.points += 1
            helper.correct = True
        helper.question_number += 1
        if helper.question_number == 10:
            if helper.points == 10:
                return Congratulations()
            else:
                return EndBody()
        else:
            return Trigonometry()

    @property
    def buttons(self):
        return []


class Congratulations(Scenario):
    """ Congratulations scenario, all answers are correct """
    def reply(self, request):
        delights = ['Вот это да! ', 'Ух ты! ', 'Да я вижу здесь прирожденного математика! ',
                    'Умные люди всегда привлекательны! ', 'Вы на высоте! ', 'Ваши умения поражают! ', '']
        facts = ['Я знаю несколько интересных фактов, могу рассказать. ',
                 'Могу поделиться с тобой сногшибательными фактами. ',
                 'Я могу рассказать тебе то, чего ты, наверное, не знаешь. ', 'Хочешь узнать что-то новое? ']
        play_again = ['Или хочешь сыграть еще раз? ', 'Или я бы посмотрела еще раз на тебя в действии, повторим? ',
                      'Если не хочешь, у меня есть еще режимы, кроме этого. Попробуешь? ', 'Или повторим? ',
                      'Или же давай заново сыграем? ']
        text = choice(delights) + 'На все вопросы ты ответил верно, у тебя твердая \"5\". ' + choice(facts) \
               + choice(play_again)
        applause_sounds = ['<speaker audio=\"dialogs-upload/75986b16-ef4a-48ae-95ce-e95c020ae7a3/87071461-1456-42f7-8cbd-5a7f2b4e4bd4.opus\">',
                           '<speaker audio=\"dialogs-upload/75986b16-ef4a-48ae-95ce-e95c020ae7a3/6d160340-afe2-4273-94d4-40631584f139.opus\">',
                           '<speaker audio=\"dialogs-upload/75986b16-ef4a-48ae-95ce-e95c020ae7a3/b2eef422-bd6d-485a-a05c-baddeb7e726d.opus\">']
        tts = choice(applause_sounds) + text
        return self.make_response(text, tts, buttons=self.buttons)

    def help(self, request: Request):
        variants = ['Если хотите сыграть заново, так и скажите, тогда мы вернемся на выбор типа задания. Если скажете '
                    '\"Факты\", я расскажу вам интересеные факты. А если вам нужно бежать, скажите \"Закончить\"',
                    'Если вам понравилось и вы хотите еще скажите \"Заново\". Я могу рассказать факт, который удивит '
                    'вас, только скажите']
        text = choice(variants)
        return self.make_response(text, buttons=self.buttons + [
            button('Повторить', hide=True)
        ])

    def handle_local_intents(self, request: Request):
        # If user wants to repeat the game
        if 'start_confirm' in request.intents or 'YANDEX.CONFIRM' in request.intents or 'повторим' in request.tokens:
            return StartBody()
        elif 'start_reject' in request.intents or 'YANDEX.REJECT' in request.intents:
            return Parting()
        elif 'interesting_facts' in request.intents:
            return InterestingFact()

    @property
    def buttons(self):
        buttons = [
            button('Сыграть заново', hide=True),
            button('Расскажи интересные факты', hide=True),
            button('Закончить', hide=True)
        ]
        return buttons


class EndBody(Scenario):
    def reply(self, request):
        delights = ['Никто не идеален! ', 'У тебя есть несколько ошибок, но ничего срашного. ',
                    'Главное не опускать руки и все получится! ', 'Ошибки делают нас сильнее ', '']
        facts = ['Я знаю несколько интересных фактов, могу рассказать. ',
                 'Могу поделиться с тобой сногшибательными фактами. ',
                 'Я могу рассказать тебе то, чего ты, наверное, не знаешь. ', 'Хочешь узнать что-то новое? ']
        play_again = ['Или хочешь сыграть еще раз? ', 'Или я бы посмотрела еще раз на тебя в действии, повторим? ',
                      'Если не хочешь, у меня есть еще режимы, кроме этого. Попробуешь? ', 'Или повторим? ',
                      'Или же давай заново сыграем? ']
        mark = 0
        if helper.points > 8:
            mark = 5
        elif helper.points > 5:
            mark = 4
        elif helper.points > 3:
            mark = 3
        else:
            mark = 2
        text = choice(delights) + 'Ты ответил верно на ' + str(helper.points) + \
               (' вопрос' if helper.points == 1 else ' вопроса'
               if helper.points < 5 and helper.points != 0 else ' вопросов') + \
               ' из 10, твоя оценка \"' + str(mark) + '\". ' + choice(facts) + choice(play_again)
        if helper.question_number != 10:
            text = choice(delights) + ' ' + choice(facts) + choice(play_again)
        sad_sounds = [
            '<speaker audio=\"dialogs-upload/75986b16-ef4a-48ae-95ce-e95c020ae7a3/79cded5f-1598-4d6e-bbf3-61e9999b092d.opus\">',
            '<speaker audio=\"dialogs-upload/75986b16-ef4a-48ae-95ce-e95c020ae7a3/c04240a1-8ef6-445a-8f1c-32a042615683.opus\">']
        tts = sad_sounds[randint(0, len(sad_sounds) - 1)] + text
        return self.make_response(text, tts, buttons=self.buttons)

    def help(self, request: Request):
        variants = [
            'Если хотите сыграть заново, так и скажите, тогда мы вернемся на выбор типа задания. Если скажете \"Факты\"'
            ', я расскажу вам интересеные факты. А если вам нужно бежать, скажите \"Закончить\"',
            'Если вам понравилось и вы хотите еще скажите \"Заново\". Я могу рассказать факт, который удивит вас,'
            ' только скажите']
        text = choice(variants)
        return self.make_response(text, buttons=self.buttons + [
            button('Повторить', hide=True)
        ])

    def handle_local_intents(self, request: Request):
        # If user wants to repeat the game
        if 'start_confirm' in request.intents or 'YANDEX.CONFIRM' in request.intents or 'повторим' in request.tokens:
            return StartBody()
        elif 'start_reject' in request.intents or 'YANDEX.REJECT' in request.intents:
            return Parting()
        elif 'interesting_facts' in request.intents:
            return InterestingFact()

    @property
    def buttons(self):
        buttons = [
            button('Сыграть заново', hide=True),
            button('Расскажи интересные факты', hide=True),
            button('Закончить', hide=True)
        ]
        return buttons

class InterestingFact(Scenario):
    def reply(self, request):
        # 'fact', 'link'
        facts = [['Сейчас мы живем в век информации и ее массового распространения, каждый день человек получает дозу'
                  ' данных, которые мозгу необходимо переработать и использовать в дальнейшем или определить, как '
                  'бесполезные и не использовать вовсе. Именно так и появилась ментальная арифметика, она помогает '
                  'легче усваивать информацию, лучше ее структурировать, а также правильно использовать.',
                  'https://www.unapersona.ru/articles/sam-sebe-psikholog/interesnye-fakty-o-mentalnoy-arifmetike.html'],
                 ['Ментальная арифметика особенно хороша для детей и подростков. Именно на этом этапе жизни стоит'
                  ' подключать развитие памяти и навыков работы с ней. Также ментальная арифметика развивает логическое'
                  ' мышление, причинно-следственные связи, помогает понять, как работают законы мироздания и не только.'
                  , 'https://www.unapersona.ru/articles/sam-sebe-psikholog/interesnye-fakty-o-mentalnoy-arifmetike.html'
                  ],
                 ['Ментальная арифметика – это новейший метод всестороннего развития мышления и восприятия. В настоящее'
                  ' время довольно трудно стать по-настоящему полезным в социуме, если вышеперечисленные качества не'
                  ' выведены на нужный уровень.',
                  'https://www.unapersona.ru/articles/sam-sebe-psikholog/interesnye-fakty-o-mentalnoy-arifmetike.html'],
                 ['Ментальная арифметика в странах Азии, включая КНР и Японию, является обязательным предметом для'
                  ' изучения в учебных заведениях. Это может быть обычный школьный урок или факультативное занятие.',
                  'https://maxxbay.livejournal.com/17292120.html'],
                 ['Древние счеты активно применяются в странах Запада, в том числе США и Канаде.',
                  'https://maxxbay.livejournal.com/17292120.html'],
                 ['Ученым давно известен тот факт, что левое полушарие отвечает за логическое мышление, а правое – за '
                  'творческие способности. К примеру, если задействовать правую руку, то включается левое полушарие и'
                  ' наоборот. Однако задействовав одновременно оба полушария, можно достичь значимых успехов в развитие'
                  ' ребенка.', 'https://maxxbay.livejournal.com/17292120.html'],
                 ['Используемая нами десятичная система счисления возникла по причине того, что у человека на руках'
                  ' 10 пальцев. Способность к абстрактному счёту появилась у людей не сразу, а использовать для счёта '
                  'именно пальцы оказалось удобнее всего.',
                  'https://ru.wikipedia.org/wiki/%D0%9F%D0%B0%D0%BB%D1%8C%D1%86%D0%B5%D0%B2%D1%8B%D0%B9_%D1%81%D1%87%D1%91%D1%82'],
                 ['Было давно замечено, что если у курицы десять цыплят, то пропажа одного вызывает у нее беспокойство.'
                  ' Считать она, конечно же, не умеет, но недостачу чувствует. А вот пропажи тринадцатого, пятнадцатого'
                  ' она уже не замечает. Удивительно, но человек ведет себя примерно так же: количества, большие десяти'
                  ', без предварительного счета он воспринимает как абстрактное множество. Количества, меньшие десяти, '
                  'мы называем «несколько» и воспринимаем уже иначе.',
                  'http://oper-sist.blogspot.com/p/blog-page_5156.html'],
                 ['Как известно, военные любят командовать. Многовековой опыт показал, что удобнее всего командовать'
                  ' четырьмя подчиненными. Поэтому обычно в полку четыре батальона, в батальоне – четыре роты, в роте'
                  ' – четыре взвода и так далее. Значит, у военных на каждой «позиции» может быть до четырех единиц! '
                  'Военные мыслят как бы в системе счисления с основанием 4. Четверичную систему используют с '
                  'незапамятных времен индейцы юкки в Калифорнии и родственное им племя в Южной Америке - они считают '
                  'на промежутках между пальцами.', 'http://oper-sist.blogspot.com/p/blog-page_5156.html'],
                 ['Мы считаем отрицательные числа чем-то естественным, но так было далеко не всегда. Впервые'
                  ' отрицательные числа были узаконены в Китае в 3 веке, но использовались лишь для исключительных '
                  'случаев, так как считались, в общем, бессмысленными. Чуть позднее отрицательные числа стали '
                  'использоваться в Индии для обозначения долгов.',
                  'http://www.nsmu.ru/student/pr_education/nauch_dejt/docs/math.pdf'],
                 ['Если мы напишем произвольное двузначное число, а затем напишем цифры этого же числа в обратном '
                  'порядке и возьмем разность полученных чисел, то эта разность всегда разделится на 9.',
                  'http://www.nsmu.ru/student/pr_education/nauch_dejt/docs/math.pdf'],
                 ['В комнате, состоящей всего из 23 человек, 50% вероятности того, что у двух человек будет одинаковый '
                  'день рождения.',
                  'https://1gai.ru/publ/523846-16-faktov-matematiki-kotorye-zastavjat-vas-skazat-ne-uzheli-jeto-pravda.html'],
                 ['Сумма цифр числа 18 вдвое меньше его самого. В этом плане оно единственное в своём роде.',
                  'https://interesnyefakty.org/interesnye-fakty-o-matematike/'],
                 ['Древние египтяне не использовали дроби.',
                  'https://interesnyefakty.org/interesnye-fakty-o-matematike/'],
                 ['Знак равенства впервые применил британский математик Роберт Рекорд в 1557 году.',
                  'http://xn--80aexocohdp.xn--p1ai/22-%D0%B8%D0%BD%D1%82%D0%B5%D1%80%D0%B5%D1%81%D0%BD%D1%8B%D1%85-%D1%84%D0%B0%D0%BA%D1%82%D0%B0-%D0%BE-%D0%BC%D0%B0%D1%82%D0%B5%D0%BC%D0%B0%D1%82%D0%B8%D0%BA%D0%B5/'],
                 ['Первые знакомые нам знаки сложения и вычитания были описаны практически 520 лет назад в книге'
                  ' «Правила алгебры», написанной Яном Видманом.',
                  'https://100-faktov.ru/50-interesnyx-faktov-o-matematike/'],
                 ['Выемки (порезы или углубления) на костях животных доказывают, что люди занимались математикой'
                  ' примерно с 30 000 лет до нашей эры.',
                  'https://vseznaesh.ru/30-interesnyh-i-udivitelnyh-faktov-o-matematike'],
                 ['Доведение числа Пи до 39 знаков позволяет измерить окружность наблюдаемой Вселенной с точностью до'
                  ' ширины одного атома водорода.',
                  'https://vseznaesh.ru/30-interesnyh-i-udivitelnyh-faktov-o-matematike']]
        index = randint(0, len(facts) - 1)
        showed = helper.showed
        if len(showed) == len(facts):
            showed = []
        while index in showed:
            index = (index + 1) % (len(facts) - 1)
        variants = [' Сыграем еще раз?', ' Еще разок сыграем?', ' Я хочу еще увидеть вас в действии.']
        return self.make_response(facts[index][0] + variants[randint(0, len(variants) - 1)], buttons=self.buttons +
               [button('ИСТОЧНИК', url=facts[index][1])], state={'showed': showed + [index]})

    def handle_local_intents(self, request: Request):
        if 'YANDEX.REJECT' in request.intents or 'start_reject' in request.intents:
            return Parting()
        else:
            return StartBody()

    def help(self, request):
        text = 'Сейчас вы услышали факт, если хотите еще порешать примеры, скажите \"Еще раз\", а если хотите' \
               ' закончить, так и скажите.'
        return self.make_response(text, buttons=self.buttons)

    @property
    def buttons(self):
        buttons = [button('Сыграть еще раз', hide=True),
                   button('Стоп', hide=True)]
        return buttons


def _list_scenarios():
    """
    :return: the list of scenarios
    """
    current_module = sys.modules[__name__]
    scenarios = []
    for name, obj in inspect.getmembers(current_module):
        if inspect.isclass(obj) and issubclass(obj, Scenario):
            scenarios.append(obj)
    return scenarios


SCENARIOS = {
    scenario.id(): scenario for scenario in _list_scenarios()
}

DEFAULT_SCENARIO = Welcome
