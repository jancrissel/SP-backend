###########################################################################################################################################
#	AUTHOR: DE RAMOS, Jan Crissel O.																									  #
#			2013-08999																													  #
#	PROGRAM DESCRIPTION: This program makes use of multiple spiders to crawl on different web sites. The scraped data will then be stored #
#						 on separate CSV files, one for each spider. 																	  #
###########################################################################################################################################

import scrapy
from scrapy.spiders import Spider
from scrapy.crawler import CrawlerProcess
from scrapy.selector import Selector
from run_scrapy.items import RunScrapyItem
import string
import MySQLdb

items = []

#############################################################################
# ----- SCRAPES DATA FROM DIFFERENT DOMAINS AND CALLS OUTPUTFILE FUNC ----- #
#############################################################################
class InquirerSpider(Spider):
	name = "Inquirer"
	allowed_domains = ["inquirer.net"]
	start_urls = ["https://www.inquirer.net/latest-stories"]

	def parse(self, response):
			hxs = Selector(response)
			titles = hxs.xpath("//h2")
			data = []
			titleList = []
			word = ""
			wordsToSplit = ""
			listOfWords = []
			news = {}
			wordFreq = 0																							   	# Hashmap of news titles

			for titles in titles:
				listOfWords = []
				item = RunScrapyItem()
				item ["author"] = "Philippine Daily Inquirer"
				item ["title"] = titles.xpath("a/text()").extract()													# Extracts Title 
				if len(item["title"]) != 0:																			# If Title field is NOT NULL,				
					item ["title"] = item ["title"][0].encode('utf-8')												# Then convert Unicode (1st element) to UTF-8
				if type(item["title"]) == list:																		# If Title field is NULL,
					item["title"] = None																			# Ignore
				
				wordsToSplit = str(titles.xpath("a/text()").extract()) 
				word = [word.strip(string.punctuation) for word in wordsToSplit.split()]							# Splits strings into tokens removing punctuation marks	
				wordFreq = len(word)
				listOfWords.append(word) 																			# Puts tokenized strings into list

				##### BAG OF WORDS / CATEGORIZATION #####
				#categorizeNews(listOfWords, wordFreq)


				item ["link"] = titles.xpath("a/@href").extract()													# Extracts Link 
				itemConverter(item,"link")																			# Checks if valid type or if not empty, then converts it to utf-8
				item ["image"] = "NULL"																				# Stores items in image field as null

				if item["link"] != None:
					request = scrapy.Request(item["link"], callback=self.parsepage2)
					request.meta["item"] = item
					request.meta["link"] = item["link"]
					yield request				
			#for item in items:
			#	titleList.append(item["title"]) 																	# Appends list of titles into new list			

			#for item in titleList:
				#print(item)
				#print(listOfWords)																					# Prints list of tokenized words	
			#return items

	def parsepage2(self,response):
		item = response.meta["item"]
		hxs = Selector(response)
		parts = hxs.xpath("//div[@id='outbrain_readmore']")

		for parts in parts:
			if len(parts.xpath("p/text()")) < 1:
				item["intro"] = parts.xpath("div/p/text()")[0].extract().encode('utf-8')	 
			else: 
				item["intro"] = parts.xpath("p/text()")[0].extract().encode('utf-8')	
		items.append(item)																							# Appends to Items
		connectDB(item, "Inquirer")
					
class PCAARRDSpider(Spider):
	name = "PCAARRD"
	allowed_domains = ["pcaarrd.dost.gov.ph"]
	start_urls = ["http://www.pcaarrd.dost.gov.ph/home/portal/index.php/2015-02-26-06-57-10/news-archive"]
	
	def parse(self, response):
		hxs = Selector(response)
		titles = hxs.xpath("//li")
		text_items = []
		titleList = []
		word = ""
		wordsToSplit = ""
		listOfWords = []
		news = {} #hashmap of news titles

		for titles in titles:
			item = RunScrapyItem()
			item ["author"] = "DOST-PCAARRD"				
			item ["title"] = titles.xpath("h2[@itemprop='name']/a/text()").extract()
			itemConverter(item, "title")
			wordsToSplit = str(titles.xpath("h2[@itemprop='name']/a/text()").extract()) 
			word = [word.strip(string.punctuation) for word in wordsToSplit.split()]
			#splits strings into tokens removing punctuation marks	
			listOfWords.append(word) #puts tokenized strings into list

			#BAG OF WORDS / HASH MAP PER TITLE
	
			item ["link"] = titles.xpath("h2[@itemprop='name']/a/@href").extract()
			linkConverter(item, "link", "http://www.pcaarrd.dost.gov.ph")			
			item ["image"] = titles.xpath("div/p/img[@class='caption']/@src").extract()
			linkConverter(item, "image", "www.pcaarrd.dost.gov.ph")
			if item["image"] == None:
				item ["image"] = "NULL" 

			if item ["link"] != None:
				request = scrapy.Request(item["link"], callback=self.parsepage2)
				request.meta["item"] = item
				request.meta["link"] = item["link"]
				yield request		

	def parsepage2(self,response):
		item = response.meta["item"]
		hxs = Selector(response)
		parts = hxs.xpath("//div[@itemprop='articleBody']")

		for parts in parts:
			item["intro"] = parts.xpath("p/text()")[0].extract().encode('utf-8')	
		items.append(item)																							# Appends to Items
		connectDB(item, "PCAARRD")


