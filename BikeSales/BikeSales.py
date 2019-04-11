
import sys
import time
import math
from datetime import datetime
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import selenium.common.exceptions as seleniumException
from selenium.webdriver.support import expected_conditions # available since 2.26.0
#import selenium.webdriver.support.Select as Select

import configdata
max_attempts = 5

def get_Element_Names(element):
    return element.find_elements_by_tag_name('th')

def get_Element_Name(element):
    return element.find_element_by_tag_name('th')

def get_Element_Values(element):
    return element.find_elements_by_tag_name('td')

def get_Element_Value(element):
    return element.find_element_by_tag_name('td')

def try_Details(element):
    attempt = 0
    while attempt < 10:
        try:
            details = element.find_element_by_id('details')
            break
        except seleniumException.ElementNotVisibleException as e:
            continue
        except:
            print ("Details Error: ",sys.exc_info()[0])

        attempt += 1
        time.sleep(2)

    if (attempt == 10):
        sys.exit("Failed to find the 'details' element")

    return details

#def try_Specifications(element):
#    idx = 0
#    while idx < 10:
#        try:
#            specifications = element.find_element_by_id('specifications-tab')
#            specifications.click()
#            break
#        except:
#            print ("Specifications Error: ",sys.exc_info()[0])

#        idx+=1
#        time.sleep(2)

#        if (idx == 10):
#            sys.exit("Failed to find the 'specifications-tab' element")

#    return

#def try_Feature_Toggle(driver):

#    idx = 0
#    while idx < 10:
#        try:
#            feature = driver.find_element_by_class_name('features-toggle-collapse')
#            feature.click()
#            break
#        except seleniumException.ElementNotVisibleException as e:
#            continue
#        except:
#            print ("Feature Toggle Error: ",sys.exc_info()[0])

#        idx+=1
#        time.sleep(2)

#    if (idx == 10):
#        sys.exit("Failed to find the 'features-toggle-collapse' element")

#    return



def try_id_click(driver,id_string):
   
    attempt = 0
    while (attempt < max_attempts):
        try:
            element = driver.find_element_by_id(id_string).click()
            return 1
    
        except seleniumException.NoSuchElementException as e:
            attempt += 1
        
        except seleniumException.ElementNotVisibleException as e:
            attempt += 1        

        except:
            attempt += 1
            time.sleep(2)        
            
    return None

def try_class_click(driver,id_string):
   
    attempt = 0
    while (attempt < max_attempts):
        try:
            element = driver.find_element_by_class_name(id_string).click()
            return 1
    
        except seleniumException.NoSuchElementException as e:
            attempt += 1
        
        except seleniumException.ElementNotVisibleException as e:
            attempt += 1        

        except:
            attempt += 1
            time.sleep(2)        
            
    return None

def try_id(driver,id_string):
   
    attempt = 0
    while (attempt < max_attempts):
        try:
            element = driver.find_element_by_id(id_string)
            return element
                
        except seleniumException.NoSuchElementException as e:
            attempt += 1
        
        except seleniumException.ElementNotVisibleException as e:
            attempt += 1        

        except:
            attempt += 1
            time.sleep(2)        
            
    return None



def get_Details(element):
    """
    Extract the details and their corresponding values from the details tab element.
    """
    keys = []
    values = []

    index = 0
    while True:
        index += 1
        # Using the index, cycle through each child div element
        try:
            details = element.find_element_by_xpath('//*[@id="details"]/div['+str(index)+']').text.split('\n')
            keys.append(details[0])
            values.append(' '.join(details[1:]))
    
        except seleniumException.NoSuchElementException as e:
            # Reached teh end of the children.
            break
    
    return keys, values
    
def get_Specifications(elements):
    """
    Extract the specification labels and values from the specifications tab element
    """

    spec = elements.text.split('\n')

    keys = []
    values = []

    sub_Titles = ['Audio/Visual Communications','Brakes','Chassis & Suspension','Convenience','Dimensions & Weights',
                  'Electrics', 'Engine','Fuel & Emissions', 'Instruments & Controls', 'Probationary Plate Status','Safety & Security','Safey & Security',
                  'Start', 'Transmission','Wheels & Tyres','Warranty & Servicing']
    idx = 0
    while idx < len(spec):
        key = spec[idx]

        # Ignore label if its one of the sub titles
        if key not in sub_Titles:
            keys.append(key)
            idx+=1
            values.append(spec[idx])
        
        idx+=1
        
    return keys, values

