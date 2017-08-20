import os
import sys
import glob
import json
import pytest
from selenium import webdriver
# from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

seleniumVersion = '3.3.1'

browsers = {
    'osx_chrome': {
    'platform': "Mac OS X 10.12",
    'browserName': "chrome",
    'version': "60",
    'seleniumVersion': seleniumVersion,
    },
    'osx_firefox': {
        'platform': "Mac OS X 10.12",
        'browserName': "firefox",
        'version': "48",
        'seleniumVersion': seleniumVersion,
    },  # SeleniumHQ/selenium
    'osx_safari': {
        'platform': "Mac OS X 10.12",
        'browserName': "safari",
        'version': "latest",
        'seleniumVersion': seleniumVersion,
    },
    'android_chrome': {
        "deviceName":"Android Emulator",
        'browserName': "chrome",
        #'version': "60",
        'seleniumVersion': seleniumVersion,
    },
    # 'linux_firefox': {
    #     'platform': "Linux",
    #     'browserName': "firefox",
    #     'version': "48",
    #     'seleniumVersion': seleniumVersion,
    # },  # SeleniumHQ/selenium#
}


@pytest.yield_fixture(scope='session', params=browsers.keys())
def browser(request):
    driver = webdriver.Remote(
        command_executor='http://chrisjsewell:2428b132-dd74-4326-a484-95eace873558@ondemand.saucelabs.com:80/wd/hub',
        desired_capabilities=browsers[request.param])
    try:
        yield driver
    finally:
        driver.quit()


def test_offline(browser):

    _unfatal_messages = [
        "ipyvolume.js - Failed to load resource",
        "TypeError: Cannot read property 'then' of undefined"
    ]

    browser.get("http://chrisjsewell.github.io/ipyv_test/ipyolume_scatter_offline.html")
    try:
        WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.TAG_NAME, "canvas")))
    except:
        log = browser.get_log('browser')
        raise RuntimeError('html file {0} timed out:\n{1}'.format("ipyolume_scatter_offline", json.dumps(log, indent=2)))
    log = browser.get_log('browser')
    for item in log:
        if item.get('level') == 'SEVERE':
            if any([msg in item['message'] for msg in _unfatal_messages]):
                # known unfatal error
                continue
            raise RuntimeError('html file {0} load fails:\n{1}'.format("ipyolume_scatter_offline", json.dumps(log, indent=2)))
