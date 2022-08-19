
from app import app
from Database.Twitch.twitch_clip_instance_scan_job import TwitchClipInstanceScanJob

from Database.monitor import Monitor
def get_columns(alchemy_class):
    columns = []
    for c in alchemy_class.__table__.columns:
        name = c.name
        type = c.type
        primary_key = c.primary_key
        columns.append((name, type, primary_key))
    return columns


def type_to_field(type_name):
    if type_name == "INTEGER":
        return "number"
    if type_name == "VARCHAR":
        return "text"

    if type_name == "DATETIME":
        return "date"

    if type_name == "FLOAT":
        return "number"

    return "text"


columns = get_columns(Monitor)
class_name = 'Monitor'


def format_table_header(columns):
    resp = []
    for column in columns:
        resp.append(f"<th>{column[0]}</th>")
    return ' '.join(resp)


def format_table_body(columns):
    resp = []
    for column in columns:
        resp.append(f"<td>{{  item.{column[0]} }}</td>")
    return ' '.join(resp)


print("""<table class='table table-responsive table-striped'>
<thead> """ + format_table_header(columns) + """
</thead>
<tbody>
<tr v-for="item in rows" :key="item.id">
""" + format_table_body(columns) + """
</tr>
</tbody>
</table>
""")


def column_to_ts_field(type_name):
    if type_name == "INTEGER":
        return "number =0"
    if type_name == "VARCHAR":
        return "string =''"

    if type_name == "DATETIME":
        return "date"

    if type_name == "FLOAT":
        return "number=0"

    return "string = ''"


def format_class_fields(columns):
    resp = []
    for column in columns:
        resp.append(f"  {column[0]}: {column_to_ts_field(column[1])}; ")
    return "\n".join(resp)


ts_class = f"export default class {class_name} {{" + """ 
   """ + f"constructor(part: Partial<{class_name}>) {{" + """
        Object.assign(this, part)
    }
""" + format_class_fields(columns) + " } ";
print(ts_class)
