import requests
from bs4 import BeautifulSoup,NavigableString,Tag
from collections import OrderedDict

class BlockSegmentor():
	def __init__(self):
		self.restrictedTags = ["script","noscript","style"]

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

	def getAtomicBlocks(self, blkStack):
		blockDict = {}
		for i,eachBlock in enumerate(blkStack):
			blockName = eachBlock.name
			eachBlockString = str(eachBlock.encode("utf-8").decode("ascii","ignore"))
			# print eachBlockString
			key = "B" + str(i)
			if ("<" in eachBlockString) and blockName:
				val = self.getSoup("<" + eachBlockString.split("<")[1].strip() + "</" + blockName + ">")
			elif ("<" not in eachBlockString.strip()):
				val = self.getSoup(eachBlockString.strip())
			if val not in blockDict.values():
				blockDict[key] = val
		# SORTING On Keys
		orderedBlockDict = OrderedDict(sorted(blockDict.items(), key=lambda x:int(x[0].strip("B"))))
		return orderedBlockDict

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

	def getDoc(self, atomicBlockDict):
		for blockId, block in atomicBlockDict.iteritems():
			blockWithDensity = {}
			blockWithDensity["id"] = blockId
			blockText = block.get_text()
			wrappedText,tokenCount = self.getWrappedLines(blockText)
			print blockText,"\n",self.getTextDensity(wrappedText,tokenCount)
			# print blockText
			# print blockText.strip().split("\n")
	
	def getWrappedLines(self, textStr):    
		wrappedTextList = []
		tokenCount = 0
		# Assuming wmax = 80
		# Will be managed from config in future
		if len(textStr) > 80:
			tokenList  = [token for token in textStr.split() if token.strip()]
			tokenCount = len(tokenList)
			# Avg 13 token per line
			# Will be managed from config in future
			# 14 = 13 + 1
			breakPoints = [i * 14 for i in range(len(tokenList))]
			if len(tokenList) > 13:
				for i in breakPoints:
					line = ""
					line += (" ").join(tokenList[i:i+13])
					if line:
						wrappedTextList.append(line.encode("utf-8").decode("ascii","ignore"))
					i += 13
		else:
			tokenCount = len(textStr.split())
			wrappedTextList.append(textStr)
		return wrappedTextList,tokenCount

	def getTextDensity(self, wrappedTextList, tokenCount):
		textDensity = 0
		if len(wrappedTextList) <= 1:
			return textDensity
		linesCount = len(wrappedTextList) - 1
		textDensity = tokenCount / float(linesCount)
		return textDensity

if __name__ == '__main__':
	url = "http://gadgets.ndtv.com/transportation/news/self-driving-car-prototypes-need-less-human-help-data-show-1655343"
	# url = "http://timesofindia.indiatimes.com/business/india-business/market-moves-up-ahead-of-rbi-policy-logs-smart-weekly-gain/articleshow/56955406.cms"
	# url = "http://timesofindia.indiatimes.com/business/india-business/coal-ministry-to-allow-commercial-mining-by-private-companies/articleshow/56940490.cms"
	htmlDoc = requests.get(url).text
	soup = BeautifulSoup(htmlDoc,"html.parser")
	blockStack = []
	bodyTag = soup.body
	blockSegmentorObject = BlockSegmentor()
	blockSegmentorObject.getBlockSegments(bodyTag,blockStack)
	blockDict = blockSegmentorObject.getAtomicBlocks(blockStack)
	blockSegmentorObject.getDoc(blockDict)
	# for k,v in blockDict.iteritems():
	#     print k,v
		# print v.get_text()