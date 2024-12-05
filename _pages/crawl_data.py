# 根据URL爬取网页页面，然后根据正则表达式来得到乌尔都语，并根据句子长度来进行过滤

import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
import re
import time
import os
import fasttext
from argparse import ArgumentParser

model = fasttext.load_model("/data/cuimenglong/CrawlData/models/lid.176.bin")

total_data = set()
requests.packages.urllib3.disable_warnings()

proxies = {
    'http': 'http://172.18.163.116:10809',
    'https': 'http://172.18.163.116:10809'
}

headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
}

parser = ArgumentParser()
parser.add_argument('--language', type=str, required=True)
parser.add_argument('--web', type=str, required=True)

args = parser.parse_args()


requests.packages.urllib3.disable_warnings()

fp = open(f'/data/cuimenglong/CrawlData/data/noise_data/{args.language}/{args.language}_{args.web}.txt', 'w', encoding='utf-8', buffering=1)


def crawl_data(url):
   try:
      response = requests.get(url, headers=headers, proxies=proxies, timeout=5, verify=False)
   except:
      time.sleep(1)
      return

   if not response.ok:
      return
   data = response.text
   soup = BeautifulSoup(data, 'html.parser')
   a_tags = soup.find_all('a')
   p_tags = soup.find_all('p')
   h1_tags = soup.find_all('h1')
   h2_tags = soup.find_all('h2')
   h3_tags = soup.find_all('h3')
   h4_tags = soup.find_all('h4')
   h5_tags = soup.find_all('h5')
   tags = a_tags + p_tags + h1_tags + h2_tags + h3_tags + h4_tags + h5_tags
   for tag in tags:
      text = tag.text.replace('\n', '').replace('\t', ' ').strip()
      # 将连续的空格替换为一个空格
      text = re.sub(r'\s+', ' ', text)
      if model.predict([text])[0][0][0] == f'__label__{args.language}' and text not in total_data:
         total_data.add(text)
         fp.write(text + '\n')


types = ['.jpg', '.png', '.mp3', '.mp4', '.jpeg', 'download']
   
with open(f'/data/cuimenglong/CrawlData/data/urls/{args.language}/{args.language}_{args.web}_url.txt', 'r', encoding='utf-8') as f:
   urls = f.readlines()
   bar = tqdm(total=len(urls))
   for url in urls:
      url = url.strip()
      flag = False
      for tpe in types:
         if tpe in url: 
            flag = True
            break
      if flag: continue
      bar.set_description(f'total: {len(total_data)}')
      crawl_data(url)
      bar.update(1)