#!/usr/bin/env python
# coding: utf-8

# In[2]:


import urllib.request
import json
import pandas as pd
import bs4
import numpy as np


# In[3]:


response = urllib.request.urlopen('http://www.burgerking.co.kr/api/store/searchmap/empty/?areacd=')
bgk_data = json.loads(response.read().decode('utf-8'))
bgk_tbl = pd.DataFrame(bgk_data)
bgk_tbl.head()


# In[4]:


bgk_locs = pd.DataFrame(bgk_tbl['NewAddr'].apply(lambda v: v.split()[:2]).tolist(),
                        columns=('d1', 'd2'))
bgk_locs.head()


# In[5]:


bgk_locs['d1'].unique()


# In[6]:


d1_aliases = """서울시:서울특별시 충남:충청남도 강원:강원도 경기:경기도 충북:충청북도 경남:경상남도 경북:경상북도
전남:전라남도 전북:전라북도 제주도:제주특별자치도 제주:제주특별자치도 대전시:대전광역시 대구시:대구광역시 인천:인천광역시
광주시:광주광역시 울산시:울산광역시 부산시:부산광역시 부산:부산광역시 인천시:인천광역시"""
d1_aliases = dict(aliasset.split(':') for aliasset in d1_aliases.split())
bgk_locs['d1'] = bgk_locs['d1'].apply(lambda v: d1_aliases.get(v, v))


# In[7]:


bgk_locs[bgk_locs['d1'] == '전주시']


# In[8]:


bgk_locs.iloc[341] = ['전라북도', '전주시']


# In[9]:


bgk_locs[bgk_locs['d1'] == '세종특별자치시']


# In[10]:


bgk_locs.iloc[210] = ['충청남도', '세종시']
bgk_locs.iloc[232] = ['충청남도', '세종시']
bgk_locs.iloc[233] = ['충청남도', '세종시']


# In[11]:


bgk_locs['d2'].unique()


# In[12]:


bgk_locs[bgk_locs['d2'] == '송도국제대로']


# In[13]:


bgk_locs.iloc[182] = ['인천광역시', '연수구']


# In[14]:


B = bgk_locs.apply(lambda r: r['d1'] + ' ' + r['d2'], axis=1).value_counts()
B.head()


# In[15]:


MCDONALDS_URL = 'http://www.mcdonalds.co.kr/www/kor/findus/district.do?sSearch_yn=Y&skey=2&pageIndex={page}&skeyword={location}'


# In[16]:


def search_mcdonalds_stores_one_page(location, page):
    response = urllib.request.urlopen(
        MCDONALDS_URL.format(location=urllib.parse.quote(location.encode('utf-8')), page=page))
    mcd_data = response.read().decode('utf-8')
    soup = bs4.BeautifulSoup(mcd_data)
    
    ret = []
    for storetag in soup.findAll('dl', attrs={'class': 'clearFix'}):
        storename = storetag.findAll('a')[0].contents[-1].strip()
        storeaddr = storetag.findAll('dd', attrs={'class': 'road'})[0].contents[0].split(']')[1]
        storeaddr_district = storeaddr.split()[:2]
        ret.append([storename] + storeaddr_district)

    return pd.DataFrame(ret, columns=('store', 'd1', 'd2')) if ret else None

# 여러 페이지를 쭉 찾아서 안 나올 때 까지 합친다.
def search_mcdonalds_stores(location):
    from itertools import count
    
    found = []
    for pg in count():
        foundinpage = search_mcdonalds_stores_one_page(location, pg+1)
        if foundinpage is None:
            break
        found.append(foundinpage)

    return pd.concat(found)


# In[17]:


search_mcdonalds_stores('전라북도').head()


# In[18]:


found = []
for distr in bgk_locs['d1'].unique():
    print("processing-->",distr)
    found.append(search_mcdonalds_stores(distr))
mcd_tbl = pd.concat(found)


# In[19]:


mcd_tbl['store'].value_counts().head()


# In[20]:


M = mcd_tbl.apply(lambda r: r['d1'] + ' ' + r['d2'], axis=1).value_counts()
M.head()


# In[21]:


# response = urllib.request.urlopen(KFC_DISTSEARCH_URL.format(code=1120))
# kfc_data = response.read().decode('utf-8')
# soup = bs4.BeautifulSoup(kfc_data)
# print(soup.findAll('script')[-3].text.split(" ")[10][-2:])
# print(soup.findAll('script')[-3].text.split(" ")[11])
def kfc_search_stores_in_dist(num):
    KFC_DISTSEARCH_URL = 'https://www.kfckorea.com/store/findStore/{code}'
    response = urllib.request.urlopen(KFC_DISTSEARCH_URL.format(code=num))
    kfc_data = response.read().decode('utf-8')
    soup = bs4.BeautifulSoup(kfc_data)
    store_name_idx = soup.findAll('script')[-3].text.find("store_name\":\"")
    store_add_idx = soup.findAll('script')[-3].text.find("old_address\":\"")
    
    store_name = soup.findAll('script')[-3].text[store_name_idx+13:].split("\"")[0]
    store_add = soup.findAll('script')[-3].text[store_add_idx+14:].split("\"")[0]
    if len(store_name) < 10:
        return store_name, store_add
    else:
        return None, None


