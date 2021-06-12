import os
import json
from importlib import reload
from lib import template

reload(template)


def import_template(path, file_name):
    file_name = os.path.join(path, '{}.{}'.format(file_name, 'json'))

    if os.path.exists(file_name):
        with open(file_name) as json_file:
            data = json.load(json_file)

    for temp in data.keys():

        for name, position in data[temp].items():
            template_inst = template.Template()
            template_inst.build(temp, name, position)
