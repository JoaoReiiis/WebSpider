BOT_NAME = "spider"

SPIDER_MODULES = ["spider.spiders"]
NEWSPIDER_MODULE = "spider.spiders"

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
MONGO_DATABASE = 'spider_data'

SPIDER_COLLECTION = 'SpiderData'

# --- CONFIGURAÇÕES DO CRAWLER  ---
MAX_DEPTH = 4
SCORE_THRESHOLD = 1.2
MAX_LINKS_PER_PAGE = 25
MAX_QUERY_PARAMS = 7

# Lógica de pontuação
HOST_MATCH_WEIGHT = 4.0
KEYWORD_PATH_WEIGHT = 2.0
ANCHOR_TEXT_WEIGHT = 1.5
DEPTH_PENALTY = 0.3

# Palavras-chave positivas
#MOB_KEYWORDS = [
#    "mobilidade", "mobilidade urbana", "cidade-inteligente", #"smart-city",
#    "transporte", "transporte-publico", "veiculo-eletrico", #"ev", "vlt",
#    "metro", "brt", "bicicleta", "ciclovia", "urbanismo", #"sustentabilidade",
#    "iot", "big-data", "ia", "inteligencia-artificial", "5g", #"blockchain",
#    "veiculos-autonomos", "veiculos-conectados", "maas", #"eVTOL",
#    "semaforos-inteligentes", "estacao-de-recarga", "v2g", #"cidade-15-minutos",
#    "mobilidade-compartilhada", "logistica-urbana", "last-#mile",
#    "sistemas-de-transporte-inteligente", "sti", "transporte-ativo",
#]

KEYWORDS = [
    # --- 1. Conceitos Fundamentais e Tipos de Inovação ---
    "inovacao", "ecossistema-de-inovacao", "cultura-de-inovacao", "inovacao-aberta",
    "open-innovation", "inovacao-disruptiva", "inovacao-radical", "inovacao-incremental",
    "inovacao-de-produto", "inovacao-de-processo", "inovacao-de-marketing",
    "inovacao-organizacional", "inovacao-social", "tecnologia", "transformacao-digital",
    "pesquisa-e-desenvolvimento", "p&d", "transferencia-de-tecnologia",

    # --- 2. Atores do Ecossistema ---
    "helice-quadrupla", "universidade", "ict", "instituicao-de-ciencia-e-tecnologia",
    "governo", "poder-publico", "sociedade-civil", "comunidade", "empreendedor",
    "startup", "scale-up", "fintech", "agrotech", "healthtech", "edutech", "hardtech",
    "deep-tech", "empresa-de-base-tecnologica", "spin-off-academica", "corporacao",
    "grande-empresa", "investidor-anjo", "venture-capital", "vc", "capital-de-risco",
    "private-equity", "corporate-venture-capital", "cvc", "fomento", "mentor", "mentoria",

    # --- 3. Ambientes de Inovação (Habitats) ---
    "hub-de-inovacao", "parque-tecnologico", "parque-cientifico", "cluster-tecnologico",
    "incubadora-de-empresas", "aceleradora-de-startups", "fab-lab", "makerspace",
    "coworking", "living-lab", "centro-de-pesquisa", "sandbox-regulatorio", "networking",

    # --- 4. Jornada da Startup (Processos e Estágios) ---
    "ideacao", "validacao-de-ideia", "prototipo", "prototipagem",
    "produto-minimo-viavel", "mvp", "tracao", "product-market-fit", "pmf",
    "escalabilidade", "pivotar", "pivot", "crescimento-exponencial", "go-to-market",
    "estrategia-de-saida", "exit", "aquisicao", "fusao", "m&a",
    "oferta-publica-inicial", "ipo", "unicornio",

    # --- 5. Financiamento e Jargão Financeiro ---
    "bootstrapping", "capital-semente", "seed-money", "rodada-de-investimento",
    "investimento-pre-seed", "investimento-seed", "serie-a", "serie-b", "serie-c",
    "valuation", "valuation-pre-money", "valuation-post-money", "due-diligence",
    "term-sheet", "cap-table", "pitch", "deck-de-investimento",

    # --- 6. Metodologias e Gestão da Inovação ---
    "metodologia-agil", "agile", "scrum", "kanban", "sprint", "lean-startup",
    "startup-enxuta", "construir-medir-aprender", "design-thinking", "business-model-canvas",
    "canvas-modelo-negocio", "proposta-de-valor", "roadmap-de-produto", "kpi",
    "indicador-chave-de-desempenho", "customer-development",

    # --- 7. Aspectos Legais e Técnicos ---
    "propriedade-intelectual", "pi", "patente", "marca-registrada", "direitos-autorais",
    "segredo-industrial", "marco-legal-das-startups"
]

# Palavras-chave que, se presentes em uma URL, a descartam
NEGATIVE_KEYWORDS = [
    "login", "cadastro", "assine", "contato", "contact", "sobre", "politica-de-privacidade",
    "termos-de-uso", "cookies", "/feed", "/rss", "/tag/", "/author/", "/search",
    "entrar", "signin", "signup", "register", "profile", "user", "cart", "checkout",
    "download", "categoria", "category"
]

# Padrões de URL a serem ignorados (regex)
BLACKLIST_REGEX = r'(?i)\.(jpg|jpeg|png|gif|pdf|zip|rar)(\?.*)?$|/page/\d+|/feed/?$|/rss/?$'

# Extraction limits
MAX_TEXT_CHARS = 100000
MAX_LINKS = 2000

# Ative (True) para que o spider varra completamente os domínios listados abaixo.
# Desative (False) para que ele use a lógica de pontuação para todos.
ENABLE_FULL_CRAWL = False

# Lista de domínios para varrer por completo.
# O spider seguirá todos os links internos destes sites, ignorando a profundidade.
FULL_CRAWL_DOMAINS = [
  "https://valedosinconfidentes.com.br/"
]

# Override the default request headers:
#DEFAULT_REQUEST_HEADERS = {
#    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
#    "Accept-Language": "en",
#}

ITEM_PIPELINES = {
  "spider.pipelines.SpiderDataMongoPipeline": 301,
}

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/autothrottle.html
AUTOTHROTTLE_ENABLED = False
AUTOTHROTTLE_START_DELAY = 5
AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0

# Set settings whose default value is deprecated to a future-proof value
FEED_EXPORT_ENCODING = "utf-8"
