import re
from typing import List, Optional
import ssl
import requests
from bs4 import BeautifulSoup

from models import Detail, SearchResult, SearchOptions, DetailItem

proxies = {
    "http": "http://127.0.0.1:7890",
    "https": "http://127.0.0.1:7890"
}
headers = {
    'User-Agent': '"User-Agent" to "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, '
                  'like Gecko) Chrome/102.0.5005.124 Safari/537.36 Edg/102.0.1245.44"',
}

# 防止因为ssl key过短导致无法请求
requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS += 'HIGH:!DH:!aNULL'
try:
    requests.packages.urllib3.contrib.pyopenssl.DEFAULT_SSL_CIPHER_LIST += 'HIGH:!DH:!aNULL'
except AttributeError:
    # no pyopenssl support used / needed / available
    pass


def remove_extra_spaces(text: str) -> str:
    """Remove extra spaces from the text."""
    return re.sub(r'[ \t]+', ' ', text).strip()


def resolve_date(text: Optional[str]) -> Optional[str]:
    """Resolve date from the given text."""
    if not text:
        return None
    match = re.match(r'(\d+)年(\d+)月(\d+)日', text)
    if match:
        return f"{match.group(1)}-{match.group(2)}-{match.group(3)}"
    return None


def resolve_price(text: Optional[str]) -> Optional[int]:
    """Resolve price from the given text."""
    if not text:
        return None
    match = re.search(r'([0-9,]+)', text)
    return int(match.group(1).replace(',', '')) if match else None


def enforce_https(url: str) -> str:
    """Enforce HTTPS on the URL."""
    if url.startswith('//'):
        return 'https:' + url
    return url


class Melonbooks:
    def __init__(self):
        self.base_url = 'http://www.melonbooks.co.jp'

    def search(self, text: str, options: SearchOptions) -> List[SearchResult]:
        query_params = {
            'mode': 'search',
            'text_type': 'title' if options.only_search_title else None,
            'name': text,
            'additional': 'pr',
            'category_ids[]': '4',
            'child_category_ids[]': ['12']
        }
        print(query_params)
        print(self.base_url + '/search/search.php')
        response = requests.get(self.base_url + '/search/search.php', params=query_params, proxies=proxies,
                                headers=headers, verify=False)

        html = response.text
        soup = BeautifulSoup(html, 'html.parser')
        result_items = soup.select('.item-list li[class^=product]')
        results = []
        for item in result_items:
            a = item.select_one('.item-image > a')
            results.append(SearchResult(
                provider='Melonbooks',
                title=a['title'].strip(),
                url=self.base_url + a['href']
            ))
        return results

    def detail(self, url: str) -> Optional[Detail]:
        response = requests.get(url)
        html = response.text
        soup = BeautifulSoup(html, 'html.parser')
        title = soup.select_one('.page-header').text.strip() if soup.select_one('.page-header') else ''
        date = resolve_date(soup.select_one('.row_sale_date').text.strip() if soup.select_one('.row_sale_date') else '')
        price = resolve_price(soup.select_one('.price .yen').text.strip() if soup.select_one('.price .yen') else '')
        priv_items = soup.select('.priv-item')
        items = []
        for item in priv_items:
            img = item.select_one('.priv_img')['src']
            img = enforce_https(img)
            info = item.select_one('.priv-item_info').text.strip() if item.select_one('.priv-item_info') else ''
            items.append(DetailItem(image=img, description=remove_extra_spaces(info)))
        return Detail(
            provider='Melonbooks',
            title=title,
            date=date,
            price=price,
            url=url,
            items=items
        )
