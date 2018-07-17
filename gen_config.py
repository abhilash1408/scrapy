import json

def addConfig(name,xpath):
    with open('config.txt') as json_file:
        config = json.load(json_file)
        config['xpaths'].append({name: xpath})
        writeConfig(config)

def writeConfig(config):
        
    with open('config.txt','w') as json_file:
        json.dump(config,json_file)



def main():
    addConfig('type',"//span[@class='hprt-roomtype-icon-link ']/text")


if __name__ == '__main__':
    main()





