from request import Request
from scenarios import SCENARIOS, DEFAULT_SCENARIO, Parting, Help, init_helper

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


def handler(event, context):
    """
    Entry-point for Serverless Function.
    :param event: request payload.
    :param context: information about current execution context.
    :return: response to be serialized as JSON.
    """

    request = Request(event)

    # Helper initialization in "scenarios.py"
    init_helper(event)

    """
    * An intent is a task that the user formulates in a specific replica. Each intent corresponds to one form.
    * A form is a container of information that Dialogs fill out by recognizing a user request. A form always
        corresponds to one intent and contains a set of typed slots.
    * Slot is a form field. Each slot has a name, a data type, and a mandatory attribute.
    * When processing a replica, Dialogs first determines which intent it belongs to. After that, the necessary
        parameters are extracted from the replica and the form slots are filled with them. Dialogues will send the
        recognized data to the skill in the request.nlu request field. If the replica does not belong to any intent,
        the request.nlu field will be empty.
    * Intents with the YANDEX prefix are provided by Dialogs. The rest of the intents are self-made.
    * For more information read https://yandex.ru/dev/dialogs/alice/doc/index.html
    """
    # If the user doesn't want to use or doesn't want to continue using the skill
    if 'start_reject' in request.intents:
        return Parting().reply(request)

    # Computing the current scene by getting the data from the "state" that saves the data during the session.
    current_scenario_id = event.get('state', {}).get('session', {}).get('scenario')
    if current_scenario_id is None:
        return DEFAULT_SCENARIO().reply(request)
    current_scenario = SCENARIOS.get(current_scenario_id, DEFAULT_SCENARIO)()

    # If the user wants the skill to repeat
    if ('YANDEX.REPEAT' in request.intents or 'say_again' in request.intents) and \
            'answer' not in event.get('state', {}).get('session', {}) and 'повторим' not in request.tokens:
        return current_scenario.reply(request)
    # If the user wants to go back to the beginning
    elif 'to_start' in request.intents:
        return DEFAULT_SCENARIO().reply(request)
    # If the user wants to know what a skill is capable of
    elif 'help' in request.intents:
        return Help().reply(request)
    # If the user needs help
    elif 'YANDEX.HELP' in request.intents:
        return current_scenario.help(request)

    next_scenario = current_scenario.handle_local_intents(request)
    # If JSON received
    if type(next_scenario) is dict:
        return next_scenario
    # If the skill understood the user's intent
    elif next_scenario is not None:
        return next_scenario.reply(request)
    # If the skill didn't understand the user's intent
    else:
        return current_scenario.fallback(request, current_scenario.buttons)
