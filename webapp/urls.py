from django.conf.urls import include, url
from django.contrib import admin

from webapp.views import wsgi

urlpatterns = [
    # Examples:
    # url(r'^$', 'wsgi_talk.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^wsgi/', wsgi)
]
