import os
import sys
import glob
import json
import http.server
import socketserver
import multiprocessing
import pytest
from selenium import webdriver
# from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

capabilities = {
    'platform': "Mac OS X 10.10",
    'browserName': "chrome",
    'version': "60",
}
PORT = 8082

@pytest.yield_fixture(scope='session')
def browser():
    if "TRAVIS_BUILD_NUMBER" in os.environ:
        username = os.environ["SAUCE_USERNAME"]
        access_key = os.environ["SAUCE_ACCESS_KEY"]
        capabilities["tunnel-identifier"] = os.environ["TRAVIS_JOB_NUMBER"]
        capabilities["build"] = os.environ["TRAVIS_BUILD_NUMBER"]
        capabilities["tags"] = [os.environ["TRAVIS_PYTHON_VERSION"], "CI"]
        hub_url = "%s:%s@localhost:4445" % (username, access_key)
    else:
        username = "chrisjsewell"
        access_key = "2428b132-dd74-4326-a484-95eace873558"
        hub_url = "%s:%s@localhost:4445" % (username, access_key)

    server = socketserver.TCPServer(('', PORT), http.server.SimpleHTTPRequestHandler)
    process = multiprocessing.Process(target=server.serve_forever)
    try:
        process.start()
        driver = webdriver.Remote(desired_capabilities=capabilities,
                                  command_executor="http://%s/wd/hub" % hub_url)

        yield driver

    finally:
        driver.quit()
        process.terminate()


def test__local(browser):

    _unfatal_messages = [
        "ipyvolume.js - Failed to load resource",
        "TypeError: Cannot read property 'then' of undefined"
    ]

    htmlpath = os.path.join(os.path.join(os.path.dirname(__file__), 'html_files'))
    #for path in glob.glob(os.path.join(htmlpath, '*online*.html')):


        # with socketserver.TCPServer(("", PORT), Handler) as httpd:
        #     print("serving at port", PORT)
        #     httpd.server_activate()

    browser.get("http://localhost:{port}/html_files/ipyolume_scatter_online.html".format(port=PORT))
    #browser.get("http://localhost:8081/html_files/" + os.path.basename(path))
    #browser.get("http://google.com")
    #browser.get('file:///'+os.path.abspath(path))
    #browser.get("https://github.com/chrisjsewell/ipyvol_html_ci/blob/master/html_files/" + os.path.basename(path))
    WebDriverWait(browser, 30).until(EC.presence_of_element_located((By.TAG_NAME, "canvas")))
    log = browser.get_log('browser')
    for item in log:
        if item.get('level') == 'SEVERE':
            if any([msg in item['message'] for msg in _unfatal_messages]):
                # known unfatal error
                continue
            raise RuntimeError('html file {0} load fails:\n{1}'.format(path, json.dumps(log, indent=2)))
