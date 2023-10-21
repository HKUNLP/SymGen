#!/usr/bin/python3
# -*- coding: utf-8 -*-
import random
import os
import json
from datasets import load_dataset
seed = 43
random.seed(seed)
n = 10
m = 500  # generate question file gen_q_file

os.makedirs("data/mtop", exist_ok=True)
train_json = "data/mtop/train.json"
dev_json = "data/mtop/dev.json"
# test_json = "data/mtop/test.json"
few_shot_file = f"data/mtop/{n}_shot.json"
dev_few_shot_file = f"data/mtop/dev_{n}_shot.json"
gen_q_file = f"data/mtop/{n}_gen_q.json"


INTENTS = ['IN:GET_MESSAGE', 'IN:GET_WEATHER', 'IN:GET_ALARM', 'IN:SEND_MESSAGE', 'IN:GET_INFO_RECIPES', 'IN:SET_UNAVAILABLE', 'IN:DELETE_REMINDER', 'IN:GET_STORIES_NEWS', 'IN:CREATE_ALARM', 'IN:GET_REMINDER', 'IN:CREATE_REMINDER', 'IN:GET_RECIPES', 'IN:QUESTION_NEWS', 'IN:GET_EVENT', 'IN:PLAY_MUSIC', 'IN:GET_CALL_TIME', 'IN:CREATE_CALL', 'IN:END_CALL', 'IN:CREATE_PLAYLIST_MUSIC', 'IN:CREATE_TIMER', 'IN:IGNORE_CALL', 'IN:GET_LIFE_EVENT', 'IN:GET_INFO_CONTACT', 'IN:UPDATE_CALL', 'IN:UPDATE_REMINDER_DATE_TIME', 'IN:GET_CONTACT', 'IN:GET_TIMER', 'IN:GET_REMINDER_DATE_TIME', 'IN:DELETE_ALARM', 'IN:PAUSE_MUSIC', 'IN:GET_AGE', 'IN:GET_SUNRISE', 'IN:GET_EMPLOYER', 'IN:GET_EDUCATION_TIME', 'IN:ANSWER_CALL', 'IN:SET_RSVP_YES', 'IN:SNOOZE_ALARM', 'IN:GET_JOB', 'IN:UPDATE_REMINDER_TODO', 'IN:IS_TRUE_RECIPES', 'IN:REMOVE_FROM_PLAYLIST_MUSIC', 'IN:GET_AVAILABILITY', 'IN:GET_CATEGORY_EVENT', 'IN:PLAY_MEDIA', 'IN:ADD_TIME_TIMER', 'IN:GET_CALL', 'IN:SET_AVAILABLE', 'IN:ADD_TO_PLAYLIST_MUSIC', 'IN:GET_EMPLOYMENT_TIME', 'IN:SHARE_EVENT', 'IN:PREFER', 'IN:START_SHUFFLE_MUSIC', 'IN:GET_CALL_CONTACT', 'IN:GET_LOCATION', 'IN:SILENCE_ALARM', 'IN:SWITCH_CALL', 'IN:GET_TRACK_INFO_MUSIC', 'IN:SUBTRACT_TIME_TIMER', 'IN:GET_SUNSET', 'IN:DELETE_TIMER', 'IN:UPDATE_TIMER', 'IN:PREVIOUS_TRACK_MUSIC', 'IN:SET_DEFAULT_PROVIDER_MUSIC', 'IN:HOLD_CALL', 'IN:GET_MUTUAL_FRIENDS', 'IN:SKIP_TRACK_MUSIC', 'IN:UPDATE_METHOD_CALL', 'IN:SET_RSVP_INTERESTED', 'IN:QUESTION_MUSIC', 'IN:GET_UNDERGRAD', 'IN:PAUSE_TIMER', 'IN:UPDATE_ALARM', 'IN:GET_REMINDER_LOCATION', 'IN:GET_ATTENDEE_EVENT', 'IN:LIKE_MUSIC', 'IN:RESTART_TIMER', 'IN:RESUME_TIMER', 'IN:MERGE_CALL', 'IN:GET_MESSAGE_CONTACT', 'IN:REPLAY_MUSIC', 'IN:LOOP_MUSIC', 'IN:GET_REMINDER_AMOUNT', 'IN:GET_DATE_TIME_EVENT', 'IN:STOP_MUSIC', 'IN:GET_DETAILS_NEWS', 'IN:GET_EDUCATION_DEGREE', 'IN:SET_DEFAULT_PROVIDER_CALLING', 'IN:GET_MAJOR', 'IN:UNLOOP_MUSIC', 'IN:GET_CONTACT_METHOD', 'IN:SET_RSVP_NO', 'IN:UPDATE_REMINDER_LOCATION', 'IN:RESUME_CALL', 'IN:CANCEL_MESSAGE', 'IN:RESUME_MUSIC', 'IN:UPDATE_REMINDER', 'IN:DELETE_PLAYLIST_MUSIC', 'IN:REWIND_MUSIC', 'IN:REPEAT_ALL_MUSIC', 'IN:FAST_FORWARD_MUSIC', 'IN:DISLIKE_MUSIC', 'IN:GET_LIFE_EVENT_TIME', 'IN:DISPREFER', 'IN:REPEAT_ALL_OFF_MUSIC', 'IN:HELP_REMINDER', 'IN:GET_LYRICS_MUSIC', 'IN:STOP_SHUFFLE_MUSIC', 'IN:GET_AIRQUALITY', 'IN:GET_LANGUAGE', 'IN:FOLLOW_MUSIC', 'IN:GET_GENDER', 'IN:CANCEL_CALL', 'IN:GET_GROUP']
ARGUMENTS = ['SL:CONTACT', 'SL:TYPE_CONTENT', 'SL:RECIPIENT', 'SL:LOCATION', 'SL:DATE_TIME', 'SL:ORDINAL', 'SL:CONTENT_EXACT', 'SL:RECIPES_ATTRIBUTE', 'SL:PERSON_REMINDED', 'SL:TODO', 'SL:NEWS_TYPE', 'SL:NEWS_CATEGORY', 'SL:RECIPES_DISH', 'SL:NEWS_TOPIC', 'SL:SENDER', 'SL:MUSIC_TYPE', 'SL:MUSIC_ARTIST_NAME', 'SL:NAME_APP', 'SL:WEATHER_ATTRIBUTE', 'SL:CATEGORY_EVENT', 'SL:MUSIC_PLAYLIST_TITLE', 'SL:METHOD_TIMER', 'SL:LIFE_EVENT', 'SL:MUSIC_TRACK_TITLE', 'SL:MUSIC_PROVIDER_NAME', 'SL:CONTACT_ADDED', 'SL:RECIPES_COOKING_METHOD', 'SL:CONTACT_RELATED', 'SL:TYPE_RELATION', 'SL:AMOUNT', 'SL:RECIPES_INCLUDED_INGREDIENT', 'SL:NEWS_REFERENCE', 'SL:NEWS_SOURCE', 'SL:WEATHER_TEMPERATURE_UNIT', 'SL:EMPLOYER', 'SL:PERIOD', 'SL:RECIPES_TYPE', 'SL:EDUCATION_DEGREE', 'SL:MUSIC_GENRE', 'SL:TITLE_EVENT', 'SL:TIMER_NAME', 'SL:RECIPES_UNIT_NUTRITION', 'SL:RECIPES_EXCLUDED_INGREDIENT', 'SL:RECIPES_DIET', 'SL:RECIPES_UNIT_MEASUREMENT', 'SL:JOB', 'SL:METHOD_RETRIEVAL_REMINDER', 'SL:CONTACT_REMOVED', 'SL:MUSIC_ALBUM_TITLE', 'SL:MUSIC_RADIO_ID', 'SL:PHONE_NUMBER', 'SL:ATTRIBUTE_EVENT', 'SL:ALARM_NAME', 'SL:SCHOOL', 'SL:SIMILARITY', 'SL:GROUP', 'SL:METHOD_RECIPES', 'SL:RECIPES_TYPE_NUTRITION', 'SL:RECIPES_MEAL', 'SL:RECIPES_RATING', 'SL:RECIPES_QUALIFIER_NUTRITION', 'SL:MUSIC_ALBUM_MODIFIER', 'SL:AGE', 'SL:ATTENDEE_EVENT', 'SL:CONTACT_METHOD', 'SL:MUSIC_REWIND_TIME', 'SL:RECIPES_SOURCE', 'SL:USER_ATTENDEE_EVENT', 'SL:RECIPES_CUISINE', 'SL:ATTENDEE', 'SL:MUSIC_PLAYLIST_MODIFIER', 'SL:MAJOR', 'SL:TYPE_CONTACT', 'SL:GENDER']


