import sys
from twisted.internet.defer import Deferred
from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor
from twisted.python import log
import txthings.coap as coap
import txthings.resource as resource
from termcolor import colored


class CloudAgent():
    def __init__(self, protocol, host, port, uri):
        self.protocol = protocol
        self.host = host
        self.port = port
        self.uri = uri
        reactor.callLater(0, self.requestResource)

    def requestResource(self):
        request = coap.Message(code=coap.GET)
        request.opt.uri_path = (self.uri,)
        request.opt.observe = 0
        request.remote = (self.host, self.port)
        d = protocol.request(request, observeCallback=self.processLaterResponse)
        d.addCallback(self.processResponse)
        d.addErrback(self.noResponse)

    def processResponse(self, response):
        print colored('Connection to cloud sensor endpoint  established by actuator', 'red' )

    def processLaterResponse(self, response):
        #Record the end time for the packet
        import json 
        import datetime
        f = open('actuator_cloud_end_3.txt', 'a+')
        f.write(str(datetime.datetime.now()) + "\n")
        f.close()
        from datetime import timedelta
        json_obj = json.loads(response.payload)
        light_state = json_obj['state']
        off_time = json_obj['time_off']
        print "Processed Observe input from sensor 3"
        #from restlets import restlets
        #sensor_processor = restlets.SensorRestlet({'time': [30, datetime.datetime.now() + timedelta(seconds=3600), 'http://127.0.0.1:8989/controlVars/time/',] })
        #sensor_processor.process_lights(light_state, off_time)

    def noResponse(self, failure):
        print 'Failed to fetch resource:'
        print failure



#log.startLogging(sys.stdout)
endpoint = resource.Endpoint(None)
protocol = coap.Coap(endpoint)
client = CloudAgent(protocol, host='127.0.0.1', port=5684, uri='sensorReading3')
reactor.listenUDP(61659, protocol)
reactor.run()
