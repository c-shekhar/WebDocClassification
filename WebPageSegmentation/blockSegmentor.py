from bs4 import BeautifulSoup,NavigableString,Tag
from collections import OrderedDict
from pymongo import MongoClient


class BlockSegmentor():
	def __init__(self):
		self.restrictedTags = ["script","noscript","style","meta"]
		self.blockCounter = -1
	
	def getBlockId(self):
		self.blockCounter += 1
		return "B"+str(self.blockCounter)

	def getSoup(self, str):
		return BeautifulSoup(str,"html.parser")

	def getBlock(self):
		block = {}
		block['id'] = self.getBlockId()
		block['text'] = []
		block['a'] = []
		return block

	def addTagTextToBlock(self, block, tag):
		#appending anchor text to block['anchor text']
		if tag.name == 'a':
			tag = tag.getText()
			block['a'].append(tag.strip())
		# appending anchor text and navigable string to block['text']
		block['text'].append(tag.strip())

	def isPreviousChildTextOrAnchor(self, tag):
		if tag.previous_sibling:
			if tag.previous_sibling.name == "a" or isinstance(tag.previous_sibling, NavigableString):
				return True
		return False

	def getBlockSegments(self, tag, blockStack):
		prev = 0
		currBlock = {}
		for child in tag.children:
			if isinstance(child, NavigableString) or child.name == "a":
				if self.isPreviousChildTextOrAnchor(child):
					self.addTagTextToBlock(currBlock, child)
				else:
					newBlock = self.getBlock()
					self.addTagTextToBlock(newBlock, child)
					currBlock = newBlock
			elif child.name is not None and child.name not in self.restrictedTags:
				if currBlock:
					blockStack.append(currBlock)
					currBlock = {}
				self.getBlockSegments(child,blockStack)
			
		return None

	# merging list of text and anchor text
	def getStructuredBlocks(self, blkStack):
		for eachBlock in blkStack:
			eachBlock['text'] = " ".join([text.encode('utf8').decode('ascii','ignore') for text in eachBlock['text'] if text.strip()])
			eachBlock['a'] = " ".join([anchorText.encode('utf8').decode('ascii', 'ignore') for anchorText in eachBlock['a']  if anchorText.strip()])
		#SORTING On Keys
		orderedBlockDict = sorted(blkStack, key=lambda x: x['id'])
		return orderedBlockDict