def get_Location(element):
    """
    Find the location element and extract the values
    """

    try:
        location = driver.find_element_by_css_selector('.seller-info.seller-location').text
    except seleniumException.NoSuchElementException as e:
        return 'none', 'none', '0000'

    suburb = location.split('\n')

    if (suburb[2] == 'Distance from me?'):
        return 'none', suburb[1], '0000'
    else:
        return get_Suburb_and_Postcode(suburb[2])

def get_Suburb_and_Postcode(loc):
    """
    Extract the suburb, state and post code from the location element
    """
    
    location = loc.split(',')
    suburb = location[0]
    state_suburb = location[-1].split(' ')
    state = state_suburb[1]
    postcode = state_suburb[-1]

    return suburb, state, postcode


def validate_Dictionary_Keys(dictionary={}, list_of_keys=[]):
    """
    Validate all the keys in the dictionary with the new list of keys.

    This will add a new key to the dictionary if a new one is encountered, the new key will be 
    populated with default values for previous occurances. If there is a key in the dictionary, 
    that does not exist in the new key list, a default value will be used to populate the missing key.

    dictionary: 
    The dictionary that contains the keys to check and which will be updated.
    
    list_of_keys: 
    A list containing strings that will consist of the keys that need to be added to the dictionary.

    """

    # There needs to be at least one key labeled 'Network ID' in the dictionary
    if ('Network ID' not in dictionary.keys()):
        return None
    size = len(dictionary['Network ID'])

    if (len(dictionary.keys()) > len(list_of_keys)):
        # The size of each list for each key should be the same length        
        missingNames = list(set(dictionary.keys()).symmetric_difference(list_of_keys))
        for newkey in missingNames:
            if newkey in dictionary.keys():
                dictionary[newkey].append('-')
            else:
                dictionary[newkey] = ['-']*size

    elif (len(dictionary.keys()) < len(list_of_keys)):
        # Add a new key to the dictionary with default values for all previous elements.
        missingNames = list(set(dictionary.keys()).symmetric_difference(list_of_keys))
        for newkey in missingNames:
            dictionary[newkey] = ['-']*size
    else:
        # check the keys are the same
        missingNames = list(set(dictionary.keys()).symmetric_difference(list_of_keys))
        if missingNames:
            print (pageId, linkIdx, 'Dictionary keys have the same length but different values')

    for key in dictionary.keys():
        if (len(dictionary[key]) < size):
            num_extra_rows = size - len(dictionary[key])
            dictionary[key] = (['-']*(num_extra_rows))+dictionary[key]
        elif (len(dictionary[key]) > size):
            print (key, len(dictionary[key]), size)

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

def write_Data_File(dictionary={}, filename='default_file.csv'):
    """
    Write the data to file using Pandas dataframe's
    """

    bikeFrame = pd.DataFrame.from_dict(dictionary,orient='columns')
    bikeFrame.drop(['Bike Facts','Bike Payment','Need Insurance?','Phone'],axis=1, inplace=True, errors='ignore')
    
    bikeFrame['Last_Seen'] = datetime.utcnow().date()

    bikeFrame.to_csv(filename)
    
def update_firstSeen(datadict, networkID):
    """
    Update the last seen date for the individual advertisement.
    """
    idx = datadict['Network ID'].index(networkID)
    
    if 'First_Seen' in list(datadict.keys()):
        datadict['First_Seen'].append(datetime.utcnow().date())
    else:
        datadict['First_Seen'] = [datetime.utcnow().date()]

    return datadict

def update_lastSeen(datadict, networkID):
    """
    Update the last seen date for the individual advertisement.
    """
    idx = datadict['Network ID'].index(networkID)
    
    if 'Last_Seen' in list(datadict.keys()):
        if (idx < len(datadict['Last_Seen'])):
            datadict['Last_Seen'][idx] = datetime.utcnow().date()
        else:
            datadict['Last_Seen'].append(datetime.utcnow().date())
    else:
        datadict['Last_Seen'] = [datetime.utcnow().date()]

    return datadict



