from bs4 import BeautifulSoup
from datetime import datetime
import pandas as pd
import re
import requests
import traceback
from ttictoc import tic, toc

# https://www.blockpalettes.com/palettes
# https://www.geeksforgeeks.org/python-web-scraping-tutorial/


df = pd.DataFrame(columns= ['palette_number', 'page_number', 'likes', 'date_posted', 'block1', 'block2', 'block3', 'block4', 'block5', 'block6'])
start_index = 1; end_index = 545

failed_queries = []

tic()
for page_number in range(start_index, end_index + 1):
    # pull page
    r = requests.get(f'https://www.blockpalettes.com/palettes?p={page_number}')
    soup = BeautifulSoup(r.content, 'html.parser')
    # print(soup.prettify())
    # scrape for palette-float thumbnails, then iterate
    palette_list = soup.find('div', class_='palettes').find_all('div', class_='palette-float')

    for palette in palette_list:
        try: 
            palette_number = re.search('(?<=palette\/).*', palette.findChildren("a" , recursive=False)[0].get('href')).group().strip()
            blocks = palette.find_all('img', class_='block')
            block_ids = [re.search('(?<=block\/).*(?=.png)', x['src']).group() for x in blocks]
            likes = palette.find('div', class_='time left half').text.strip()
            try: date_posted = palette.find('div', class_='time right half').text.strip()
            except: date_posted = 'Staff Pick'

            # add to df
            df.loc[len(df.index)] = [palette_number, page_number, likes, date_posted] + block_ids

        except Exception:
            print(f'Page {page_number}:', traceback.format_exc())
            print(palette)
            print(palette.findChildren("a" , recursive=False))
            failed_queries.append(str(page_number))

# output to console
print(end_index - start_index + 1, 'queries')
print(round(toc(), 1), 'seconds')
print(len(failed_queries), 'errors')
print()
print(df)

# write to files
df.to_csv('palettes.csv')
with open('metadata.txt', 'w') as f:
    f.write(f'''last_updated: {datetime.now().strftime("%d/%m/%Y %H:%M:%S")},
    start_index: {start_index},
    end_index: {end_index},
    failed_queries: ''' + ''.join(failed_queries))