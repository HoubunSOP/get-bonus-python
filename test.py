from melonbooks import Melonbooks, resolve_date
from models import SearchOptions

melonbooks = Melonbooks()


async def main():
    # 调用 search 方法进行搜索
    search_results = melonbooks.search('まちカドまぞく', options=SearchOptions(only_search_title=True, category=''))
    for result in search_results:
        print(result.title, result.url)

    # 调用 detail 方法获取详细信息
    detail_info = detail(search_results[0].url)
    if detail_info:
        print('Title:', detail_info.title)
        print('Date:', detail_info.date)
        print('Price:', detail_info.price)
        print('URL:', detail_info.url)
        for item in detail_info.items:
            print('Image:', item.image)
            print('Description:', item.description)


async def test():
    resolve_date('発売日：2022年04月27日')


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
