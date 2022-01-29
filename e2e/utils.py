import time
from functools import wraps
from typing import Union

from autoparaselenium import run_on as a_run_on
from selenium import webdriver

from reporting import report_file

TWeb = Union[webdriver.Firefox, webdriver.Chrome]

def run_on(*args):
    def wrapper(func):
        @a_run_on(*args)
        @wraps(func)
        def inner(web):
            try:
                return func(web)
            except Exception as e:
                screenshot = f"failure-{func.__name__}-{browser_str(web)}.png"
                web.save_screenshot(screenshot)
                report_file(func.__name__, browser_str(web), screenshot)
                raise e
        return inner
    return wrapper

def browser_str(driver: TWeb):
    if isinstance(driver, webdriver.Chrome):
        return "chrome"
    if isinstance(driver, webdriver.Firefox):
        return "firefox"
    return "unknown"

def retry(cb, amount=30, interval=1):
    for i in range(amount):
        try:
            return cb()
        except Exception as e:
            if i == amount - 1:
                raise e
            time.sleep(interval)

def with_retry(amount=30, interval=0.5):
    return lambda cb: lambda *args, **kwargs: retry(lambda: cb(*args, **kwargs), amount, interval)

@with_retry()
def switch_to_chatframe(web: TWeb):
    web.switch_to.frame(web.find_element_by_css_selector("#chatframe"))

@with_retry()
def get_hc_buttons(web: TWeb):
    """
    Get HyperChat buttons.

    Needs to be in chatframe context.
    """
    buttons = web.find_elements_by_css_selector("#hc-buttons > div")
    assert len(buttons) == 2, "not correct amount of buttons"
    return buttons