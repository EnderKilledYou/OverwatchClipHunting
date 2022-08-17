import json
import sys


def cloud_logger():
    args = '<none>'
    name = '<unknown_function>'
    args_json = '{}'
    try:
        getframe = sys._getframe(1)

        if hasattr(getframe, 'f_locals') and len(getframe.f_locals) > 0:
            args = str(getframe.f_locals)
            try:
                args_json = json.dumps(args)
            except:
                pass
        if hasattr(getframe, 'f_code') and hasattr(getframe.f_code, 'co_name'):
            name = getframe.f_code.co_name

        print(f'|CLOUD LOG FUNCTION ENTRY: |{name} ({args})')

    except BaseException as e:
        print(f'|CLOUD LOG FUNCTION ENTRY: |{name} ({args})  Error printing function' + str(e))
        print(sys.exc_info()[2])
    print(args_json)