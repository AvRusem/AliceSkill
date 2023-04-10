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


class Request:
    """ Class for more convenient work with the request """
    def __init__(self, request_body):
        self.request_body = request_body

    def __getitem__(self, key):
        return self.request_body[key]

    @property
    def intents(self):
        return self.request_body['request'].get('nlu', {}).get('intents', {})

    @property
    def tokens(self):
        return self.request_body['request'].get('nlu', {}).get('tokens', {})

    @property
    def entities(self):
        return self.request_body['request'].get('nlu', {}).get('entities', {})

    @property
    def type(self):
        return self.request_body.get('request', {}).get('type')
