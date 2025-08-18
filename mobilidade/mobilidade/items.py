import scrapy
from itemloaders.processors import TakeFirst, MapCompose, Join
from w3lib.html import remove_tags
import dateparser
import unicodedata

def safe_remove_tags(value):
    if value is None:
        return ""
    return remove_tags(str(value))

def clean_text(text):
    if text is None:
        return ""
    text = unicodedata.normalize('NFC', text)
    return text.strip()

def parse_date(date_str: str):
    if not date_str:
        return ""
    try:
        parsed_date = dateparser.parse(date_str, languages=['pt'])
        return parsed_date.strftime('%Y-%m-%d') if parsed_date else ""
    except (TypeError, ValueError):
        return ""

class MobilidadeItem(scrapy.Item):
    titulo = scrapy.Field(
        input_processor=MapCompose(safe_remove_tags, clean_text),
        output_processor=TakeFirst()
    )
    url_fonte = scrapy.Field(
        output_processor=TakeFirst()
    )
    pagina_de_origem = scrapy.Field(
        output_processor=TakeFirst()
    )
    conteudo_texto = scrapy.Field(
        input_processor=MapCompose(safe_remove_tags),
        output_processor=Join('\n')
    )
    data_publicacao = scrapy.Field(
        input_processor=MapCompose(clean_text, parse_date),
        output_processor=TakeFirst()
    )

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