#!/usr/bin/env python
# coding: utf-8

# In[2]:


import urllib.request
import json
import pandas as pd
import bs4
import numpy as np


# In[126]:


response = urllib.request.urlopen('http://www.burgerking.co.kr/api/store/searchmap/empty/?areacd=')
bgk_data = json.loads(response.read().decode('utf-8'))
bgk_tbl = pd.DataFrame(bgk_data)
bgk_tbl.head()


# In[127]:


bgk_locs = pd.DataFrame(bgk_tbl['NewAddr'].apply(lambda v: v.split()[:2]).tolist(),
                        columns=('d1', 'd2'))
bgk_locs.head()


# In[128]:


bgk_locs['d1'].unique()


# In[129]:


d1_aliases = """서울시:서울특별시 충남:충청남도 강원:강원도 경기:경기도 충북:충청북도 경남:경상남도 경북:경상북도
전남:전라남도 전북:전라북도 제주도:제주특별자치도 제주:제주특별자치도 대전시:대전광역시 대구시:대구광역시 인천:인천광역시
광주시:광주광역시 울산시:울산광역시 부산시:부산광역시 부산:부산광역시 인천시:인천광역시"""
d1_aliases = dict(aliasset.split(':') for aliasset in d1_aliases.split())
bgk_locs['d1'] = bgk_locs['d1'].apply(lambda v: d1_aliases.get(v, v))


# In[130]:


bgk_locs[bgk_locs['d1'] == '전주시']


# In[131]:


bgk_locs.iloc[341] = ['전라북도', '전주시']


# In[132]:


bgk_locs[bgk_locs['d1'] == '세종특별자치시']


# In[133]:


bgk_locs.iloc[210] = ['충청남도', '세종시']
bgk_locs.iloc[232] = ['충청남도', '세종시']
bgk_locs.iloc[233] = ['충청남도', '세종시']


# In[134]:


bgk_locs['d2'].unique()


# In[135]:


bgk_locs[bgk_locs['d2'] == '송도국제대로']


# In[136]:


bgk_locs.iloc[182] = ['인천광역시', '연수구']


# In[137]:


B = bgk_locs.apply(lambda r: r['d1'] + ' ' + r['d2'], axis=1).value_counts()
B.head()


# In[138]:


MCDONALDS_URL = 'http://www.mcdonalds.co.kr/www/kor/findus/district.do?sSearch_yn=Y&skey=2&pageIndex={page}&skeyword={location}'


# In[139]:


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


# In[140]:


def search_mcdonalds_stores(location):
    from itertools import count
    
    found = []
    for pg in count():
        foundinpage = search_mcdonalds_stores_one_page(location, pg+1)
        if foundinpage is None:
            break
        found.append(foundinpage)

    return pd.concat(found)


# In[141]:


search_mcdonalds_stores('서울특별시').head()


# In[314]:


found = []
for distr in bgk_locs['d1'].unique():
    print("processing-->",distr)
    found.append(search_mcdonalds_stores(distr))
mcd_tbl = pd.concat(found)


# In[315]:


mcd_tbl['store'].value_counts().head()


# In[320]:


mcd_tbl.head()


# In[322]:


mcd_tbl[mcd_tbl['d2']=="광역시"] = ["부산동명대DT점", "부산광역시", "남구"]


# In[321]:


mcd_tbl.iloc[0] = ["부산동명대DT점", "부산광역시", "남구"]


# In[301]:


M = mcd_tbl.apply(lambda r: r['d1'] + ' ' + r['d2'], axis=1).value_counts()
M.head()


# In[145]:


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


# In[146]:


kfc_list = []
count = 0
for i in range(1001, 2101): 
    if i%100 == 0:
        print("processing store code ~", i, " / count : ", count)
        count = 0
    loc1, loc2 = kfc_search_stores_in_dist(i)
    if loc1 != None:
        # print("name-", loc1, "/ address-",loc2.split()[0], "-", loc2.split()[1], end = " ")
        kfc_list.append([loc1, loc2.split()[0], loc2.split()[1]])
        count += 1
        
print(len(kfc_list))


# In[147]:


