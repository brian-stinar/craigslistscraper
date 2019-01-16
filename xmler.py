#!/usr/bin/python
from lxml import etree

class Xmler:
    def buildXmlHeader(self):
        self.document = etree.Element('opml', version="1.0")
        title = etree.SubElement(self.document, 'title')
        title.text = "Subscriptions of Brian J. Stinar from Inoreader [https://www.inoreader.com]"
        body = etree.SubElement(self.document, 'body')
        outline = etree.SubElement(body, 'outline', text="Craigslist", texts="Craiglist")
    
    def printXml(self): 
        s = etree.tostring(self.document, pretty_print=True)    
        print s

    def addOutlineChild(self, outlineChild):
        # Get the first child of the body, which is the first outline element
        outlineParent = self.document[1][0]

        # Add our outline child as the last element there
        outlineParent.insert(len(outlineChild), outlineChild)


if __name__ == "__main__":
        xmler = Xmler()
        xmler.buildXmlHeader()
        #xmler.printXml()

        outlineChild = etree.Element('outline', firstname="Brian", lastname="Stinar")        
        xmler.addOutlineChild(outlineChild)

        xmler.printXml()        
