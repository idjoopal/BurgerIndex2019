#!/usr/bin/env python
# coding: utf-8

# In[3]:


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


# In[38]:


from matplotlib import pyplot as plt
from matplotlib import rcParams, style
style.use('ggplot')
rcParams['font.size'] = 12


# In[304]:


plt.figure(figsize=(4, 3))
BMK.sum(axis=0).iloc[:3].plot(kind='bar')


# In[421]:


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


# In[420]:


BMKLS = pd.DataFrame({'B': B.B, 'M': M.M, 'K': K.K, 'L': L.L, 'MS': MS.MS}).fillna(0)
BMKLS['total'] = BMKLS.sum(axis=1)
BMKLS = BMKLS.sort_values(by=['total'], ascending=False)
BMKLS.head(10)


# In[163]:


style.use('ggplot')
rcParams['font.size'] = 12
plt.figure(figsize=(4, 3))
BMKLS.sum(axis=0).iloc[:5].plot(kind='bar')


# In[438]:


fig = plt.figure(figsize=(12, 12))

def plot_nstores3(b1, b2, label1, label2):
    plt.scatter(bgt[b1] + np.random.random(len(bgt)),
                bgt[b2] + np.random.random(len(bgt)),
                edgecolor='none', alpha=0.75, s=6, c='black')
    plt.xlim(-1, 15 if (b1 != 'L') & (b1 != 'MS') else 35)
    plt.ylim(-1, 15 if (b2 != 'L') & (b2 != 'MS') else 35)
    plt.xlabel(label1)
    plt.ylabel(label2)
    
    r = scipy.stats.pearsonr(bgt[b1], bgt[b2])
    
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


# In[433]:


plt.figure(figsize=(10, 4))
for col, label in [('B', 'Burger King'), ('K', 'KFC'), ('M', "McDonald's"), ('L', "Lotteria"), ('MS', "Mom's Touch")]:
    cumulv = np.cumsum(sorted(BMKLS[col], reverse=True)) / BMKLS[col].sum()
    plt.plot(cumulv, label='{} ({})'.format(label, int(BMKLS[col].sum())))
plt.legend(loc='best')
plt.xlabel('Number of districts (si/gun/gu)')
plt.ylabel('Cumulative fraction')


# In[371]:


B.to_excel('./export/res_burgerking.xlsx', sheet_name='sheet1')
M.to_excel('./export/res_mcdonalds.xlsx', sheet_name='sheet1')
K.to_excel('./export/res_kfc.xlsx', sheet_name='sheet1')
L.to_excel('./export/res_lotteria.xlsx', sheet_name='sheet1')
MS.to_excel('./export/res_momstouch.xlsx', sheet_name='sheet1')


# In[4]:


B = pd.read_excel('./export/res_burgerking.xlsx')
M = pd.read_excel('./export/res_mcdonalds.xlsx')
K = pd.read_excel('./export/res_kfc.xlsx')
L = pd.read_excel('./export/res_lotteria.xlsx')
MS = pd.read_excel('./export/res_momstouch.xlsx')
B.head()


# In[5]:


tmp = pd.read_excel("./data/인구_서울특별시.xlsx", usecols=[0,1], names=["d1d2d3", "population"])
tmp['d1'], tmp['d2d3'] = tmp['d1d2d3'].str.split(' ', 1).str
tmp['d2'], tmp['d3'] = tmp['d2d3'].str.split(' ', 1).str
tmp = tmp[3:]


# In[6]:


district = pd.DataFrame({'d1': tmp.d1, 'd2': tmp.d2, 'd3': tmp.d3, 'population': tmp.population})


# In[7]:


def get_distDF(loc):
    filename = "./data/인구_" + loc + ".xlsx"
    tmp = pd.read_excel(filename, usecols=[0,1], names=["d1d2d3", "population"])
    tmp['d1'], tmp['d2d3'] = tmp['d1d2d3'].str.split(' ', 1).str
    tmp['d2'], tmp['d3'] = tmp['d2d3'].str.split(' ', 1).str
    tmp = tmp[3:]
    dist = pd.DataFrame({'d1': tmp.d1, 'd2': tmp.d2, 'd3': tmp.d3, 'population': tmp.population})
    return dist


