#!/usr/bin/python
# coding=utf-8   # Not always the best, but I wanted some cool unicode to describe the relationships
#
# Noventum Custom Software
# Brian J. Stinar 
# Craigslist Lead Generator Generator
#
# Country
#    |
#    ▼
# State (Potentially lowest level)
#    |
#    |  (optional region, like NY metro area) 
#    ▼   
# (Optional City, if present then the lowest level)
#
# Cities are NORMALLY the lowest level, but not always (Rhode Island, Puerto Rico.) 
# For right now, I'm only concerned with U.S. areas. This may change outside the U.S.

from BeautifulSoup import BeautifulSoup
import urllib2
#import mysql # Not yet, my precious
from random import shuffle # Pick a card, any card
import traceback
import random
import time
import json
import sys

class CraigslistGrabber:
    development = 1 
    stateLinks = {} 
    cityLinks = {}    
    #careAboutCategories = ['web-html-info-design', 
    #    'software-qa-dba-etc', 
    #    'systems-networking',]

    careAboutCategories = {'web-html-info-design' : "sof",
        "web-html-info-design goes" : "web", 
        "systems-networking" : "sad"
    }
    
    # software-qa-dba goes to sof 
    # web-html-info-design goes to web
    # systems-networking goes to sad 
    # ...
    # therefore, this should be a map, and not a list 

    totalResults = {}
    justUrls = []

    # Make this populate a states table. States don't change that often
    def downloadStates(self):
        page = urllib2.urlopen('https://albuquerque.craigslist.org/', timeout=10)
        soup = BeautifulSoup(page)
        soup.prettify()
        # Save this as a file, if in development mode
        if (self.developement):
            self.writeCraigslistToFile(str (soup), 'outfile.craigslist')
        self.craigslistPage = soup

    def writeCraigslistToFile(self, craigslistHomePage, fileName):
        outfile = open(fileName, "w")
        outfile.write(craigslistHomePage)
        outfile.close()

    def populateStateUrls(self):
        # Open the cached file, if in development mode
        if (self.development):
            inputfile = open('outfile.craigslist', 'r')
            self.craigslistPage = inputfile.read()
            inputfile.close()
        
        else: 
            self.downloadStates() # Not sure about this yet. Need to test. Should work.

        soup = BeautifulSoup(self.craigslistPage) 
        h5s = soup.findAll('h5')

        for element in h5s: # Probably abstract this portion to grab whatever section is passed as a parameter
            if "us states" in element: # Can easily be changed to whatever
                links = element.findNext('ul').findAll('a')
                for link in links[:-1]: # Last one is ...more junk
                    #print link.string
                    href = "https:" + link['href'] + '/?lang=en' # Make sure we only deal with English results, for now
                    self.stateLinks[link.text] = href


    def populateCity(self, state):
        print self.stateLinks[state]
        page = urllib2.urlopen(self.stateLinks[state], timeout=10)
        redirectedUrl = page.geturl() # Thanks Puerto Rican craigslist... They use 302s, which I don't handle by default
        print redirectedUrl # This still doesn't worl
        #page = urllib2.urlopen(redirectedUrl, timeout=10)
        self.stateLinks[state] = redirectedUrl 
        soup = BeautifulSoup(page)
        soup.prettify()

        cities = []
        if self.areThereCities(soup):
            #uls = soup.findAll('ul', class_="geo-site-list") # I cannot get this class selector to work here...
            uls = soup.findAll('ul')
            for ul in uls:
                if "geo-site-list" in str(ul): # I'd MUCH rather have the above selector working.
                    links = ul.findAll('a')
                    for link in links:
                        text = link['href']
                        if "http" not in text:
                            text = "https:" + text
                        cities.append(text)
                
        else:
            cities = [self.stateLinks[state][:-1]] # Weird extra / on single-city states...? 
            # This only works for the non-divided cities. For those, I require additional logic

        cityLinks = {}
        for city in cities:
            categoryLinks = []
            for category in self.careAboutCategories: 
                link = city + "/d/" + category + "/search/" + self.careAboutCategories[category] + "/?lang=en&cc=us"
                categoryLinks.append(link)
                self.justUrls.append(link)
            cityLinks[city] = categoryLinks
        self.totalResults[state] = {self.stateLinks[state] : cityLinks}


    def populateCityLinks(self):
        keys = list(self.stateLinks.keys()) # Mix it up to avoid bot detection
        shuffle(keys)

        #There's still something wrong with this...?
        #keys = ['connecticut', 'virginia', 'indiana', 'new jersey', 'maryland', 'washington']

        badKeys = ['puerto rico'] # Jacked up redirects on Spanish speaking ones, maybe I'll handle this for phase 2

        counter = 0 
        for state in keys:
            if state in badKeys:
                continue
            print str(counter) + "  - opening " + state
            self.populateCity(state)

            counter = counter + 1
            time.sleep(random.uniform(2.0, 5.0)) # Add some random delays to mess up Craigslist's (probable) rate limiter

            if counter >= 2:
                return        


    # Some states are listings by themselves, while others contain listings of cities (New Mexico) or neighborhoods (NY)
    def areThereCities(self, soup):
        # If it contains "geo-site-list" then that's the descriptor for the city list
        if 'geo-site-list' in str(soup):
            return True

        for category in self.careAboutCategories:
            if category in str(soup):
                return False

        print("ERROR - this function is not fully spec'd out for " + str(soup))
        traceback.print_stack()
        

    def __readCraigslistFromFile(self, fileName):
        print "hello world" 
    
if __name__ == "__main__": 
    craigslistGrabber = CraigslistGrabber()
    craigslistGrabber.populateStateUrls()
    craigslistGrabber.populateCityLinks()
    '''for state in craigslistGrabber.totalResults:
        print state
        for city in craigslistGrabber.totalResults[state]:
            print "\t\t" + city
            for category in craigslistGrabber.careAboutCategories:
                print "\t\t\t" + city + "/d/" + category + "/search/web"
    '''
    
    prettyJson = json.dumps(craigslistGrabber.totalResults, sort_keys=True, indent=4, separators=(',', ': '))
    outfile = open('everything.json', 'w')
    outfile.write(prettyJson) 

    prettyJson = json.dumps(craigslistGrabber.justUrls, sort_keys=True, indent=4, separators=(',', ': '))
    outfile = open('justUrls.json', 'w')
    outfile.write(prettyJson)