class PhilStarSpider(Spider):
	name = "PhilStar"
	allowed_domains = ["philstar.com"]
	start_urls = ["http://www.philstar.com/breakingnews"]

	def parse(self, response):
			hxs = Selector(response)
			titles = hxs.xpath("//div[@class='article-teaser-wrapper clearfix']")
			items = []
			text_items = []
			titleList = []
			word = ""
			wordsToSplit = ""
			listOfWords = []
			news = {} 																							# Hashmap of news titles

			for titles in titles:
				item = RunScrapyItem()
				item ["author"] = "Philippine Star"				
				item ["title"] = titles.xpath("span[@class='article-title']/a/text()").extract()[0].encode('utf-8')
				wordsToSplit = str(titles.xpath("span[@class='article-title']/a/text()").extract()) 
				word = [word.strip(string.punctuation) for word in wordsToSplit.split()]						# Splits strings into tokens removing punctuation marks	
				listOfWords.append(word) 																		# Puts tokenized strings into list

				#BAG OF WORDS / HASH MAP PER TITLE

				item ["link"] = titles.xpath("span[@class='article-title']/a/@href").extract()[0].encode('utf-8')
				item ["link"] = "http://philstar.com"+item["link"]
				item ["image"] = titles.xpath("span[@class='img-left']/img/@src").extract()
				itemConverter(item, "image")
				if item["image"] == None:
					item ["image"] = "NULL" 

				#print(item)
				if item ["link"] != None:
					request = scrapy.Request(item["link"], callback=self.parsepage2)
					request.meta["item"] = item
					request.meta["link"] = item["link"]
					yield request		

	def parsepage2(self,response):
		item = response.meta["item"]
		hxs = Selector(response)
		parts = hxs.xpath("//div[@class='field-items']/div[@class='field-item even']")
		i = 0

		for parts in parts:
			if i == 2:
				if len(parts.xpath("p/text()")) < 1:															
					item["intro"] = parts.xpath("div/text()")[0].extract().encode('utf-8')	
				else:			
					item["intro"] = parts.xpath("p/text()")[0].extract().encode('utf-8')	 
			i = i + 1	#counter update
	
		items.append(item)																						# Appends to Items	
		connectDB(item, "PhilStar")																				# Inserts to database

			
#############################################################################################
# ----- FUNCTION THAT CHECKS IF ITEM FIELD IS NULL AND CONVERTS IT (UNICODE) TO UTF-8 ----- #
#############################################################################################
def itemConverter(item, fieldType):
		if len(item[fieldType]) != 0:																			# If item field is NOT NULL,	
			item [fieldType] = item [fieldType][0].encode('utf-8')												# Then convert Unicode (1st element) to UTF-8
		if type(item[fieldType]) == list:																		# If item field is NULL,
			item[fieldType] = None																			    # Ignore

####################################################################################################
# ----- SPECIAL ITEM CONVERTER FOR LINKS AND IMAGES THAT HAVE NO DOMAIN NAME IN SCRAPED LINK ----- #
####################################################################################################
def linkConverter(item, fieldType, domain):
		if len(item[fieldType]) != 0:																			# If item field is NOT NULL,				
			item [fieldType] = domain + item [fieldType][0].encode('utf-8')										# Then convert Unicode to UTF-8 then concat domain
		if type(item[fieldType]) == list:																		# If item field is NULL,
			item[fieldType] = None																			    # Ignore		

################################################################################################
# ----- CATEGORIZES NEWS HEADLINES INTO ITS CORRESPONDING CATEGORY USING TF-IDF & KMEANS ----- #
################################################################################################
def categorizeNews(listOfWords, wordFreq):
	# After Tokenizing the news titles,
	# TF-IDF COMPUTATION. Weights of the words are computed here.
	print(wordFreq)
	#Get the Term Frequency by the number of times a word appears in the title, normalized by dividing by the total number of words found in the title 


######################################################
# ----- FUNCTION THAT INSERTS DATA TO MYSQL DB ----- #
######################################################
def connectDB(item, name):
	mydb = MySQLdb.connect(host='localhost',
	    user='aggregator',
	    passwd='aggregator',
	    db='newsDB')
	cursor = mydb.cursor()
	
	if (cursor.execute('SELECT * FROM NEWS LIMIT 1') == 0):														# If NEWS table is EMPTY,
		cursor.execute('ALTER TABLE NEWS AUTO_INCREMENT=1')														# Resets news_id 
																										
	if(cursor.execute('SELECT * FROM NEWS WHERE title like '+"'%"+item['title']+"%' LIMIT 1")==0):				# If Title is NOT a duplicate,																	
		# Proceed to insertion
		cursor.execute('INSERT INTO NEWS(title, author, link, introText, image) VALUES("'+item['title']+'","'+item['author']+'","'+item['link']+'","'+item['intro']+'","'+item['image']+'")')	
		print "Inserted successfully!"			
	mydb.commit()													
	cursor.close()																								# Close the connection to the database
	print "Done"

#################################################
# ----- DECLARES AND STARTS ALL PROCESSES ----- #
#################################################
process = CrawlerProcess()
process.crawl(InquirerSpider)
process.crawl(PCAARRDSpider)
process.crawl(PhilStarSpider)
process.start()

#BAG OF WORDS
#Put list of words into hashmap
#Key ay yung word tapos value ay yung weights
#Each line/title, look for the frequencies of the weights
#Dun mo malalaman yung category nya, depende sa kung gano kadami yung
#category na yung. Kunyari maraming 2, which is politics.. Edi Politics sya.