# In[22]:


kfc_list = []
for i in range(1000, 2000): 
    if i%100 == 0:
        print("")
        print("processing store code", i)
    loc1, loc2 = kfc_search_stores_in_dist(i)
    if loc1 != None:
        print("name-", loc1, "/ address-",loc2.split()[0], "-", loc2.split()[1], end = " ")
        kfc_list.append([loc1, loc2.split()[0], loc2.split()[1]])
print("")


# In[23]:


print(len(kfc_list))
kfc_tbl = pd.DataFrame(kfc_list, columns=('store', 'd1', 'd2'))
# kfc_alldist = pd.DataFrame(np.array(kfc_list), columns=('d1', 'd2'))
# kfc_alldist.head()


# In[24]:


kfc_tbl['d1'].unique()


# In[25]:


kfc_tbl[kfc_tbl['d1']=="세종특별자치시"]


# In[26]:


kfc_tbl.iloc[83] = ["세종이마트", "충청남도", "세종시"]


# In[27]:


d1_aliases = """서울:서울특별시 인천:인천광역시 강원:강원도 경기:경기도 충남:충청남도 충북:충청북도 경남:경상남도 경북:경상북도
전남:전라남도 전북:전라북도 대전:대전광역시 대구:대구광역시 광주:광주광역시 울산:울산광역시 부산:부산광역시"""
d1_aliases = dict(aliasset.split(':') for aliasset in d1_aliases.split())
kfc_tbl['d1'] = kfc_tbl['d1'].apply(lambda v: d1_aliases.get(v, v))


# In[28]:


K = kfc_tbl.apply(lambda r: r['d1'] + ' ' + r['d2'], axis=1).value_counts()
K.head()


# In[29]:


BMK = pd.DataFrame({'B': B, 'M': M, 'K': K}).fillna(0)
BMK['total'] = BMK.sum(axis=1)
BMK = BMK.sort_values(by=['total'], ascending=False)
BMK.head(10)


# In[30]:


from matplotlib import pyplot as plt
from matplotlib import rcParams, style
style.use('ggplot')
rcParams['font.size'] = 12


# In[31]:


plt.figure(figsize=(4, 3))
BMK.sum(axis=0).iloc[:3].plot(kind='bar')


# In[32]:


import scipy.stats


# In[33]:


fig = plt.figure(figsize=(9, 3))

def plot_nstores(b1, b2, label1, label2):
    plt.scatter(BMK[b1] + np.random.random(len(BMK)),
                BMK[b2] + np.random.random(len(BMK)),
                edgecolor='none', alpha=0.75, s=6, c='black')
    plt.xlim(-1, 15)
    plt.ylim(-1, 15)
    plt.xlabel(label1)
    plt.ylabel(label2)
    
    r = scipy.stats.pearsonr(BMK[b1], BMK[b2])
    plt.annotate('r={:.3f}'.format(r[0]), (10, 12.5))

ax = fig.add_subplot(1, 3, 1)
plot_nstores('B', 'M', 'Burger King', "McDonald's")

ax = fig.add_subplot(1, 3, 2)
plot_nstores('B', 'K', 'Burger King', 'KFC')

ax = fig.add_subplot(1, 3, 3)
plot_nstores('M', 'K', "McDonald's", 'KFC')

plt.tight_layout()


# In[34]:


plt.figure(figsize=(4, 3))
for col, label in [('B', 'Burger King'), ('K', 'KFC'), ('M', "McDonald's")]:
    cumulv = np.cumsum(sorted(BMK[col], reverse=True)) / BMK[col].sum()
    plt.plot(cumulv, label='{} ({})'.format(label, int(BMK[col].sum())))
plt.legend(loc='best')
plt.xlabel('Number of districts (si/gun/gu)')
plt.ylabel('Cumulative fraction')


# In[75]:


LOTTERIA_URL = 'http://www.lotteria.com/Shop/Shop_Ajax.asp'
LOTTERIA_VALUES = {
    'Page': 1, 'PageSize': 2000, 'BlockSize': 2000,
    'SearchArea1': '', 'SearchArea2': '', 'SearchType': "TEXT",
    'SearchText': '', 'SearchIs24H': '', 'SearchIsWifi': '',
    'SearchIsDT': '', 'SearchIsHomeService': '', 'SearchIsGroupOrder': '',
    'SearchIsEvent': ''}
