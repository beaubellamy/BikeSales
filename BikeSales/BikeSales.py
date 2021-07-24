
import sys
import time
import math
import random
from datetime import datetime
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import selenium.common.exceptions as seleniumException
from selenium.webdriver.support import expected_conditions # available since 2.26.0
#import selenium.webdriver.support.Select as Select
import re

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
        except seleniumException.NoSuchElementException as e:
            return None
        except:
            print ("Details Error: ",sys.exc_info()[0])
            

        attempt += 1
        time.sleep(2)

    if (attempt == 10):
        sys.exit("Failed to find the 'details' element")

    return details


def try_id_click(driver,id_string):

    robot_check(driver)
    
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
    robot_check(driver)
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

def try_class_names(driver,string):
    robot_check(driver)
    attempt = 0
    while (attempt < max_attempts):
        try:
            element = driver.find_elements_by_class_name(string)
            return element
    
        except seleniumException.NoSuchElementException as e:
            attempt += 1
        
        except seleniumException.ElementNotVisibleException as e:
            attempt += 1        

        except:
            attempt += 1
            time.sleep(2)        
            
    return None


def try_id(driver,id_string):
    robot_check(driver)
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

def try_get(driver, url):
    robot_check(driver)
    attempts = 0

    while True:
        try:
            driver.get(url)
            break;
        except seleniumException.TimeoutException:
            print ("Timeout exception: ",attempts, url)
            time.sleep(5)
            attempts += 1
            continue

    return driver

def try_class_name_selectors(driver, class_string, index):
    robot_check(driver)
    attempt = 0
    while attempt < 5:
        try:                        
           return driver.find_elements_by_class_name(class_string)[index].find_elements_by_css_selector('a')


        except seleniumException.ElementNotVisibleException as e:
            attempt += 1
        except:
            driver.get(driver.current_url)
            attempt += 1

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
            # Reached the end of the children.
            break
    
    return keys, values
    
