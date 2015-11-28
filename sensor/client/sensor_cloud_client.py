
import sys

from twisted.internet.defer import Deferred
from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor
from twisted.python import log

import txthings.coap as coap
import txthings.resource as resource
import random


class SensorAgent():
    def __init__(self, protocol):
        self.protocol = protocol
        reactor.callLater(0, self.putResource)

    def putResource(self):
        import datetime
        num = str(random.randint(1,3))
        f = open('sensor_cloud_start_%s.txt'%(num,), 'a+')
        f.write(str(datetime.datetime.now()) + "\n")
        f.close()
        payload = "OFF"
        request = coap.Message(code=coap.PUT, payload=payload)
        request.opt.uri_path = ("sensorReading" + num,)
        request.opt.content_format = coap.media_types_rev['text/plain']
        request.remote = ('127.0.0.1', 5684)
        d = protocol.request(request)
        d.addCallback(self.printResponse)
        reactor.callLater(random.randint(0,10), self.putResource)

    def printResponse(self, response):
        print 'Activated Cloud Sensor'
	    #reactor.stop()

#log.startLogging(sys.stdout)

endpoint = resource.Endpoint(None)
protocol = coap.Coap(endpoint)
client = SensorAgent(protocol)

reactor.listenUDP(61617, protocol)
reactor.run()
