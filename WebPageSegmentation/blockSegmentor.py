from bs4 import BeautifulSoup,NavigableString,Tag
from collections import OrderedDict
from pymongo import MongoClient


class BlockSegmentor():
	def __init__(self):
		self.restrictedTags = ["script","noscript","style","meta"]
		

	def getSoup(self, str):
		return BeautifulSoup(str,"html.parser")

	def getBlockSegments(self, tag, blockStack):
		for child in tag.children:
			if child.name is not None and child.name not in self.restrictedTags:
				blockStack.append(child)
				self.getBlockSegments(child,blockStack)
			elif isinstance(child, NavigableString):
				if self.isSurroundedByTags(child):
					if str(child.encode("utf-8")).strip():
						if child not in blockStack:
							blockStack.append(child)
				elif self.isLastNavigableString(child):
					if str(child.encode("utf-8")).strip():
						if child not in blockStack:
							blockStack.append(child)
		return None

	
	def isSurroundedByTags(self, navStr):
		prevSibling = ""
		nextSibling = ""
		if navStr.previous_sibling:
			prevSibling = str(navStr.previous_sibling.encode("utf-8"))
		if navStr.next_sibling:
			nextSibling = str(navStr.next_sibling.encode("utf-8"))
		if ((prevSibling.endswith(">")) and (nextSibling.startswith("<"))):
			return True
		return False

	def isLastNavigableString(self, navStr):
		prevSibling = ""
		if navStr.previous_sibling:
			prevSibling = str(navStr.previous_sibling.encode("utf-8"))
		if (prevSibling.endswith(">")):
			return True
		return False

	def getAtomicBlocks(self, blkStack):
		blockDict = {}
		for i,eachBlock in enumerate(blkStack):
			blockName = eachBlock.name
			eachBlockString = str(eachBlock.encode("utf-8").decode("ascii","ignore"))
			key = "B" + str(i)
			if ("<" in eachBlockString) and blockName:
				val = self.getSoup("<" + eachBlockString.split("<")[1].strip() + "</" + blockName + ">")
			elif ("<" not in eachBlockString.strip()):
				val = self.getSoup(eachBlockString.strip())
			blockDict[key] = val
		# SORTING On Keys
		orderedBlockDict = OrderedDict(sorted(blockDict.items(), key=lambda x:int(x[0].strip("B"))))
		return orderedBlockDict

	

