import uuid
from urllib.parse import urlparse, urlunparse, parse_qsl, urlencode
import json
from lxml import html

def normalize_url(url):
    """
    Aplica normalização mínima em uma URL.
    - Lowercase no host.
    - Remove fragmentos (#...).
    - Remove parâmetros de tracking (utm_*, fbclid, gclid).
    """
    if not url:
        return None
    parsed_url = urlparse(url)
    # Lowercase no scheme e netloc
    scheme = parsed_url.scheme.lower()
    netloc = parsed_url.netloc.lower()
    # Remove parâmetros de tracking
    query_params = parse_qsl(parsed_url.query)
    filtered_params = [
        (k, v) for k, v in query_params
        if not k.startswith('utm_') and k not in ['fbclid', 'gclid']
    ]
    # Monta a URL normalizada
    normalized_url = urlunparse((
        scheme,
        netloc,
        parsed_url.path,
        parsed_url.params,
        urlencode(filtered_params),
        ''  # Remove o fragmento
    ))
    return normalized_url

def build_bronze_item(response, parent_meta):
    """
    Constrói um item no formato Bronze a partir da resposta da requisição.
    """
    # Extrai a data de publicação de metatags
    page_date = response.xpath(
        '//meta[@property="article:published_time"]/@content'
    ).get() or response.xpath(
        '//meta[@itemprop="datePublished"]/@content'
    ).get()

    # Tenta extrair de JSON-LD
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

    # Normalização de URLs
    redirect_urls = [normalize_url(url) for url in response.request.meta.get('redirect_urls', [])]
    final_url = normalize_url(response.url)
    if final_url not in redirect_urls:
        redirect_urls.append(final_url)

    seed_url = normalize_url(parent_meta.get('seed_url'))
    parent_url = normalize_url(parent_meta.get('parent_url'))

    return {
        "id": str(uuid.uuid4()),
        "seed_url": seed_url,
        "source_domain": urlparse(seed_url).netloc if seed_url else None,
        "url": final_url,
        "page_date": page_date,
        "raw_html": response.text,
        "content_length": len(response.body),
        "redirect_chain": redirect_urls,
        "parent_url": parent_url,
        "depth": response.meta.get('depth', 0)
    }