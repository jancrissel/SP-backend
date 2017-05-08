###########################################################################################################################################
#	AUTHOR: DE RAMOS, Jan Crissel O.																									  #
#			2013-08999																													  #
#	PROGRAM DESCRIPTION: This program makes use of multiple spiders to crawl on different web sites. The scraped data will then be stored #
#						 on separate CSV files, one for each spider. 																	  #
###########################################################################################################################################
						 
from scrapy.spiders import Spider
from scrapy.crawler import CrawlerProcess
from scrapy.selector import Selector
from run_scrapy.items import RunScrapyItem
import string
import csv
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
			items = []
			data = []
			titleList = []
			word = ""
			wordsToSplit = ""
			listOfWords = []
			news = {} #hashmap of news titles

			for titles in titles:
				item = RunScrapyItem()
				item ["author"] = "Philippine Daily Inquirer"
				item ["title"] = titles.xpath("a/text()").extract()													# Extracts Title 
				if len(item["title"]) != 0:																			# If Title field is NOT NULL,				
					item ["title"] = item ["title"][0].encode('utf-8')												# Then convert Unicode (1st element) to UTF-8
				if type(item["title"]) == list:																		# If Title field is NULL,
					item["title"] = None																			# Ignore
				
				wordsToSplit = str(titles.xpath("a/text()").extract()) 
				word = [word.strip(string.punctuation) for word in wordsToSplit.split()]							# Splits strings into tokens removing punctuation marks	
				listOfWords.append(word) 																			# Puts tokenized strings into list

				##### BAG OF WORDS / HASH MAP PER TITLE #####
				
				item ["link"] = titles.xpath("a/@href").extract()													# Extracts Link 
				itemConverter(item,"link")																			# Checks if valid type or if not empty, then converts it to utf-8
				item ["image"] = "NULL"																				# Stores items in image field as null
				items.append(item)																					# Appends to Items

			#for item in items:
			#	titleList.append(item["title"]) 																	# Appends list of titles into new list			

			#for item in titleList:
				#print(item)
				#print(listOfWords)																					# Prints list of tokenized words	
			#return items
			outputFile(items,"Inquirer")
			connectDB(items, "Inquirer")
				
class PCAARRDSpider(Spider):
	name = "PCAARRD"
	allowed_domains = ["pcaarrd.dost.gov.ph"]
	start_urls = ["http://www.pcaarrd.dost.gov.ph/home/portal/index.php/2015-02-26-06-57-10/news-archive"]

	def parse(self, response):
			hxs = Selector(response)
			titles = hxs.xpath("//li")
			items = []
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
				linkConverter(item, "link", "www.pcaarrd.dost.gov.ph")			
				item ["image"] = titles.xpath("div/p/img[@class='caption']/@src").extract()
				linkConverter(item, "image", "www.pcaarrd.dost.gov.ph")
				items.append(item)

			#for item in items:
			#titleList.append(item["title"]) #appends list of titles into new list			

#			for item in titleList:
				#print(item)
				#print(listOfWords)	#prints list of tokenized words
			#print items
			outputFile(items,"PCAARRD")
			connectDB(items, "PCAARRD")

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
			news = {} #hashmap of news titles

			for titles in titles:
				item = RunScrapyItem()
				item ["author"] = "Philippine Star"				
				item ["title"] = titles.xpath("span[@class='article-title']/a/text()").extract()[0]
				wordsToSplit = str(titles.xpath("span[@class='article-title']/a/text()").extract()) 
				word = [word.strip(string.punctuation) for word in wordsToSplit.split()]
				#splits strings into tokens removing punctuation marks	
				listOfWords.append(word) #puts tokenized strings into list

				#BAG OF WORDS / HASH MAP PER TITLE


				item ["link"] = titles.xpath("span[@class='article-title']/a/@href").extract()[0]
				item ["link"] = "http://philstar.com"+item["link"]
				item ["image"] = titles.xpath("span[@class='img-left']/img/@src").extract()
				itemConverter(item, "image")
				items.append(item)

			#for item in items:
			#titleList.append(item["title"]) #appends list of titles into new list			

#			for item in titleList:
				#print(item)
				#print(listOfWords)	#prints list of tokenized words
			#print items
			outputFile(items,"PhilStar")
			connectDB(items,"PhilStar")
			
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


###################################################################
# ----- FUNCTION THAT OUTPUTS SCRAPED ITEMS INTO A CSV FILE ----- #
###################################################################
def outputFile(items,name):
			writer = csv.writer(open("{}.csv".format(name),'wb'))
			writer.writerow(['title', 'author', 'link', 'image'])
			for item in items:
				if item["title"] in (None,""): 																	# Skips empty fields
					continue		
				else:																							# Writes Fields with complete data
					writer.writerow([item['title'], item['author'], item['link'], item['image']])			
			return items

####################################################################
# ----- FUNCTION THAT INSERTS DATA FROM CSV FILE TO MYSQL DB ----- #
####################################################################
def connectDB(items, name):
	mydb = MySQLdb.connect(host='localhost',
	    user='aggregator',
	    passwd='aggregator',
	    db='newsDB')
	cursor = mydb.cursor()

	csv_data = csv.reader(file(name+'.csv'))
	next(csv_data)																									# SKIP first line	
	
	if (cursor.execute('SELECT * FROM NEWS LIMIT 1') == 0):															# If NEWS table is EMPTY,
		cursor.execute('ALTER TABLE NEWS AUTO_INCREMENT=1')															# Resets news_id 
	
	for row in csv_data:	
		#if (cursor.execute('SELECT COUNT(TITLE) FROM NEWS WHERE TITLE LIKE ''') == 0)
		cursor.execute('INSERT INTO NEWS(title, author, link, image) VALUES(%s, %s, %s, %s)', row)					# Insert each data into table
	mydb.commit()													
	cursor.close()																									# Close the connection to the database
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

