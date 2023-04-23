import os
import re
import requests
import concurrent.futures
import logging
from bs4 import BeautifulSoup

articles = []
# 从网页中提取多个 url 和标题 以及日期
# <h3 class="Havebg">
#   <a target="_blank" class="sys_url" href="http://phtv.ifeng.com/program/qqsrx/detail_2014_08/26/38504520_0.shtml">周轶君：国家越是封闭 社会思潮越开放</a>
# </h3>
# logging.basicConfig(filename='error.log', format='[%(levelname)s] %(asctime)s %(message)s', level=logging.ERROR)
logger = logging.getLogger()
logger.setLevel(logging.INFO)
# create file handler which logs even debug messages
fh = logging.FileHandler('error.log')
fh.setLevel(logging.INFO)
# create console handler with a higher log level
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
# create formatter and add it to the handlers
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
ch.setFormatter(formatter)
fh.setFormatter(formatter)
# add the handlers to logger
logger.addHandler(ch)
logger.addHandler(fh)

def log_error(msg):
    print("ERROR: " + msg)
    logger.error(msg)

def craw_main():
    url_tpl = "http://phtv.ifeng.com/program/qqsrx/list_0/{}.shtml"
    from_index = 0
    end_index = 55
    for page in range(from_index, end_index + 1):
        url = url_tpl.format(page)
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        items = soup.find_all('h3', {'class': 'Havebg'})
        for item in items:
            title = item.find('a').text
            url = item.find('a')['href']
            url_to_extract_date = re.sub(r'[_/]', '', url)
            match = re.search(r'\d{8}', url_to_extract_date)
            if match:
                date = match.group()
            else:
                date = ""
                log_error(f"Error extract date: {url}, title: {title}")
                continue
            if not date:
                date = ""
                log_error(f"Error extract date: {url}")
            title = date + ' ' + title
            print(f"Title: {title}\nURL: {url}\n")
            filename = f"{title}.txt"
            if filename in os.listdir():
                print(f"Skip: {filename}")
                continue

            global articles
            articles.append((url, title))


def craw_article(url, title):
    # http://phtv.ifeng.com/program/qqsrx/detail_2014_08/26/38504520_0.shtml
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    # 提取第一页的正文内容
    main_content = soup.find('div', {'id': 'main_content'})
    if not main_content:
        main_content = soup.find('div', {'id': 'artical_real'})
    if not main_content:
        log_error(f" main_content not found: {url}")
        return (None, title, url)
    paragraphs = main_content.find_all('p')
    text = '\n\n'.join([p.text.strip() for p in paragraphs])

    # 查找下一页的链接，并循环提取所有页的正文内容
    original_url = url
    next_page = soup.find('a', {'id': 'pagenext'})
    while next_page and next_page['href'] != 'javascript:void(0);':
        url = next_page['href']
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        main_content = soup.find('div', {'id': 'main_content'})
        if not main_content:
            main_content = soup.find('div', {'id': 'artical_real'})    
        if not main_content:
            log_error(f" main_content not found in sub page: {url}, original url: {original_url}")
            return (None, title, url)
        paragraphs = main_content.find_all('p')
        text += '\n\n' + '\n\n'.join([p.text.strip() for p in paragraphs])
        next_page = soup.find('a', {'id': 'pagenext'})
    
    filename = f"{title}.txt"
    if text:
        with open(filename, 'w') as f:
            f.write(text)
    else:
        log_error(f"error crawl article: {url}, title: {title}")
    return (text, title, url)

def craw_cocurrent():
    # 创建一个线程池并提交任务
    global articles
    with concurrent.futures.ThreadPoolExecutor(max_workers=15) as executor:
        futures = [executor.submit(craw_article, article[0], article[1]) for article in articles]

    # 处理任务结果
    for future in concurrent.futures.as_completed(futures):
        try:
            text, title, url = future.result()
        except Exception as e:
            # 处理异常
            print(e)    
    
if __name__ == '__main__':
    # craw_main()
    craw_main()
    print("count(articles:) " + str(len(articles)))
    craw_cocurrent()
    logging.shutdown()

