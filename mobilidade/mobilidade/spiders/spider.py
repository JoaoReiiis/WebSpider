import scrapy
from urllib.parse import urlparse
from ..items import BronzeItem
from ..utils import build_bronze_item

class MobilidadeSpider(scrapy.Spider):
    name = "mobilidade"
    
    start_urls = [
        "https://mobilidade.estadao.com.br/",
        "https://www.mobilize.org.br/noticias/",
        "https://valedosinconfidentes.com.br/"
    ]
        
    KEYWORDS = [
        "mobilidade", "mobilidade-urbana", "cidade-inteligente", "smart-city",
        "transporte", "transporte-publico", "veiculo-eletrico", "ev", "vlt",
        "metro", "brt", "bicicleta", "ciclovia", "urbanismo", "sustentabilidade",
        "iot", "big-data", "ia", "inteligencia-artificial", "5g", "blockchain",
        "veiculos-autonomos", "veiculos-conectados", "maas", "eVTOL",
        "semaforos-inteligentes", "estacao-de-recarga", "v2g",
        "cidade-15-minutos", "mobilidade-compartilhada", "logistica-urbana", "last-mile",
        "sistemas-de-transporte-inteligente", "sti", "transporte-ativo",
    ]

    NEGATIVE_KEYWORDS = [
        'login', 'cadastro', 'assine', 'contato', 'sobre-nos', 
        'politica-de-privacidade', 'termos-de-uso', 'cookies'
    ]
    
    def __init__(self, *args, **kwargs):
        super(MobilidadeSpider, self).__init__(*args, **kwargs)
        self.max_depth = 16

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url, callback=self.parse, meta={'seed_url': url, 'parent_url': None, 'depth': 0})

    def parse(self, response):
        parent_meta = {
            'seed_url': response.meta.get('seed_url'),
            'parent_url': response.meta.get('parent_url')
        }
        yield BronzeItem(build_bronze_item(response, parent_meta))

        current_depth = response.meta.get('depth', 0)
        if current_depth >= self.max_depth:
            self.logger.info(f"Profundidade máxima ({self.max_depth}) atingida em: {response.url}")
            return

        for link in response.css('a::attr(href)').getall():
            absolute_link = response.urljoin(link)
            if self.deve_seguir_o_link(response, absolute_link):
                yield scrapy.Request(
                    absolute_link,
                    callback=self.parse,
                    meta={
                        'depth': current_depth + 1,
                        'seed_url': response.meta.get('seed_url'),
                        'parent_url': response.url
                    }
                )
 
    def deve_seguir_o_link(self, response, url: str) -> bool:
        if not url.startswith(('http', 'https')):
            return False

        url_lower = url.lower()

        if any(neg_keyword in url_lower for neg_keyword in self.NEGATIVE_KEYWORDS):
            return False

        dominio_origem = urlparse(response.url).netloc

        if dominio_origem in url:
            return True

        if any(keyword in url_lower for keyword in self.KEYWORDS):
            return True

        return False