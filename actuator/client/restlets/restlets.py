import sys
from twisted.internet.defer import Deferred
from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor
from twisted.python import log
import txthings.coap as coap
import txthings.resource as resource
from termcolor import colored

class CacheAgent():
    def __init__(self,  host, port, uri):
        self.host = host
        self.port = port
        self.uri = uri
        endpoint = resource.Endpoint(None)
        protocol = coap.Coap(endpoint)
        self.protocol = protocol
        reactor.listenUDP(61661, protocol)
        reactor.callLater(0, self.requestResource)

    def requestResource(self):
        request = coap.Message(code=coap.GET)
        request.opt.uri_path = (self.uri,)
        request.opt.observe = 1
        request.remote = (self.host, self.port)
        d = self.protocol.request(request, observeCallback=None)
        d.addCallback(self.processResponse)
        d.addErrback(self.noResponse)

    def processResponse(self, response):
        fp = open('control_variable_loaded.txt', 'w')
        fp.write(response.payload)
        fp.close()
        return response.payload

    def noResponse(self, failure):
        print 'Failed to fetch resource:'
        print failure
        
class ANDRestlet(object):
    def __init__(self, control_variable):
        self.control_variable = control_variable
        
    def process_inputs(self, input1, input2):
        if self.control_variable:
            return False
        else:
            return input1 and input2
            
class IsLargerThanRestlet(object):
    def __init__(self, control_variable):
       self.control_variable = control_variable
        
    def process_inputs(self, input1, input2):
       if self.control_variable:
           return False
       else:
           return input1 > input2   

class CacheControlRestlet(object):
    def __init__(self, control_variables):
        """ 
        Base class which implements basc RestLet processing logic along with cache/loading control for control_variables
        @param: control_variables: A dictionary keys are the control variable names and values are lists of the format [value, expiry_time,       load_url]
        
        """
        self.control_variables = control_variables
        
    def json_serializable_variable_dict(self):
        d = {}
        for k,v in self.control_variables.items():
            v2 = []
            v2.append(v[0])
            v2.append(str(v[1]))
            v2.append(v[2])
            d[k] = v2
        return d      
          
    def load_control_variable(self, control_variable_name):
        import json
        import dateutil.parser
        fp = open('control_variables.txt', 'r+')
        control_variables = json.loads(fp.read())
        fp.close()
        try:
            item = control_variables[control_variable_name]
            self.control_variables[control_variable_name][0] = item[0]
            self.control_variables[control_variable_name][1] = dateutil.parser.parse(item[1])
        except KeyError:
            pass
        load_uri = self.control_variables[control_variable_name][2]
        client = CacheAgent( host='127.0.0.1', port=5684, uri=load_uri)
        fp = open('control_variable_loaded.txt', 'r')
        json_obj = json.loads(fp.read())
        fp.close()
        fp = open('control_variables.txt', 'w')
        fp.write(json.dumps(self.json_serializable_variable_dict()))
        fp.close()
        value  =  json_obj['value']
        expiry_time = dateutil.parser.parse(json_obj['expires_at'])
        self.control_variables[control_variable_name][1] = expiry_time
        self.control_variables[control_variable_name][0] = value
        return control_variable
        
    def get_control_variable(self, control_variable_name):
        import datetime
        try:
            expiry_time = self.control_variables[control_variable_name][1]
        except KeyError:
            raise ValueError("Control Variable %s not defined"%(control_variable_name,))
        if expiry_time is None:
            control_variable = self.load_control_variable(control_variable_name)
        elif datetime.datetime.now() > expiry_time:
            control_variable = self.load_control_variable(control_variable_name)
        else:
            control_variable = self.control_variables[control_variable_name][0]
            
        return control_variable
        

class SensorRestlet(CacheControlRestlet):
    def __init__(self, control_variables):
        super(SensorRestlet, self).__init__(control_variables)
        
    def process_sensor_input(self, sensor_number, skip_reading=False):
        from termcolor import colored
        import dateutil.parser
        import datetime
        from datetime import timedelta
        if not skip_reading:
            #Write the last recorded stamp of the sensor input
            fp = open('sensor_%s.txt'%(str(sensor_number),), 'w')
            fp.write(str(datetime.datetime.now()))
            fp.close()
        #GET the last recorded state of the sensors
        fp = open('sensor_1.txt', 'r')
        s1ls= dateutil.parser.parse(fp.read())
        fp.close()
        fp = open('sensor_2.txt', 'r')
        s2ls = dateutil.parser.parse(fp.read())
        fp.close()
        fp = open('sensor_3.txt', 'r')
        s3ls = dateutil.parser.parse(fp.read())
        fp.close()
        #GET the current state of the AC
        fp = open('ac_state.txt', 'r')
        ac_state = fp.read()
        fp.close()
        delta_time = self.get_control_variable('time')
        andr = ANDRestlet(False).process_inputs
        islr = IsLargerThanRestlet(False).process_inputs
        max_time = timedelta(seconds=delta_time)
        cur_time = datetime.datetime.now()
        if andr(andr(islr(cur_time- s1ls , max_time ), islr(cur_time- s2ls , max_time)) , islr(cur_time- s3ls , max_time)):
            if ac_state == 'ON\n':
                fp = open('ac_state.txt', 'w+')
                fp.write("OFF\n")
                fp.close()
                print colored('Motion not detected for:' + str(delta_time) +' seconds, turning off AC', 'red')  
            if ac_state == 'OFF\n':
                pass
        else:
            if ac_state == 'ON\n':
                pass
            if ac_state == 'OFF\n':
                fp = open('ac_state.txt', 'w+')
                fp.write("ON\n")
                fp.close()
                print colored( 'AC turned ON', 'red')           
        

            

