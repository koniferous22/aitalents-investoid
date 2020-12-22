import requests
from bs4 import BeautifulSoup
from os import path
from itertools import takewhile

num_of_total_pages = 254

def removesuffix(string, suffix):
    if suffix and string.endswith(suffix):
        return string[:-len(suffix)]
    else:
        return string[:]

def get_pr_article_urls_per_page(page):
    url = f'https://www.allianz.com/en/press/news.result.html/{page}.html'
    soup = BeautifulSoup(requests.get(url).text, 'html.parser')
    labels = soup.find_all('h5', class_='c-teaser--press-release__article__heading')
    return list(map(lambda el: el.find('a').attrs['href'], labels))

def get_plaintext(el):
    return [ descendant.string.strip() for descendant in el.descendants if hasattr(descendant, 'string') and not hasattr(descendant, 'children') and descendant.string is not None ]

def process_article_title(title_el):
    heading_els = title_el.find_all('div', class_='headline', recursive=False)
    return [ entry for el in heading_els for entry in get_plaintext(el) ]

def process_article(pr_element):
    content = filter(lambda el: any(map(lambda pattern: pattern in el.attrs['class'], ['text','headline'])), takewhile(lambda el: 'experiencefragment' not in el.attrs['class'], pr_element.find_all('div',recursive=False)))
    return [
        entry for el in content for entry in get_plaintext(el)
    ]



dirname = path.dirname(__file__)
output_directory = path.realpath(path.join(dirname, '../../data/alianz'))

def get_article_contents(url):
    soup = BeautifulSoup(requests.get(url).text, 'html.parser')
    content_elements = soup.find_all('div', class_='c-wrapper')
    title_element = content_elements[0]
    pr_element = content_elements[1]
    filename = path.join(output_directory, removesuffix(url.split('/')[-1], '.html'))
    print(f'Filename: {filename}')
    with open(f'{filename}.txt', 'w') as  f:
        f.writelines(list(map(lambda x: x + '\n', process_article_title(title_element) + process_article(pr_element))))



# print(get_pr_article_urls_per_page(1))
for page in range(1,num_of_total_pages + 1):
    print(f'Processing page {page}')
    articles = get_pr_article_urls_per_page(page)
    for article_url in articles:
        print(f'Processing url {article_url}')
        get_article_contents(f'https://www.allianz.com{article_url}')
print('Done')


