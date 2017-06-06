from autobahn.asyncio.websocket import WebSocketServerProtocol, \
    WebSocketServerFactory
import asyncio
import json
import time



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


            #Befindet sich an der Startstation
            if x['auth'] == "STARTSTATION":
                self.firstFlag = True

                #Hier soll die RFID Authentifizierung stattfinden
                if x['type'] == "RFID":
                    #datenbankzugriff mit x[value]

                    #sollte sich mit dem RFID authentifiuiert werden, soll direkt die Kamera ausgelöst werden.
                    camStart = {'camStart': "camStart"}
                    self.sendMessage(json.dumps(camStart).encode('utf8'))

                if x['type'] == "GPIO":
                    #datenbankzugriff

                    #Sende die Nachricht Second, wenn die erste Lichtschranken durchbrochen ist
                    second = {'Second': "Second"}
                    self.sendMessage(json.dumps(second).encode('utf8'))


            #Befindet sich in der Endstation
            if x['auth'] == 'ENDSTATION':
                if self.firstFlag == True:
                    if x['type'] == "GPIO":
                        #Datenbankzugriff mit x[value]

                        #wenn die zweite Lichtschranke durchbrochen ist, soll die Kamera 5 Sekunden später aufhören zu filmen
                        camStop = {'camStop': "camStop"}
                        time.sleep(5)
                        self.sendMessage(json.dumps(camStop).encode('utf8'))
                        self.firstflag = False


    def __init__(self):
        self.firstFlag = False



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
