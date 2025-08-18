import scrapy

class BronzeItem(scrapy.Item):
    id = scrapy.Field()
    seed_url = scrapy.Field()
    source_domain = scrapy.Field()
    url = scrapy.Field()
    page_date = scrapy.Field()
    raw_html = scrapy.Field()
    content_length = scrapy.Field()
    redirect_chain = scrapy.Field()
    parent_url = scrapy.Field()
    depth = scrapy.Field()

class SilverItem(scrapy.Item):
    silver_id = scrapy.Field()
    bronze_id = scrapy.Field()
    url = scrapy.Field()
    source_domain = scrapy.Field()
    crawl_date = scrapy.Field()
    title = scrapy.Field()
    description = scrapy.Field()
    lang = scrapy.Field()
    readable_text = scrapy.Field()
    text_length = scrapy.Field()
    published_date = scrapy.Field()
    links_internal = scrapy.Field()
    links_external = scrapy.Field()