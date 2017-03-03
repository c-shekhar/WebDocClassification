import requests
from bs4 import BeautifulSoup,NavigableString,Tag
from collections import OrderedDict
from pymongo import MongoClient

hostName = "localhost"
portName = 27017
clientObject = MongoClient(hostName,portName)
dbName = "webDocClassification"
dbObject = clientObject[dbName]
coll = "Data"

class BlockSegmentor():
	def __init__(self):
		self.restrictedTags = ["script","noscript","style","meta"]
		self.threhold = 0.4

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
		docs = []
		for blockId, block in atomicBlockDict.iteritems():
			metaDict = {}
			blockText = block.get_text()
			wrappedText = self.getWrappedLines(blockText)
			blockTextDensity = self.getTextDensity(wrappedText)
			metaDict['blockId'] = blockId
			metaDict['data'] = blockText
			metaDict['textDensity'] = blockTextDensity
			docs.append(metaDict)
		fusedDocs = self.getFusedTextBlocks(docs)
		fusedDocsWithTokenCount = self.addTokenCount(fusedDocs)
		# print fusedDocsWithTokenCount
		return fusedDocsWithTokenCount

	def getWrappedLines(self, textStr):    
		wrappedTextList = []
		# Assuming wmax = 80
		# Will be managed from config in future
		if len(textStr) > 80:
			tokenList  = [token for token in textStr.split() if token.strip()]
			# Avg 13 token per line
			# Will be managed from config in future
			# 14 = 13 + 1
			breakPoints = [i * 13 for i in range(len(tokenList))]
			if len(tokenList) > 13:
				for i in breakPoints:
					line = ""
					line += (" ").join(tokenList[i:i+13])
					if line:
						wrappedTextList.append(line.encode("utf-8").decode("ascii","ignore"))
			else:
				lineText = (" ").join([self.stripEndChars(eachToken) for eachToken in textStr.split()])
				wrappedTextList.append(lineText)
		else:
			lineText = (" ").join([self.stripEndChars(eachToken) for eachToken in textStr.split()])
			wrappedTextList.append(lineText)
		return wrappedTextList

	def getTextDensity(self, wrappedTextList):
		tDashBx = []
		textDensity = 0
		# -1 is done to exclude last line's effect
		for i in range(len(wrappedTextList)-1):
			tokenList = wrappedTextList[i].split()
			tokenList = [self.stripEndChars(token) for token in tokenList]
			tDashBx.append(tokenList)
		flattDashBx = [item for sublist in tDashBx for item in sublist]
		if len(wrappedTextList) > 1:
			textDensity = float(len(flattDashBx))/(len(wrappedTextList)-1)
		elif len(wrappedTextList) == 1:
			singleLineTokens = wrappedTextList[0].split()
			singleLineTokens = [self.stripEndChars(token) for token in singleLineTokens]
			textDensity = float(len(singleLineTokens))
		return textDensity
		
	def getFusedTextBlocks(self, blocksList):
		blocks = blocksList
		nonEmptyBlocks = [eachBlock for eachBlock in blocks if eachBlock["data"]]
		toLoop = True
		listToIterate = nonEmptyBlocks[:]
		tempBlock = {
						'data' : '',
						'textDensity' : 0,
						'blockId' : ''
					}
		while toLoop:
			toLoop = False
			endIndex = len(listToIterate) - 1
			i = 1
			while (i < endIndex):
				if (self.checkThreeBlockFusion(listToIterate[i-1],listToIterate[i],listToIterate[i+1])):
					fusedBlock = self.fuseThreeBlocks(listToIterate[i-1],listToIterate[i],listToIterate[i+1])
					listToIterate[i-1] = tempBlock
					listToIterate[i] = tempBlock
					listToIterate[i+1] = fusedBlock
					# Skipping block i+1
					toLoop = True 
					i = i + 1
				elif (self.checkTwoBlockFusion(listToIterate[i-1],listToIterate[i])):
					fusedBlock = self.fuseTwoBlocks(listToIterate[i-1],listToIterate[i])
					listToIterate[i-1] = tempBlock
					listToIterate[i] = fusedBlock
					toLoop = True
				i = i + 1
			listToIterate = [eachBlock for eachBlock in listToIterate if eachBlock["textDensity"] > 0]
		return listToIterate
	
	def checkThreeBlockFusion(self, prevBlock, currBlock, nextBlock):
		if (prevBlock["textDensity"] == nextBlock["textDensity"])\
		and (currBlock["textDensity"] < prevBlock["textDensity"]):
			return True
		return False

	def checkTwoBlockFusion(self, prevBlock, currBlock):
		if (self.getTextDensityDelta(prevBlock,currBlock)\
		<= self.threhold):
			return True
		return False

	def fuseTwoBlocks(self, prevBlock, currBlock):
		fusedBlock = {}
		data = prevBlock["data"] + " ||" + currBlock["data"]
		textDensity = prevBlock["textDensity"] + currBlock["textDensity"]
		blockId = prevBlock["blockId"] + " | " + currBlock["blockId"]
		getFusedTextBlocksock["data"] = data
		fusedBlock["textDensity"] = textDensity
		fusedBlock["blockId"] = blockId
		return fusedBlock

	def fuseThreeBlocks(self, prevBlock, currBlock, nextBlock):
		fusedBlock = {}
		data = prevBlock["data"] + " ||" + currBlock["data"] + " ||" + nextBlock["data"]
		textDensity = prevBlock["textDensity"] + currBlock["textDensity"] + nextBlock["textDensity"]
		blockId = prevBlock["blockId"] + " | " + currBlock["blockId"] + " | " + nextBlock["blockId"]
		fusedBlock["data"] = data
		fusedBlock["textDensity"] = textDensity
		fusedBlock["blockId"] = blockId
		return fusedBlock

	def getTextDensityDelta(self, prevBlock, currBlock):
		# return abs(prevBlock["textDensity"] - currBlock["textDensity"])
		numrtr = abs(prevBlock["textDensity"] - currBlock["textDensity"])
		denomtr = max(prevBlock["textDensity"], currBlock["textDensity"])
		if denomtr == 0:
			return 0
		return numrtr/denomtr

	def addTokenCount(self, fusedDocs):
		fusedDocsWithTokenCount = []
		for eachDoc in fusedDocs:
			docWithTokenCount = eachDoc
			data = eachDoc['data']
			docWithTokenCount['tokenCount'] = len(data.split())
		 	fusedDocsWithTokenCount.append(docWithTokenCount)
		return fusedDocsWithTokenCount

	def stripEndChars(self, token):
		return token.strip(",").strip(".").strip("-").strip(" ").strip(":")

def runner(url):
	htmlDoc = requests.get(url).text
	soup = BeautifulSoup(htmlDoc,"html.parser")
	blockStack = []
	bodyTag = soup.body
	blockSegmentorObject = BlockSegmentor()
	blockSegmentorObject.getBlockSegments(bodyTag,blockStack)
	atomicBlockDict = blockSegmentorObject.getAtomicBlocks(blockStack)
	return blockSegmentorObject.getDoc(atomicBlockDict)

if __name__ == '__main__':
	url1 = "http://gadgets.ndtv.com/transportation/news/self-driving-car-prototypes-need-less-human-help-data-show-1655343"
	url2 = "http://timesofindia.indiatimes.com/business/india-business/market-moves-up-ahead-of-rbi-policy-logs-smart-weekly-gain/articleshow/56955406.cms"
	url3 = "http://timesofindia.indiatimes.com/business/india-business/coal-ministry-to-allow-commercial-mining-by-private-companies/articleshow/56940490.cms"
	for url in [url1,url2,url3]:
		doc = {}
		doc["_id"] = url
		doc["blocks"] = runner(url)
		try:
			dbObject[coll].insert(doc)

		except Exception as e:
			print e
		# break