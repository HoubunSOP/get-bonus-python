import asyncio
from typing import Dict, List, Optional
from models import SearchResult, Detail, SearchOptions, Provider


async def _search_provider(provider: 'Provider', text: str, options: SearchOptions,
                           only_search_title: bool) -> tuple:
    try:
        resp = await provider.search(text, options)

        if only_search_title:
            pieces = [piece for piece in text.split(' ') if piece]
            filtered = [result for result in resp if all(piece in result.title for piece in pieces)]
            resp[:] = filtered

        return (provider.id, resp)
    except Exception as error:
        print(f"搜索 {provider.id} 失败: {text}")
        print(error)
        return (provider.id, [])


class Scraper:
    def __init__(self, *providers: 'Provider'):
        self.providers = providers

    async def search(self, text: str, options: Optional[SearchOptions] = {}) -> Dict[str, List[SearchResult]]:
        only_search_title = options.get('onlySearchTitle', True)

        results = await asyncio.gather(*[
            _search_provider(provider, text, options, only_search_title)
            for provider in self.providers
        ])

        return dict(results)

    async def get_detail(self, platform: str, url: str) -> Optional[Detail]:
        providers = [p for p in self.providers if p.id == platform]
        if len(providers) == 1:
            return await providers[0].detail(url)
        else:
            return None

    async def get_all_details(self, search: Dict[str, List[SearchResult]]) -> Dict[str, List[Detail]]:
        return {
            id: [detail for detail in await asyncio.gather(*[
                self.get_detail(t.provider, t.url) for t in list
            ]) if detail is not None]
            for id, list in search.items()
        }
