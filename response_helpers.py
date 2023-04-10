def button(title, payload=None, url=None, hide=False):
    """
    :param title: button text.
    :param payload: arbitrary JSON code that Yandex Dialogs should send to the handler when clicked.
    :param url: the address of the page that the button should open.
    :param hide: a sign that the button should be removed after the next user's remark.
    :return: property - a button made according to a template.
     "buttons": [
        {
            "title": "text",
            "payload": {},
            "url": "https://example.com/",
            "hide": true
        }
    ]
    """
    new_button = {
        'title': title,
        'hide': hide,
    }
    if payload is not None:
        new_button['payload'] = payload
    if url is not None:
        new_button['url'] = url
    return new_button
