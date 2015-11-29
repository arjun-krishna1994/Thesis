
import sys

from twisted.internet.defer import Deferred
from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor
from twisted.python import log

import txthings.coap as coap
import txthings.resource as resource
import random
import os


class SensorAgent():
    def __init__(self, protocol, num, remote_host, remote_port):
        self.protocol = protocol
        self.num = num
        self.remote_host = remote_host
        self.remote_port = remote_port
        reactor.callLater(0, self.putResource)

    def putResource(self):
        import datetime
        num = self.num
        f = open('sensor_cloud_start_%s.txt'%(num,), 'a+')
        f.write(str(datetime.datetime.now()) + "\n")
        f.close()
        payload = "OFF"
        request = coap.Message(code=coap.PUT, payload=payload)
        request.opt.uri_path = ("sensorReading" + num,)
        request.opt.content_format = coap.media_types_rev['text/plain']
        request.remote = (self.remote_host, self.remote_port)
        d = self.protocol.request(request)
        d.addCallback(self.printResponse)
        #reactor.callLater(random.randint(0,10), self.putResource)

    def printResponse(self, response):
        reactor.stop()

#log.startLogging(sys.stdout)
def main(num=None):
    if num is None:
        num = random.randint(1,3)
    endpoint = resource.Endpoint(None)
    protocol = coap.Coap(endpoint)
    client = SensorAgent(protocol, str(num), os.environ['rmt_host'], 5684)
    reactor.listenUDP(61617, protocol)
    reactor.run()