LOTTERIA_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.10; rv:12.0) Gecko/20100101',
    'Host': 'www.lotteria.com',
    'Accept': 'text/html, */*; q=0.01',
    'Accept-Language': 'en-us,en;q=0.5',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'X-Requested-With': 'XMLHttpRequest',
    'Referer': 'http://www.lotteria.com/Shop/Shop_List.asp?Page=1&PageSize=2000&BlockSize=2000&Se'
               'archArea1=&SearchArea2=&SearchType=TEXT&SearchText=&SearchIs24H=&SearchIsWifi=&Se'
               'archIsDT=&SearchIsHomeService=&SearchIsGroupOrder=&SearchIsEvent=',
}


# In[76]:


postdata = urllib.parse.urlencode(LOTTERIA_VALUES).encode('utf-8')
req = urllib.request.Request(LOTTERIA_URL, postdata, LOTTERIA_HEADERS)
response = urllib.request.urlopen(req)
ltr_data = response.read().decode('utf-8')
soup = bs4.BeautifulSoup(ltr_data)


# In[80]:


found = []
for tag in soup.findAll('tr', {'class': 'shopSearch'}):
    subtag = tag.findAll('td', {'style': 'padding-right:10px;'})
    for sub in subtag:
        found.append(sub.text)

for n in range(len(found)):
    print(n, found[n], end=" / ")


# In[48]:


get_ipython().system('pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org selenium')


# In[49]:


from selenium import webdriver


# In[62]:


driver = webdriver.Chrome('./driver/chromedriver')
driver.get("https://map.naver.com/")


# In[81]:


name = found[154]
str = "롯데리아" + name + "점"
driver.find_element_by_id('search-input').clear()
driver.find_element_by_id('search-input').send_keys(str)
element = driver.find_element_by_xpath("""//*[@type="submit"]""")
driver.execute_script("arguments[0].click();", element)
    
driver.implicitly_wait(2)
    
try:
    html = driver.page_source
    soup = bs4.BeautifulSoup(html, 'html.parser')
    ultag = soup.find("ul", "lst_site")
    addr = ultag.find("dd", "addr").text
    print([name, addr.split()[0], addr.split()[1]])
except:
    pass


# In[82]:


ltr_list = []
for name in found:
    str = "롯데리아" + name + "점"
    driver.find_element_by_id('search-input').clear()
    driver.find_element_by_id('search-input').send_keys(str)
    element = driver.find_element_by_xpath("""//*[@type="submit"]""")
    driver.execute_script("arguments[0].click();", element)
    
    driver.implicitly_wait(2)
    
    try:
        html = driver.page_source
        soup = bs4.BeautifulSoup(html, 'html.parser')
        ultag = soup.find("ul", "lst_site")
        addr = ultag.find("dd", "addr").text
        ltr_list.append([name, addr.split()[0], addr.split()[1]])
    except:
        print(name, end=" / ")
        pass
print("Fin")


# In[ ]:


def get_lotteria2():
    time.sleep(2)
    
    store_list = []
    results = []
    prev_first = "없다요"
    mustRe = True
    mustNext = True
    
    for n in range(1, 135):
        # 페이지 로드 확인
        while mustRe == True:
            time.sleep(1)
            html = driver.page_source
            soup = bs4.BeautifulSoup(html, 'html.parser')
            tmp = soup.find_all("td","first num")
            
            # 이전 페이지와 파싱된 매장 이름이 같으면 다시 로드를 기다린다.
            if prev_first == tmp[0].text:
                print("|", end="")
                mustRe = True
            else:
                mustRe = False
                print(")")
                
        # 로드가 되었으면 파싱한 것을 저장
        store_list += tmp
        prev_first = tmp[0].text
        
        # 현재페이지가 끝이 아니라면 다음 페이지 선택
        if n < 134:
            mustRe = True
            
            # 10페이지마다 저장상태 확인 메세지 및 화살표 누르기
            if n%10 == 0:
                print("page", n, tmp[0].text)
                ele = driver.find_element_by_xpath("""//*[@class="go next"]""")
                driver.execute_script("arguments[0].click();", ele)
                
                # 화살표 누른 뒤, 로딩 기다리기
                mustNext = True
                while mustNext == True:
                    time.sleep(3)
                    html = driver.page_source
                    soup = bs4.BeautifulSoup(html, 'html.parser')
                    tdiv = soup.find("div", "paging_basic")
                    tmpN = tdiv.find_all("a")[2]
            
                    if n+1 != int(tmpN.text):
                        print("3 seconds more delay for load page / finding ", n+1, "now, but I got", tmpN.text)
                        mustNext = True
                    else:
                        mustNext = False
            
            # 다음 페이지(n+1)로 이동
            xpath1 = """//*[@href="javascript: goPage("""
            xpath2 = str(n+1)
            xpath3 = """);"]"""
            ele = driver.find_element_by_xpath(xpath1+xpath2+xpath3)
            driver.execute_script("arguments[0].click();", ele)
            

    for store in store_list:
        results.append(store.text)

    return results


# In[ ]:





# In[ ]:




