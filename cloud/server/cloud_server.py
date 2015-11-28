import datetime
import logging
import asyncio
import aiocoap.resource as resource
import aiocoap
        
class SensorDetailResource(resource.Resource):
    def __init__(self, sensor_number):
        super(SensorDetailResource, self).__init__()
        import os
        host = os.environ('sensor_%s_addr'%(str(sensor_number)))
        import json
        content = json.dumps({'host':host, 'port':'5683', 'uri': 'reading' + str(sensor_number)}) 
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
        self.sensor_number = str(sensor_number)

    @asyncio.coroutine
    def render_get(self, request):
        import json
        payload = json.dumps({'state': self.state, 'time_off': self.time_off}).encode('ascii')
        response = aiocoap.Message(code=aiocoap.CONTENT, payload=payload)
        return response
    @asyncio.coroutine
    def render_put(self, request):
        print('Reading obtained on sensor ' + self.sensor_number)
        payload = request.payload
        self.state = payload.decode("utf-8") 
        payload = str(self.state).encode('utf8')
        self.notify()
        return aiocoap.Message(code=aiocoap.CHANGED, payload=payload)
        
    def notify(self):
        import datetime
        if self.state == 'OFF':
            if self.last_off_record:
                self.time_off = self.time_off + (datetime.datetime.now() - self.last_off_record).seconds
            self.last_off_record = datetime.datetime.now()
        if self.state == 'ON':
            self.time_off = 0
            self.last_off_record = None
        # Record the start time for the packet
        self.updated_state()

class TimeControlVariableResource(resource.Resource):
    def __init__(self):
        super(TimeControlVariableResource, self).__init__()
        import json
        content = json.dumps({'value':30, 'expires_at': str(datetime.datetime.now() + datetime.timedelta(days=1)), }) 
        self.content = content.encode("ascii")

    @asyncio.coroutine
    def render_get(self, request):
        print ("Control Variable Time requested.")
        response = aiocoap.Message(code=aiocoap.CONTENT, payload=self.content)
        return response	

class TimeResource(resource.ObservableResource):
    """
    Example resource that can be observed. The `notify` method keeps scheduling
    itself, and calles `update_state` to trigger sending notifications.
    """
    def __init__(self):
        super(TimeResource, self).__init__()

        self.notify()

    def notify(self):
        self.updated_state()
        asyncio.get_event_loop().call_later(60, self.notify)

    @asyncio.coroutine
    def render_get(self, request):
        payload = datetime.datetime.now().strftime("%Y-%m-%d %H:%M").encode('ascii')
        return aiocoap.Message(code=aiocoap.CONTENT, payload=payload)

class BasicResource(resource.Resource):
    """
    Example resource which supports GET and PUT methods. It sends large
    responses, which trigger blockwise transfer.
    """

    def __init__(self):
        super(BasicResource, self).__init__()
        self.content = ("Basic Content").encode("ascii")

    @asyncio.coroutine
    def render_get(self, request):
        response = aiocoap.Message(code=aiocoap.CONTENT, payload=self.content)
        return response

    @asyncio.coroutine
    def render_put(self, request):
        #print('PUT payload: %s' % request.payload)
        self.content = request.payload
        payload = ("I've accepted the new payload. You may inspect it here in "\
                "Python's repr format:\n\n%r"%self.content).encode('utf8')
        return aiocoap.Message(code=aiocoap.CHANGED, payload=payload)

    @asyncio.coroutine
    def render_post(self, request):
        #print('PUT payload: %s' % request.payload)
        self.content = request.payload
        payload = ("I've accepted the new payload. You may inspect it here in "\
                "Python's repr format:\n\n%r"%self.content).encode('utf8')
        return aiocoap.Message(code=aiocoap.CHANGED, payload=payload)
        
#logging.basicConfig(level=logging.INFO)
#logging.getLogger("coap-server").setLevel(logging.DEBUG)

def main(host="::", port=5684):
    print("Running Cloud Server on port %s."%(str(port),))
    root = resource.Site()
    root.add_resource(('basic',), BasicResource())
    root.add_resource(('sensor1',), SensorDetailResource(1))
    root.add_resource(('sensor2',), SensorDetailResource(2))
    root.add_resource(('sensor3',), SensorDetailResource(3))
    root.add_resource(('sensorReading1',), SensorReadingResource(1))
    root.add_resource(('sensorReading2',), SensorReadingResource(2))
    root.add_resource(('sensorReading3',), SensorReadingResource(3))
    root.add_resource(('time',), TimeControlVariableResource())
    root.add_resource(('timer',), TimeResource())
    asyncio.async(aiocoap.Context.create_server_context(root, bind=(host,port)))

    asyncio.get_event_loop().run_forever()

if __name__ == "__main__":
    main(port=5684)
