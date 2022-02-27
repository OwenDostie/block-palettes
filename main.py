import re
import requests
import pandas as pd
from ttictoc import tic, toc
from bs4 import BeautifulSoup

# https://www.geeksforgeeks.org/python-web-scraping-tutorial/

# print(soup.prettify())

df = pd.DataFrame(columns= ['palette_number', 'likes', 'date_posted', 'username', 'block1', 'block2', 'block3', 'block4', 'block5', 'block6'])
start_index = 1; end_index = 23270

failed_queries = []

tic()
for palette_number in range(start_index, end_index + 1, 100):
    try: 
        # pull page
        r = requests.get(f'https://www.blockpalettes.com/palette/{palette_number}')
        soup = BeautifulSoup(r.content, 'html.parser')

        # scrape blocks
        s = soup.find('div', class_='blocks')
        lines = s.find_all('img')
        block_ids = [re.search('(?<=block\/).*(?=.png)', x['src']).group() for x in lines]

        # scrape palette#, likes, date_posted, username
        likes = soup.find('span', class_='likes_count').text.strip()
        date_posted = soup.find('div', class_='time').text.strip()
        try: username = soup.find('a', class_='userLink').text.strip()[:-5]
        except: username = ""

        # add to df
        df.loc[len(df.index)] = [palette_number, likes, date_posted, username] + block_ids

        if palette_number % 1000 == 1:
            df.to_csv('medfile.csv')
    except Exception as e:
        print(f'palette_number:{palette_number}', e)
        failed_queries.append(str(palette_number))

# output to console
print(len(df), 'queries')
print(round(toc(), 1), 'seconds')
print()
print(df)

# write to files
df.to_csv('medfile.csv')
with open('failed-queries.txt', 'w') as f:
    f.write(''.join(failed_queries))

# 23270 palettes total
# 100 queries, 59.5 seconds - 13938 seconds total query, less than 4 hours