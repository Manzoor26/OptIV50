import requests
import pandas as pd
from bs4 import BeautifulSoup
import random
from lxml.html import fromstring
from itertools import cycle
import pygsheets as pg
ivThreshold = 50 #Set Min IV = 50
#Pushing to Gsheet
gs = pg.authorize(service_file='YOUR_CREDENTIAL_FILE_HERE.json')
try:
    gs.delete("NSEOptionswithIV>50")
except:
    sh = gs.create("NSEOptionswithIV>50")
sh=gs.open("NSEOptionswithIV>50")
sh.share('anyone', role='reader', expirationTime=None, is_group=False)
sh.share('YOUR_EMAIL_HERE', role='writer', expirationTime=None, is_group=False)
try:
    wsIV = sh.worksheet_by_title("OptionswithIV>50")
except:
    wsIV = sh.add_worksheet(title="OptionswithIV>50", rows="1", cols="8")
values = ['Stock','Type','Strike','LTP','IV','OI','COI','VOL']
for x in range(8):
    wsIV.update_cell((1,x+1), values[x])
#Fetch Proxies
def get_proxies():
    url = 'https://www.sslproxies.org/'
    response = requests.get(url)
    parser = fromstring(response.text)
    proxies = set()
    for i in parser.xpath('//tbody/tr')[:10]:
        if i.xpath('.//td[7][contains(text(),"yes")]'):
            proxy = ":".join([i.xpath('.//td[1]/text()')[0], i.xpath('.//td[2]/text()')[0]])
            proxies.add(proxy)
    return proxies
proxies = get_proxies()
print(proxies)
proxy_pool = cycle(proxies)
user_agent_list = [
   #Chrome
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36',
    'Mozilla/5.0 (Windows NT 5.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36',
    #Firefox
    'Mozilla/4.0 (compatible; MSIE 9.0; Windows NT 6.1)',
    'Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko',
    'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0)',
    'Mozilla/5.0 (Windows NT 6.1; Trident/7.0; rv:11.0) like Gecko',
    'Mozilla/5.0 (Windows NT 6.2; WOW64; Trident/7.0; rv:11.0) like Gecko',
    'Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko',
    'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.0; Trident/5.0)',
    'Mozilla/5.0 (Windows NT 6.3; WOW64; Trident/7.0; rv:11.0) like Gecko',
    'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0)',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64; Trident/7.0; rv:11.0) like Gecko',
    'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; WOW64; Trident/6.0)',
    'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; Trident/6.0)',
    'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; .NET CLR 2.0.50727; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729)'
]

#Fetch FNO Stocks
fnoStocks = []
url= 'https://www.nseindia.com/live_market/dynaContent/live_watch/stock_watch/foSecStockWatch.json'
#Get a proxy from the pool
proxy = next(proxy_pool)
user_agent = random.choice(user_agent_list)
headers = {'User-Agent': user_agent}
r = requests.get(url,headers = headers,proxies={"http": proxy, "https": proxy})
data = r.json()
fnoStocks = []
stockList = data['data']
for symbol in stockList:
    fno = (symbol['symbol'])
    fnoStocks.append(fno)
fnoStocks.sort()
print(fnoStocks)
col_list_head = ['Stock','Type','Strike','LTP','IV','OI','COI','VOL']

data_Req = []

for stock in fnoStocks:

    Base_url =(f"https://www.nseindia.com/live_market/dynaContent/live_watch/option_chain/optionKeys.jsp?symbolCode=2772&symbol={stock}&instrument=OPTSTK&date=-&segmentLink=17&segmentLink=17")

    page = requests.get(Base_url)
    soup = BeautifulSoup(page.content, 'html.parser')

    table_it = soup.find_all(class_="opttbldata")
    table_cls_1 = soup.find_all(id="octable")
    col_list = []

    # Fetch headers from table
    for mytable in table_cls_1:
        table_head = mytable.find('thead')

        try:
            rows = table_head.find_all('tr')
            for tr in rows:
                cols = tr.find_all('th')
                for th in cols:
                    er = th.text
                    ee = er.encode('utf8')
                    ee = str(ee, 'utf-8')
                    col_list.append(ee)
        except:
            print ("no thead")

    table_cls_2 = soup.find(id="octable")
    all_trs = soup.select('#octable > tr')
    req_row = soup.select('#octable > tr')
    tdf = pd.DataFrame(index=range(0,len(req_row)-3) , columns=col_list_head)
    row_marker = 0

    for row_number, tr_nos in enumerate(req_row):

        # Check if row has data
        if row_number <=1 or row_number == len(req_row)-1:
            continue

        td_columns = tr_nos.find_all('td')

        # Columns that we require
        optType = ['CE','PE']
        cols = [[11,5,4,1,2,3],[11,17,18,21,20,19]]
        ivData = [4,18]
        # Loop for CE and PE
        for type in range(2):
            col = 2
            tdf_data = td_columns[ivData[type]].get_text().strip('\n\r\t":,- ').replace(',','')
            if(tdf_data == "-" or tdf_data == ""):
                tdf_data="0"
            if(float(tdf_data) > ivThreshold):
                tdf.at[row_marker,'Stock']= stock
                tdf.at[row_marker,'Type']= optType[type]
                for c in cols[type]:
                    tdf_data = td_columns[c].get_text().strip('\n\r\t":, ').replace(',','')
                    if(tdf_data=="-" or tdf_data==""):
                        tdf_data="0"
                    tr = tdf_data.encode('utf-8')
                    tr = str(tr, 'utf-8')
                    tdf.at[row_marker,col_list_head[col]]= tr
                    col += 1
                row_marker += 1
    print(tdf.dropna())
    data_Req.append(tdf.dropna())
result = pd.concat(data_Req)

# Write to gsheet
wsIV.set_dataframe(result,'A1', copy_index=False, copy_head=True, fit=True, escape_formulae=False)
