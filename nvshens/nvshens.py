import requests
import time
import os
from lxml import etree
from concurrent.futures import ThreadPoolExecutor, as_completed

album_num = 1

def main():
    website_url = 'https://www.nvshens.net'
    bianhao = input('请输入网址栏中妹子编号：')
    print('正在爬取，请等待爬取结束')
    home_url = website_url +'/girl/'+ bianhao + '/album/'
    headers_home={
        'Referer': home_url,
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36'
    }
    home_resp = get_html(home_url,headers_home)
    home_html = etree.HTML(home_resp.text)
    home_urls = home_html.xpath('.//li[@class="igalleryli"]//a[@class="igalleryli_link"]/@href') #获取图集网址
    pic_dir = home_html.xpath('.//li[@class="igalleryli"]//div[@class="igalleryli_title"]//text()') #获取图集名称
    k = 0
    for url in home_urls:
        dir_name = pic_dir[k]+'_'+str(k+1)+'/'
        os.mkdir(dir_name)  #以图集名称+序号为名创建文件夹
        get_album(url,website_url,dir_name)
        k+=1
    print('爬虫结束')
    os.system('pause')


def get_html(url,headers):  #有时候获取页面的响应比较慢，故多次请求
    i = 0
    while i < 10:
        try:
            html = requests.get(url,headers=headers, timeout=10)
            return html
        except requests.exceptions.RequestException:
            i += 1
        finally:
            if i==10:
                return
    print('网络错误')

def get_img(src,headers):    #有时候获取图片地址的响应比较慢，故多次请求
    i = 0
    while i < 10:
        try:
            img = requests.get(src,headers=headers, timeout=10)
            return img
        except requests.exceptions.RequestException:
            i += 1
        finally:
            if i == 10:
                return

def download_img(src,headers,pic_dir):
    filename = src.split('/')[-1]
    img = get_img(src,headers)
    with open(pic_dir+filename,'wb') as file:
        file.write(img.content)

def get_page(url,headers,treadpool,pic_dir):
    resp = get_html(url, headers=headers)
    html = etree.HTML(resp.text)
    srcs = html.xpath('.//div[@id="high"]//img/@src')  #获得每页的三张图片地址
    pic = ThreadPoolExecutor(max_workers=3)            #开启三个线程爬取
    for src in srcs:
        treadpool.append(pic.submit(download_img,src,headers,pic_dir))
    n_l = html.xpath('.//a[contains(text(),"下一页")]/@href') #获得下一页地址
    return n_l[0]

def get_album(url,website_url,pic_dir):
    global album_num
    first_link = website_url+url
    finall_link = website_url
    headers_album = {
        'Referer': first_link,
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36'
    }
    treadpool = []
    time.sleep(0.5)
    next_link = website_url + get_page(first_link,headers_album,treadpool,pic_dir)
    print('正在爬取第',album_num,'个图集...')
    time.sleep(0.5)
    while not (finall_link == first_link):  #图集最后一页的“下一页”按钮指向第一页
        next_link = website_url + get_page(next_link,headers_album,treadpool,pic_dir)
        finall_link = next_link + '/'
        time.sleep(0.5)
    for i in as_completed(treadpool): #等待所有线程结束
        k = 1
    print('第',album_num,'个图集爬取完成')
    album_num += 1

if __name__ == '__main__':
    main()