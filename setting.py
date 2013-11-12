import json, util

with open('settings.json') as settingFile:
    settings = util.convert(json.load(settingFile))

settings['lookup_fields'] = settings['fields'] + ['key', 'extra', 'thing']
settings['fields'] = settings['fields'] + ['key', 'extra']

#deprecated
def lookup_table_name(field):
    return field + 'lookup'

