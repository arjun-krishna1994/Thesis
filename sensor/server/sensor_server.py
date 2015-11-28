import datetime
import logging
import asyncio
import aiocoap.resource as resource
import aiocoap

        
class SensorDetailResource(resource.Resource):
    def __init__(self):
        super(SensorDetailResource, self).__init__()
        import json
        content = json.dumps({'host':'localhost', 'port':'5683', 'uri': 'reading'}) 
        self.content = content.encode("ascii")

    @asyncio.coroutine
    def render_get(self, request):
        response = aiocoap.Message(code=aiocoap.CONTENT, payload=self.content)
        return response

class SensorReadingResource(resource.ObservableResource):

    def __init__(self, sensor_number):
        super(SensorReadingResource, self).__init__()
        self.time_off = 0
        self.last_off_record = None
        self.state = "ON"
        self.sensor_number = sensor_number

    @asyncio.coroutine
    def render_get(self, request):
        import json
        payload = json.dumps({'state': self.state, 'time_off': self.time_off}).encode('ascii')
        response = aiocoap.Message(code=aiocoap.CONTENT, payload=payload)
        return response
    @asyncio.coroutine
    def render_put(self, request):
        print('Sensor' + self.sensor_number + ' activated.')
        payload = request.payload
        self.state = payload.decode("utf-8") 
        payload = str(self.state).encode('utf8')
        self.notify(record=True)
        return aiocoap.Message(code=aiocoap.CHANGED, payload=payload)
        
    def notify(self, record=True):
        
        import datetime
        if self.state == 'OFF':
            if self.last_off_record:
                self.time_off = self.time_off + (datetime.datetime.now() - self.last_off_record).seconds
            self.last_off_record = datetime.datetime.now()
        if self.state == 'ON':
            self.time_off = 0
            self.last_off_record = None
        # Record the start time for the packet
        if record:
            f = open('sensor_server_start_%s.txt'%(self.sensor_number), 'a+')
            f.write(str(datetime.datetime.now()) + "\n")
            f.close() 
        self.updated_state()
        #asyncio.get_event_loop().call_later(30, self.notify)
        

#logging.basicConfig(level=logging.INFO)
#logging.getLogger("coap-server").setLevel(logging.DEBUG)

def main(host="::", port=5683):
    print("Running Sensor Server on port %s."%(str(port),))
    root = resource.Site()
    root.add_resource(('reading1',), SensorReadingResource(str(1)))
    root.add_resource(('reading2',), SensorReadingResource(str(2)))
    root.add_resource(('reading3',), SensorReadingResource(str(3)))
    asyncio.async(aiocoap.Context.create_server_context(root, bind=(host,port)))
    asyncio.get_event_loop().run_forever()

if __name__ == "__main__":
    main(port=5683)
