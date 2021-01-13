import requests
import bs4
import re
import os
import json

def getWangYe(goalPage,keyWord,rootDirName,startPage=1,rootUrl='https://search.jd.com/Search'):
    p1 = {
        'keyword':keyWord,
        'page':1,
        's':1,
        'click':0
    }
    if not os.path.exists(rootDirName):
        os.mkdir(rootDirName)
    soupList = []
    for i in range(goalPage):
        try:
            p1['page'] = i+startPage
            p1['s'] = 1+(i+startPage-1)*25
            r = requests.get(rootUrl,params=p1,headers={'user-agent':'Edge'})
            r.raise_for_status()
            print('['+str(i+1)+']',r.url)
            dirName = rootDirName+'/page_'+str(i+startPage)
            if not os.path.exists(dirName):
                os.mkdir(dirName)
            if (r.encoding != 'UTF-8') and (r.encoding != 'utf-8'):
                r.encoding = r.apparent_encoding 
            s = bs4.BeautifulSoup(r.text,'html.parser')
            filename = './'+dirName+'/html.txt'
            with open(filename,'w',encoding='utf-8') as f:
                f.write(s.prettify())
                soupList.append(s)
        except:
            print('page',i,'failed',r.status_code)
            pass
    print(len(soupList),'get')
    return soupList

def getImg(url,filename):
    try:
        r = requests.get(url,timeout=10)
        r.raise_for_status()
        with open(filename,'wb') as f:
            f.write(r.content)
    except:
        print('...getImg error:',r.status_code,'IMG_URL:',url)

def getJson(filename,dicts):
    try:
        with open(filename,'w',encoding='utf-8') as f:
            f.write(json.dumps(dicts,ensure_ascii=False))
    except:
        print('...getJson error')

def getHtml(url,filename):
    try:
        r = requests.get(url,timeout=10)
        r.raise_for_status()
        if (r.encoding != 'UTF-8') and (r.encoding != 'utf-8'):
            r.encoding = r.apparent_encoding
        with open(filename,'w',encoding='utf-8') as f:
            f.write(r.text)
    except:
        print('...getHtml error:',r.status_code,url)
rootUrl = 'https://search.jd.com/Search'
keyWord = input('key word:')
rootDirName = input('dir name:')
startPage = int(input('start page:'))
goalPage = int(input('page num:'))

soupList = getWangYe(goalPage,keyWord,rootDirName,startPage=startPage,rootUrl=rootUrl)


pagesInfoList = []
for soup in soupList:
    pageinfoList = []
    divTag = soup.find(id='J_goodsList')
    if divTag == None:
        continue
    for liTag in divTag.find_all(name='li'):
        divTag2 = liTag.find('div')
        if divTag2 == None:
            continue
        infoDict = {}
        for divTag3 in divTag2.children:
            try:
                if (type(divTag3) != bs4.element.Tag) or (divTag3.name != 'div'):
                    continue
                if 'p-price' in divTag3.attrs['class']:
                    infoDict['price'] = float(divTag3.i.string.strip())
                elif 'p-name' in divTag3.attrs['class']:
                    emTag = divTag3.em
                    name = ''
                    for x in emTag.contents:
                        if type(x) == bs4.element.NavigableString:
                            name+=x
                    infoDict['wuName'] = name.replace('\n','').replace('\t','')
                    infoDict['wuUrl'] = 'https:'+divTag3.a.attrs['href']
                elif 'p-img' in divTag3.attrs['class']:
                    infoDict['imgUrl'] = 'https:'+divTag3.img.attrs['src']
            except:
                print('get info error',divTag3.attrs)
        pageinfoList.append(infoDict)
    pagesInfoList.append(pageinfoList)
print('get info list success\ndownloading')
for i in range(len(pagesInfoList)):
    pageinfoList = pagesInfoList[i]
    dirName = rootDirName+'/page_'+str(i+startPage)
    for j in range(len(pageinfoList)):
        dirName1 = dirName+'/wu_'+str(j+1)
        if not os.path.exists(dirName1):
            os.mkdir(dirName1)
        info = pageinfoList[j]
        filename = './'+dirName1+'/'
        getImg(info['imgUrl'],filename+'IMG.jpg')
        getJson(filename+'INFO.json',info)
        getHtml(info['wuUrl'],filename+'WU.html')
print('finished')