print(len(kfc_list))
kfc_tbl = pd.DataFrame(kfc_list, columns=('store', 'd1', 'd2'))


# In[148]:


kfc_tbl['d1'].unique()


# In[149]:


kfc_tbl[kfc_tbl['d1']=="세종특별자치시"]


# In[150]:


kfc_tbl.iloc[83] = ["세종이마트", "충청남도", "세종시"]


# In[151]:


d1_aliases = """서울:서울특별시 인천:인천광역시 강원:강원도 경기:경기도 충남:충청남도 충북:충청북도 경남:경상남도 경북:경상북도
전남:전라남도 전북:전라북도 대전:대전광역시 대구:대구광역시 광주:광주광역시 울산:울산광역시 부산:부산광역시"""
d1_aliases = dict(aliasset.split(':') for aliasset in d1_aliases.split())
kfc_tbl['d1'] = kfc_tbl['d1'].apply(lambda v: d1_aliases.get(v, v))


# In[152]:


K = kfc_tbl.apply(lambda r: r['d1'] + ' ' + r['d2'], axis=1).value_counts()
K.head()


# In[302]:


BMK = pd.DataFrame({'B': B, 'M': M, 'K': K}).fillna(0)
BMK['total'] = BMK.sum(axis=1)
BMK = BMK.sort_values(by=['total'], ascending=False)
BMK.head(10)


# In[303]:


from matplotlib import pyplot as plt
from matplotlib import rcParams, style
style.use('ggplot')
rcParams['font.size'] = 12


# In[304]:


plt.figure(figsize=(4, 3))
BMK.sum(axis=0).iloc[:3].plot(kind='bar')


# In[156]:


import scipy.stats


# In[157]:


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


# In[158]:


plt.figure(figsize=(4, 3))
for col, label in [('B', 'Burger King'), ('K', 'KFC'), ('M', "McDonald's")]:
    cumulv = np.cumsum(sorted(BMK[col], reverse=True)) / BMK[col].sum()
    plt.plot(cumulv, label='{} ({})'.format(label, int(BMK[col].sum())))
plt.legend(loc='best')
plt.xlabel('Number of districts (si/gun/gu)')
plt.ylabel('Cumulative fraction')


# In[4]:


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


# In[5]:


postdata = urllib.parse.urlencode(LOTTERIA_VALUES).encode('utf-8')
req = urllib.request.Request(LOTTERIA_URL, postdata, LOTTERIA_HEADERS)
response = urllib.request.urlopen(req)
ltr_data = response.read().decode('utf-8')
soup = bs4.BeautifulSoup(ltr_data)


# In[8]:


found = []
for tag in soup.findAll('tr', {'class': 'shopSearch'}):
    subtag = tag.findAll('td', {'style': 'padding-right:10px;'})
    for sub in subtag:
        st_name = sub.text.replace("D/T", "DT")
        st_name = st_name.replace("D/I","DI")
        st_name = st_name.replace("(상)","")
        st_name = st_name.replace("(하)","")
        found.append(st_name)

for n in range(len(found)):
    print(n+1, found[n], end=" / ")


# In[7]:


get_ipython().system('pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org selenium')


# In[9]:


from selenium import webdriver


# In[10]:


driver = webdriver.Chrome('./driver/chromedriver')
driver.get("https://map.naver.com/")


# In[11]:


from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# In[12]:


# naver map
ltr_list = []
count = 1
for name in found:
    if count%100 == 0:
        print(count,"번째")
    count += 1
    
    driver.get("https://map.naver.com/")
    try:
        element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "search-input"))
        )
    finally:
        pass
    
    str = "롯데리아 " + name + "점"
    driver.find_element_by_id('search-input').clear()
    driver.find_element_by_id('search-input').send_keys(str)
    element = driver.find_element_by_xpath("""//*[@type="submit"]""")
    driver.execute_script("arguments[0].click();", element)
    
    try:
        element = WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.CLASS_NAME, "lsnx"))
        )
        html = driver.page_source
        soup = bs4.BeautifulSoup(html, 'html.parser')
        ultag = soup.find("ul", "lst_site")
        real_name = ultag.find("dt").find("a").text
        addr = ultag.find("dd", "addr").text
        ltr_list.append([name, real_name, addr.split()[0], addr.split()[1]])
    except:
        print(name, end=" / ")
        ltr_list.append([name, None, None, None])
        
    finally:
        pass
