import re
from bs4 import BeautifulSoup

with open('farpost_auto.html', encoding='utf-8') as f:
    html = f.read()

soup = BeautifulSoup(html, 'html.parser')
links = soup.find_all('a', href=True)
for a in links:
    if '/auto/' in a['href'] or '/vladivostok/auto/' in a['href']:
        print(a.get('class'), a.text.strip(), a['href'])
