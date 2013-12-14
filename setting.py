import json, os
import util

setting_path = os.path.join(os.path.dirname(__file__), 'settings.json')
with open(setting_path) as settingFile:
    settings = util.convert(json.load(settingFile))

extras = ['papertype', 'key', 'extra']

settings['lookup_fields'] = settings['bib_fields'] + extras + ['thing']
settings['fields'] = settings['bib_fields'] + extras


