import json
import sys


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
                args_json = json.dumps(args)
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
                pass
        print(f'|CLOUD LOG FUNCTION ENTRY: |{name} ({args}) ({error_str})')

    except BaseException as e:
        print(f'|CLOUD LOG FUNCTION ENTRY: |{name} ({args})  Error printing function' + str(e))
        print(sys.exc_info()[2])
    print(args_json)