print("Fin")


# In[88]:


# kakao map
ltr_list = []
count = 1
for name in found:
    if count%100 == 0:
        print(count,"번째")
    count += 1
    
    str = "https://map.kakao.com/?q=롯데리아 " + name + "점"
    driver.get(str)
    
    element = WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.ID, "info.search.place.list"))
    )
    html = driver.page_source
    soup = bs4.BeautifulSoup(html, 'html.parser')
    ultag = soup.find("ul", {"id": "info.search.place.list"})
    real_name = ultag.find("a", {"data-id": "name"}).text
    addr = ultag.find("p", {"data-id": "address"}).text
    ltr_list.append([name, real_name.replace("롯데리아", "").lstrip(), addr.split()[0], addr.split()[1]])
    
print("Fin")


# In[72]:


len(ltr_list)


# In[71]:


ltr_tbl = pd.DataFrame(ltr_list, columns=('store', 'realname', 'd1', 'd2'))


# In[27]:


ltr_tbl.to_excel('lotteria.xlsx', sheet_name='sheet1')


# In[75]:


ltr_tbl[ltr_tbl['d1'].isnull()]


# In[74]:


ltr_tbl.iloc[0] = ["롯데마트영통", None, "경기도", "수원시"]
ltr_tbl.iloc[24] = ["여수예술랜드", None, "전라북도", "여수시"]
ltr_tbl.iloc[37] = ["대전세이", None, "대전광역시", "중구"]
ltr_tbl.iloc[62] = ["인천공항제2여객터미널3층", None, "인천광역시", "중구"]
ltr_tbl.iloc[80] = ["롯데마트김포한강신도시", None, "경기도", "김포시"]
ltr_tbl.iloc[82] = ["경주보문", None, "경상북도", "경주시"]
ltr_tbl.iloc[94] = ["롯데마트시흥배곧", None, "경기도", "시흥시"]
ltr_tbl.iloc[101] = ["하나로고양", None, "경기도", "고양시"]
ltr_tbl.iloc[108] = ["신부산역사", None, "부산광역시", "동구"]
ltr_tbl.iloc[116] = ["잠실야구장1층", None, "서울특별시", "송파구"]
ltr_tbl.iloc[117] = ["잠실야구장2층", None, "서울특별시", "송파구"]
ltr_tbl.iloc[118] = ["잠실야구장3층", None, "서울특별시", "송파구"]
ltr_tbl.iloc[119] = ["백령도", None, "인천광역시", "옹진군"]
ltr_tbl.iloc[123] = ["롯데백창원식품관", None, "경상남도", "창원시"]
ltr_tbl.iloc[127] = ["원주혁신도시", None, "강원도", "원주시"]
ltr_tbl.iloc[148] = ["수서역사", None, "서울특별시", "강남구"]
ltr_tbl.iloc[155] = ["안성휴게소", None, "경기도", "안성시"]
ltr_tbl.iloc[167] = ["안성맞춤휴게소", None, "경기도", "안성시"]
ltr_tbl.iloc[168] = ["안성맞춤휴게소", None, "경기도", "안성시"]
ltr_tbl.iloc[169] = ["죽암휴게소DT", None, "충청북도", "청주시"]
ltr_tbl.iloc[177] = ["전주하가DI", None, "전라북도", "전주시"]
ltr_tbl.iloc[181] = ["오창2산단", None, "충청북도", "청주시"]
ltr_tbl.iloc[185] = ["현풍테크노폴리스", None, "대구광역시", "달성군"]
ltr_tbl.iloc[194] = ["부산키자니아", None, "부산광역시", "해운대구"]
ltr_tbl.iloc[236] = ["용인휴게소", None, "경기도", "용인시"]
ltr_tbl.iloc[237] = ["패션아일랜드대전", None, "대전광역시", "동구"]
ltr_tbl.iloc[263] = ["롯데이천아울렛", None, "경기도", "이천시"]
ltr_tbl.iloc[385] = ["동대구역사2호", None, "대구광역시", "동구"]
ltr_tbl.iloc[389] = ["화성사강DT", None, "경기도", "화성시"]
ltr_tbl.iloc[415] = ["인천허브DI", None, "인천광역시", "중구"]
ltr_tbl.iloc[418] = ["순천향대학DT", None, "충청남도", "아산시"]
ltr_tbl.iloc[428] = ["투나송내", None, "경기도", "부천시"]
ltr_tbl.iloc[458] = ["원마운트워터파크", None, "경기도", "고양시"]
ltr_tbl.iloc[464] = ["안산반월", None, "경기도", "안산시"]
ltr_tbl.iloc[465] = ["롯데안양", None, "경기도", "안양시"]
ltr_tbl.iloc[467] = ["송산휴게소", None, "경기도", "화성시"]
ltr_tbl.iloc[468] = ["홈플러스포천송우", None, "경기도", "포천시"]
ltr_tbl.iloc[487] = ["홈플러스동광주", None, "광주광역시", "북구"]
ltr_tbl.iloc[494] = ["안양박달DI", None, "경기도", "안양시"]
ltr_tbl.iloc[502] = ["롯데마트시흥", None, "경기도", "시흥시"]
ltr_tbl.iloc[508] = ["서산휴게소(下)", None, "충청남도", "서산시"]
ltr_tbl.iloc[512] = ["홈플러스유성", None, "대전광역시", "유성구"]
ltr_tbl.iloc[513] = ["안양관양", None, "경기도", "안양시"]
ltr_tbl.iloc[516] = ["빅마켓금천", None, "서울특별시", "금천구"]
ltr_tbl.iloc[604] = ["목동행복한백화점", None, "서울특별시", "양천구"]
ltr_tbl.iloc[653] = ["광명역사", None, "경기도", "광명시"]
ltr_tbl.iloc[663] = ["용산역사ST", None, "서울특별시", "용산구"]
ltr_tbl.iloc[671] = ["길음뉴타운점", None, "서울특별시", "성북구"]
ltr_tbl.iloc[746] = ["성남단대", None, "경기도", "성남시"]
ltr_tbl.iloc[755] = ["부천뉴코아", None, "경기도", "부천시"]
ltr_tbl.iloc[767] = ["전주동산", None, "전라북도", "전주시"]
ltr_tbl.iloc[785] = ["대전괴정DT", None, "대전광역시", "서구"]
ltr_tbl.iloc[816] = ["해운대세이브존", None, "부산광역시", "해운대구"]
ltr_tbl.iloc[845] = ["신당역", None, "서울특별시", "중구"]
ltr_tbl.iloc[893] = ["경산롯데씨네마", None, "경상북도", "경산시"]
ltr_tbl.iloc[918] = ["의정부가능역점", None, "경기도", "의정부시"]
ltr_tbl.iloc[936] = ["동아쇼핑반월당", None, "대구광역시", "중구"]
ltr_tbl.iloc[980] = ["의정보금오", None, "경기도", "의정부시"]
ltr_tbl.iloc[993] = ["포항두호", None, "경상북도", "포항시"]
ltr_tbl.iloc[1143] = ["홈플러스영통", None, "경기도", "수원시"]
ltr_tbl.iloc[1240] = ["영천시장", None, "서울특별시", "서대문구"]
ltr_tbl.iloc[1267] = ["성남양지", None, "경기도", "성남시"]
ltr_tbl.iloc[1328] = ["잠실아이스링크", None, "서울특별시", "송파구"]
ltr_tbl.iloc[1329] = ["서울랜드점", None, "경기도", "과천시"]
ltr_tbl.iloc[1338] = ["홈서비스과천", None, "경기도", "과천시"]
ltr_tbl.iloc[1339] = ["홈서비스부암(부산역)", None, "부산광역시", "부산진구"]
ltr_tbl.iloc[1340] = ["홈서비스성황", None, "충청남도", "천안시"]

