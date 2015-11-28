import sys
from twisted.internet.defer import Deferred
from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor
from twisted.python import log
import txthings.coap as coap
import txthings.resource as resource
from termcolor import colored

class SensorAgent():

    def __init__(self, protocol, host, port, uri):
        self.protocol = protocol
        self.host = host
        self.port = port
        self.uri = uri
        reactor.callLater(5, self.notify)
        reactor.callLater(0, self.requestResource)

    def requestResource(self):
        request = coap.Message(code=coap.GET)
        request.opt.uri_path = (self.uri,)
        request.opt.observe = 0
        request.remote = (self.host, self.port)
        d = protocol.request(request, observeCallback=self.processLaterResponse)
        d.addCallback(self.processResponse)
        d.addErrback(self.noResponse)
        
    def notify(self):
        import datetime
        from restlets import restlets
        from datetime import timedelta
        sensor_processor = restlets.SensorRestlet({'time': [30, datetime.datetime.now() + timedelta(seconds=30), 'time_var',] })
        sensor_processor.process_sensor_input(0, True)        
        reactor.callLater(5, self.notify)
    def processResponse(self, response):
        print colored( 'Connected to the sensor.' , 'red',)

    def processLaterResponse(self, response):
        import json 
        import datetime
        f = open('actuator_sensor_end_2.txt', 'a+')
        f.write(str(datetime.datetime.now()) + "\n")
        f.close()
        from datetime import timedelta
        json_obj = json.loads(response.payload)
        light_state = json_obj['state']
        off_time = json_obj['time_off']
        from restlets import restlets
        sensor_processor = restlets.SensorRestlet({'time': [30, datetime.datetime.now() + timedelta(seconds=300), 'time_var',] })
        sensor_processor.process_sensor_input(2)

    def noResponse(self, failure):
        print 'Failed to fetch resource:'
        print failure

class Agent():
    def __init__(self, protocol):
        self.protocol = protocol
        reactor.callLater(0, self.requestResource)

    def requestResource(self):
        request = coap.Message(code=coap.GET)
        request.opt.uri_path = ('sensor2',)
        request.opt.observe = 1
        request.remote = ("127.0.0.1", 5684)
        d = protocol.request(request, observeCallback=self.processLaterResponse)
        d.addCallback(self.processResponse)
        d.addErrback(self.noResponse)

    def processResponse(self, response):
        print 'Sensor Address Obtained: ' + response.payload
        import json
        json_obj = json.loads(str(response.payload))
        host = json_obj['host']
        port = int(json_obj['port'])
        uri = json_obj['uri']
        endpoint = resource.Endpoint(None)
        protocol = coap.Coap(endpoint)
        client = SensorAgent(protocol, host, port, uri)
        print colored(  'Establishing the connection to the sensor', 'red',)

    def processLaterResponse(self, response):
        print 'Observe result: ' + response.payload

    def noResponse(self, failure):
        print 'Failed to fetch resource:'
        print failure


#log.startLogging(sys.stdout)
endpoint = resource.Endpoint(None)
protocol = coap.Coap(endpoint)
client = Agent(protocol)
reactor.listenUDP(61638, protocol)
reactor.run()

