import sys
import asyncio
import json
import functools
from autobahn.asyncio.websocket import WebSocketClientProtocol, \
    WebSocketClientFactory
from itertools import cycle
import MFRC522


# import RPi.GPIO as GPIO

# GPIO.setmode(GPIO.BOARD)
# GPIO.setup(18, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)


class StartStation(object):
    class StationStartProtocol(WebSocketClientProtocol):
        STARTSTATION = 'STARTSTATION'
        READY = 'READY'
        RESET = 'RESET'
        AUTH = 'AUTH'

        def __init__(self):
            super().__init__()
            self.inService = False
            self.serverFlag = False
            self.rfidFlag = False

        def onOpen(self):
            auth = {
                'type': self.AUTH,
                'value': self.STARTSTATION
            }
            self.sendMessage(json.dumps(auth).encode('utf8'))
            self.factory.loop.run_in_executor(None, functools.partial(self.sensorThread, self.callbackRFID,
                                                                      self.callbackGPIO))

        def onMessage(self, payload, isBinary):
            if not isBinary:
                try:
                    msg = json.loads(payload.decode('utf8'))

                    if msg['type'] == self.READY:
                        self.serverFlag = True
                    elif msg['type'] == self.RESET:
                        self.reset()
                    else:
                        print("MSG: %s" % msg)
                except:
                    print("PLAINTEXTMSG: %s" % payload)

        def onClose(self, wasClean, code, reason):
            if reason:
                print(reason)
                self.factory.loop.stop()

        def callbackGPIO(self, data):
            # GPIO Messung
            gpioMessage = {
                "type": "GPIO",
                "value": data
            }
            self.sendMessage(json.dumps(gpioMessage).encode('utf8'))

        def callbackRFID(self, data):
            # RFID Messung
            rfidMessage = {
                "type": "RFID",
                "value": data
            }
            self.sendMessage(json.dumps(rfidMessage).encode('utf8'))

        def handleGPIO(self, callback):
            gpioInput = input("GPIO: ")
            if gpioInput:
                self.inService = True
                callback(gpioInput)

        def handleRFID(self, callback):
            rfidInput = input("RFID: ")
            if rfidInput:
                print("Input: %s" % rfidInput)
                self.rfidFlag = True
                callback(rfidInput)

        def sensorThread(self, callbackRFID, callbackGPIO):
            rfidInput = None
            gpioInput = None
            while True:
                if not self.inService:
                    if self.rfidFlag:
                        if self.serverFlag:
                            self.handleGPIO(callbackGPIO)
                        else:
                            pass
                            # print("Server not yet ready.")
                    else:
                        self.handleRFID(callbackRFID)

        def reset(self):
            self.inService = False
            self.rfidFlag = False
            self.serverFlag = False

    def __init__(self, host, port):
        self.host = host
        self.port = port

    def create_factory(self):
        factory = WebSocketClientFactory('ws://%s:%s' % (self.host, self.port))
        factory.protocol = StartStation.StationStartProtocol
        return factory

    def run(self):
        factory = self.create_factory()
        loop = asyncio.get_event_loop()
        coro = loop.create_connection(factory, self.host, self.port)
        trans, prot = loop.run_until_complete(coro)

        loop.run_forever()
        loop.close()


if __name__ == '__main__':
    host = sys.argv[1]
    port = sys.argv[2]
    startStation = StartStation(host, port)
    startStation.run()
    print("Please specify host and port as first and second argument.")