ltr_tbl.iloc[5] = ["전북진안", "롯데리아 전북진안점", "전라북도", "진안군"]


# In[76]:


ltr_tbl['d1'].unique()


# In[66]:


ltr_tbl[ltr_tbl['d1']=="세종특별자치시"]


# In[67]:


ltr_tbl.iloc[189] = ["세종종촌", "롯데리아 세종종촌점", "충청북도", "세종시"]
ltr_tbl.iloc[217] = ["세종부강", "롯데리아 세종부강점", "충청북도", "세종시"]
ltr_tbl.iloc[284] = ["세종첫마을", "롯데리아 세종첫마을점", "충청북도", "세종시"]
ltr_tbl.iloc[287] = ["홈플러스세종", "롯데리아 홈플러스세종점", "충청북도", "세종시"]
ltr_tbl.iloc[824] = ["홈플러스조치원", "롯데리아 홈플러스조치원점", "충청북도", "세종시"]
ltr_tbl.iloc[881] = ["조치원", "롯데리아 조치원점", "충청북도", "세종시"]


# In[69]:


ltr_tbl['d2'].unique()


# In[77]:


L = ltr_tbl.apply(lambda r: r['d1'] + ' ' + r['d2'], axis=1).value_counts()
L.head()


# In[86]:


def moms_search_stores_in_dist(num):
    store_list = []
    MT_DISTSEARCH_URL = 'http://www.momstouch.co.kr/sub/store/store_01_list.html?pg={code}'
    response = urllib.request.urlopen(MT_DISTSEARCH_URL.format(code=num))
    mt_data = response.read()
    soup = bs4.BeautifulSoup(mt_data)
    table = soup.find("table", {"class": "store_List"})
    trs = table.findAll("tr")[1:]
    
    for tr in trs:
        store_name = tr.findAll("td")[1].text
        store_add = tr.find("td", {"class": "td_Left"}).text
        store_list.append([store_name, store_add.split()[0], store_add.split()[1]])
        
    return store_list


