import json, util

with open('settings.json') as settingFile:
    settings = util.convert(json.load(settingFile))

extras = ['papertype', 'key', 'extra']

settings['lookup_fields'] = settings['bib_fields'] + extras + ['thing']
settings['fields'] = settings['bib_fields'] + extras


