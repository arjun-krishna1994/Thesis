import sys
from twisted.internet.defer import Deferred
from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor
from twisted.python import log
import txthings.coap as coap
import txthings.resource as resource
from termcolor import colored

def check_ac():
    import datetime
    from restlets import restlets
    from datetime import timedelta
    sensor_processor = restlets.SensorRestlet({
                                              'time': [30, datetime.datetime.now() + timedelta(seconds=400), 'time',] ,
                                              'time2': [15, datetime.datetime.now() + timedelta(seconds=400), 'time2',]})
    sensor_processor.process_sensor_input(0, True)        
    reactor.callLater(2, check_ac)

class SensorAgent():

    def __init__(self, protocol, host, port, uri, ):
        self.protocol = protocol
        self.host = host
        self.port = port
        self.uri = uri
        self.sensor_number = uri[-1:]
        #reactor.callLater(5, self.notify)
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
        print colored( 'Connected to the sensor.' , 'red',)

    def processLaterResponse(self, response):
        import json 
        import datetime
        f = open('actuator_sensor_end_%s.txt'%(self.sensor_number,), 'a+')
        f.write(str(datetime.datetime.now()) + "\n")
        f.close()
        from datetime import timedelta
        json_obj = json.loads(response.payload)
        light_state = json_obj['state']
        off_time = json_obj['time_off']
        from restlets import restlets
        sensor_processor = restlets.SensorRestlet({
                                                'time': [30, datetime.datetime.now() + timedelta(seconds=400), 'time',], 
                                                'time2': [15, datetime.datetime.now() + timedelta(seconds=400), 'time2',]})
        sensor_processor.process_sensor_input(int(self.uri[-1:]))

    def noResponse(self, failure):
        print 'Failed to fetch resource:'
        print failure

class Agent():
    def __init__(self, protocol):
        self.protocol = protocol
        reactor.callLater(0, self.requestResource1)
        reactor.callLater(3, self.requestResource2)
        reactor.callLater(6, self.requestResource3)
        import os
        self.remote_hst = os.environ['rmt_host']

    def requestResource1(self):
        request = coap.Message(code=coap.GET)
        request.opt.uri_path = ('sensor1',)
        request.opt.observe = 1
        request.remote = (self.remote_hst, 5684)
        d = protocol.request(request, observeCallback=self.processLaterResponse)
        d.addCallback(self.processResponse)
        d.addErrback(self.noResponse)
    def requestResource2(self):
        request = coap.Message(code=coap.GET)
        request.opt.uri_path = ('sensor2',)
        request.opt.observe = 1
        request.remote = (self.remote_hst, 5684)
        d = protocol.request(request, observeCallback=self.processLaterResponse)
        d.addCallback(self.processResponse)
        d.addErrback(self.noResponse)
    def requestResource3(self):
        request = coap.Message(code=coap.GET)
        request.opt.uri_path = ('sensor3',)
        request.opt.observe = 1
        request.remote = (self.remote_hst, 5684)
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
reactor.listenUDP(61636, protocol)
reactor.callLater(5, check_ac)
reactor.run()

