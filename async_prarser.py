import asyncio, time
from icecream import ic
from bs4 import BeautifulSoup as bs
from lxml import html
from httpx import AsyncClient
import openpyxl
from openpyxl import Workbook


async def dict_to_excel(data: list, filename: str):
    wb = Workbook()
    ws = wb.active
    ws.append(['title', 'text', 'image'])
    for item in data:
        ws.append([item['title'], '\n'.join(item['text']), '\n'.join(item['image'])])
    wb.save(filename)

async def get_html(url: str):
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.142.86 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    }
    client = AsyncClient()
    response = await client.get(url, headers=headers)
    await asyncio.sleep(1.5)
    return response.text


async def get_soup_data(data: str):
    soup = bs(data, 'lxml')
    # tree = html.fromstring(data)
    title = soup.find('h1').text
    texts = soup.find_all('p')
    text = [text.text for text in texts]
    images = soup.find_all('img')
    image = [image.get('srcset') if image.get('srcset') else image.get('src') for image in images]
    ic(image)
    return {'title': title, 'text': text, 'image': image}


async def get_soup_url(data: str):
    soup = bs(data, 'lxml')
    urls = soup.find_all('a', {'class': 'dY4O3hR0 dY4O3hR0'})
    list_url = []
    for url in urls:
        list_url.append(url.get('href'))
    return list_url


async def main(urls: list):
    tasks = [get_html(url) for url in urls]
    results = await asyncio.gather(*tasks)
    all_list = []
    dict_list = []
    for res in results:
        process_res = await get_soup_url(res)
        all_list.extend(process_res)
    results = [get_html(url) for url in all_list]
    process_res = await asyncio.gather(*results)
    datas = [get_soup_data(res) for res in process_res]
    dict_ = await asyncio.gather(*datas)
    for data in dict_:
        dict_list.append(data)
    await dict_to_excel(dict_list, 'test.xlsx')


if __name__ == '__main__':
    num = input('Input number: ')
    url = 'https://4pda.to/page/{num}/'
    urls = [url.format(num=i) for i in range(1, int(num) + 1)]
    asyncio.run(main(urls))