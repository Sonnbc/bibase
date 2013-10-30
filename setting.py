import json, util

with open('settings.json') as settingFile:
	settings = util.convert(json.load(settingFile))

settings['lookup_fields'] = ['thing', 'key'] + settings['fields']
settings['fields'] = ['key'] + settings['fields']

#deprecated
def lookup_table_name(field):
	return field + 'lookup'

