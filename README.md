# ScrapyProject

# 项目一：爬取图书网站书本信息 #
## 1 项目需求 ##
	爬取http://books.toscrape.com网站中的书籍信息
### (1) 每本书籍信息包括 ###
	- 书名
	- 价格
	- 评价等级
	- 产品编码
	- 库存量
	- 评价数量

### (2) 爬取的结果保存在csv文件中 ###

## 2 页面分析 ##
### (1) 以第一本书页面为例 ###
	`scrapy shell "http://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html"`
	
#### 运行这条命令后，scrapy shell 使用url参数构造一个Request对象，并提交Scrapy引擎，页面下载完成后程序进入一个python shell中####
#### 环境已有的常用对象函数，有以下几个 ####
	`request
		最近一个下载对应的Request对象
	response
		最近一次下载对应的Response对象
	fetch(req_or_url)
		该函数用于下载页面，可传入一个Request对应或url字符串，调用后会更新变量Request or response
	view(response)
		该函数用于在浏览器中显示response中的页面
`
## 3 编码实现 ##
	1.创建一个scrapy项目，取名为toscrapy_book
    
	`scrapy startproject toscrape_book`
	
	2.创建Spider文件以及Spider类，可以使用scrapy genspider <SPIDER_NAME><DOMAIN>命令生成模板
	
	`cd toscrape_book
	scrapy genspider books books.toscrape.com	
	`
	3. 定义封装书籍信息的Item类，在toscrape_book/items.py中添加如下代码
	`class BookItem(scrapy.item):
	    name = scrapy.Field()  # 书名
	    price = scrapy.Field()  # 价格
	    review_rating = scrapy.Field()  # 评价等级，1~5星
	    review_num = scrapy.Field()  # 评价数量
	    upc = scrapy.Field()  # 产品编码
	    stock = scrapy.Field()  # 库存量`
	
	4. 实现书籍列表页面的解析函数
		`# -*-coding:utf-8-*-
	import scrapy
	from scrapy.linkextractors import LinkExtractor
	from ..items import BookItem


	class BooksSpider(scrapy.Spider):

	    name = 'books'
	    allowed_domains = ['books.toscrape.com']
	    start_urls = ['http://books.toscrape.com/']

	    # 书籍列表页面的解析函数
	    def parse(self, response):
	        le = LinkExtractor(restrict_css='article.product_pod h3')
	        for link in le.extract_links(response):
	            yield scrapy.Request(link.url, callback=self.parse_book)
	
	        # 提取“下一页”的链接
	        le = LinkExtractor(restrict_css="ul.pager li.next")
	        links = le.extract_links(response)
	        if links:
	            next_url = links[0].url
	            yield scrapy.Request(next_url, callback=self.parse)
	
	    # 书籍页面的解析函数
	    def parse_book(self, response):
	        book = BookItem()
	        sel = response.css('div.product_main')
	        book['name'] = sel.xpath('./h1/text()').get()
	        book['price'] = sel.css('p.price_color::text').get()
	        book['review_rating'] = sel.css('p.star-rating::attr(class)').re_first('star-rating ([A-Za-z]+)')
	        sel = response.css('table.table.table-striped')
	        book['upc'] = sel.xpath('(.//tr)[1]/td/text()').get()
	        book['stock'] = sel.xpath('(.//tr)[last()-1]/td/text()').re_first('\((\d+) available\)')
	        book['review_num'] = sel.xpath('(.//tr)[last()]/td/text()').get()
	        yield book

	5. pipelines.py 实现评价等级one、Two...,转换为阿拉伯数字
		class BookPipeline(object):
		    review_rating_map = {
		        'One': 1,
		        'Two': 2,
		        'Three': 3,
		        'Four': 4,
		        'Five': 5,
		    }

		    def process_item(self,item,spider):
		        rating = item.get('review_rating')
		        if rating:
		            item['review_rating'] = self.review_rating_map[rating]
		
		        return item

	6. 配置文件settings.py
		#使用FEED_EXPORT_FIELDS指定各列的次序：      
		FEED_EXPORT_FIELDS = ['upc', 'name', 'price', 'stock', 'review_rating', 'review_num']
		
		#启用BookPipeline
		ITEM_PIPELINES = {
   			'toscrape_book.pipelines.BookPipeline': 300,
		}

## 4 运行爬虫 ##	
     scrapy crawl books -o books.csv --nolog