def get_Specifications(elements):
    """
    Extract the specification labels and values from the specifications tab element
    """

    spec = elements.text.split('\n')

    keys = []
    values = []

    sub_Titles = ['Audio/Visual Communications','Brakes','Chassis & Suspension','Convenience','Dimensions & Weights', 'Details',
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
    robot_check(driver)
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
            dictionary[key] = dictionary[key][0:size]

    return dictionary

def get_Number_Of_Pages(driver=None, bikesPerPage=12):
    """
    Get the number of pages that will need to be traversed. This will depend on the number 
    of bikes shown per page.

    webdriver:
    The driver element of the webpage

    bikePerPage: (default = 12)
    The number of bikes shown per page.
    """
    robot_check(driver)

    numberOfBikes = bikesPerPage # default value

    elements = driver.find_elements_by_class_name('title')
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
        
    bikeFrame.to_csv(filename,index=False)
    
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


def get_filter_list(driver):
    robot_check(driver)

    filter_block = driver.find_elements_by_class_name('element-selection')
    filterList = filter_block[0].find_elements_by_class_name("nav-element")
    return filterList

def robot_check(driver):
    if driver.find_element_by_tag_name('title').parent.title == 'You have been blocked':
        print ('Pause here: Captcha check')


def clean_bikeModel(bike):
    bike = bike.text.replace(' ','-')
    bike = bike.replace('-/-','-')
    bike = bike.replace('/','')
    bike = bike.replace('(','')
    bike = bike.replace(')','')
    return bike

def get_subtypes(driver):
    robot_check(driver)
    if not driver.find_elements_by_class_name('aspect-name'):
        subTypes = ['None']
    else:
        subTypes = try_class_name_selectors(driver, 'aspect', 0)

    return subTypes

def filter_list(list):
    if len(list) > 2:
        if list[-2].text in ['view all...','view all makes...','view all models...']:
            list[-2].click()
            list = list[0:-2]

    return list

def goToBikeMake(driver, makeList, makeIdx, offset):
    robot_check(driver)
    time.sleep(2)
    try:
        driver.get(makeList[makeIdx].get_attribute('href'))
    except seleniumException.ElementNotVisibleException as e:
        print ("Make Error "+e.msg)
        print (makeList[makeIdx].text)
        time.sleep(5)
        makeList = try_class_name_selectors(driver, 'aspect', 2-offset) ##1
        if makeList == None:
            return None
                    
        if len(makeList) > 2:
            makeList = filter_list(makeList)
            time.sleep(2)
            try:
                driver.get(makeList[makeIdx].get_attribute('href'))
            except:
                return None
    except:
        return None

    return makeList

def getModelList(driver, offset):
    robot_check(driver)
    modelList = try_class_name_selectors(driver, 'aspect', 3-offset) ##2
    if modelList == None:
        return None

    if modelList[0].text == '':
        modelList = try_class_name_selectors(driver, 'aspect', 2-offset)

    modelList = filter_list(modelList)
    return modelList

def goToBikeModel(driver, modelSelection):

    robot_check(driver)
    time.sleep(2)
    try:
        driver.get(modelSelection.get_attribute('href'))

    except seleniumException.ElementNotVisibleException as e:
        print ("Error "+e.msg)
        print ('Missed ',modelSelection.text)
        return None
    except seleniumException.ElementClickInterceptedException as e:
        print (f'ElementClickInterceptedException Exception at [{modelList[model_idx].text}]')
        driver.get(modelSelection.get_attribute('href'))
        #continue
    except:
        print (modelSelection.text)
        return None

    return 0 # Succefully completed function

                        

if __name__ == '__main__':
    # Read the bikeSales csv file, if it exists
    filename = '..\BikeSalesData-2021.csv'
    try:
        df = pd.read_csv(filename, sep=',')
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
    base_url = 'https://www.bikesales.com.au/bikes'
    sortedBikes = 'https://www.bikesales.com.au/bikes/?q=Service.Bikesales.&Sort=Price'
    #from selenium import webdriver
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--incognito")  

    driver = webdriver.Chrome(chromedriver, chrome_options=chrome_options)
    driver.implicitly_wait(30)
    #driver.get(sortedBikes)

    time.sleep(5+2*random.random())
    #robot_check(driver)
    #filterList = get_filter_list(driver)

    #----
    #for filter in filterList:
    #    if filter.text == 'Bike Type':
    #        filter.click()
    #        break

    ## get the bike type list (categoryList) from the popup window.
    #categoryList = driver.find_elements_by_class_name('multiselect-facets-item.border-bottom')

    bikeType = {'atv-quad': ['agriculture', 'electric', 'farm', 'fun', 'sport'],
                'dirt-bikes': ['comptetition', 'electric-bikes', 'enduro-2-stroke', 'endure-4-stroke', 'farm', 'fun', 'motorcross-2-stroke', 'motorcross-4-stroke', 'trail', 'trails'],
                'racing': [],
                'road': ['adventure-sport', 'adventure-touring', 'cruiser', 'electric-bikes', 'electric-scooters', 
                         'farm', 'naked', 'scooters', 'sport-touring', 'super-motard', 'super-sport', 'tourig', 'vintage'],
                'sxs-utv': ['agriculture', 'electric', 'fun', 'recreational-utility', 'sport', 'utility']}
    makeList = ['adly', 'aeon', 'american-ironhorse', 'aprilia', 'ariel', 'atk', 
                 'baroni', 'benelli', 'benzhou', 'beta', 'big-bear-choppers', 'big-dog', 'bimota', 'bmw', 'bobber', 
                 'bolwell-scoota', 'boom-trike', 'braaap', 'brough-superior', 'bsa', 'buell', 'bultaco', 
                 'cafe-racer', 'cagiva', 'can-am', 'ccm', 'cfmoto', 'chopper', 'confederate', 
                 'daelim', 'derbi', 'deus-ex-machina', 'ducati', 
                 'ebr-erik-buell-racing', 'emd-scooters', 'emos', 'evoke', 'exile', 
                 'fantic', 'fonzarelli', 
                 'gas-gas', 'gilera', 
                 'harley-davidson', 'hercules', 'honda', 'hunter-scooter', 'husaberg', 'husqvarna', 'hyosung', 
                 'ikonik', 'indian', 
                 'jawa', 'jiajue', 
                 'kandi', 'kawasaki', 'ktm', 'kymco', 
                 'lambretta', 'landboss', 'laro', 'laverda', 'linhai', 'lml-scooter', 
                 'manhattan', 'mci', 'montesa', 'moto-guzzi', 'moto-morini', 'motobi', 'mutt', 'mv-agusta', 
                 'norton', 
                 'odes', 'oz-trike', 
                 'peugeot', 'piaggio', 'pista', 'pit-bike', 'polaris', 
                 'rieju', 'royal-enfield', 
                 'scootarelli', 'scorpion-trikes', 'segway', 'service', 'sherco', 'sol-invictus-motorcycle-co.', 
                 'super-soco', 'suzuki', 'swm', 'sym', 'tgb', 
                 'titan', 'tonelli', 'torino', 'touro', 'trike', 'triumph', 
                 'ural', 
                 'vectrix', 'velocette', 'vespa', 'victory', 'vmoto', 
                 'walt-siegal-motorcycles', 
                 'yamaha', 'ycf', 
                 'zero', 'znen', 'zoot']
    makeList = ['can-am']
    #----

    # loop through the bake categories
    #for category_idx in range(len(categoryList)):
        
    ######
    # Might be able to reconstruct the web address for each bike type and subtype
    #https://www.bikesales.com.au/bikes/road/naked-subtype/?sort=Price
    #https://www.bikesales.com.au/bikes/road/cruiser-subtype/?sort=Price
    #https://www.bikesales.com.au/bikes/road/adventure-sport-subtype/?sort=Price
    #
    #https://www.bikesales.com.au/bikes/dirt-bikes/electric-bikes-subtype/?sort=Price
    #https://www.bikesales.com.au/bikes/dirt-bikes/enduro-2-stroke-subtype/?sort=Price
    #https://www.bikesales.com.au/bikes/dirt-bikes/competition-subtype/?sort=Price

    #https://www.bikesales.com.au/bikes/atv-quad/agriculture-subtype/can-am/?sort=Price
    ######

    for type in bikeType.keys():

        for subtype in bikeType[type]:
            for make in makeList:

                # Build the url
                url = base_url+'/'+type+'/'+subtype+'-subtype/'+make+'/?sort=Price'
                print (f'{url}')
                # go to the url
                
                time.sleep(5+2*random.random())
                driver.get(url)
                print ('checking for bikes')
                # Check if we have returned home (base_url) - wrong make, or subtype
                # check there are bikes available
                if driver.find_elements_by_class_name('title')[0].text[0] == '0':
                    continue

                print ('there are some bikes to view')
                numberOfPages = math.ceil(int(driver.find_elements_by_class_name('title')[0].text.split()[0].replace(',',''))/12)

                if numberOfPages > 100:
                    print (f'{type}: {subtype} {make}')
                    print ('stop')


                # Loop through each page
                #for pageId in range(numberOfPages):
                #    pageUrl = url+'&offset='+str(pageId*bikesPerPage)
                #    driver.get(pageUrl)


                # Get the list of all the bikes on the page
                bikesInPage = driver.find_elements_by_css_selector('.listing-item.standard')

                bikeLinks = []
                # Extract the links into a list
                for bike in bikesInPage:
                    link = bike.find_element_by_css_selector('a').get_attribute('href')
                    bikeLinks.append(link)

                if not bikeLinks:
                    link = driver.find_elements_by_class_name('js-encode-search.view-more.view-more-gallery')[0].get_attribute('href')
                    bikeLinks.append(link)

                for linkIdx, bike in enumerate(bikeLinks):
            
                    networkID = bike.split('/')[6]

                    if networkID in dictionaryIDs:
                        # Update the advert last seen date
                        update_lastSeen(datadict, networkID)
                        # Skip to next iteration
                        continue

                    attempt = 0
                    print (linkIdx, bike)

                    try:   
                        driver.get(bike)
                    except seleniumException.TimeoutException:
                        print ("Timeout exception: ",bike)
                        continue

                    # extract the model of the bike
                    title = driver.find_element_by_class_name('col-lg-8.col-sm-10').text
                    ##-----
                    # Assume year is always the first item
                    title = title.lower().split()[1:]
                    title = '-'.join(title)
                    # find where the make ends in the string
                    model_idx = title.find(make)+len(make)+1
                    model = title[model_idx:]
                    # check if the model year is at the end
                    make_year = re.findall('[a-zA-Z]{2}\d{2}', model)
                    if make_year:
                        model = model[:-5]
                    model = model.replace('-', ' ')



                    ##------

                    details = try_Details(driver)
                    if (details == None):
                        continue
                    
                    keyList, valueList = get_Details(details)
            
                    robot_check(driver)
                    # Comments/Description section
                    try:
                        driver.find_element_by_class_name('view-more').click()

                        description = driver.find_element_by_class_name('view-more-target').text
                        description = ' '.join(description.replace('\n',' ').split())
                
                    except seleniumException.ElementNotVisibleException as e:
                        description = driver.find_element_by_class_name('view-more-target').text
                        description = ' '.join(description.replace('\n',' ').split())
            
                    except: #seleniumException.NoSuchElementException as e:
                        description = ''
                            
                    keyList.append('Description')
                    valueList.append(description)

                    # Specifications
                    time.sleep(2+2*random.random())
                    click = try_id_click(driver,'specifications-tab')
                    if (click == None):
                        continue
         
                    click = try_class_click(driver,'features-toggle-collapse')
                    if (click == None):
                        continue

                    robot_check(driver)
                    try:
                        wait_to_expand = driver.find_element_by_css_selector('.multi-collapse.collapse.show')
                    except:
                        continue

                    specifications = try_id(driver,'specifications')
                    if (specifications == None):
                        continue
                    key, values = get_Specifications(specifications)
                    keyList += key
                    valueList += values

                    suburb, state, postcode = get_Location(driver)

                    keyList += ['Suburb', 'State', 'Postcode','Category','SubType', 'Make', 'Model']
                    valueList += [suburb, state, postcode, type, subtype, make, model]
def old_funtion():

        base_url+BikeType+subtype+make

        category = categoryList[category_idx].text.split('\n')[0].replace(' & ','-')
        category = category.replace(' ','-')

        time.sleep(5)
        robot_check(driver)
        element = categoryList[category_idx].find_element_by_css_selector('a')
        driver.execute_script("arguments[0].click();", element)

        subTypes = get_subtypes(driver)

        #if subTypes == None:
        #    continue

        subTypes = filter_list(subTypes)

        for subtype_idx in range(len(subTypes)):
            
            offset = 0
            if subTypes[subtype_idx] != 'None':
                bikeType = subTypes[subtype_idx].text.replace(' ','-')
                subCategory = bikeType
                bikeType = bikeType+'-subtype'
                print (bikeType)

                time.sleep(2)
                if category == 'Racing':
                    bikeType = ''
                    offset = 1
                else:
                    time.sleep(2+2*random.random())
                    robot_check(driver)
                    driver.get(subTypes[subtype_idx].get_attribute('href'))

            else:               
                bikeType = ''
                subCategory = bikeType
                offset = 1

            # get the make
            time.sleep(2+2*random.random())
            robot_check(driver)
            makeList = try_class_name_selectors(driver, 'aspect', 2-offset) ##1
            if makeList == None:
                continue

            makeList = filter_list(makeList)

            # select the make
            for makeIdx in range(len(makeList)):
                               
                time.sleep(2+2*random.random())
                bikeMake = makeList[makeIdx].text.replace(' ','-')
                success = goToBikeMake(driver, makeList, makeIdx, offset)
                if success == None:
                    continue

                print (f'  {bikeMake}')

                
                # Get the model
                time.sleep(2+2*random.random())
                modelList = getModelList(driver, offset)
                if modelList == None:
                    continue

                # loop through models
                for model_idx in range(len(modelList)):
                    # encountered catcha (im not a robot)
                    bikeModel = clean_bikeModel(modelList[model_idx])

                    time.sleep(2+2*random.random())
                    success = goToBikeModel(driver, modelList[model_idx])
                    if success == None:
                        continue

                    print (f'    {bikeModel}')

                    try:
                        time.sleep(5)
                        robot_check(driver)
                        numberOfPages = math.ceil(int(driver.find_elements_by_class_name('title')[1].text.split()[0].replace(',',''))/12)
                        
                    except Exception as e:
                        continue

                    if numberOfPages > 100:
                        print (f'{model_idx}: {modelList[model_idx].text}')
                        print ('stop')

                    # loop through the bikes
                    for pageId in range(numberOfPages):
   
                        # Generalise the link to all the pages
                        pageUrl = "https://www.bikesales.com.au/bikes/"+category+"/"+bikeType+"/"+bikeMake+"/"+bikeModel+"/?Sort=Price&offset="+str(pageId*bikesPerPage)

                        time.sleep(2+10*random.random())
                        robot_check(driver)
                        try:
                            driver.get(pageUrl)
                        except:
                            continue

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
                            
                            time.sleep(2+2*random.random())
                            robot_check(driver)
                            try:   
                                driver.get(bike)
                            except seleniumException.TimeoutException:
                                print ("Timeout exception: ",bike)
                                continue

                            try:
                                robot_check(driver)
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
                            time.sleep(2+2*random.random())
                            details = try_Details(driver)
                            if (details == None):
                                continue
                            keyList, valueList = get_Details(details)
            
                            robot_check(driver)
                            # Comments/Description section
                            try:
                                driver.find_element_by_class_name('view-more').click()

                                description = driver.find_element_by_class_name('view-more-target').text
                                description = ' '.join(description.replace('\n',' ').split())
                
                            except seleniumException.ElementNotVisibleException as e:
                                description = driver.find_element_by_class_name('view-more-target').text
                                description = ' '.join(description.replace('\n',' ').split())
            
                            except: #seleniumException.NoSuchElementException as e:
                                description = ''
                            
                            keyList.append('Description')
                            valueList.append(description)

                            # Specifications
                            time.sleep(2+2*random.random())
                            click = try_id_click(driver,'specifications-tab')
                            if (click == None):
                                continue
         
                            click = try_class_click(driver,'features-toggle-collapse')
                            if (click == None):
                                continue

                            robot_check(driver)
                            try:
                                wait_to_expand = driver.find_element_by_css_selector('.multi-collapse.collapse.show')
                            except:
                                continue

                            specifications = try_id(driver,'specifications')
                            if (specifications == None):
                                continue
                            key, values = get_Specifications(specifications)
                            keyList += key
                            valueList += values

                            suburb, state, postcode = get_Location(driver)

                            keyList += ['Suburb', 'State', 'Postcode','Category','SubType', 'Make', 'Model']
                            valueList += [suburb, state, postcode,category, subCategory, bikeMake, bikeModel]
                            

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
                            if (((pageId % 10) == 0) & (linkIdx == len(bikeLinks)-1)):
                                write_Data_File(dictionary=datadict, filename=filename)
                   
                    robot_check(driver)
                    # reset the model filter
                    driver = try_get(driver,"https://www.bikesales.com.au/bikes/"+category+"/"+bikeType+"/"+bikeMake+"/?Sort=Price")
                    modelList = getModelList(driver, offset)
                    if modelList == None:
                        continue

                write_Data_File(dictionary=datadict, filename=filename)
                # reset the make filter
                
                print ('  end of make filter')
                robot_check(driver)
                driver = try_get(driver,"https://www.bikesales.com.au/bikes/"+category+"/"+bikeType+"/?Sort=Price")
                    
                makeList = try_class_name_selectors(driver, 'aspect', 2-offset)##2
                if makeList == None:
                    continue

                makeList = filter_list(makeList)
                
            write_Data_File(dictionary=datadict, filename=filename)
            # reset subtype
            print ('end of subtype filter')
            driver = try_get(driver,"https://www.bikesales.com.au/bikes/"+category+"/?Sort=Price")
                
            subTypes = get_subtypes(driver)
            
            if subTypes == None:
                    continue

            subTypes = filter_list(subTypes)
            if category == 'Racing': 
                bikeType = ''
                offset = 1

        # reset the category
        robot_check(driver)
        driver.get(sortedBikes)
        categoryList  = get_category_list(driver)
        #category_block = driver.find_elements_by_class_name('aspect-navigation-element')
        #categoryList = category_block[0].find_elements_by_class_name("facet-visible")
            
        # Write the subtype to file
        write_Data_File(dictionary=datadict, filename=filename)

    #driver.close()

    #write_Data_File(dictionary=datadict, filename=filename)

    