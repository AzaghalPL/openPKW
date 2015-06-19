# -*- coding: utf-8 -*-
import json
from django.shortcuts import render
from django.contrib import messages
from django.db import transaction
from django.http import HttpResponse
from models import Wojewodztwo, Powiat, Gmina, Obwod

def obwody(request):
	wojewodztwa = Wojewodztwo.objects.all();
	context = { 'wojewodztwa' : wojewodztwa };
	if request.method == 'POST':
		if request.POST.get('parent_id'):
			return komisje(request, None, None);
		wojewodztwo_id = request.POST.get('wojewodztwo_id');
		powiat_id = request.POST.get('powiat_id');
		gmina_id = request.POST.get('gmina_id');
		if wojewodztwo_id:
			context['wojewodztwo_id'] = int(wojewodztwo_id);
			context['powiaty'] = Powiat.objects.filter(wojewodztwo__id=int(wojewodztwo_id));
		if powiat_id:
			if Powiat.objects.get(id=int(powiat_id)).city():
				return komisje(request, powiat_id, True);
			else:
				context['powiat_id'] = int(powiat_id);
				context['gminy'] = Gmina.objects.filter(powiat__id=int(powiat_id));
		if gmina_id:
			return komisje(request, gmina_id, False);
	return render(request, 'wybor.html', context);

def komisje(request, parent_id=None, powiat=None):
	if request.method == 'POST':
		context = {};
		if powiat == None:
			powiat = (request.POST.get('powiat') == 'True');
		if not parent_id:
			parent_id = request.POST.get('parent_id');
		obwody = Obwod.objects.filter(in_city_status=bool(powiat), area_id=int(parent_id)).only('id', 'name', 'cards', 'population');
		context['obwody'] = obwody;
		context['parent_id'] = int(parent_id);
		context['powiat'] = bool(powiat);
	else:
		raise Http404;
	return render(request, 'komisje.html', context);

def komisje_data(request):
	if request.method == 'GET':
		id = int(request.GET.get('id'));
		response_data = {};
		obwod = Obwod.objects.get(id=id);
		response_data['cards'] = obwod.cards;
		response_data['population'] = obwod.population;
		response_data['version'] = obwod.version;
		return HttpResponse(
			json.dumps(response_data),
			content_type = 'application/json');
	else:
		raise Http404;

def komisje_update(request):
	if request.method == 'POST':
		id = int(request.POST.get('id'));
		cards = request.POST.get('cards');
		population = request.POST.get('population');
		version = int(request.POST.get('version'));
		response_data = {};
		status_code = 200;
		if not cards.isdigit():
			status_code = 400;
			response_data['cards'] = True;
		if not population.isdigit():
			status_code = 400;
			response_data['population'] = True;
		if not response_data:
			with transaction.atomic():
				obwod = Obwod.objects.get(id=id);
				if (obwod.version == version):
					obwod.cards = int(cards);
					obwod.population = int(population);
					obwod.version += 1;
					obwod.save();
				else:
					status_code = 409;
				response_data['cards'] = obwod.cards;
				response_data['population'] = obwod.population;
				response_data['version'] = obwod.version;
		return HttpResponse(
			status = status_code,
			content = json.dumps(response_data),
			content_type = 'application/json');
	else:
		raise Http404;