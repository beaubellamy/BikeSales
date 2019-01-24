
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import selenium.common.exceptions as seleniumException
#import selenium.webdriver.support.Select as Select

import configdata

chromedriver = configdata.chromedriver
baseUrl = "https://www.bikesales.com.au/"

sortedBikes = "https://www.bikesales.com.au/bikes/?q=Service.Bikesales.&Sort=Price"

driver = webdriver.Chrome(chromedriver)
driver.get(sortedBikes)

# Get a link to all the pages

# Get the list of all the bikes on the page

# Go to each bike link

# save details to a data frame
