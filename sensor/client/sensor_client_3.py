import sys
from twisted.internet.defer import Deferred
from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor
from twisted.python import log
import txthings.coap as coap
import txthings.resource as resource


class SensorAgent():

    def __init__(self, protocol, host, port, uri, payload):
        self.protocol = protocol
        self.host = host
        self.port = port
        self.uri = uri
        self.payload = payload
        reactor.callLater(0, self.putResource)

    def putResource(self):
	import datetime
	#Record the start time here
        f = open('sensor_cloud_start_3.txt', 'a+')
        f.write(str(datetime.datetime.now()) + "\n")
        f.close()
        request = coap.Message(code=coap.PUT, payload=self.payload)
        request.opt.uri_path = ("sensorReading3",)
        request.opt.content_format = coap.media_types_rev['text/plain']
        request.remote = ('127.0.0.1', 5684)
        d = self.protocol.request(request)
        d.addCallback(self.processResponse)

    def processResponse(self, response):
	reactor.stop()

def main(host='127.0.0.1', port=5684, uri='sensorReading3', payload='OFF'):
    log.startLogging(sys.stdout)
    endpoint = resource.Endpoint(None)
    protocol = coap.Coap(endpoint)
    client = SensorAgent(protocol, host, port, uri, payload)
    reactor.listenUDP(61649, protocol)
    reactor.run()
    
if __name__ == 'main':
    main()
