"""
Sample request sent by Alice:

{
    "meta": {
        "client_id": "ru.yandex.searchplugin/7.16 (none none; android 4.4.2)",
        "interfaces": {
            "account_linking": {},
            "payments": {},
            "screen": {}
        },
        "locale": "ru-RU",
        "timezone": "UTC"
    },
    "request": {
        "original_utterance": "user text",
        "command": "",
        "nlu": {
            "entities": [],
            "tokens": [],
            "intents": {}
        },
        "markup": {
            "dangerous_context": false
        },
        "type": "SimpleUtterance"
    },
    "session": {
        "message_id": 0,
        "new": true,
        "session_id": "ea6be08d-9794-4ae2-89e2-e94f6734cc65",
        "skill_id": "a8f78148-8184-4010-b508-ec70badddf82",
        "user_id": "94748746704CDF263F766BC5E1F0F9D68CD6DB739F2E7CCEF975EC7FCF2A9666",
        "user": {
            "user_id": "86507D953A1790E1F26F46ED4874098F7BC2658CFC9588F9CCC3E1DD9C061A95"
        },
        "application": {
            "application_id": "94748746704CDF263F766BC5E1F0F9D68CD6DB739F2E7CCEF975EC7FCF2A9666"
        }
    },
    "state": {
        "session": {},
        "user": {},
        "application": {}
    },
    "version": "1.0"
}
"""


class Helper:
    """ Class for more convenient work with user data """
    def __init__(self, event):
        self._points = event.get('state', {}).get('session', {}).get('points')
        if self._points is None:
            self._points = 0

        self._question_number = event.get('state', {}).get('session', {}).get('question_number')
        if self._question_number is None:
            self._question_number = 0

        self._answer = event.get('state', {}).get('session', {}).get('answer')
        if self._answer is None:
            self._answer = 2001

        self._answer_den = event.get('state', {}).get('session', {}).get('answer_den')
        if self._answer_den is None:
            self._answer_den = 1

        self._asked = event.get('state', {}).get('session', {}).get('asked')
        if self._asked is None:
            self._asked = []

        self._showed = event.get('state', {}).get('session', {}).get('showed')
        if self._showed is None:
            self._showed = [-1]

        # If the user answered the question correctly, the variable _correct will be True
        self._correct = False

    def set_points(self, points):
        self._points = points

    def get_points(self):
        return self._points

    def set_question_number(self, question_number):
        self._question_number = question_number

    def get_question_number(self):
        return self._question_number

    def set_correct(self, correct):
        self._correct = correct

    def get_correct(self):
        return self._correct

    @property
    def answer(self):
        return self._answer

    @property
    def answer_den(self):
        return self._answer_den

    @property
    def asked(self):
        return self._asked

    @property
    def showed(self):
        return self._showed

    points = property(get_points, set_points)
    question_number = property(get_question_number, set_question_number)
    correct = property(get_correct, set_correct)
