from bs4 import BeautifulSoup,NavigableString,Tag
from collections import OrderedDict

class BlockFusion():
	def __init__(self, maxChar, noLines):
		self.threshold = 0.4
		self.maxChar = maxChar
		self.noLines = noLines
	def getWrappedLines(self, textStr):    
		wrappedTextList = []
		# Assuming wmax = 80
		# Will be managed from config in future
		if len(textStr) > self.maxChar:
			tokenList  = [token for token in textStr.split() if token.strip()]
			# Avg 13 token per line
			# Will be managed from config in future
			# 14 = 13 + 1
			breakPoints = len(tokenList)/self.noLines
			if breakPoints > 0:
				for i in range(breakPoints):
					line = ""
					line += (" ").join(tokenList[self.noLines*i:self.noLines*(i+1)])
					if line:
						wrappedTextList.append(line.encode("utf-8").decode("ascii","ignore"))
				line = (" ").join(tokenList[self.noLines*breakPoints:])
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
		<= self.threshold):
			return True
		return False

	def fuseTwoBlocks(self, prevBlock, currBlock):
		fusedBlock = {}
		data = prevBlock["data"] + " ||" + currBlock["data"]
		textDensity = prevBlock["textDensity"] + currBlock["textDensity"]
		blockId = prevBlock["blockId"] + " | " + currBlock["blockId"]
		fusedBlock["data"] = data
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
			if docWithTokenCount['tokenCount'] > 30:
				docWithTokenCount['label'] = 'main'
			else:
				docWithTokenCount['label'] = 'boiler plate'
		 	fusedDocsWithTokenCount.append(docWithTokenCount)
		return fusedDocsWithTokenCount

	def stripEndChars(self, token):
		return token.strip(",").strip(".").strip("-").strip(" ").strip(":")

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
		return fusedDocsWithTokenCount