# In[87]:


moms_list = []
tmp_list = []
for i in range(1, 120): 
    tmp_list = moms_search_stores_in_dist(i)
    moms_list += tmp_list
        
print(len(moms_list))


# In[89]:


moms_tbl = pd.DataFrame(moms_list, columns=('store', 'd1', 'd2'))


# In[92]:


moms_tbl['d1'].unique()


# In[95]:


moms_tbl[moms_tbl['d1']=="전주시덕진구"]


# In[94]:


moms_tbl.iloc[1] = ["전주에코시티점", "전라북도", "전주시"]


# In[96]:


moms_tbl[moms_tbl['d1']=="선릉로64길"]


# In[100]:


moms_tbl.iloc[30] = ["한티역점", "서울특별시", "강남구"]


# In[98]:


moms_tbl[moms_tbl['d1']=="경기도안산시"]


# In[101]:


moms_tbl.iloc[249] = ["안산한대역점", "경기도", "안산시"]


# In[102]:


moms_tbl[moms_tbl['d1']=="부산해운대구해운대로"]


# In[103]:


moms_tbl.iloc[824] = ["장산역점", "부산광역시", "해운대구"]


# In[110]:


moms_tbl[moms_tbl['d1']=="고양시"]


# In[111]:


moms_tbl.iloc[220] = ["고양능곡점", "경기도", "고양시"]


# In[116]:


moms_tbl[moms_tbl['d1']=="제주시"]


# In[117]:


moms_tbl.iloc[783] = ["한라대점", "제주특별자치도", "제주시"]
moms_tbl.iloc[849] = ["함덕점", "제주특별자치도", "제주시"]
moms_tbl.iloc[896] = ["이도점", "제주특별자치도", "제주시"]
moms_tbl.iloc[898] = ["연삼로점", "제주특별자치도", "제주시"]


# In[120]:


moms_tbl['d1'].unique()


# In[119]:


