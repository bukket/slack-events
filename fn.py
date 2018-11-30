import os
import logging
from flask import jsonify
from slackclient import SlackClient
import requests
import urllib
import random


def get_token():
    try:
        token = os.environ['BUKKET_SLACK_TOKEN']
    except KeyError:
        print("BUKKET_SLACK_TOKEN is required.")
        raise
    else:
        return token


def get_channel():
    try:
        channel = os.environ['BUKKET_CHANNEL']
    except KeyError:
        print("BUKKET_CHANNEL is required.")
        raise
    else:
        return channel


def get_bukket_url():
    try:
        url = os.environ['BUKKET_URL']
    except KeyError:
        print("BUKKET_URL is required.")
        raise
    else:
        return url


def get_bot_id():
    try:
        bot_id = os.environ['BUKKET_BOT_ID']
    except KeyError:
        print("BUKKET_BOT_ID is required.")
        raise
    else:
        return bot_id


sc = SlackClient()


def bukket_event(request):
    token = get_token()
    channel = get_channel()
    url = get_bukket_url()
    bot_id = get_bot_id()

    request_json = request.get_json()
    if request_json is None:
        return jsonify({"message": "hello :)"})
    
    if request_json.get('type') == 'url_verification':
        challenge = request_json['challenge']
        return jsonify({"challenge": challenge})
    else:  # This is a message to a channel
        evt = request_json['event']
        txt = evt.get('text', '')
        if 250 > len(txt) > 0:
            return 'ok'
        if evt['channel_type'] == 'channel' and evt['channel'] == channel and evt.get('bot_id', '') != bot_id:
            if len(txt) > 250 or len(txt) == 0:
                return 'ok'
            txt = urllib.parse.quote(txt.lower())
            response = requests.get(f"{url}/factoid/search/{txt}")
            if response.status_code == 200:
                response_data = response.json()['data']
                if len(response_data) == 0:
                    return 'ok'
                idx = random.randint(0, len(response_data)-1)
                try:
                    sc.api_call(
                        'chat.postMessage',
                        channel=channel,
                        text=response_data[idx]['tidbit']
                    )
                except IndexError:
                    logging.warn("IndexError encountered when getting random fact.")
                    return 'ok'
        logging.info(evt)
        return 'ok'
