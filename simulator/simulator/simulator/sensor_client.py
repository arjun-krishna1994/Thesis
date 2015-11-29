import sys
from twisted.internet.defer import Deferred
from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor
from twisted.python import log
import txthings.coap as coap
import txthings.resource as resource
import random


class SensorAgent(object):
    def __init__(self, protocol, host, port, uri, payload, num):
        self.protocol = protocol
        self.host = host
        self.port = port
        self.uri = uri
        self.payload = payload
        self.num = num
        reactor.callLater(0, self.putResource)
        
    def putResource(self):
        num = self.num
        print "Activated Sensor " + str(num)
        import datetime
        request = coap.Message(code=coap.PUT, payload=self.payload)
        request.opt.uri_path = ("reading" + num,)
        request.opt.content_format = coap.media_types_rev['text/plain']
        request.remote = (self.host, int(self.port))
        d = self.protocol.request(request)
        d.addCallback(self.processResponse)
        # reactor.callLater(random.randint(0, 10), self.putResource)
        
    def processResponse(self, response):
	    reactor.stop()

#log.startLogging(sys.stdout)
def main(num=None):
    if num is None:
        num = random.randint(1,3)
    endpoint = resource.Endpoint(None)
    protocol = coap.Coap(endpoint)
    client = SensorAgent(protocol, '127.0.0.1', '5683', 'reading1', 'WORKING', str(num))
    reactor.listenUDP(61651, protocol)
    reactor.run()