# In[8]:


locs = ["강원도", "경기도", "경상남도", "경상북도", "광주광역시", "대구광역시", "대전광역시", "부산광역시", "세종특별자치시", "울산광역시", "인천광역시", "전라남도", "전라북도", "제주특별자치도", "충청남도", "충청북도"]
for loc in locs:
    district = district.append(get_distDF(loc), ignore_index=True)
    


# In[9]:


district.head()


# In[10]:


district.index = district.apply(lambda r: r['d1'] + ' ' + r['d2'], axis=1)


# In[11]:


district = district[district['d3'].str.startswith("(")]


# In[12]:


district[district['d2']=="수원시"]


# In[13]:


bgt = pd.DataFrame({'B': B.B, 'M': M.M, 'K': K.K, 'L': L.L, 'MS': MS.MS}).fillna(0)
bgt = pd.merge(district, bgt, how='outer', left_index=True, right_index=True)
bgt.head()


# In[14]:


bgt[bgt['d1'].isnull()]


# In[15]:


bgt[bgt['d1']=="세종특별자치시"]


# In[16]:


bgidx_cols = ['B', 'M', 'K', 'L', 'MS']
bgt.loc['경상남도 거제시', bgidx_cols] += bgt.loc['광주광역시 거제시', bgidx_cols]
bgt.loc['경상남도 김해시', bgidx_cols] += bgt.loc['광주광역시 김해시', bgidx_cols]
bgt.loc['경상남도 진주시', bgidx_cols] += bgt.loc['광주광역시 진주시', bgidx_cols]
bgt.loc['경상남도 창녕군', bgidx_cols] += bgt.loc['광주광역시 창녕군', bgidx_cols]
bgt.loc['경상남도 창원시', bgidx_cols] += bgt.loc['광주광역시 창원시', bgidx_cols]
bgt.loc['경상남도 통영시', bgidx_cols] += bgt.loc['광주광역시 통영시', bgidx_cols]
bgt.loc['부산광역시 남구', bgidx_cols] += bgt.loc['부산 광역시', bgidx_cols]
bgt.loc['부산광역시 부산진구', bgidx_cols] += bgt.loc['부산광역시 진구', bgidx_cols]

bgt.loc['세종특별자치시 세종특별자치시', bgidx_cols] += bgt.loc['세종특별자치시 나성동', bgidx_cols]
bgt.loc['세종특별자치시 세종특별자치시', bgidx_cols] += bgt.loc['세종특별자치시 부강면', bgidx_cols]
bgt.loc['세종특별자치시 세종특별자치시', bgidx_cols] += bgt.loc['세종특별자치시 절재로', bgidx_cols]
bgt.loc['세종특별자치시 세종특별자치시', bgidx_cols] += bgt.loc['세종특별자치시 조치원읍', bgidx_cols]
bgt.loc['세종특별자치시 세종특별자치시', bgidx_cols] += bgt.loc['세종특별자치시 종촌동', bgidx_cols]
bgt.loc['울산광역시 중구', bgidx_cols] += bgt.loc['울산광역시 유곡동', bgidx_cols]
bgt.loc['인천광역시 미추홀구', bgidx_cols] += bgt.loc['인천광역시 남구', bgidx_cols]
bgt.loc['전라남도 여수시', bgidx_cols] += bgt.loc['전라북도 여수시', bgidx_cols]
bgt.loc['세종특별자치시 세종특별자치시', bgidx_cols] += bgt.loc['충청남도 세종시', bgidx_cols]
bgt.loc['충청북도 청주시', bgidx_cols] += bgt.loc['충청북도 청원군', bgidx_cols]

bgt = bgt[~bgt['d1'].isnull()].fillna(0)


