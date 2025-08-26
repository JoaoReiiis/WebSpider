import re
import logging
from urllib.parse import urlparse
from collections import namedtuple
from operator import itemgetter
from typing import List

import scrapy

from ..items import SpiderDataItem
from ..utils import build_spider_data_item, normalize_url

logger = logging.getLogger(__name__)

def extract_host(url: str) -> str:
    return urlparse(url).netloc.lower()

LinkCandidate = namedtuple("LinkCandidate", ["url", "anchor", "score"])


class Spider(scrapy.Spider):
    name = "spider"

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
        spider = super(Spider, cls).from_crawler(crawler, *args, **kwargs)
        
        settings = crawler.settings
        spider.max_depth = settings.getint("MAX_DEPTH")
        spider.score_threshold = settings.getfloat("SCORE_THRESHOLD")
        spider.max_links_per_page = settings.getint("MAX_LINKS_PER_PAGE")
        spider.max_query_params = settings.getint("MAX_QUERY_PARAMS")
        spider.KEYWORDS = settings.getlist("KEYWORDS")
        spider.NEGATIVE_KEYWORDS = settings.getlist("NEGATIVE_KEYWORDS")
        
        blacklist_regex = settings.get("BLACKLIST_REGEX")
        spider._blacklist_re = re.compile(blacklist_regex, re.I)

        spider.host_match_weight = settings.getfloat("HOST_MATCH_WEIGHT")
        spider.keyword_path_weight = settings.getfloat("KEYWORD_PATH_WEIGHT")
        spider.anchor_text_weight = settings.getfloat("ANCHOR_TEXT_WEIGHT")
        spider.depth_penalty = settings.getfloat("DEPTH_PENALTY")
        
        return spider

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(
                url,
                callback=self.parse,
                meta={
                    "seed_url": url, 
                    "parent_url": None, 
                    "depth": 0,
                    "redirect_chain": [normalize_url(url)]
                },
            )

    def parse(self, response):
        try:
            spider_data_payload = build_spider_data_item(response, self.settings)
            yield SpiderDataItem(spider_data_payload)
        except Exception as e:
            self.logger.error(f"Erro ao criar item SpiderData para {response.url}: {e}")

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

        current_redirect_chain = response.meta.get('redirect_chain', [])

        for cand in candidates:
            if cand.score >= self.score_threshold:
                priority = int(cand.score)
                meta = {
                    "depth": current_depth + 1,
                    "seed_url": response.meta.get("seed_url"),
                    "parent_url": response.url,
                    "anchor_text": cand.anchor,
                    "redirect_chain": current_redirect_chain + [normalize_url(cand.url)],
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
                score -= 0.1 * param_count
        
        return max(0.0, round(score, 2))