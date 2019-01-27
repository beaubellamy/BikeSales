
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import selenium.common.exceptions as seleniumException
#import selenium.webdriver.support.Select as Select

import configdata

def get_Element_Names(element):
   return element.find_elements_by_tag_name('th')

def get_Element_Name(element):
   return element.find_element_by_tag_name('th')

def get_Element_Values(element):
    return element.find_elements_by_tag_name('td')

def get_Element_Value(element):
    return element.find_element_by_tag_name('td')
    


if __name__ == '__main__':

    chromedriver = configdata.chromedriver
    #baseUrl = "https://www.bikesales.com.au/"

    sortedBikes = "https://www.bikesales.com.au/bikes/?q=Service.Bikesales.&Sort=Price"
    bikesPerPage = 12 # assumed constant
    numberOfBikes = 100 # default value
    datadict = {}

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

    bikeLinks = []
    # Extract the links into a list
    for bike in bikesInPage:
        link = bike.find_element_by_css_selector('a').get_attribute('href')
        bikeLinks.append(link)


    # Go to each bike link
    for bike in bikeLinks:
        attempt = 0
    
        sleep(5)
        print ('URL: ',bike)
        driver.get(bike)
        # Wait for completion

        # check access is allowed
        while (attempt < 3 and driver.find_element_by_tag_name('h1').text == 'Access Denied'):
            sleep(5)
            driver.get(bike)
            print (attempt)
            attempt += 1

        if (driver.find_element_by_tag_name('h1').text == 'Access Denied'):
            continue

        sleep(5)

        # save details to a data frame
        
        # Bike Details section
        details = driver.find_element_by_css_selector('section.component:nth-child(2)')
        detailsName = get_Element_Names(details)
        detailsValue = get_Element_Values(details)

       
        # how do we deal with new column values ????
        for idx in range(len(detailsName)):
            key = detailsName[idx].text
            value = detailsValue[idx].text
            if key in list(datadict.keys()):
                datadict[key].append(value)
            else:
                datadict[key] = [value]

        


    # Go back to the previous page to access the next bike link
    print(datadict.shape)


