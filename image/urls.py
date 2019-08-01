from django.conf.urls import url
from . import views


urlpatterns = [
    url(r'^(total|avatar)/$', views.total_and_avatar),
    url(r'^(poster|casts|relmovpos|stills|stills_thumbnail)/$', views.movie_info_pic),
    url(r'^picode/.*$', views.verify_code),
    url(r'^background/$', views.background),
]