def agg(raw_items):
    from collections import OrderedDict
    agged = OrderedDict()
    for raw_item in raw_items:
        prefix = raw_item.split("_")[0]
        value = "_".join(raw_item.split("_")[1:])
        if not prefix in agged.keys():
            agged[prefix] = []
        agged[prefix].append(value)
    agged_str = " | ".join(["{}: {}".format(key, ", ".join(value)) for key, value in agged.items()])
    return agged_str


def save_jsonl(path, entries):
    with open(path, 'w', encoding='utf8') as fh:
        for entry in entries:
            fh.write(f'{json.dumps(entry)}\n')


def keep_xy(example):
    return {"question": example['question'], 'logical_form': example['logical_form']}


data = load_dataset("iohadrubin/mtop", "mtop")

train = list(data['train'].map(keep_xy, load_from_cache_file=False, remove_columns=data['train'].column_names))
save_jsonl(train_json, train)

dev = list(data['validation'].map(keep_xy, load_from_cache_file=False, remove_columns=data['validation'].column_names))
save_jsonl(dev_json, dev)

# test = list(data['test'])[:1000]
# save_jsonl(test_json, test)

random.shuffle(train)
items_few = train[:n]
ice_ids = list(range(n))
for item in dev:
    item['ctxs'] = ice_ids


print(f"few-shot: {len(items_few)}; dev: {len(dev)}")
save_jsonl(few_shot_file, items_few)
save_jsonl(dev_few_shot_file, dev)


datas = []
for i in range(m):
    ice_ids = list(range(n))
    random.shuffle(ice_ids)
    data = {"question": "", "logical_form": "", "ctxs": ice_ids, 'structure': agg(INTENTS)}
    datas.append(data)

save_jsonl(gen_q_file, datas)