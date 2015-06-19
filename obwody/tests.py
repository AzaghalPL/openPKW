from django.test import TestCase, Client, LiveServerTestCase
from django.contrib.contenttypes.models import ContentType
from urlparse import urljoin
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions

from models import Wojewodztwo, Powiat, Obwod

# Create your tests here.

class PowiatTestCase(TestCase):
    def setUp(self):
        Powiat.objects.create(name="Test", city_status=True, wojewodztwo_id=0)

    def testCityStatus(self):
        self.assertEqual(Powiat.objects.get(name="Test").city(), True)

class ObwodTestCase(TestCase):
    def setUp(self):
        Obwod.objects.create(id=0, name="Test", area_id=0, area_type_id=0)

    def testObwodAJAXGet(self):
        client = Client()
        response = client.get("/obwody/data", {"id" : 0})
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response["Content-Type"], "application/json")

    def testObwodAJAXPost(self):
        client = Client()
        response = client.post("/obwody/update", {"id" : 0, "cards" : 14, "population" : 11, "version" : 0})
        self.assertEquals(response.status_code, 200)
        obwod = Obwod.objects.get(name="Test")
        self.assertEquals(obwod.cards, 14)
        self.assertEquals(obwod.population, 11)
        self.assertEquals(obwod.version, 1)

class ObwodListTestCase(LiveServerTestCase):
    def setUp(self):
        Wojewodztwo.objects.create(id=1, name="woj_test")
        powiat = Powiat.objects.create(id=1, name="pow_test", wojewodztwo_id=1, city_status=True)
        Obwod.objects.create(id=1, name="obw_test", area_id=1, area_type=ContentType.objects.get_for_model(powiat), in_city_status=True)

        self.selenium = webdriver.Firefox()
        self.selenium.maximize_window()
        super(ObwodListTestCase, self).setUp()

    def tearDown(self):
        self.selenium.quit()
        super(ObwodListTestCase, self).tearDown()

    def testObwodList(self):
        self.selenium.get(urljoin(self.live_server_url, '/obwody/'))
	self.assertIn("jednostki", self.selenium.title)
        select = self.selenium.find_element_by_name('wojewodztwo_id')
	for option in select.find_elements_by_tag_name('option'):
    		if option.text == 'woj_test':
        		option.click()
        		break
        self.selenium.find_element_by_id("submit").submit()
        select = self.selenium.find_element_by_name('powiat_id')
	for option in select.find_elements_by_tag_name('option'):
    		if option.text == 'pow_test':
        		option.click()
        		break
        self.selenium.find_element_by_id("submit").click()
        self.assertIn("Lista komisji", self.selenium.title)

