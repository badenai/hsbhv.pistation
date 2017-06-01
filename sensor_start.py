import sys
import asyncio
import json
from autobahn.asyncio.websocket import WebSocketClientProtocol, \
    WebSocketClientFactory
from itertools import cycle

STARTSTATION = 'STARTSTATION'

class StartStation(object):
    class StationStartProtocol(WebSocketClientProtocol):
        def onOpen(self):
            auth = {'auth': STARTSTATION}
            self.sendMessage(json.dumps(auth).encode('utf8'))

        def onMessage(self, payload, isBinary):
            if not isBinary:
                res = json.loads(payload.decode('utf8'))
                print("Result received: {}".format(res))
                #self.sendClose()

        def onClose(self, wasClean, code, reason):
            if reason:
                print(reason)
            #loop.stop()

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.protocol = None

    def sendMessage(self, payload):
        if self.protocol:
            self.protocol.sendMessage(json.dumps(payload).encode('utf8'))
        else:
            print('Can not send Message.')

    async def callbackRFID(self, rfid):
        # RFID empfangen
        pass

    async def callbackGPIO(self, data):
        # GPIO Messung
        print(data)

    async def sensorRFID(self, callback):
        while True:
            #check here for rfid registration
            #callback(rfid)
            pass


    async def sensorGPIO(self, callback):
        while True:
            #check here for rfid registration
            print("sensorGPIO")
            await callback("test")


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