if __name__ == '__main__':

    # Read the bikeSales csv file, if it exists
    filename = '..\BikeSalesData.csv'
    try:
        df = pd.read_csv(filename, sep=',',index_col=0)
        dict = df.to_dict()

        # Convert the dictionary of dictionary's, to a dictionary of lists.
        datadict = {}
        for key in dict.keys():
            datadict[key] = list(dict[key].values())

        # Extract the existing reference codes
        dictionaryIDs = datadict['Network ID']

        
    except FileNotFoundError:
        datadict = {}
        dictionaryIDs = []
        
    # Set up the webdriver
    chromedriver = configdata.chromedriver
    bikesPerPage = 12
    sortedBikes = "https://www.bikesales.com.au/bikes/?q=Service.Bikesales.&Sort=Price"
    

    driver = webdriver.Chrome(chromedriver)
    driver.implicitly_wait(30)
#    driver.manage().timeouts().implicitlyWait()
    driver.get(sortedBikes)
        
    numberOfPages = get_Number_Of_Pages(webdriver=driver, bikesPerPage=bikesPerPage)

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
            
            networkID = bike.split('/')[6]

            if networkID in dictionaryIDs:
                # Update the advert last seen date
                update_lastSeen(datadict, networkID)
                # Skip to next iteration
                continue

            attempt = 0
            print (pageId, linkIdx, bike)
 
            try:   
                driver.get(bike)
            except seleniumException.TimeoutException:
                print ("Timeout exception: ",bike)
                continue




            try:
                driver.find_element_by_tag_name('h1')
                # Try again if the connection failed
                while (attempt < max_attempts and driver.find_element_by_tag_name('h1').text == 'Access Denied'):
                    time.sleep(5)
                    try:   
                        driver.get(bike)
                    except seleniumException.TimeoutException:
                        print ("Timeout exception: ",bike)
                        continue
                    print (attempt)
                    attempt += 1

                if (driver.find_element_by_tag_name('h1').text == 'Access Denied'):
                    continue

            except seleniumException.NoSuchElementException:
                print('FAILED: ', pageId, linkIdx, bike)
                continue

            # Details tab
            #details = driver.find_element_by_id('details') # try - catch
            details = try_Details(driver)
            keyList, valueList = get_Details(details)
            
            # Comments/Description section
            try:
                driver.find_element_by_class_name('view-more').click()
                description = driver.find_element_by_class_name('view-more-target').text
                description = ' '.join(description.replace('\n',' ').split())
                
            except seleniumException.ElementNotVisibleException as e:
                description = driver.find_element_by_class_name('view-more-target').text
                description = ' '.join(description.replace('\n',' ').split())
            
            except seleniumException.NoSuchElementException as e:
                description = ''
            

            keyList.append('Description')
            valueList.append(description)

            # Specifications
            #driver.find_element_by_id('specifications-tab').click()
            click = try_id_click(driver,'specifications-tab')
            if (click == None):
                continue
            #driver.find_element_by_class_name('features-toggle-collapse').click()
            click = try_class_click(driver,'features-toggle-collapse')
            if (click == None):
                continue

            wait_to_expand = driver.find_element_by_css_selector('.multi-collapse.collapse.show')
            #specifications = driver.find_element_by_id('specifications')
            specifications = try_id(driver,'specifications')
            if (specifications == None):
                continue
            key, values = get_Specifications(specifications)
            keyList += key
            valueList += values

            suburb, state, postcode = get_Location(driver)

            keyList += ['Suburb', 'State', 'Postcode']
            valueList += [suburb, state, postcode]

            # Remove the duplicate of Engine Capacity from both lists
            if (keyList.count('Engine Capacity') > 1):
                removeIdx = keyList.index('Engine Capacity')
                del keyList[removeIdx]
                del valueList[removeIdx]

           
            # Add the values to the dictionary.
            for idx, key in enumerate(keyList):
                value = valueList[idx]
                if key in list(datadict.keys()):            
                    datadict[key].append(value)
                else: 
                    datadict[key] = [value]

            # Add the reference URL to the dictionary
            if 'URL' in list(datadict.keys()):          
                datadict['URL'].append(bike)
            else: 
                datadict['URL'] = [bike]

            # Add the (date of the advert) first seen date
            update_firstSeen(datadict, networkID)
            # Update the advert last seen date
            update_lastSeen(datadict, networkID)
            keyList += ['URL','First_Seen','Last_Seen']

            # Make sure the list for each key is the same length
            datadict = validate_Dictionary_Keys(datadict, keyList)


            # Update the file with the last 100 pages of bike data
            if (((pageId % 100) == 0) & (linkIdx == len(bikeLinks)-1)):
                write_Data_File(dictionary=datadict, filename=filename)


    driver.close()

    write_Data_File(dictionary=datadict, filename=filename)

    