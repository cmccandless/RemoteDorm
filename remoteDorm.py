#!/usr/bin/python

import sys
import re
import serial
import time
import json
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream

config = None
with open('.config','r') as configFile:
    config = json.loads(configFile.read().replace('\n',''))

serialPorts = {}
for port in config['serialPorts']:
    serialPorts[port['name']]=port['path']

ser = None
try:
    ser = {'light':serial.Serial(serialPorts['light'],9600,timeout=0),}
          #'thermostat':serial.Serial(serialPorts['thermostat'],9600,timeout=0,
except Exception as ex:
    print(str(ex))

rgxLight = re.compile(r".*light\s+(?P<command>on|off)",re.I)
rgxTemp = re.compile(r".*(?:temp(?:erature)?|thermo(?:stat)?)\s+(?P<command>up|down)",re.I)

class StdOutListener(StreamListener):
    def on_data(self,data):
        tweet = json.loads(data)
        text = tweet['text'].lower()
        print(text)
        
        serialPort = None        
        var = ''
        
        hashtags = []
        for tag in tweet['entities']['hashtags']:
            hashtags.append(tag['text'].lower())
        
        if 'remotedorm' not in hashtags:
            return True

        if rgxLight.match(text):
            serialPort = ser['light']
            command = rgxLight.match(text).group('command')
            print('Turning light {}...'.format(command))
            if command == 'on':
                var = '1'
            elif command == 'off':
                var = '0'
        if rgxTemp.match(text):
            serialPort = ser['thermostat']
            command = rgxTemp.match(text).group('command')
            print('Adjusting temperature {} 5 deg F...'.format(command))
            if command == 'up':
                var = '1'
            elif command == 'down':
                var = '0'

        if serialPort:
            try:
                serialPort.write(var.encode())
            except SyntaxError as e:
                print(str(e))
        return True

    def on_error(self,status):
        print('Error code: {}'.format(status))


if __name__ == '__main__':

    listener=StdOutListener()
    auth = OAuthHandler(config['consumer_key'],config['consumer_secret'])
    auth.set_access_token(config['access_token'], config['access_token_secret'])
    stream = Stream(auth,listener)
    filterUsers = []
    for user in config['validUsers']:
        filterUsers.append(user['id'])
    stream.filter(follow=filterUsers,track=['remoteDorm'])
