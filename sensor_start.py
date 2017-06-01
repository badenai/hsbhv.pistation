import sys
import asyncio
import json
from autobahn.asyncio.websocket import WebSocketClientProtocol, \
    WebSocketClientFactory
from itertools import cycle
import MFRC522
import RPi.GPIO as GPIO


GPIO.setmode(GPIO.BOARD)
GPIO.setup(18, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)

STARTSTATION = 'STARTSTATION'

class StartStation(object):

    class StationStartProtocol(WebSocketClientProtocol):
        def onOpen(self):
            auth = {'auth': STARTSTATION}
            self.sendMessage(json.dumps(auth).encode('utf8'))

        def onMessage(self, payload, isBinary):
            if not isBinary:

                if payload == 'kannbeginnen':
                    serverFlag = True
                if payload == 'reset':

                res = json.loads(payload.decode('utf8'))
                print("Result received: {}".format(res))
                #self.sendClose()

        def onClose(self, wasClean, code, reason):
            if reason:
                print(reason)
            #loop.stop()

    def __init__(self, host, port):
        self.serverFlag = False
        self.rfidFlag = False
        self.host = host
        self.port = port
        self.protocol = None

    def resetAll(self):
        self.rfidFlag = False
        self.serverFlag = False

    def sendMessage(self, payload):
        if self.protocol:
            self.protocol.sendMessage(json.dumps(payload).encode('utf8'))
        else:
            print('Can not send Message.')

    async def callbackRFID(self, rfid):
        print(rfid)

        rfidMessage = { "type": "RFID",
                        "value": rfid}

        self.sendMessage(json.dumps(rfidMessage).encode('utf8'))
        # RFID empfangen
        #pass

    async def callbackGPIO(self, data):
        # GPIO Messung
        print(data)

        gpioMessage = {
            "type": "GPIO",
            "value": data
        }
        self.sendMessage(json.dumps(gpioMessage).encode('utf8'))

    async def sensorRFID(self, callback):

        #rfid1 = '182.160.142.141'
        MIFAREReader = MFRC522.MFRC522()

        while True:
            (status,TagType) = MIFAREReader.MFRC522_Request(MIFAREReader.PICC_REQIDL)
            (status,uid) = MIFAREReader.MFRC522_Anticoll()
            if status == MIFAREReader.MI_OK:
                self.rfidFlag = True
                await callback(str(uid[0])+"."+str(uid[1])+"."+str(uid[2])+"."+str(uid[3]))
            #check here for rfid registration
            #callback(rfid)
            #pass


    async def sensorGPIO(self, callback):
        while True:
            if self.rfidFlag == True and self.serverFlag == True:
                if GPIO.input(18) == GPIO.HIGH :
                    #print("sensorGPIO")
                    await callback("1")

            #check here for rfid registration
           # print("sensorGPIO")
            #await callback("test")


    async def display_spinner(self, char=cycle('/|\-')):
        while True:
            print('\r' + next(char), flush=True, end='')
            await asyncio.sleep(.3)

    def run(self):
        factory = WebSocketClientFactory('ws://%s:%s' % (self.host, self.port))
        factory.protocol = StartStation.StationStartProtocol
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
    startStation = StartStation(host, port)
    startStation.run()
    print("Please specify host and port as first and second argument.")
