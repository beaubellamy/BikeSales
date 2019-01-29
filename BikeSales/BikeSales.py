
import time
from datetime import datetime
import pandas as pd
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
    
def validate_Dictionary_Keys(dictionary={}, list_of_keys=[]):

    
    # check all the keys are the same
    if (len(dictionary.keys()) > len(list_of_keys)):
        # more keys already in dict
        size = len(dictionary['Ref Code'])
        missingNames = list(set(dictionary.keys()).symmetric_difference(list_of_keys))
        for newkey in missingNames:
            if newkey in dictionary.keys():
                dictionary[newkey].append('-')
            else:
                dictionary[newkey] = ['-']*size

    elif (len(dictionary.keys()) < len(list_of_keys)):
        # add more keys to dict
        size = len(datadict['Ref Code'])
        missingNames = list(set(dictionary.keys()).symmetric_difference(list_of_keys))
        for newkey in missingNames:
            dictionary[newkey] = ['-']*size
    else:
        # check the keys are the same
        missingNames = list(set(dictionary.keys()).symmetric_difference(list_of_keys))
        if missingNames:
            print (pageId, linkIdx, 'Dictionary keys have the same length but different values')

    return dictionary



if __name__ == '__main__':

    chromedriver = configdata.chromedriver
    #baseUrl = "https://www.bikesales.com.au/"
    bikesPerPage = 12 # assumed constant
    #numberOfBikes = 100 # default value
    sortedBikes = "https://www.bikesales.com.au/bikes/?q=Service.Bikesales.&Sort=Price"
    #"offsdet"+(pageId*bikesPerPage)
    
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


    #numberOfPages = numberOfBikes / bikesPerPage
    timing = []

    numberOfPages = 5
    for pageId in range(numberOfPages):
   
        # Generalise the link to all the pages
        pageUrl = sortedBikes+"&offset="+str(pageId*bikesPerPage)
        driver.get(pageUrl)

        # Get the list of all the bikes on the page
        bikesInPage = driver.find_elements_by_css_selector('.listing-item.standard')

        
        bikeLinks = []
        # Extract the links into a list
        for bike in bikesInPage:
            link = bike.find_element_by_css_selector('a').get_attribute('href')
            bikeLinks.append(link)


        # Go to each bike link
        for linkIdx, bike in enumerate(bikeLinks):
            attempt = 0
            t0 = time.clock()

#            time.sleep(5)
            print ('URL: ',bike)
            driver.get(bike)

            # check access is allowed
            while (attempt < 3 and driver.find_element_by_tag_name('h1').text == 'Access Denied'):
                time.sleep(5)
                driver.get(bike)
                print (attempt)
                attempt += 1

            if (driver.find_element_by_tag_name('h1').text == 'Access Denied'):
                continue

            #time.sleep(5)

            # Bike Details section
            details = driver.find_element_by_css_selector('section.component:nth-child(2)')
            detailsName = get_Element_Names(details)
            detailsValue = get_Element_Values(details)

            # Create a list of the keys and values for the dictionary
            keyList = []
            [keyList.append(detailsName[idx].text) for idx in range(len(detailsName))]
            valueList = []
            [valueList.append(detailsValue[idx].text) for idx in range(len(detailsValue))]
            
            # Remove the duplicate of Engine Capacity from both lists
            if (keyList.count('Engine Capacity') > 1):
                removeIdx = keyList.index('Engine Capacity')
                del keyList[removeIdx]
                del valueList[removeIdx]


            if (pageId > 0 or linkIdx > 0):
                datadict = validate_Dictionary_Keys(datadict, keyList)

            # Add the values to the dictionary.
            for idx, key in enumerate(keyList):
                value = valueList[idx]
                if key in list(datadict.keys()):            
                    datadict[key].append(value)
                else: 
                    datadict[key] = [value]

            # Add the reference URL to the dictionary
            if 'URL' in list(datadict.keys()):          
                datadict['URL'][-1] = bike
            else: 
                datadict['URL'] = [bike]



            t1 = time.clock()
            timing.append(t1-t0)

    
        
    
        

    print ("Size of the dictionary: ",len(datadict),"; Average time: ",sum(timing)/len(timing))

    driver.close()

    bikeFrame = pd.DataFrame.from_dict(datadict,orient='columns')
    bikeFrame.drop(['Bike Facts','Bike Payment','Need Insurance?','Phone'],axis=1, inplace=True)
    bikeFrame['Scrape_Date'] = datetime.utcnow().date()
    
    bikeFrame.to_csv('..\BikeSalesData.csv')