d1_aliases = """서울:서울특별시 서울시:서울특별시 충남:충청남도 강원:강원도 경기:경기도 충북:충청북도 경남:경상남도 경북:경상북도
전남:전라남도 전북:전라북도 제주도:제주특별자치도 제주:제주특별자치도 대전:대전광역시 대전시:대전광역시 대구:대구광역시 대구시:대구광역시 인천:인천광역시
광주:광주광역시 광주시:광주광역시 울산:울산광역시 울산시:울산광역시 부산시:부산광역시 부산:부산광역시 인천시:인천광역시 세종:세종특별자치시 세종시:세종특별자치시 세종특별시:세종특별자치시"""
d1_aliases = dict(aliasset.split(':') for aliasset in d1_aliases.split())
moms_tbl['d1'] = moms_tbl['d1'].apply(lambda v: d1_aliases.get(v, v))


# In[121]:


moms_tbl[moms_tbl['d1']=="세종특별자치시"]


# In[368]:


moms_tbl.iloc[18] = ["세종도담점", "세종특별자치시", "세종특별자치시"]
moms_tbl.iloc[72] = ["세종대평점", "세종특별자치시", "세종특별자치시"]
moms_tbl.iloc[112] = ["세종국책연구소점", "세종특별자치시", "세종특별자치시"]
moms_tbl.iloc[152] = ["세종새롬점", "세종특별자치시", "세종특별자치시"]
moms_tbl.iloc[259] = ["세종아름점", "세종특별자치시", "세종특별자치시"]
moms_tbl.iloc[280] = ["세종보람점", "세종특별자치시", "세종특별자치시"]
moms_tbl.iloc[383] = ["세종고운점", "세종특별자치시", "세종특별자치시"]
moms_tbl.iloc[432] = ["세종어진점", "세종특별자치시", "세종특별자치시"]
moms_tbl.iloc[456] = ["세종cgv점", "세종특별자치시", "세종특별자치시"]
moms_tbl.iloc[558] = ["조치원역점", "세종특별자치시", "세종특별자치시"]
moms_tbl.iloc[712] = ["한국영상대점", "세종특별자치시", "세종특별자치시"]
moms_tbl.iloc[900] = ["홍익대세종캠퍼스점", "세종특별자치시", "세종특별자치시"]
moms_tbl.iloc[925] = ["고려대세종캠퍼스점", "세종특별자치시", "세종특별자치시"]
moms_tbl.iloc[1046] = ["신세종첫마을점", "세종특별자치시", "세종특별자치시"]
moms_tbl.iloc[1049] = ["세종부강점", "세종특별자치시", "세종특별자치시"]


# In[369]:


MS = moms_tbl.apply(lambda r: r['d1'] + ' ' + r['d2'], axis=1).value_counts()
MS.head()


# In[ ]:


# 크롤링 데이터 저장
B.to_excel('./export/res_burgerking.xlsx', sheet_name='sheet1')
M.to_excel('./export/res_mcdonalds.xlsx', sheet_name='sheet1')
K.to_excel('./export/res_kfc.xlsx', sheet_name='sheet1')
L.to_excel('./export/res_lotteria.xlsx', sheet_name='sheet1')
MS.to_excel('./export/res_momstouch.xlsx', sheet_name='sheet1')


# In[3]:


# 저장한 데이터 사용
B = pd.read_excel('./export/res_burgerking.xlsx')
M = pd.read_excel('./export/res_mcdonalds.xlsx')
K = pd.read_excel('./export/res_kfc.xlsx')
L = pd.read_excel('./export/res_lotteria.xlsx')
MS = pd.read_excel('./export/res_momstouch.xlsx')
B.head()


# In[4]:


BMKLS = pd.DataFrame({'B': B[0], 'M': M[0], 'K': K[0], 'L': L[0], 'MS': MS[0]}).fillna(0)
BMKLS['total'] = BMKLS.sum(axis=1)
BMKLS = BMKLS.sort_values(by=['total'], ascending=False)
BMKLS.head(10)


# In[7]:


from matplotlib import pyplot as plt
from matplotlib import rcParams, style


# In[8]:


style.use('ggplot')
rcParams['font.size'] = 12
plt.figure(figsize=(4, 3))
BMKLS.sum(axis=0).iloc[:5].plot(kind='bar')


# In[13]:


