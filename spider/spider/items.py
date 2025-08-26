import scrapy

class SpiderDataItem(scrapy.Item):
    url = scrapy.Field()
    source_domain = scrapy.Field()
    title = scrapy.Field()
    crawl_date = scrapy.Field()
    published_date = scrapy.Field()
    description = scrapy.Field()
    lang = scrapy.Field()
    readable_text = scrapy.Field()
    text_length = scrapy.Field()
    links_internal = scrapy.Field()
    links_external = scrapy.Field()
    redirect_chain = scrapy.Field()
    depth = scrapy.Field()