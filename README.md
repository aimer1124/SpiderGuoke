# Guoke Spider

Use [scrapy](https://scrapy.org/) to crawl [Guoke](http://www.guokr.com/).

## Usage

### Command line
- `scrapy crawl guoke`: start to scrapy data

###  Tech

- DB: Mongo
- spider: scrapy

## Day 2

### 引用Flask后端框架

- 在`api.py`中添加

```
class Questions(Resource):
    def get(self):
        questions = mongo.db.Guoke_info.find({'answer': '3'})
        listQuestion = []
        for question in questions:
            listQuestion.append({'title': question['title']})
        return jsonify(listQuestion)
```

- 启动Flask: python api.py

```
127.0.0.1 - - [19/Jul/2017 11:39:41] "GET /questions HTTP/1.1" 200 -
 * Detected change in '/Users/yjshi/Documents/ENV3.6/Guoke/api.py', reloading
 * Restarting with stat
 * Debugger is active!
 * Debugger PIN: 558-247-970

```

## Day 1

### Learn from [Scrapy爬虫：果壳热门和精彩问答信息爬取](http://bulolo.cn/2017/06/20/scrapy3/#more)


1. `guoke.py`中设置请求的base url地址

```python
class GuokeSpider(scrapy.Spider):
    
    ...
    
    allowed_domains = ["guokr.com"]
    start_urls = ['http://www.guokr.com/ask/hottest/?page={}'.format(n) for n in range(1, 8)] + [
        'http://www.guokr.com/ask/highlight/?page={}'.format(m) for m in range(1, 101)]
    
    ...
     
```

2. `middlewares.py`中配制代理

```python
class RotateUserAgentMiddleware(UserAgentMiddleware):
    def __init__(self, user_agent=''):
        self.user_agent = user_agent
    def process_request(self, request, spider):
        ua = random.choice(self.user_agent_list)
        if ua:
            print(ua)
            request.headers.setdefault('User-Agent', ua)
    user_agent_list = [
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1"
        "Mozilla/5.0 (X11; CrOS i686 2268.111.0) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.57 Safari/536.11",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1092.0 Safari/536.6",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1090.0 Safari/536.6",
        "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/19.77.34.5 Safari/537.1",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.9 Safari/536.5",
        "Mozilla/5.0 (Windows NT 6.0) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.36 Safari/536.5",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_0) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
    ]

```

3. 实现爬虫`策略`

在`guoke.py`中使用`parse`方法来实现具体的爬虫策略，本示例中是爬去指定URL地址的信息


4. 获取爬虫的`数据对象`

```python

...
item = GuokeItem()
i = 0
for content in response.xpath('/html/body/div[3]/div[1]/ul[2]/li'):
    item['title'] = content.xpath('//div[2]/h2/a/text()').extract()[i]
    item['Focus'] = content.xpath('//div[@class="ask-hot-nums"]/p[1]/span/text()').extract()[i]
    item['answer'] = content.xpath('//div[1]/p[2]/span/text()').extract()[i]
    item['link'] = content.xpath('//div[2]/h2/a/@href').extract()[i]
    item['content'] = content.xpath('//div[2]/p/text()').extract()[i]
    i += 1
    yield item
...

```

5. `加工、处理`数据对象，`保存`爬虫结果

```python
class GuokePipeline(object):
    def __init__(self):
        self.client = pymongo.MongoClient(host=settings['MONGO_HOST'], port=settings['MONGO_PORT'])
        self.db = self.client[settings['MONGO_DB']]
        self.post = self.db[settings['MONGO_COLL']]
    def process_item(self, item, spider):
        postItem = dict(item)
        self.post.insert(postItem)
        return item
class JsonWriterPipeline(object):
    def __init__(self):
        self.file = open('guoke.json', 'w', encoding='utf-8')
    def process_item(self, item, spider):
        line = json.dumps(dict(item), ensure_ascii=False) + "\n"
        self.file.write(line)
        return item
    def spider_closed(self, spider):
        self.file.close()
```

6. 在`settings.py`启用相应配制：数据库、中间件、管道

```buildoutcfg
# 配置mongodb
MONGO_HOST = "127.0.0.1"  # 主机IP
MONGO_PORT = 27017  # 端口号
MONGO_DB = "Guoke"  # 库名
MONGO_COLL = "Guoke_info"  # collection

# 中间件配制
DOWNLOADER_MIDDLEWARES = {
   'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
   'Guoke.middlewares.RotateUserAgentMiddleware': 400,

}


#管道配制
ITEM_PIPELINES = {
   'Guoke.pipelines.JsonWriterPipeline': 300,
   'Guoke.pipelines.GuokePipeline': 300,
}
```
### Scrapy架构 - [Architecture](https://doc.scrapy.org/en/latest/topics/architecture.html#topics-architecture)

![Scrapy架构](https://doc.scrapy.org/en/latest/_images/scrapy_architecture_02.png)

- The Engine gets the initial Requests to crawl from the Spider.
- The Engine schedules the Requests in the Scheduler and asks for the next Requests to crawl.
- The Scheduler returns the next Requests to the Engine.
- The Engine sends the Requests to the Downloader, passing through the Downloader Middlewares (see process_request()).
- Once the page finishes downloading the Downloader generates a Response (with that page) and sends it to the Engine, passing through the Downloader Middlewares (see process_response()).
- The Engine receives the Response from the Downloader and sends it to the Spider for processing, passing through the Spider Middleware (see process_spider_input()).
- The Spider processes the Response and returns scraped items and new Requests (to follow) to the Engine, passing through the Spider Middleware (see process_spider_output()).
- The Engine sends processed items to Item Pipelines, then send processed Requests to the Scheduler and asks for possible next Requests to crawl.