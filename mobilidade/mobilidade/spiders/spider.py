import re
import logging
from urllib.parse import urlparse
from collections import namedtuple
from operator import itemgetter
from typing import List

import scrapy

from ..items import BronzeItem, SilverItem
from ..utils import build_bronze_item, build_silver_item

logger = logging.getLogger(__name__)

def extract_host(url: str) -> str:
    """Extrai o host de uma URL (ex: 'www.exemplo.com')."""
    return urlparse(url).netloc.lower()

LinkCandidate = namedtuple("LinkCandidate", ["url", "anchor", "score"])


class MobilidadeSpider(scrapy.Spider):
    name = "mobilidade"

    start_urls = [
        "https://valedosinconfidentes.com.br/",
        "https://ecossistemainovap.com.br/",
        "https://nortevalley.com/",
        "https://parquetecnologicosrs.com.br/",
        "https://cesullab.com.br/index.html",
        "https://inovatech.pnl.mg.gov.br",
        "https://bdtechhub.com.br/bd/",
        "https://tiradentesinnovation.com/",
        "https://inovai.org.br/itajuba-hardtech/#:~:text=O%20Ecossistema,e%20inova%C3%A7%C3%A3o%20de%20Itajub%C3%A1%2FMG",
        "https://centev.ufv.br/",   
        "https://uberhub.com.br/"
    ]

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        # Este é o ponto de entrada correto para criar o spider.
        # Ele nos dá acesso ao 'crawler', que contém as 'settings'.
        spider = super(MobilidadeSpider, cls).from_crawler(crawler, *args, **kwargs)
        
        # Carrega todas as configurações diretamente das settings do crawler
        settings = crawler.settings
        spider.max_depth = settings.getint("MOB_MAX_DEPTH")
        spider.score_threshold = settings.getfloat("MOB_SCORE_THRESHOLD")
        spider.max_links_per_page = settings.getint("MOB_MAX_LINKS_PER_PAGE")
        spider.max_query_params = settings.getint("MOB_MAX_QUERY_PARAMS")
        spider.KEYWORDS = settings.getlist("MOB_KEYWORDS")
        spider.NEGATIVE_KEYWORDS = settings.getlist("MOB_NEGATIVE_KEYWORDS")
        
        blacklist_regex = settings.get("MOB_BLACKLIST_REGEX")
        spider._blacklist_re = re.compile(blacklist_regex, re.I)

        # Carrega os pesos para a lógica de pontuação
        spider.host_match_weight = settings.getfloat("MOB_HOST_MATCH_WEIGHT")
        spider.keyword_path_weight = settings.getfloat("MOB_KEYWORD_PATH_WEIGHT")
        spider.anchor_text_weight = settings.getfloat("MOB_ANCHOR_TEXT_WEIGHT")
        spider.depth_penalty = settings.getfloat("MOB_DEPTH_PENALTY")
        
        return spider

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(
                url,
                callback=self.parse,
                meta={"seed_url": url, "parent_url": None, "depth": 0},
            )

    def parse(self, response):
        parent_meta = {
            "seed_url": response.meta.get("seed_url"),
            "parent_url": response.meta.get("parent_url"),
        }

        try:
            bronze_item_data = build_bronze_item(response, parent_meta)
            yield BronzeItem(bronze_item_data)
        except Exception as e:
            self.logger.error(f"Erro ao criar item Bronze para {response.url}: {e}")

        try:
            if self.settings.getbool("EXTRACT_HEAVY_IN_CRAWLER", False):
                silver_payload = build_silver_item(bronze_item_data, response, self.settings)
                yield SilverItem(silver_payload)
        except Exception as e:
            self.logger.error(f"Erro ao criar item Silver para {response.url}: {e}")

        current_depth = response.meta.get("depth", 0)
        if current_depth >= self.max_depth:
            return

        candidates: List[LinkCandidate] = []
        for a_sel in response.css("a[href]"):
            href = a_sel.attrib.get("href")
            if not href:
                continue

            try:
                abs_url = response.urljoin(href)
            except Exception:
                continue

            anchor_text = a_sel.xpath("normalize-space(string())").get(default="").strip()
            score = self._score_link(response, abs_url, anchor_text, current_depth)
            
            if score > 0:
                candidates.append(LinkCandidate(url=abs_url, anchor=anchor_text, score=score))

        candidates = sorted(candidates, key=itemgetter(2), reverse=True)[:self.max_links_per_page]

        for cand in candidates:
            if cand.score >= self.score_threshold:
                priority = int(cand.score)
                meta = {
                    "depth": current_depth + 1,
                    "seed_url": response.meta.get("seed_url"),
                    "parent_url": response.url,
                    "anchor_text": cand.anchor,
                }
                yield response.follow(cand.url, callback=self.parse, meta=meta, priority=priority)

    def _score_link(self, response, candidate_url: str, anchor_text: str, current_depth: int) -> float:
        try:
            url_parts = urlparse(candidate_url)
            url_lower = candidate_url.lower()
        except Exception:
            return 0.0

        if url_parts.scheme not in ('http', 'https'):
            return 0.0
        if any(neg_kw in url_lower for neg_kw in self.NEGATIVE_KEYWORDS):
            return 0.0
        if self._blacklist_re.search(url_lower):
            return 0.0

        score = 0.0

        try:
            origin_host = extract_host(response.url)
            candidate_host = extract_host(candidate_url)
            if origin_host and candidate_host and origin_host == candidate_host:
                score += self.host_match_weight
        except Exception:
            pass

        path_lower = url_parts.path.lower()
        if any(kw in path_lower for kw in self.KEYWORDS):
            matches = sum(1 for kw in self.KEYWORDS if kw in path_lower)
            score += self.keyword_path_weight * matches

        anchor_lower = anchor_text.lower()
        if any(kw in anchor_lower for kw in self.KEYWORDS):
            matches = sum(1 for kw in self.KEYWORDS if kw in anchor_lower)
            score += self.anchor_text_weight * matches

        score -= self.depth_penalty * current_depth

        query = url_parts.query
        if query:
            param_count = len(query.split('&'))
            if param_count > self.max_query_params:
                score -= 2.0
            else:
                score -= 0.15 * param_count
        
        return max(0.0, round(score, 2))