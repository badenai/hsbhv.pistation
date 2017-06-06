import sys
import asyncio
import json
from autobahn.asyncio.websocket import WebSocketClientProtocol, \
    WebSocketClientFactory
from itertools import cycle
import picamera
import RPi.GPIO as GPIO


GPIO.setmode(GPIO.BOARD)
GPIO.setup(18, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)

CAMSTATION = 'CAMSTATION'

class camStation(object):

    class StationCamProtocol(WebSocketClientProtocol):
        def onOpen(self):
            auth = {'auth': CAMSTATION}
            self.sendMessage(json.dumps(auth).encode('utf8'))

        def onMessage(self, payload, isBinary):
            if not isBinary:

                #Wenn die RFID authentifiziert wurde, soll die Kamera beginnen zu Filmen
                if payload == 'camStart':
                    self.camFlag = True

                #Wenn die zweite Lichtschranke durchbrochen wurde, soll das Filmen gestoppt werden
                if payload == 'camStop':
                    self.camStop = True

                res = json.loads(payload.decode('utf8'))
                print("Result received: {}".format(res))
                #self.sendClose()

        def onClose(self, wasClean, code, reason):
            if reason:
                print(reason)
            #loop.stop()

    def __init__(self, host, port):
        self.camStop = False
        self.camFlag = False
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


    async def callbackCam(self, data):
        filename = 'run.h264'
        if data == "Start":
            cam.start_recording(filename)


        # Wenn die zweite Lichtschranke durchbrochen ist, soll nach x Sekunden aufgehört werden, zu filmen
        if data == "Stop":
            cam.stop_recording()
            #Filmmaterial speichern/an server schicken
            cam.close()


    async def sensorCam(self, callback):
        while True:
            if self.serverFlag == True and self.camFlag == True:
                await callback("Start")

            if self.serverFlag == True and self.camStop == True:
                await callback("Stop")


    async def display_spinner(self, char=cycle('/|\-')):
        while True:
            print('\r' + next(char), flush=True, end='')
            await asyncio.sleep(.3)

    def run(self):
        factory = WebSocketClientFactory('ws://%s:%s' % (self.host, self.port))
        factory.protocol = camStation.StationEndProtocol
        loop = asyncio.get_event_loop()

        coro = loop.create_connection(factory, self.host, self.port)
        trans,prot = loop.run_until_complete(coro)

        #loop.run_until_complete(self.display_spinner())
        loop.run_until_complete(self.sensorCam(self.callbackCam))

        loop.run_forever()
        loop.close()

if __name__ == '__main__':
    host = sys.argv[1]
    port = sys.argv[2]
    camStation = camStation(host, port)
    camStation.run()
    print("Please specify host and port as first and second argument.")
