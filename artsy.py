try:
    from urllib.request import urlopen,urlretrieve
except:
    from urllib import urlopen,urlretrieve
import threading
import time
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

start = time.time()
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options

from contextlib import contextmanager
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support.ui import WebDriverWait
import os, errno

@contextmanager
def wait_for_page_load(driver, timeout=30.0):
    source = driver.page_source
    yield
    WebDriverWait(driver, timeout, ignored_exceptions=(WebDriverException,)).until(lambda d: source != d.page_source)
def require_dir(path):
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno != errno.EEXIST:
            raise

def get_catagory(catagory):
    options = Options()
    options.add_argument("--headless")
    driver = webdriver.Firefox(firefox_options=options)
    for pageno in range(1,100):
        url = "https://www.artsy.net/collect?page={}&medium={}".format(pageno,catagory)
        driver.get(url)
        data = driver.page_source
        soup = BeautifulSoup(data,"html.parser")
        content=soup.find("div", { "class" : "cf-artworks" })
        img_links= content.findAll("img")
        for img in img_links:
            link=img['src']
            filename=img['alt']
            name ="".join([c for c in filename if c.isalpha() or c.isdigit() or c==' ']).rstrip()
            directory = os.path.join(os.path.dirname(os.path.abspath(__file__)), catagory)
            require_dir(directory)
            filename = os.path.join(directory, name)
            print (filename)
            try:
                with urlopen(link, context=ctx) as u, \
                    open("{}.jpg".format(filename), 'wb') as f:
                        f.write(u.read())
                f.close()
            except:
                print("error in {}".format(filename))
            #urlretrieve(link, ,context=ctx)
    driver.quit()

catagories=["painting", "photography", "drawing", "sculpture"]
for catagory in catagories:
    threads = [threading.Thread(target=get_catagory, args=(catagory,)) for catagory in catagories]
for thread in threads:
    thread.start()
for thread in threads:
    thread.join()
