from django.core.management.base import NoArgsCommand
from django.db import transaction

import urllib;
import re;
from bs4 import BeautifulSoup;

from obwody.models import Wojewodztwo, Powiat, Gmina, Obwod

class Command(NoArgsCommand):
	help = "Pobiera liste wojewodztw, powiatow, gmin, komisji"

	base_url = "http://prezydent2010.pkw.gov.pl/PZT/PL/WYN/W/";
	index_url = "index.htm";

	def create_obwody(self, filename, parent, is_parent_powiat):
		source = urllib.urlopen(self.base_url + filename);
		soup = BeautifulSoup(source);			
		for link in soup.find_all("a", href=re.compile("^\/?\.\.\/\.\.\/WYN\/P.*", re.U)):
			# dodaj komisje
			komisja = Obwod.objects.create(name=link.string, in_city_status=is_parent_powiat, area=parent);
			komisja.save();
		source.close();
		return;

	def extract_links(self, filename):
		source = urllib.urlopen(self.base_url + filename);
		soup = BeautifulSoup(source);
		table = soup.find("table", id="s0");
		links = table.find_all("a", href=re.compile("^\/?\d+\.htm", re.U));
		source.close();
		return links;

	@transaction.atomic
	def handle_noargs(self, **options):
		i = 1;
		for link_wojewodztwo in self.extract_links(self.index_url):
			print('Wojewodztwo' + str(i));
			i += 1;
			wojewodztwo = Wojewodztwo.objects.create(name=link_wojewodztwo.string);
			wojewodztwo.save();
			for link_powiat in self.extract_links(link_wojewodztwo["href"]):
				powiat = Powiat.objects.create(name=link_powiat.string, wojewodztwo=wojewodztwo, city_status = 1 if (link_powiat["href"][4:6] != "00" and link_powiat.string != "Warszawa") else 0);
				powiat.save();
				# czy to miasto na prawach powiatu?
				if (powiat.city()):
					self.create_obwody(link_powiat["href"], powiat, True);						
				for link_gmina in self.extract_links(link_powiat["href"]):
					gmina = Gmina.objects.create(name=link_gmina.string, powiat=powiat);
					gmina.save();
					self.create_obwody(link_gmina["href"], gmina, False);
