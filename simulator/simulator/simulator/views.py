from django.http.response import HttpResponse
from django.template.loader import get_template
from django.template import RequestContext
import os

def screen_state(request):
    fp = open(os.environ['state_file'], 'r')
    state = fp.read()[:-1]
    t = get_template('screen_state.html')
    c = RequestContext(request, {'screen_state': state})
    return HttpResponse(t.render(c))
    
def simulate_input(request):
    t = get_template('simulate_input.html')
    c = RequestContext(request, {})
    return HttpResponse(t.render(c))

def activate_sensor(request):
    pathway = request.GET['pathway']
    pk = request.GET['pk']
    if pathway == 'binding':
        from multiprocessing import Process
        import sensor_client
        p = Process(target=sensor_client.main, args=(pk,))
        p.start()
    if pathway == 'cloud':
        from multiprocessing import Process
        import sensor_cloud_client
        p = Process(target=sensor_cloud_client.main, args=(pk,))
        p.start()
    return HttpResponse('Success')

