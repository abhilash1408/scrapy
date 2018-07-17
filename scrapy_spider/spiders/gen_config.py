import json

def addConfig(name,xpath):
	with open('config.txt','w') as json_file:
		config = json.load(json_file)
		config['xpaths'][0][name] = xpath
		json.dump(config,json_file)













