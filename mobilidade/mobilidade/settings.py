BOT_NAME = "mobilidade"

SPIDER_MODULES = ["mobilidade.spiders"]
NEWSPIDER_MODULE = "mobilidade.spiders"

ADDONS = {}


# Crawl responsibly by identifying yourself (and your website) on the user-agent
USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64; rv:140.0) Gecko/20100101 Firefox/140.0"

# Obey robots.txt rules
ROBOTSTXT_OBEY = True

# Concurrency and throttling settings
CONCURRENT_REQUESTS = 16
CONCURRENT_REQUESTS_PER_DOMAIN = 2
DOWNLOAD_DELAY = 2

MONGO_URI = 'mongodb://localhost:27017/'
MONGO_DATABASE = 'mobilidade_db'

BRONZE_COLLECTION = 'mobilidade_bronze'
SILVER_COLLECTION = 'mobilidade_silver'

# --- CONFIGURAÇÕES DO CRAWLER  ---
MOB_MAX_DEPTH = 8
MOB_SCORE_THRESHOLD = 3.0
MOB_MAX_LINKS_PER_PAGE = 15
MOB_MAX_QUERY_PARAMS = 5

# Lógica de pontuação
MOB_HOST_MATCH_WEIGHT = 4.0
MOB_KEYWORD_PATH_WEIGHT = 2.0
MOB_ANCHOR_TEXT_WEIGHT = 1.5
MOB_DEPTH_PENALTY = 0.2

# Palavras-chave positivas
MOB_KEYWORDS = [
    "mobilidade", "mobilidade urbana", "cidade-inteligente", "smart-city",
    "transporte", "transporte-publico", "veiculo-eletrico", "ev", "vlt",
    "metro", "brt", "bicicleta", "ciclovia", "urbanismo", "sustentabilidade",
    "iot", "big-data", "ia", "inteligencia-artificial", "5g", "blockchain",
    "veiculos-autonomos", "veiculos-conectados", "maas", "eVTOL",
    "semaforos-inteligentes", "estacao-de-recarga", "v2g", "cidade-15-minutos",
    "mobilidade-compartilhada", "logistica-urbana", "last-mile",
    "sistemas-de-transporte-inteligente", "sti", "transporte-ativo",
]

# Palavras-chave que, se presentes em uma URL, a descartam
MOB_NEGATIVE_KEYWORDS = [
    "login", "cadastro", "assine", "contato", "sobre", "politica-de-privacidade",
    "termos-de-uso", "cookies", "/feed", "/rss", "/tag/", "/author/", "/search",
]

# Padrões de URL a serem ignorados (regex)
MOB_BLACKLIST_REGEX = r'\.(jpg|jpeg|png|gif|pdf|zip|rar)(\?.*)?$|/page/\d+'

# Custom settings
EXTRACT_HEAVY_IN_CRAWLER = True

# Extraction limits
MAX_TEXT_CHARS = 1000000
MAX_LINKS = 200

# Override the default request headers:
#DEFAULT_REQUEST_HEADERS = {
#    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
#    "Accept-Language": "en",
#}

ITEM_PIPELINES = {
  "mobilidade.pipelines.BronzeMongoPipeline": 301,
  "mobilidade.pipelines.SilverMongoPipeline": 302,
}

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/autothrottle.html
AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 5
AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0

# Set settings whose default value is deprecated to a future-proof value
FEED_EXPORT_ENCODING = "utf-8"