import os
import time

from selenium import webdriver

start_t = time.time()

LMAN = """
LDC 0
LDF 4
CONS
RTN
LD 0 0
LDC 1
ADD
ST 0 0
LD 0 0
LD 0 0
LDC 3
DIV
LDC 4
LDF 35
AP 2
CONS
ST 0 0
LD 0 0
DBUG
LD 0 1
CAR
LD 0 1
LDF 43
AP 0
LDF 32
AP 1
DBUG
LDF 48
AP 2
DBUG
LD 0 0
RTN
LD 0 0
LD 0 0
RTN
LD 0 0
LD 0 0
LD 0 1
DIV
LD 0 1
MUL
SUB
RTN
CDR
CAR
CDR
CAR
RTN
LD 0 1
LD 0 1
CAR
LD 0 1
CDR
LD 0 0
LDF 66
AP 2
LDF 66
AP 2
RTN
LD 0 1
LD 0 0
DBUG
DBUG
LD 0 0
LD 0 1
RTN
LD 0 1
LD 0 0
TSEL 71 69
CAR
RTN
LD 0 0
LDC 1
SUB
LD 0 1
CDR
LDF 66
TAP 2
"""

DIRNAME = os.path.dirname(__file__)
def rel(*pieces):
    return os.path.abspath(os.path.join(DIRNAME, *pieces))

url = 'file://%s' % (rel('materials', 'game.html'), )

print url

browser = webdriver.Firefox()
browser.get(url)

load_button = browser.find_element_by_id('load')
step_button = browser.find_element_by_id('step')
lman_text = browser.find_element_by_id('lambda')

# for some reason the clear is necessary, otherwise we just get the default
# behavior
lman_text.clear()
lman_text.send_keys(LMAN)

load_button.click()
browser.execute_script('scroll(0, 1600)')

step_button.click()
step_button.click()

total_t = time.time() - start_t

print '%2.4f' % (total_t,)
