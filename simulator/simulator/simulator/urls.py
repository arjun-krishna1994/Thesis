from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'simulator.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^screen/$', 'simulator.views.screen_state'),
    url(r'^simulator/$', 'simulator.views.simulate_input'),
    url(r'^activate/$', 'simulator.views.activate_sensor', name='activate-sensor'),
)
