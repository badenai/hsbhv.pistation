import sys
import asyncio
import json
from autobahn.asyncio.websocket import WebSocketClientProtocol, \
    WebSocketClientFactory
from itertools import cycle
import MFRC522
import RPi.GPIO as GPIO
import time


GPIO.setmode(GPIO.BOARD)
GPIO.setup(18, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)

ENDSTATION = 'ENDSTATION'

class EndStation(object):

    class StationEndProtocol(WebSocketClientProtocol):
        def onOpen(self):
            auth = {'auth': ENDSTATION}
            self.sendMessage(json.dumps(auth).encode('utf8'))

        def onMessage(self, payload, isBinary):
            if not isBinary:


                #Wenn die erste Lichtschranke durchbrochen ist, soll die zweite Lichtschranke aktiviert werden.
                if payload == 'Second':
                    serverFlag = True

                res = json.loads(payload.decode('utf8'))
                print("Result received: {}".format(res))
                #self.sendClose()

        def onClose(self, wasClean, code, reason):
            if reason:
                print(reason)
            #loop.stop()

    def __init__(self, host, port):
        self.serverFlag = False
        self.host = host
        self.port = port
        self.protocol = None

    def resetAll(self):
        self.serverFlag = False

    def sendMessage(self, payload):
        if self.protocol:
            self.protocol.sendMessage(json.dumps(payload).encode('utf8'))
        else:
            print('Can not send Message.')


    async def callbackGPIO(self, data):
        # GPIO Messung
        print(data)

        gpioMessage = {
            "type": "GPIO",
            "value": data
        }
        self.sendMessage(json.dumps(gpioMessage).encode('utf8'))

        #Wenn die zweite Lichtschranke durchbrochen wurde, soll noch weiter 5 Sekunden gefilmt werden und dann die Kamera deaktiviert werden
        time.sleep(5)
        stopCam = {'stopCam': "stopCam"}
        self.sendMessage(json.dumps(stopCam).encode('utf8'))



    async def sensorGPIO(self, callback):
        while True:
            if self.serverFlag == True:
                if GPIO.input(18) == GPIO.HIGH :
                    #print("sensorGPIO")
                    await callback("1")


    async def display_spinner(self, char=cycle('/|\-')):
        while True:
            print('\r' + next(char), flush=True, end='')
            await asyncio.sleep(.3)

    def run(self):
        factory = WebSocketClientFactory('ws://%s:%s' % (self.host, self.port))
        factory.protocol = EndStation.StationEndProtocol
        loop = asyncio.get_event_loop()

        coro = loop.create_connection(factory, self.host, self.port)
        trans,prot = loop.run_until_complete(coro)

        #loop.run_until_complete(self.display_spinner())
        loop.run_until_complete(self.sensorRFID(self.callbackRFID))
        loop.run_until_complete(self.sensorGPIO(self.callbackGPIO))

        loop.run_forever()
        loop.close()

if __name__ == '__main__':
    host = sys.argv[1]
    port = sys.argv[2]
    endStation = EndStation(host, port)
    endStation.run()
    print("Please specify host and port as first and second argument.")
