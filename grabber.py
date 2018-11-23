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
import re
import os
import pprint

class CraigslistGrabber:
    development = 1 
    stateLinks = {} 
    cityLinks = {}    
    
    careAboutTerms = ["business / mgmt", "software / qa / dba", "systems / network", "web / info design"]
    careAboutCategories = {}     

    totalResults = {}
    justUrls = []

    def inferCategories(self):
        # Load a URL, and then iterate through each category - doesn't matter which one - www.craigslist.com works
        page = urllib2.urlopen('https://www.craigslist.org')
        soup = BeautifulSoup(page)
        soup.prettify()

        spans = soup.findAll("span")
        for span in spans: 
            if span.text in self.careAboutTerms:
                href = span.parent.get('href')
                dashes = href.split('/')[2]
                threeLetters = href.split('/')[-1]
                self.careAboutCategories[str(dashes)] = str(threeLetters)

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
                    #href = "https:" + link['href'] + '/?lang=en' # Make sure we only deal with English results, for now
                    href = "https:" + link['href']
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
                #link = city + "/d/" + category + "/search/" + self.careAboutCategories[category] + "/?lang=en&cc=us"
                #link = city + "/search/" + self.careAboutCategories[category] + "/?lang=en&cc=us"
                link = city + "/search/" + self.careAboutCategories[category]
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
            self.populateCity(state)

            counter = counter + 1
            time.sleep(random.uniform(2.0, 5.0)) # Add some random delays to mess up Craigslist's (probable) rate limiter

            if counter >= 5:
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
 
    def printXml(self, xmlFileName):       
        
        if not self.totalResults:
            print "Error - self.totalResults does not exist!"
            sys.exit(1)

        with open(xmlFileName, 'w') as outfile:
            header = """<?xml version="1.0" encoding="UTF-8"?>
<opml version="1.0">
    <head>
        <title>Subscriptions of Brian J. Stinar from Inoreader [https://www.inoreader.com]</title>
    </head>
    <body>
        <outline text =\"Craigslist\" texts=\"Craigslist\"/>
"""
            outfile.write(header)

            pp = pprint.PrettyPrinter(indent=4)

            for state in self.totalResults:
                print "state = " + state
                counter = 0
                if counter > 3: 
                    break
                print "self.totalResults[state] = ",
                pp.pprint(self.totalResults[state]) 
                for category in self.totalResults[state]:
                    print "\tcategory = " + category 
                    for city in self.totalResults[state][category]: 
                        print "\t\tcity = " + city
                        print("self.totalResults[state] = "),
                        pp.pprint(self.totalResults[state])
                        print ("state = " + str(state))
                        print ("category = " + str(category))
                        print("self.totalResults[state][state][category] = "), 
                        pp.pprint(self.totalResults[state][category])

                        for listing in self.totalResults[state][category][city]:
                            print "\t\t\tlisting = " + str(listing)
                            cityString = ""
                            if len(city) >= 8: 
                                cityString = city[8:].split('.')[0]
                            categorySmall = str(listing.split('/')[-1])
                            outfile.write("\t\t\t\t<outline text=\"" + state + " " + cityString + " " + categorySmall  + "\" title=\"" + state + " " + cityString + " " + categorySmall +  "\" type=\"rss\" xmlUrl=\"" + listing + "?format=rss\" htmlUrl=\"" + listing + "?format=rss\"\>\n")

        with open(xmlFileName, 'rb+') as filehandle:
            filehandle.seek(-1, os.SEEK_END)
            filehandle.truncate()
        
        with open(xmlFileName, 'a') as outfile:
            outfile.write("</outline>\n")
            outfile.write("\t</body>\n")
            outfile.write("</opml>") 

    def __readCraigslistFromFile(self, fileName):
        print "hello world" 
    
if __name__ == "__main__": 

    craigslistGrabber = CraigslistGrabber() # Consider a constructor for this - getting complicated enough

    if len(sys.argv) == 1:
        craigslistGrabber.inferCategories() 
        craigslistGrabber.populateStateUrls()
        craigslistGrabber.populateCityLinks()
        
        # Make a method that takes this json file as a constructor for the object, then I don't have to go through
        # all of the population each time
        prettyJson = json.dumps(craigslistGrabber.totalResults, sort_keys=True, indent=4, separators=(',', ': '))
        outfile = open('everything.json', 'w')
        outfile.write(prettyJson) 

        prettyJson = json.dumps(craigslistGrabber.justUrls, sort_keys=True, indent=4, separators=(',', ': '))
        outfile = open('justUrls.json', 'w')
        outfile.write(prettyJson)

    if len(sys.argv) == 2:
        with open(sys.argv[1], 'r') as inputFile:
            content = inputFile.read()
            craigslistGrabber.totalResults = json.loads(content)
            craigslistGrabber.printXml("out.xml")
