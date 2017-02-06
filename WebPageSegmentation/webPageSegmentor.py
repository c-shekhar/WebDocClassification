import requests
from bs4 import BeautifulSoup,NavigableString
from collections import OrderedDict

class BlockSegmentor():
	def __init__(self):
		self.restrictedTags = ["script","noscript","style"]

	def getBlockSegments(self, tag, blockStack):
		for child in tag.children:
			if child.name is not None and child.name not in self.restrictedTags:
				blockStack.append(child)
				self.getBlockSegments(child,blockStack)
			elif self.isInstanceOf(child, NavigableString):
				if str(child.encode("utf-8").decode("ascii","ignore").strip()):	
					blockStack.append(child)
		return None

	def getAtomicBlocks(self, blkStack):
		blockDict = {}
		for i,eachBlock in enumerate(blkStack):
			blockName = eachBlock.name
			eachBlockString = str(eachBlock.encode("utf-8").decode("ascii","ignore"))
			key = "B" + str(i)
			if ("<" not in eachBlockString.strip()):
				val = eachBlockString.strip()
			else:
				val = "<" + eachBlockString.split("<")[1].strip() + "</" + blockName + ">"
			blockDict[key] = val
			# # val = eachBlockString.split("<")[1]
			# # tag = BeautifulSoup("","html.parser").new_tag(blockName)
			# # tag.append(val)
			# blockDict[key] = tag
		# SORTING On Keys
		orderedBlockDict = OrderedDict(sorted(blockDict.items(), key=lambda x:int(x[0].strip("B"))))
		return orderedBlockDict


	def isInstanceOf(self, tag, tagType):
		if type(tag) == NavigableString:
			return True
		return False

	def getTextDensity(self, atomicBlock):
		pass

if __name__ == '__main__':
	# url = "http://gadgets.ndtv.com/transportation/news/self-driving-car-prototypes-need-less-human-help-data-show-1655343"
	# url = "http://timesofindia.indiatimes.com/business/india-business/market-moves-up-ahead-of-rbi-policy-logs-smart-weekly-gain/articleshow/56955406.cms"
	url = "http://timesofindia.indiatimes.com/business/india-business/coal-ministry-to-allow-commercial-mining-by-private-companies/articleshow/56940490.cms"
	htmlDoc = requests.get(url).text
	soup = BeautifulSoup(htmlDoc,"html.parser")
	blockStack = []
	bodyTag = soup.body
	blockSegmentorObject = BlockSegmentor()
	blockSegmentorObject.getBlockSegments(bodyTag,blockStack)
	blockDict = blockSegmentorObject.getAtomicBlocks(blockStack)
	for k,v in blockDict.iteritems():
		print k,v