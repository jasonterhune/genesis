# -*- coding: utf-8 -*-
from selenium import webdriver
from django.core.urlresolvers import reverse
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from subprocess import Popen, PIPE
from django.utils.translation import activate
from datetime import date
from django.utils import formats


class CygwinFirefoxProfile(FirefoxProfile):

    @property
    def path(self):

        path = self.profile_dir

        # cygwin requires to manually specify Firefox path a below:
        # PATH=/cygdrive/c/Program\ Files\ \(x86\)/Mozilla\ Firefox/:$PATH
        try:
            proc = Popen(['cygpath', '-d', path], stdout=PIPE, stderr=PIPE)
            stdout, stderr = proc.communicate()
            stdout = str(stdout).split("'")[1][:-1]
            path = stdout

        except OSError:
            print("No cygwin path found")

        return path

class HomeNewVisitorTest(StaticLiveServerTestCase):
 
    def setUp(self):
        binary = FirefoxBinary(r'/cygdrive/c/Program Files (x86)/Mozilla Firefox/firefox.exe')
        firefoxProfile = CygwinFirefoxProfile()
        self.browser = webdriver.Firefox(firefox_profile=firefoxProfile, firefox_binary=binary)
        self.browser.implicitly_wait(3)
        activate('en')

    def tearDown(self):
        self.browser.quit()
 
    def get_full_url(self, namespace):
        return self.live_server_url + reverse(namespace)
 
    def test_home_title(self):
        self.browser.get(self.get_full_url("home"))
        self.assertIn("TaskBuster", self.browser.title)
 
    def test_h1_css(self):
        self.browser.get(self.get_full_url("home"))
        h1 = self.browser.find_element_by_tag_name("h1")
        self.assertEqual(h1.value_of_css_property("color"), 
                         "rgba(200, 50, 255, 1)")
        
    def test_home_files(self):
        self.browser.get(self.live_server_url + "/robots.txt")
        self.assertNotIn("Not Found", self.browser.title)
        self.browser.get(self.live_server_url + "/humans.txt")
        self.assertNotIn("Not Found", self.browser.title)

    def test_internationalization(self):
        for lang, h1_text in [('en', 'Welcome to TaskBuster!'),
                                    ('ca', 'Benvingut a TaskBuster!')]:
            activate(lang)
            self.browser.get(self.get_full_url("home"))
            h1 = self.browser.find_element_by_tag_name("h1")
            self.assertEqual(h1.text, h1_text)

    def test_localization(self):
        today = date.today()
        for lang in ['en', 'ca']:
            activate(lang)
            self.browser.get(self.get_full_url("home"))
            local_date = self.browser.find_element_by_id("local-date")
            non_local_date = self.browser.find_element_by_id("non-local-date")
            self.assertEqual(formats.date_format(today, use_l10n=True),
                                  local_date.text)
            self.assertEqual(today.strftime('%Y-%m-%d'), non_local_date.text)
    
    def test_time_zone(self):
        self.browser.get(self.get_full_url("home"))
        tz = self.browser.find_element_by_id("time-tz").text
        utc = self.browser.find_element_by_id("time-utc").text
        ny = self.browser.find_element_by_id("time-ny").text
        self.assertNotEqual(tz, utc)
        self.assertNotIn(ny, [tz, utc]) 