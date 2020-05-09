from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
from selenium.webdriver import ActionChains
import random

def get_track(distance):      # distance为传入的总距离
    # 移动轨迹
    track=[]
    # 当前位移
    current=0
    # 减速阈值
    mid=distance*4/5
    # 计算间隔
    t=0.2
    # 初速度
    v=1
    while current<distance:
        if current<mid:
            # 加速度为2
            a=4
        else:
            # 加速度为-2
            a=-3
        v0=v
        # 当前速度
        v=v0+a*t
        # 移动距离
        move=v0*t+1/2*a*t*t
        # 当前位移
        current+=move
        # 加入轨迹
        track.append(round(move))
    return track

#滑动到270就可以了
def move_to_gap(driver,slider,tracks):
    ActionChains(driver).click_and_hold(slider).perform()
    for x in tracks:
        ActionChains(driver).move_by_offset(xoffset=x,yoffset=0).perform()
    time.sleep(0.1)
    ActionChains(driver).release().perform()


#处理验证码
def handle_vertify(driver):
    iframe = driver.find_elements_by_xpath('//div[@class="sufei-tb-dialog-content sufei-tb-overlay-content"]//iframe') 
    if len(iframe) == 0:
        return 
    driver.switch_to_frame(iframe[0])
    trys = 0
    while trys < 5:
        trys += 1
        slider=driver.find_element_by_xpath("//*[@id='nc_1_n1t']/span")#需要滑动的元素
        ActionChains(driver).click_and_hold(slider).perform()
        trace = [10,20,30,40,40,40,30,30,30,30]
        for i in range(len(trace)):
            ActionChains(driver).move_by_offset(xoffset=trace[i],yoffset=0).perform()
        ActionChains(driver).release().perform()
        #move_to_gap2(driver,slider,get_track(270))
        refresh = driver.find_elements_by_xpath("//span[@class='nc-lang-cnt']/a")
        if len(refresh) > 0:
            refresh[0].click()
            continue
        time.sleep(random.randint(2,5))
        if driver.page_source.find("nc_1_n1t") == -1:
            driver.switch_to.parent_frame()
            break
    if trys >= 5:
        print("[Error]:vertify code error")
    else:
        print("[Success]:vertify code error")


def get_items(driver,next_count):
    i = 0
    all_goods = []
    while i < next_count:
        i += 1
        items = driver.find_elements_by_xpath('//div[@class="item J_MouserOnverReq  "]')
        for item in items:
            href = item.find_elements_by_xpath(".//a")[0].get_attribute("data-href")
            good = item.find_elements_by_xpath(".//a/img")[0].get_attribute("alt")
            sells =item.find_elements_by_xpath('.//div[@class="deal-cnt"]')[0].get_attribute('innerHTML') 
            all_goods.append([good,href,sells])
        next_page = driver.find_elements_by_xpath('//li[@class="item next"]')[0].click()
        time.sleep(5)
    return all_goods


def get_comment(driver,url):
     if url.find("http") == -1:
         url = "https:" + url
     driver.get(url)
     time.sleep(5)
     feature_comment=[]
     #点击获取评论列表
     try:
         driver.find_elements_by_xpath('//em[@class="J_ReviewsCount"]')[0].click()
         time.sleep(5)
         handle_vertify(driver)
     except:
         print("[Error]:click on %s comment" % url)
         return

     #点击获取根多feature
     try:
         driver.find_elements_by_xpath('//span[@class="rate-tag-toggle"]')[0].click()
         time.sleep(5)
         handle_vertify(driver)
     except:
         pass
     features = driver.find_elements_by_xpath('//div[@class="rate-tag-inner"]//span')

     #依次遍历每个feature
     for feature_i in range(0,len(features)):
         driver.execute_script('window.scrollTo(800,0)')
         item = driver.find_elements_by_xpath('//div[@class="rate-tag-inner"]//span')[feature_i]
         feature_element = item.find_elements_by_xpath(".//a")[0].click()
         time.sleep(3)
         handle_vertify(driver)

         feature = item.find_elements_by_xpath(".//a")[0].get_attribute("innerHTML")
         feature = feature.split("(")[0]
         #遍历此feature下的评论
         comments_list = []
         index = 0
         #index指定每个评论查看多少页
         while True and index < 2:
             index += 1
             comments = driver.find_elements_by_xpath('//div[@class="tm-rate-content"]//div[@class="tm-rate-fulltxt"]//b')
             #和feature相关的评论记录
             with open("./data/%s.txt" % feature,"a") as f:
                for i in range(len(comments)):
                    comment = comments[i].get_attribute("innerHTML")
                    comments_list.append(comment)
                    f.write("%s\n" % comment.replace("\n",""))
             #可以翻页就翻页
             no_next_page = driver.find_elements_by_xpath('//span[@class="rate-tag-toggle"]')
             if len(no_next_page) != 0:
                 break
             next_page = driver.find_elements_by_xpath('//div[@class="rate-paginator"]//a')[-1].click()
             time.sleep(2)
             handle_vertify(driver)
         feature_comment.append([feature,comments_list])

def save_page(page_name,content):
    with open("save_page/%s.html" % page_name,"w") as f:
        f.write(content)


def get_driver():
    chrome_options = Options()
    chrome_options.add_experimental_option("debuggerAddress","127.0.0.1:9222")
    #chrome_options.add_experimental_option("prefs", {"profile.managed_default_content_settings.images": 2}) 

    chrome_driver = "/usr/bin/chromedriver"
    driver = webdriver.Chrome(chrome_driver,chrome_options=chrome_options)
    return driver

if __name__ == "__main__":
    driver = get_driver()
    url = "//detail.tmall.com/item.htm?id=610945761670&ns=1&abbucket=5"
    get_comment(driver,url)
    #url = "https://s.taobao.com/search?initiative_id=tbindexz_20170306&ie=utf8&spm=a21bo.2017.201856-taobao-item.2&sourceId=tb.index&search_type=item&ssid=s5-e&commend=all&imgfile=&q=t%E6%81%A4%E7%94%B7&suggest=0_2&_input_charset=utf-8&wq=T&suggest_query=T&source=suggest&sort=sale-desc"
    #driver.get(url)
    #all_goods = get_items(driver,2)
    #with open("./save_page/good.txt","a") as f:
    #    for each in all_goods:
    #        f.write("%s\t%s\t%s\r\n" % (each[0].replace("\t","").replace("\n",""),each[1],each[2]))
