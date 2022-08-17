import json_fix  # import this before the JSON.dumps gets called
import json
import os
import sys

from twitchAPI import Twitch

should_log = "CLOUD_PRINT" in os.environ

class_checker = lambda obj: isinstance(obj, Twitch)

# then assign it to a function that does the converting
json.override_table[class_checker] = lambda obj_of_that_class: "Twitch Api"


def cloud_error_logger(e,file=sys.stderr):
    args = '<none>'
    name = '<unknown_function>'
    args_json = '{}'
    error_str = str(e)
    try:
        getframe = sys._getframe(1)

        if hasattr(getframe, 'f_code') and hasattr(getframe.f_code, 'co_name'):
            name = getframe.f_code.co_name

        if hasattr(getframe, 'f_locals') and len(getframe.f_locals) > 0:
            try:
                getframe.f_locals['__function_name'] = name
                args = str(getframe.f_locals)
                args_json = json.dumps(getframe.f_locals)
            except BaseException as b:
                error_str += "also while parsing this error, Error: " + str(b)

        else:
            try:
                fake = {}
                fake['__function_name'] = name
                args = str(fake)
                args_json = json.dumps(fake)
            except BaseException as b:
                error_str += "also while parsing this error, Error: " + str(b)

        print(f'|CLOUD ERROR ENTRY: |{name} ({args}) ({error_str})', file=file)

    except BaseException as e:
        print(f'|CLOUD ERROR ENTRY: |{name} ({args})  Error printing function' + str(e), file=file)

    print(sys.exc_info()[2], file=file)
    print(args_json, file=file)


def cloud_logger():
    args = '<none>'
    name = '<unknown_function>'
    args_json = '{}'
    error_str = ''
    try:
        getframe = sys._getframe(1)

        if hasattr(getframe, 'f_code') and hasattr(getframe.f_code, 'co_name'):
            name = getframe.f_code.co_name

        if hasattr(getframe, 'f_locals') and len(getframe.f_locals) > 0:
            try:
                getframe.f_locals['__function_name'] = name
                args = str(getframe.f_locals)
                args_json = json.dumps(getframe.f_locals)
            except BaseException as b:
                error_str = "Error: " + str(b)

        else:
            try:
                fake = {}
                fake['__function_name'] = name
                args = str(fake)
                args_json = json.dumps(fake)
            except BaseException as b:
                error_str = "Error: " + str(b)

        print(f'|CLOUD LOG FUNCTION ENTRY: |{name} ({args}) ({error_str})')

    except BaseException as e:
        print(f'|CLOUD LOG FUNCTION ENTRY: |{name} ({args})  Error printing function' + str(e))
        print(sys.exc_info()[2])
    print(args_json)
