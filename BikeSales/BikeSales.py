
import time
import math
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
    """
    Validate all the keys in the dictionary with the new list of keys.

    This will add a new key to the dictionary if a new one is encoutnered, the new key will be 
    populated with default values for previous occurances. If there is a key in the dictionary, 
    that does not exist in teh new key list, a default value will be used to populate the missing key.

    dictionary: 
    The dictionary that contains the keys to check and which will be updated.
    
    list_of_keys: 
    A list containing strings that will consist of the keys that need to be added to the dictionary.

    """

    # There needs to be at least one key labeled 'Ref Code' in the dictionary
    if ('Ref Code' not in dictionary.keys()):
        return None

    if (len(dictionary.keys()) > len(list_of_keys)):
        # The size of each list for each key should be the same length
        size = len(dictionary['Ref Code'])
        missingNames = list(set(dictionary.keys()).symmetric_difference(list_of_keys))
        for newkey in missingNames:
            if newkey in dictionary.keys():
                dictionary[newkey].append('-')
            else:
                dictionary[newkey] = ['-']*size

    elif (len(dictionary.keys()) < len(list_of_keys)):
        # Add a new key to the dictionary with default values for all previous elements.
        size = len(dictionary['Ref Code'])
        missingNames = list(set(dictionary.keys()).symmetric_difference(list_of_keys))
        for newkey in missingNames:
            dictionary[newkey] = ['-']*size
    else:
        # check the keys are the same
        missingNames = list(set(dictionary.keys()).symmetric_difference(list_of_keys))
        if missingNames:
            print (pageId, linkIdx, 'Dictionary keys have the same length but different values')

    return dictionary

def get_Number_Of_Pages(webdriver=None, bikesPerPage=12):
    """
    Get the number of pages that will need to be traversed. This will depend on the number 
    of bikes shown per page.

    webdriver:
    The driver element of the webpage

    bikePerPage: (default = 12)
    The number of bikes shown per page.
    """
    numberOfBikes = bikesPerPage # default value

    elements = webdriver.find_elements_by_class_name('title')
    for element in elements:
        if ("Motorcycles for Sale" in element.text):
            tokens = element.text.split()
            for token in tokens:
                token = token.replace(',','')
                if (token.isdigit()):
                    numberOfBikes = float(token)
                    break
        
    # Return the calculated number of pages as an integer
    return int(math.ceil(numberOfBikes / bikesPerPage))






if __name__ == '__main__':

    # Read the bikeSales csv file, if it exists
    filename = '..\BikeSalesData1.csv'
    try:
        df = pd.read_csv(filename, sep=',',index_col=0)
        dict = df.to_dict()

        # Convert the dictionary of dictionary's, to a dictionary of lists.
        datadict = {}
        for key in dict.keys():
            datadict[key] = list(dict[key].values())

        # Extract the existing reference codes
        dictionaryCodes = datadict['Ref Code']

    except FileNotFoundError:
        datadict = {}
        dictionaryCodes = []


    

    

    chromedriver = configdata.chromedriver
    bikesPerPage=12
    sortedBikes = "https://www.bikesales.com.au/bikes/?q=Service.Bikesales.&Sort=Price"
    
    #datadict = {}

    driver = webdriver.Chrome(chromedriver)
    driver.get(sortedBikes)
        
    timing = []

    #numberOfPages = get_Number_Of_Pages(webdriver=driver,bikesPerPage)
    numberOfPages = 3

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
            print (pageId, linkIdx,'; URL: ',bike)
            driver.get(bike)

            # Try again if the connection failed
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
            
            ### Check if current Ref Code in existing data; yes, update last seen date and skip to next link
            ### NO: continue with following code
            # ??? what if 'ref Code' isn't in keyList ????
            currentCode = valueList[keyList.index('Ref Code')]
            

            if currentCode in dictionaryCodes:
                # Skip to next iteration
                continue

            # Add the advert description to the lists and process the description text
            keyList.append('Description')
            description = details.find_element_by_class_name('description').text
            description = ' '.join(description[12:-1].replace('\n',' ').split())
            valueList.append(description)


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
    
    bikeFrame['First_Seen'] = datetime.utcnow().date()
    bikeFrame['Last_Seen'] = datetime.utcnow().date()

    
    bikeFrame.to_csv(filename)
