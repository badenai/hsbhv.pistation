from autobahn.asyncio.websocket import WebSocketServerProtocol, \
    WebSocketServerFactory
import asyncio
from asyncio import log
import json
import sys

class StationServer(object):
    class StationServerFactory(WebSocketServerFactory):
        def __init__(self, server, url):
            WebSocketServerFactory.__init__(self, url)
            self.server = server
            self.stations = dict()

        def get_server(self):
            if self.server:
                return self.server
            else:
                raise Exception("StationServerFactory has no server.")

        def register_station(self, station_type, station):
            print("registered station {}".format(station_type))
            self.stations[station_type] = station

        def unregister(self, station_type, station):
                print("unregistered station {}".format(station_type))
                self.stations.remove(station_type)

        def broadcast(self, msg):
            print("sending message to stations...")
            for k, v in self.stations.iteritems():
                v.sendMessage(msg.encode('utf8'))
                print("message sent to {}".format(k))

    class StationServerProtocol(WebSocketServerProtocol):
        STARTSTATION = 'STARTSTATION'
        AUTH = 'AUTH'
        READY = 'READY'
        RESET = 'RESET'
        RFID = 'RFID'
        GPIO = 'GPIO'

        def __init__(self):
            super().__init__()

        async def onOpen(self):
            print("Client connected...")

        async def onMessage(self, payload, isBinary):
            if not isBinary:
                try:
                    msg = json.loads(payload.decode('utf8'))
                    type = msg['type']
                    value = msg['value']

                    if type == self.AUTH:
                        self.factory.register_station(value, self)
                    elif type == self.RFID:
                        self.sendMessage(json.dumps({
                            'type': self.READY,
                            'value': ''
                        }).encode('utf8'))
                    elif type == self.GPIO:
                        print("GPIO VALUE: %s" % value)
                except Exception as e:
                    self.sendClose(1000, "Exception raised: {0}".format(e))


    def run(self):
        ws_server_url = u"ws://127.0.0.1:9000"
        factory = StationServer.StationServerFactory(self, ws_server_url)
        factory.protocol = StationServer.StationServerProtocol

        loop = asyncio.get_event_loop()
        coro = loop.create_server(factory, '127.0.0.1', 9000)
        server = loop.run_until_complete(coro)
        print("Server running...")
        try:
            loop.run_forever()
        except KeyboardInterrupt:
            pass
        finally:
            server.close()
            loop.close()

if __name__ == '__main__':
    server = StationServer()
    server.run()