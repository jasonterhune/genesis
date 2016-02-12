# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from subprocess import Popen, PIPE
import unittest


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

class NewVisitorTest(unittest.TestCase):
 
    def setUp(self):
    	binary = FirefoxBinary(r'/cygdrive/c/Program Files (x86)/Mozilla Firefox/firefox.exe')
    	firefoxProfile = CygwinFirefoxProfile()
    	self.browser = webdriver.Firefox(firefox_profile=firefoxProfile, firefox_binary=binary)
    	self.browser.implicitly_wait(3)

    def tearDown(self):
        self.browser.quit()
 
    def test_it_worked(self):
        self.browser.get('http://localhost:8000')
        self.assertIn('Welcome to Django', self.browser.title)
 
if __name__ == '__main__':
    unittest.main(warnings='ignore')