from django.conf.urls.defaults import patterns, include, url

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()


urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'shylock.views.home', name='home'),
    # url(r'^shylock/', include('shylock.foo.urls')),
    url(r'^shylock/$', 'shylock.tabs.views.index'),
    url(r'^shylock/addTab*', 'shylock.tabs.views.addTabCall'),
    
    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)