import scipy.stats
from matplotlib import pyplot as plt
from matplotlib import rcParams, style
from matplotlib import rcParams
from matplotlib import cm, colors, _cm
rcParams['font.family'] = 'NanumBarunGothic'


# In[14]:


fig = plt.figure(figsize=(12, 12))

def plot_nstores3(b1, b2, label1, label2):
    plt.scatter(BMKLS[b1] + np.random.random(len(BMKLS)),
                BMKLS[b2] + np.random.random(len(BMKLS)),
                edgecolor='none', alpha=0.75, s=6, c='black')
    plt.xlim(-1, 15 if (b1 != 'L') & (b1 != 'MS') else 35)
    plt.ylim(-1, 15 if (b2 != 'L') & (b2 != 'MS') else 35)
    plt.xlabel(label1)
    plt.ylabel(label2)
    
    r = scipy.stats.pearsonr(BMKLS[b1], BMKLS[b2])
    
    if r[0]>=0.75:
        color='red'
    elif r[0]<0.5:
        color='blue'
    else:
        color='black'
        
    plt.annotate('r={:.3f}'.format(r[0]), (9 if (b1 != 'L') & (b1 != 'MS') else 20, 12.5 if (b2 != 'L') & (b2 != 'MS') else 20), fontsize=14, color=color)

bgbrands = [
    ('B', '버거킹'), ('K', 'KFC'),
    ('M', '맥도날드'), ('L', '롯데리아'), ('MS', '맘스터치'),
]

for a in range(len(bgbrands) - 1):
    for b in range(1, len(bgbrands)):
        if a >= b:
            continue
        ax = fig.add_subplot(len(bgbrands)-1, len(bgbrands)-1, a * 4 + b)
        acol, alabel = bgbrands[a]
        bcol, blabel = bgbrands[b]
        plot_nstores3(bcol, acol, blabel, alabel)

plt.tight_layout()
plt.savefig("./graph/EDA-burgerindex.pdf")


# In[15]:


plt.figure(figsize=(10, 4))
for col, label in [('B', 'Burger King'), ('K', 'KFC'), ('M', "McDonald's"), ('L', "Lotteria"), ('MS', "Mom's Touch")]:
    cumulv = np.cumsum(sorted(BMKLS[col], reverse=True)) / BMKLS[col].sum()
    plt.plot(cumulv, label='{} ({})'.format(label, int(BMKLS[col].sum())))
plt.legend(loc='best')
plt.xlabel('Number of districts (si/gun/gu)')
plt.ylabel('Cumulative fraction')


# In[16]:


from sklearn import manifold


# In[20]:


bgbrands = [
    ('B', '버거킹'), ('K', 'KFC'),
    ('M', '맥도날드'), ('L', '롯데리아'), ('MS', '맘스터치'),
]
totalList = []
tempList= None
for a in range(len(bgbrands)):
    tempList=[]
    tempList.append(bgbrands[a][1])
    for b in range(len(bgbrands)):
        acol, alabel = bgbrands[a]
        bcol, blabel = bgbrands[b]
        r = scipy.stats.pearsonr(BMKLS[bcol], BMKLS[acol])
        if r[0] == 1:
            tempList.append(0)
        else:
            tempList.append((1-r[0])*100)
    totalList.append(tempList)

dists = []
burgers = []
for d in totalList:
    burgers.append(d[0])
    dists.append(d[1:])

adist = np.array(dists)

mds = manifold.MDS(n_components=2, dissimilarity="precomputed", random_state=5)
results = mds.fit(adist)

coords = results.embedding_

plt.subplots_adjust(bottom = 0.1)
plt.scatter(
    coords[:, 0], coords[:, 1], marker = 'o'
    )
for label, x, y in zip(burgers, coords[:, 0], coords[:, 1]):
    plt.annotate(
        label,
        xy = (x, y), xytext = (-5, 5),
        textcoords = 'offset points', ha = 'right', va = 'bottom',
        bbox = dict(boxstyle = 'round,pad=0.5', fc = 'yellow', alpha = 0.5),
        arrowprops = dict(arrowstyle = '->', connectionstyle = 'arc3,rad=0'))

plt.show()

