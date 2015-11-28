#Simulate input to the sensor server
import sys

from twisted.internet.defer import Deferred
from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor
from twisted.python import log

import txthings.coap as coap
import txthings.resource as resource
class SensorAgent():
    """
    Example class which performs single PUT request to iot.eclipse.org
    port 5683 (official IANA assigned CoAP port), URI "/large-update".
    Request is sent 1 second after initialization.

    Payload is bigger than 64 bytes, and with default settings it
    should be sent as several blocks.
    """

    def __init__(self, protocol, host, port, uri, payload):
        self.protocol = protocol
        self.host = host
        self.port = port
        self.uri = uri
        self.payload = payload
        reactor.callLater(1, self.putResource)

    def putResource(self):
	import datetime
        payload = "OFF"
        request = coap.Message(code=coap.PUT, payload=payload)
        request.opt.uri_path = ("sensorReading",)
        request.opt.content_format = coap.media_types_rev['text/plain']
        request.remote = ('127.0.0.1', 5684)
        d = protocol.request(request)
        d.addCallback(self.printResponse)

    def printResponse(self, response):
        #print 'Response Code: ' + coap.responses[response.code]
        #print 'Payload: ' + response.payload
	reactor.stop()

def simulate_to_sensor(host='127.0.0.1', port=5683, uri='reading', payload='OFF'):
    log.startLogging(sys.stdout)
    endpoint = resource.Endpoint(None)
    protocol = coap.Coap(endpoint)
    client = SensorAgent(protocol, host, port, uri, payload)
    reactor.listenUDP(61619, protocol)
    reactor.run()

#Simulate input to the cloud server
from client import sensor_client

def main():
    yield sensor_client.main()
    simulate_to_sensor()
