from autobahn.asyncio.websocket import WebSocketServerProtocol, \
    WebSocketServerFactory
import asyncio
import json


class SlowSquareServerProtocol(WebSocketServerProtocol):
    async def onOpen(self):
        print("Connection open")

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


if __name__ == '__main__':
    factory = WebSocketServerFactory(u"ws://127.0.0.1:9000")
    factory.protocol = SlowSquareServerProtocol

    loop = asyncio.get_event_loop()
    coro = loop.create_server(factory, '127.0.0.1', 9000)
    server = loop.run_until_complete(coro)

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.close()
        loop.close()