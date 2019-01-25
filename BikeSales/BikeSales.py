
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import selenium.common.exceptions as seleniumException
#import selenium.webdriver.support.Select as Select

import configdata

chromedriver = configdata.chromedriver
baseUrl = "https://www.bikesales.com.au/"

sortedBikes = "https://www.bikesales.com.au/bikes/?q=Service.Bikesales.&Sort=Price"
bikesPerPage = 12
numberOfBikes = 100 # default value

driver = webdriver.Chrome(chromedriver)
driver.get(sortedBikes)

# Add filters
# This will be left until last to deal with

# Figour out how many pages there will be.
elements = driver.find_elements_by_class_name('title')
for element in elements:
    if ("Motorcycles for sale" in element.text):
        tokens = element.split()
        for token in tokens:
            token = token.replace(',','')
            if (token.isdigit()):
                numberOfBikes = int(token)


numberOfPages = numberOfBikes / bikesPerPage

# Get a link to all the pages


# Get the list of all the bikes on the page
bikesInPage = driver.find_elements_by_css_selector('.listing-item.standard')
# Extract the links into a list
#bikeLinks = 


# Go to each bike link
for bikes in bikeLinks:

    driver.get(bike)

    # save details to a data frame

    # Go back to the previous page to access the next bike link
    