# In[17]:


bgt[(bgt['L'] == 0) & (bgt['MS'] == 0) & (bgt['B'] + bgt['M'] + bgt['K'] > 0)]


# In[18]:


bgt[(bgt['L'] == 0) & (bgt['MS'] == 0)]


# In[48]:


bgt['BMK'] = bgt['B'] + bgt['M'] + bgt['K']
bgt['LMS'] = bgt['L'] + bgt['MS']
bgt['OldBgIdx'] = bgt['BMK'] / bgt['L']
bgt['NewBgIdx'] = bgt['BMK'] / bgt['LMS']
bgt['NewBgIdx2'] = (bgt['BMK'] + bgt['LMS']*0.04) / bgt['LMS']


# In[20]:


bgt = bgt.sort_values(by='OldBgIdx', ascending=False)
bgt.head(10)


# In[22]:


bgt = bgt.sort_values(by='NewBgIdx', ascending=False)
bgt.head(10)


# In[50]:


bgts = bgt[bgt['NewBgIdx2']!=0].sort_values(by='NewBgIdx2', ascending=True)
bgts.head(10)


# In[49]:


bgt[bgt['d1']=="세종특별자치시"]


# In[25]:


def short_distr(name):
    wide, narrow = name.split()
    if narrow == '세종특별자치시': 
        return '세종'
    elif wide.endswith('광역시'):
        return wide[:2] + (narrow[:-1] if len(narrow) > 2 else narrow)
    elif narrow.endswith('구'):
        return wide[:2] + (narrow[:-1] if len(narrow) > 2 else narrow)
    elif narrow == '고성군': # 고성군은 강원도, 경상남도에 있다.
        return '고성({})'.format({'강원도': '강원', '경상남도': '경남'}[wide])
    else:
        return narrow[:-1]

bgt['shortname'] = list(map(short_distr, bgt.index))
bgt.head()


# In[26]:


blockpositions = pd.read_excel('./data/block_map.xlsx', header=None, usecols=range(15))
blockpositions.head()


# In[27]:


flatrows = []
for y, colcities in blockpositions.iterrows():
    for x, city in colcities.iteritems():
        if isinstance(city, str):
            flatrows.append((x, y, city))

blockpositions_tbl = pd.DataFrame(flatrows, columns=('x', 'y', 'city')).set_index('city').sort_index()
bgtb = pd.merge(bgt, blockpositions_tbl, how='left', left_on='shortname', right_index=True)
bgtb.head()


# In[28]:


bgtb[bgtb['x'].apply(np.isnan)]


# In[29]:


import locale
from locale import atof
locale.setlocale(locale.LC_NUMERIC, '')


# In[30]:


bgtb['population'] = bgtb['population'].apply(atof)


# In[31]:


bgtb[(bgtb['LMS']==0)]


# In[32]:


bgtb.to_excel('./export/res_final.xlsx', sheet_name='sheet1')


# In[33]:


from matplotlib import rcParams
from matplotlib import cm, colors, _cm
rcParams['font.family'] = 'Malgun Gothic'


# In[34]:


bgtb['OldBgIdx'] = bgtb['OldBgIdx'].fillna(0)
bgtb['NewBgIdx'] = bgtb['NewBgIdx'].fillna(0)
bgtb['NewBgIdx2'] = bgtb['NewBgIdx2'].fillna(0)


# In[35]:


