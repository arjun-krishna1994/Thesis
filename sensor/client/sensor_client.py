import sys
from twisted.internet.defer import Deferred
from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor
from twisted.python import log
import txthings.coap as coap
import txthings.resource as resource
import random


class SensorAgent(object):
    def __init__(self, protocol, host, port, uri, payload):
        self.protocol = protocol
        self.host = host
        self.port = port
        self.uri = uri
        self.payload = payload
        reactor.callLater(0, self.putResource)
        
    def putResource(self):
        num = str(random.randint(1,3))
        print "Activated Sensor " + str(num)
        import datetime
        request = coap.Message(code=coap.PUT, payload=self.payload)
        request.opt.uri_path = ("reading" + num,)
        request.opt.content_format = coap.media_types_rev['text/plain']
        request.remote = ('172.50.85.82', 5683)
        d = self.protocol.request(request)
        d.addCallback(self.processResponse)
        reactor.callLater(random.randint(0, 10), self.putResource)
        
    def processResponse(self, response):
	    pass

#log.startLogging(sys.stdout)
endpoint = resource.Endpoint(None)
protocol = coap.Coap(endpoint)
client = SensorAgent(protocol, '127.0.0.1', '5683', 'reading1', 'ACTIVATED')
reactor.listenUDP(61647, protocol)
reactor.run()

