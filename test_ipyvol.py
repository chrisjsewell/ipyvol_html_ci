import os
import sys
import glob
import json
import pytest
from selenium import webdriver
#from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# platform = sys.platform
# drivers = {'chrome':(webdriver.Chrome, os.path.join(os.path.dirname(__file__), 'drivers', 'chromedriver_'+platform)),
#            # firefox hangs
#            #'firefox': (webdriver.Firefox, os.path.join(os.path.dirname(__file__), 'drivers', 'geckodriver_' + platform))
#           #'safari':(webdriver.Safari, None)
#            }
#
#
# @pytest.yield_fixture(scope='session', params=drivers.keys())
# def browser(request):
#     klass, dpath = drivers[request.param]
#     if dpath is not None:
#         driver = klass(executable_path=dpath)
#     else:
#         driver = klass()
#     yield driver
#     driver.quit()

desired_cap = {
    'platform': "Mac OS X 10.9",
    'browserName': "chrome",
    'version': "31",
}

@pytest.yield_fixture(scope='session')
def browser():
    driver = webdriver.Remote(
        command_executor='http://chrisjsewell:2428b132-dd74-4326-a484-95eace873558@ondemand.saucelabs.com:80/wd/hub',
        desired_capabilities=desired_cap)
    yield driver
    driver.quit()


def test_all(browser):

    _unfatal_messages = [
        "ipyvolume.js - Failed to load resource",
        "TypeError: Cannot read property 'then' of undefined"
    ]

    htmlpath = os.path.join(os.path.join(os.path.dirname(__file__), 'html_files'))
    for path in glob.glob(os.path.join(htmlpath, '*.html')):

        #browser.get('file:///'+os.path.abspath(path))
        element = browser.find_element_by_id("fileUpload")
        element.send_keys("os.path.abspath(path)")
        WebDriverWait(browser, 20).until(EC.presence_of_element_located((By.TAG_NAME, "canvas")))
        log = browser.get_log('browser')
        for item in log:
            if item.get('level') == 'SEVERE':
                if any([msg in item['message'] for msg in _unfatal_messages]):
                    # known unfatal error
                    continue
                raise RuntimeError('html file {0} load fails:\n{1}'.format(path, json.dumps(log, indent=2)))