BORDER_LINES = [
    [(3, 2), (5, 2), (5, 3), (9, 3), (9, 1)], # 인천
    [(2, 5), (3, 5), (3, 4), (8, 4), (8, 7), (7, 7), (7, 9), (4, 9), (4, 7), (1, 7)], # 서울
    [(1, 6), (1, 9), (3, 9), (3, 10), (8, 10), (8, 9),
     (9, 9), (9, 8), (10, 8), (10, 5), (9, 5), (9, 3)], # 경기도
    [(9, 12), (9, 10), (8, 10)], # 강원도
    [(10, 5), (11, 5), (11, 4), (12, 4), (12, 5), (13, 5),
     (13, 4), (14, 4), (14, 2)], # 충청남도
    [(11, 5), (12, 5), (12, 6), (15, 6), (15, 7), (13, 7),
     (13, 8), (11, 8), (11, 9), (10, 9), (10, 8)], # 충청북도
    [(14, 4), (15, 4), (15, 6)], # 대전시
    [(14, 7), (14, 9), (13, 9), (13, 11), (13, 13)], # 경상북도
    [(14, 8), (16, 8), (16, 10), (15, 10),
     (15, 11), (14, 11), (14, 12), (13, 12)], # 대구시
    [(15, 11), (16, 11), (16, 13)], # 울산시
    [(17, 1), (17, 3), (18, 3), (18, 6), (15, 6)], # 전라북도
    [(19, 2), (19, 4), (21, 4), (21, 3), (22, 3), (22, 2), (19, 2)], # 광주시
    [(18, 5), (20, 5), (20, 6)], # 전라남도
    [(16, 9), (18, 9), (18, 8), (19, 8), (19, 9), (20, 9), (20, 10)], # 부산시
]


# In[36]:


def draw_blockcolormap(tbl, datacol, vmin, vmax, whitelabelmin, cmap, gamma, datalabel, dataticks, filename):
#     cmap = colors.LinearSegmentedColormap(cmapname + 'custom',
#                       getattr(_cm, '_{}_data'.format(cmapname)), gamma=gamma)
#     cmap.set_bad('white', 1.)

    mapdata = pd.pivot_table(tbl, index='y', columns='x', values=datacol)
    masked_mapdata = np.ma.masked_where(np.isnan(mapdata), mapdata)
    

    plt.figure(figsize=(9, 16))
#     plt.pcolor(masked_mapdata.astype(float), vmin=vmin, vmax=vmax, edgecolor='#aaaaaa', linewidth=0.5)
    plt.pcolor(masked_mapdata.astype(float), vmin=vmin, vmax=vmax, cmap=cmap,
               edgecolor='#aaaaaa', linewidth=0.5)

    # 지역 이름 표시
    for idx, row in tbl.iterrows():
        # 광역시는 구 이름이 겹치는 경우가 많아서 시단위 이름도 같이 표시한다. (중구, 서구)
        if row['d1'].endswith('시') and not row['d1'].startswith('세종'):
            dispname = '{}\n{}'.format(row['d1'][:2], row['d2'][:-1])
            if len(row['d2']) <= 2:
                dispname += row['d2'][-1]
        elif row["d1"]=="세종특별자치시":
            dispname = "세종"
        else:
            dispname = row['d2'][:-1]

        # 서대문구, 서귀포시 같이 이름이 3자 이상인 경우에 작은 글자로 표시한다.
        if len(dispname.splitlines()[-1]) >= 3:
            fontsize, linespacing = 12, 1.2
        else:
            fontsize, linespacing = 14, 1.03
        
        annocolor = 'white' if row[datacol] > whitelabelmin else 'black'
        
        plt.annotate(dispname, (row['x']+0.5, row['y']+0.5), weight='bold',
                     fontsize=fontsize, ha='center', va='center', color=annocolor,
                     linespacing=linespacing)

    # 시도 경계 그린다.
    for path in BORDER_LINES:
        ys, xs = zip(*path)
        plt.plot(xs, ys, c='black', lw=2)

    plt.gca().invert_yaxis()
    plt.gca().set_aspect(1)

    plt.axis('off')
    
    cb = plt.colorbar(shrink=.1, aspect=10)
    cb.set_label(datalabel)
    cb.set_ticks(dataticks)

    plt.tight_layout()
    plt.savefig("./graph/"+filename+"-burgerindex.pdf")


# In[39]:


draw_blockcolormap(bgtb, 'OldBgIdx', 0, 3.5, 2.3, 'PuBu', 0.75, '버거지수', np.arange(0, 3.6, 0.5), "버거지수2019_구지표_")


