
from datetime import datetime
import requests

now = datetime.now().strftime('%Y%m%d')
print(now)
url = f"https://forex-news-alerts.p.rapidapi.com/api/v1/ForexNewsUpdates/Req12345678/Gold/{now}"

headers = {
	"X-RapidAPI-Key": "69cd2eb0cbmsh8a2d0881e2f20d3p1a7228jsn86d83ccc3a44",
	"X-RapidAPI-Host": "forex-news-alerts.p.rapidapi.com"
}

response = requests.get(url, headers=headers)

d= {}
i = 0
print(response.json())
while True:
    try:
        a = response.json()['results'][i]['title']
        b = response.json()['results'][i]['publicationTimeInGmt']
        d[b] = a
        print(b, a )
        i += 1
    except:
        i = 0
        break

with open('news.csv', 'a') as file:
    for i,j in d.items():
        file.writelines(i)
        file.write('\t')
        file.writelines(j)
        file.writelines("\n")