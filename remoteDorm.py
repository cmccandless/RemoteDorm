#!/usr/bin/python

import sys
import time
import re
import serial
import time
import json
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream

access_token = "58977892-vAkjYFInL4YVplaZJ39vPRNLK2dQ096Y9drehtXq9"
access_token_secret = "QywWir3zVBwjIfaXzCyqfl9A3fo1I25YTTpA7r2gvYDnr"
consumer_key = "h24uOoQodangdg4oLa0gFccOC"
consumer_secret = "VkQrwEKGW9kf66tLIKg8KqAYTnouLKmPZGEfabH4Pr6vJG6aGm"

validUsers = {'CRMcCandless':'58977892'}

ardPorts = {'light':'/dev/rfcomm0',}

ser = None
try:
    ser = [serial.Serial(ardPorts['light'],9600,timeout=0),]
    ser[0].write('1'.encode())
    time.sleep(1)
    ser[0].write('0'.encode())    
except Exception as ex:
    print(str(ex))
    sys.exit(0)

rgxLight = re.compile(r".*light\s+(?P<command>on|off)",re.I)

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

        print('Valid Command...')

        if rgxLight.match(text):
            serialPort = ser[0]
            match = rgxLight.match(text)
            print('Turning light {}...'.format(match.group('command')))
            if match.group('command') == 'on':
                var = '1'
            elif match.group('command') == 'off':
                var = '0'
        else:
            print('No match')

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
    auth = OAuthHandler(consumer_key,consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    stream = Stream(auth,listener)
    stream.filter(follow=[validUsers['CRMcCandless']],track=['remoteDorm'])