# In[40]:


draw_blockcolormap(bgtb, 'NewBgIdx', 0, 1.5, 1.0, 'PuBu', 0.75, '버거지수', np.arange(0, 1.6, 0.5), "버거지수2019_신지표_")


# In[51]:


draw_blockcolormap(bgtb, 'NewBgIdx2', 0, 2.0, 1.42, 'PuBu', 0.75, '버거지수', np.arange(0, 2.1, 0.5), "버거지수2019_신지표보정_")


# In[398]:


bgtb['Lp10T'] = bgtb['L'] / bgtb['population'] * 10000
draw_blockcolormap(bgtb, 'Lp10T', 0, 1, 0.75, 'YlGn', 1, '1만명당 롯데리아 점포수', np.arange(0, 1.1, 0.2), "만명당롯데리아_")


# In[399]:


bgtb['LMSp10T'] = bgtb['LMS'] / bgtb['population'] * 10000
draw_blockcolormap(bgtb, 'LMSp10T', 0, 2, 1.35, 'YlGn', 1, '1만명당 롯데+맘스 점포수', np.arange(0, 2.1, 0.2), "만명당롯리+맘터_")


# In[400]:


bgtb['MSp10T'] = bgtb['MS'] / bgtb['population'] * 10000
draw_blockcolormap(bgtb, 'MSp10T', 0, 1, 0.55, 'YlGn', 1, '1만명당 맘스터치 점포수', np.arange(0, 1.1, 0.2), "만명당맘스터치_")


# In[402]:


bgtb['BMKp10T'] = bgtb['BMK'] / bgtb['population'] * 10000
draw_blockcolormap(bgtb, 'BMKp10T', 0, 1, 0.55, 'RdPu', 1, '1만명당 B+M+K 점포수', np.arange(0, 1.1, 0.2), "만명당BMK_")


# In[403]:


bgtb['Bp10T'] = bgtb['B'] / bgtb['population'] * 10000
draw_blockcolormap(bgtb, 'Bp10T', 0, 0.5, 0.3, 'RdPu', 1, '1만명당 버거킹 점포수', np.arange(0, 0.6, 0.1), "만명당버거킹_")


# In[41]:


bgtb['Mp10T'] = bgtb['M'] / bgtb['population'] * 10000
draw_blockcolormap(bgtb, 'Mp10T', 0, 0.35, 0.3, 'RdPu', 1, '1만명당 맥도날드 점포수', np.arange(0, 0.45, 0.1), "만명당맥도날드_")


# In[405]:


bgtb['Kp10T'] = bgtb['K'] / bgtb['population'] * 10000
draw_blockcolormap(bgtb, 'Kp10T', 0, 0.3, 0.181, 'RdPu', 1, '1만명당 KFC 점포수', np.arange(0, 0.4, 0.1), "만명당KFC_")


# In[42]:


bgtb['BMKLp10T'] = (bgtb['BMK']+bgtb['L']) / bgtb['population'] * 10000
draw_blockcolormap(bgtb, 'BMKLp10T', 0, 1.5, 0.81, 'Oranges', 1, '1만명당 BMKL 점포수', np.arange(0, 1.6, 0.5), "만명당BMKL_")


# In[407]:


bgtb['BMKLMSp10T'] = (bgtb['BMK']+bgtb['LMS']) / bgtb['population'] * 10000
draw_blockcolormap(bgtb, 'BMKLMSp10T', 0, 2.0, 0.7, 'Oranges', 1, '1만명당 패스트푸드 점포수', np.arange(0, 2.1, 0.5), "만명당패스트푸드_")


# In[56]:


bgtb['BIp10T'] = bgtb['NewBgIdx'] / bgtb['population'] * 10000
draw_blockcolormap(bgtb, 'BIp10T', 0, 0.2, 0.13, 'RdPu', 1, '1만명당 버거지수', np.arange(0, 0.3, 0.1), "만명당BIdx_")

