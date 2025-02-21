from bs4 import BeautifulSoup
from requests import get
from ThreadwithRet import ThreadWithReturnValue
import time


def alternateGetTotalNotices(soup):
    next_page_links = soup.find_all('li', class_='page-link')
    link = next_page_links[-1].find('a')
    last_page_no = link['data-ci-pagination-page']
    return last_page_no


def getTotalNotices(soup):
    next_page_links = soup.find_all('li', class_='next page-link')
    last_page_no = -1
    for i in next_page_links:
        if 'last' in i.get_text().lower():
            last_page_link = i
            Link = last_page_link.find('a')
            last_page_no = Link['data-ci-pagination-page']
            break
    if(last_page_no == -1):
        last_page_no = alternateGetTotalNotices(soup)
    return int(last_page_no)


def getLinksToNotices(soup, url):
    totalNotices = getTotalNotices(soup)
    links = []
    for page in range(1, totalNotices+1):
        links += [url+'?per_page='+str(page)]
    return links


def getNotices(notices_url):
    try:
        notices_page = get(notices_url)
    except:
        print(f"wasn't able to fetch url: {notices_url} .......... Skipping......")
        return []

    soup = BeautifulSoup(notices_page.content, 'html.parser')
    NoticesLists = soup.find('ul', class_='list-group list-gr')
    NoticesLi = NoticesLists.find_all('li')
    Notices = []
    for notice in NoticesLi:
        link = notice.find('a', href=True)
        href = link['href']
        text = link.get_text()
        date = text[:text.index(' ')].replace('\xa0', '')
        title = text[text.index(' ')+1:]
        Notices += [
            {
                "date": date,
                "title": title,
                "link": href
            }]
    return Notices


def getAllNoticesFromLinks(linksToNotices):
    Notices = []
    threads = []
    for link in linksToNotices:
        thread = ThreadWithReturnValue(target=getNotices,args=(link,))
        threads.append(thread)
    for thread in threads:
        thread.start()
    for thread in threads:
        notice = thread.join()
        Notices += notice
    return Notices


def getNoticesFromBaseUrl(url):
    try:
        page = get(url)
    except:
        print(f"wasn't able to make get request to {url} .......... Skipping......")
        return []
    soup = BeautifulSoup(page.content, 'html.parser')

    linksToNotices = getLinksToNotices(soup, url)
    return getAllNoticesFromLinks(linksToNotices)
