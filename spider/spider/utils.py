import uuid
from urllib.parse import urlparse, urlunparse, parse_qsl, urlencode
import json
import datetime
from goose3 import Goose
from goose3.configuration import Configuration
from lxml import html

def normalize_url(url):
    if not url:
        return None
    parsed_url = urlparse(url)
    scheme = parsed_url.scheme.lower()
    netloc = parsed_url.netloc.lower()
    query_params = parse_qsl(parsed_url.query)
    filtered_params = [
        (k, v) for k, v in query_params
        if not k.startswith('utm_') and k not in ['fbclid', 'gclid']
    ]
    normalized_url = urlunparse((
        scheme,
        netloc,
        parsed_url.path,
        parsed_url.params,
        urlencode(filtered_params),
        ''  
    ))
    return normalized_url

def build_spider_data_item(response, settings):
    page_date = response.xpath(
        '//meta[@property="article:published_time"]/@content'
    ).get() or response.xpath(
        '//meta[@itemprop="datePublished"]/@content'
    ).get()

    if not page_date:
        json_ld_scripts = response.xpath('//script[@type="application/ld+json"]/text()').getall()
        for script in json_ld_scripts:
            try:
                data = json.loads(script)
                if isinstance(data, list):
                    for item in data:
                        if item.get('@type') == 'NewsArticle' or item.get('@type') == 'Article':
                            page_date = item.get('datePublished')
                            if page_date:
                                break
                elif isinstance(data, dict):
                    if data.get('@type') == 'NewsArticle' or data.get('@type') == 'Article':
                        page_date = data.get('datePublished')
                if page_date:
                    break
            except json.JSONDecodeError:
                continue

    crawl_path = response.meta.get('redirect_chain', [])
    final_url = normalize_url(response.url)
    
    if not crawl_path or crawl_path[-1] != final_url:
        crawl_path.append(final_url)

    seed_url = normalize_url(response.meta.get('seed_url'))

    bronze_data = {
        "redirect_chain": crawl_path,
        "depth": response.meta.get('depth', 0),
        "source_domain": urlparse(seed_url).netloc if seed_url else None,
        "url": final_url
    }

    g_config = Configuration()
    g_config.enable_image_fetching = False
    g_config.use_meta_language = False
    g_config.target_language = 'pt'

    goose = Goose(g_config)
    article = goose.extract(raw_html=response.text)

    MAX_TEXT_CHARS = settings.getint('MAX_TEXT_CHARS', 1000000)
    MAX_LINKS = settings.getint('MAX_LINKS', 200)

    internal_links = set()
    external_links = set()
    source_domain = bronze_data.get("source_domain")
    if source_domain:
        for link in response.css('a::attr(href)').getall():
            try:
                link_domain = urlparse(response.urljoin(link)).netloc
                if source_domain in link_domain:
                    internal_links.add(link)
                else:
                    external_links.add(link)
            except Exception:
                pass
    
    cleaned_text = getattr(article, 'cleaned_text', '')
    
    return {
        'url': bronze_data['url'],
        'source_domain': bronze_data['source_domain'],
        'crawl_date': datetime.datetime.now(datetime.timezone.utc),
        'published_date': getattr(article, 'publish_date', None) or page_date,
        'title': getattr(article, 'title', ''),
        'description': getattr(article, 'meta_description', ''),
        'lang': getattr(article, 'meta_lang', ''),
        'readable_text': cleaned_text[:MAX_TEXT_CHARS],
        'text_length': len(cleaned_text),
        'links_internal': list(internal_links)[:MAX_LINKS],
        'links_external': list(external_links)[:MAX_LINKS],
        'redirect_chain': bronze_data['redirect_chain'],
        'depth': bronze_data['depth']
    }