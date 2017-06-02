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
            self.clientStartStation = None

        def get_server(self):
            if self.server:
                return self.server
            else:
                raise Exception("StationServerFactory has no server.")

        def register(self, client):
            if client not in self.clients:
                print("registered client {}".format(client.peer))
                self.clients.append(client)

        def unregister(self, client):
            if client in self.clients:
                print("unregistered client {}".format(client.peer))
                self.clients.remove(client)

        def broadcast(self, msg):
            print("sending message to client...")
            for c in self.clients:
                c.sendMessage(msg.encode('utf8'))
                print("message sent to {}".format(c.peer))

    class StationServerProtocol(WebSocketServerProtocol):
        async def onConnect(self, request):
            print(request)
            headers = {'MyCustomDynamicServerHeader1': 'Hello'}
            if 'mycustomclientheader' in request.headers:
                headers['MyCustomDynamicServerHeader2'] = request.headers['mycustomclientheader']
            return (None, headers)

        async def onOpen(self):
            print("Client connected...")

        async def onMessage(self, payload, isBinary):
            if not isBinary:
                print("got Message")
                x = json.loads(payload.decode('utf8'))
                try:
                    print(x)
                except Exception as e:
                    self.sendClose(1000, "Exception raised: {0}".format(e))
                else:
                    self.sendMessage(json.dumps(x).encode('utf8'))

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