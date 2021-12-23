# ScrapyProject

# 项目一：toscrape_book（爬取图书网站书本信息） #
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
	
#### 运行这条命令后，scrapy shell 使用url参数构造一个Request对象，并提交Scrapy引擎，页面下载完成后程序进入一个python shell中

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
	# -*-coding:utf-8-*-
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

## 4 运行爬虫
     scrapy crawl books -o books.csv --nolog






# 项目二：matplotlib_examples（下载matplotlib源码文件） #
## 1 项目需求 ##

	下载http://matplotlib.org网站中所有例子的源码文件到本地。

## 2 页面分析 ##
### (1) 查看页面 ###

	scrapy shell "https://matplotlib.org/2.0.2/examples/index.html"
	view(response)

### （2）获取所有页面链接 ###

 	le = LinkExtractor(restrict_css='div.toctree-wrapper.compound li.toctree-l2')
    links = le.extract_links(response)
    [link.url for link in links]
### （3）获取列子源码下载链接 ###

	调用fetch函数下载第一个例子页面，并调用view函数在浏览器中查看页面
 	fetch('http://matplotlib.org/examples/animation/animate_decay.html')
    view(response)
	href = response.css('a.reference.external::attr(href)').extract_first()


## 3 编码实现 ##
	1.创建scrapy项目，取名为matplotlib_examples
    
	scrapy startproject matplotlib_examples
	
	2.创建Spider文件以及Spider类，可以使用scrapy genspider <SPIDER_NAME><DOMAIN>命令生成模板
	
	cd matplotlib_examples
	scrapy genspider examples matplotlib.org	
	
	3. 实现ExampleItem，需定义file_urls和files两个字段
	
	class ExampleItem(scrapy.Item):
	    file_urls = scrapy.Field()
	    files = scrapy.Field()
	
	4. 实现页面的解析函数
	# -*-coding:utf-8-*-
	import scrapy
	from scrapy.linkextractors import LinkExtractor
	from ..items import ExampleItem
	
	
	class ExamplesSpider(scrapy.Spider):
	    name = 'examples'
	    allowed_domains = ['matplotlib.org']
	    start_urls = ['https://matplotlib.org/2.0.2/examples/index.html',]
	
	    def parse(self, response):
	        # le = LinkExtractor(restrict_css="div.toctree-wrapper.compound", deny='/index.html$')
	        # for link in le.extract_links(response):
	        #     yield scrapy.Request(link.url, callback=self.parse_example)
	
	        # response.follow_all
	        #links = response.css('div.toctree-wrapper.compound li.toctree-l2 a.reference.internal::attr(href)').getall()
	        yield from response.follow_all(css='div.toctree-wrapper.compound li.toctree-l2 a.reference.internal', callback=self.parse_example)
	
	    def parse_example(self, response):
	        href = response.css('a.reference.external::attr(href)').get()
	        url = response.urljoin(href)
	        example = ExampleItem()
	        example['file_urls'] = [url]
	        return example

	5. pipelines.py 实现评价等级one、Two...,转换为阿拉伯数字
	from scrapy.pipelines.files import FilesPipeline
	from urllib.parse import urlparse
	from os.path import basename, dirname, join
	
	
	# 实现FilesPipeline,覆写file_path方法
	# 修改FilesPipeline为文件命名的规则
	class MyFilePipeline(FilesPipeline):
	
	    def file_path(self, request, response=None, info=None):
	        # http://matplotlib.org/mpl_examples/axes_grid/demo_floating_axes.py
	        # path = axes_grid/demo_floating_axes.py
	        path = urlparse(request.url).path
	        # basename(dirname(path)) = axes_grid   basename(path) =demo_floating_axes.py
	        return join(basename(dirname(path)), basename(path))

	6. 配置文件settings.py
		
		# 启动FilesPipeline 并指定下载目录
		ITEM_PIPELINES = {
		    'matplotlib_examples.pipelines.MyFilePipeline': 1,
		    #'scrapy.pipelines.files.FilesPipeline': 1,
		}
		
		FILES_STORE = 'example_src'
		

## 4 运行爬虫
     scrapy crawl examples -o examples.json






# 项目三：art_image（下载360图片） #
## 1 项目需求 ##

	下载http://image.so.com网站中艺术分类下的所有图片到本地。

## 2 页面分析 ##

	页面中向下滚动鼠标滚轮，便会有更多图片加载出来，图片加载是由JavaScript脚本完成的，其响应结果是一个json串
	
	第1次加载：https://image.so.com/zjl?ch=art&sn=0
	第2次加载：https://image.so.com/zjl?ch=art&sn=30
	第3次加载：https://image.so.com/zjl?ch=art&sn=60
	
	sn参数　从第几张图片开始加载，即结果列表中第一张图片在服务器端的序号。

## 3 编码实现 ##
	1.创建scrapy项目，取名为art_image
    
	scrapy startproject art_image
	
	2.创建Spider文件以及Spider类，可以使用scrapy genspider <SPIDER_NAME><DOMAIN>命令生成模板
	
	cd art_image
	scrapy genspider images image.so.com	
	
	3. 实现ExampleItem，需定义file_urls和files两个字段
	
	class ExampleItem(scrapy.Item):
	    file_urls = scrapy.Field()
	    files = scrapy.Field()
	
	4. 实现下载的解析函数
	# -*- coding:utf-8 -*-
	import scrapy
	from scrapy import Request
	import json
	
	
	class ImagesSpider(scrapy.Spider):
	    name = 'images'
	    allowed_domains = ['image.so.com']
	    BASE_URL = 'https://image.so.com/zjl?ch=beauty&sn=%s'
	    start_urls = [BASE_URL % 0]
	    start_index = 0
	
	    # 限制最大下载数量，防止磁盘用量过大
	    MAX_DOWNLOAD_NUM = 300
	
	    def parse(self, response):
	        # 使用JSON模块解析响应结果
	        infos = json.loads(response.body.decode('utf-8'))
	
	        # 提取所有图片下载url到一个列表，赋给item的'image_urls'字段
	        yield {'image_urls': [info['qhimg_url'] for info in infos['list']]}
	
	        # 如count字段大于0，并且下载数量不足MAX_DOWNLOAD_NUM，继续获取下一页
	        self.start_index += infos['count']
	        if infos['count'] > 0 and self.start_index < self.MAX_DOWNLOAD_NUM:
	            yield Request(self.BASE_URL % self.start_index)

	5. 配置文件settings.py
		
		# 启动ImagesPipeline 并指定下载目录
		ITEM_PIPELINES = {
		    'scrapy.pipelines.images.ImagesPipeline': 1,
		}
		IMAGES_STORE = 'download_images'
				

## 4 运行爬虫
     scrapy crawl images

