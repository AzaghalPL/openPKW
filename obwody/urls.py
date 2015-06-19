from django.conf.urls import url
from . import views

urlpatterns = [
	url(r'^data', views.komisje_data),
	url(r'^update', views.komisje_update),
	url(r'^$', views.obwody, name='obwody'),
]
