from selenium import webdriver
from selenium.webdriver.chrome.options import Options


def make_driver(headless: bool = False) -> webdriver.Chrome:
    opts = Options()
    if headless:
        opts.add_argument("--headless=new")
    opts.add_argument("--window-size=1920,1080")
    return webdriver.Chrome(options=opts)
