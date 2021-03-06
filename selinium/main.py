from selenium.webdriver import Firefox
import time
import traceback, os
import pandas as pd
from all_fun import find_tags, save_csv, get_real_date, checkName
from selenium.webdriver import Chrome
driver = Chrome('./chromedriver')
# driver = Firefox(executable_path = './geckodriver')

# url = 'https://www.google.com.tw/maps'
# url = 'https://www.google.com.tw/maps/@25.0422976,121.5238281,17.29z' # 中正區北商位置
# url = 'https://www.google.com.tw/maps/@25.029295,121.5439541,14.9z' # 信義區北醫位置
# url = 'https://www.google.com.tw/maps/@25.0680263,121.5239719,16z' # 中山區中山國小位置
# url = 'https://www.google.com.tw/maps/@25.0476077,121.5256058,17.02z' # 中山區長安東路
# url = 'https://www.google.com.tw/maps/@25.0193684,121.5260166,15z' # 中正區台電大樓

# ================= 搜尋條件 =================
# district = '中山區' # 這個區的餐廳才拿資料
city = '台北市'
keyword = '熱炒'    # 關鍵字
totalpage = 10      # 總共要下載到幾頁的資料
# ===========================================
# =========== global 所需變數 =================
start_time = time.time()
lst_store = []
dic_store = {}
lst_store_csv = []
# df_stores = pd.DataFrame()
lst_review = []
dic_review = {}
# df_reviews = pd.DataFrame()
bfinal = False
bError = False
page = 0
restart = 0
district = ''
folder = ''
stores_path = ''
folder_keyword = './csv/'+ keyword + '/'
if not os.path.exists(folder_keyword) :
    os.mkdir(folder_keyword)
# ===========================================
def reset_paras():
    global page
    global bfinal
    global bError
    global district
    global folder
    global stores_path

    global lst_store
    global dic_store
    global lst_store_csv
    global lst_review
    global dic_review

    page = 0
    bfinal = False
    bError = False
    district = ''
    folder = ''
    stores_path = ''
    lst_store = []
    dic_store = {}
    lst_store_csv = []

    lst_review = []
    dic_review = {}
# 目前位置
# mylocation = driver.find_elements_by_id('widget-mylocation')
# print(len(mylocation))
# while len(mylocation) == 0:
#     print('mylocation')
#     mylocation = driver.find_elements_by_id('widget-mylocation')
# mylocation[0].click()

dic_tag = {
    'input':'tactile-searchbox-input',
    'stores':'section-result',
    'store_info':'section-info-action-button',
    'reviews_div':'section-rating-term-list',
    'allreviews':'widget-pane-link',
    'label':'aria-label',
    'ddl':'section-layout-flex-horizontal',
    'sort_item':'action-menu-entry',
    'loading':'section-loading',
    'review_date':'section-review-publish-date',
    'review_star':'section-review-stars',
    'review_text':'section-review-review-content',
    'price':'section-result-cost',
    'back_store':'ozj7Vb3wnYq__action-button-clickable',
    'back_list':'section-back-to-list-button',
    'next_page':'n7lv7yjyC35__section-pagination-button-next'
}

# =============== Start =====================
def start():
    url = 'https://www.google.com.tw/maps/@25.0193684,121.5260166,15z' # 中正區台電大樓
    driver.get(url)
    time.sleep(2)  # 等待2秒

    input = find_tags(driver, dic_tag['input'])[0] # 找到搜尋欄的tag
    input.send_keys(keyword) # 寫入要搜尋的字
    print('輸入搜尋關鍵字:', keyword)
    print('點擊搜尋')
    driver.find_element_by_id('searchbox-searchbutton').click()
    time.sleep(5)

start()
while True:
    if bfinal and not bError: # 若不是error結束跳出的，代表真的搜尋完所有頁面，結束
        print('bfinal and not bError，結束~~~~~~~~~')
        break
    elif bfinal and bError: # 若是error結束跳出的，將瀏覽器關閉、重開、變數reset，重新再搜尋
        if restart > 10:
            break
        driver.close()
        restart += 1
        reset_paras()
        driver = Chrome('./chromedriver')
        start()
    while not bfinal:
        try:
            sessions = find_tags(driver, dic_tag['stores'])
            count_thispage = len(sessions)
            print('sessions數，一開始:', count_thispage)
            count_store = 0
            total_store = 0

            page += 1
            print('進入第', page, '頁')
            if page > totalpage:
                print('目前頁數', page, '已超過設定頁數：', totalpage)
                bfinal = True
                break

            for i in range(count_thispage):
                if bfinal:
                    print('跳出本頁搜尋列表')
                    break
                dic_store = {} # 每個店家的資訊存進dic_store
                choose = False # selenium.common.exceptions.StaleElementReferenceException: Message: stale element reference: element is not attached to the page document

                sessions = find_tags(driver, dic_tag['stores'])

                if sessions[i].get_attribute(dic_tag['label']) != '':
                    ad = sessions[i].find_elements_by_class_name('ad-badge')[0] # 會有多個廣告tag，只看第一個
                    name = checkName(sessions[i].get_attribute(dic_tag['label'])) # 若含有特殊符號，無法作為檔名儲存
                    pricetag = sessions[i].find_elements_by_class_name(dic_tag['price'])[0].get_attribute(dic_tag['label']) # 找到價錢tag
                    price = ''
                    if pricetag != None:
                        price = pricetag.split(' ')[-1][0]
                    saved_latest_date = ''
                    saved_latest_review = ''

                    addr = ''
                    if 'display' not in ad.get_attribute('style') :
                        print('跳過這個廣告店家:', name)
                        continue # 廣告，跳過

                    sessions[i].click()
                    print('=== 點擊第'+ str(i+1) + '個店家:', name, '===')

                    infolines = find_tags(driver, dic_tag['store_info'])

                    for infoline in infolines:
                        addrinfo = infoline.get_attribute(dic_tag['label'])
                        if '地址' in addrinfo:
                            addr = addrinfo.split('、')[-1] # 取得店家完整地址
                            if not city in addr:
                                print('不是', city, '跳過') # 不是台北市的店家不要抓
                                choose = False
                                break
                        elif '區 ' in addrinfo:
                            district = addrinfo.split(' ')[1] # 2GVC+6W 中正區 台北市
                            choose = True
                        elif '里 'in addrinfo or '區 ' in addrinfo:
                            district = addrinfo.split(' ')[-1].replace('台北市', '') # 3G36+P4 永樂里 台北市大同區
                            choose = True
                    if choose:
                        folder = './csv/' + keyword + '/' + district + '/' # 路徑為./csv/熱炒/stores.csv
                        stores_path = './csv/' + keyword + '/stores.csv'
                        review_path = folder + name + '_review.csv' # 路徑為./csv/熱炒/行政區/店名_review.csv
                        if not os.path.exists(folder):
                            os.mkdir(folder)
                        print('區：', district, name)

                        # ============== 若此店家已儲存過評論，取出目前已存的最後一筆評論日期、評論內容 =======================
                        if os.path.exists(review_path):
                            df_cur = pd.read_csv(review_path)
                            saved_latest_date = df_cur.iloc[-1]['date']  # 最後一列的column'date'的值
                            saved_latest_review = df_cur.iloc[-1]['text'] # 最後一列的column'text'的值
                            print('第' + str(i + 1) + '個店家:', name, '的評論已經存過，已存的最新評論日期為', saved_latest_date)

                        empty_review = 0 # 紀錄空白評論數
                        total_review = 0
                        count_store += 1
                        total_store += 1
                        lst_review = [] # 每個店家的所有review存進lst_review
                        dic_store['tmpid'] = total_store
                        dic_store['name'] = name
                        dic_store['price'] = price
                        dic_store['addr'] = addr

                        reviews_div = find_tags(driver, dic_tag['reviews_div']) # 先找到包住"所有評論"tag的框框，再找"所有評論"的tag，若此店家完全無評論就找不到"所有評論的tag"
                        allreviews = reviews_div[-1].find_elements_by_class_name(dic_tag['allreviews']) # 若此店家完全無評論就找不到"所有評論的tag"
                        print('搜尋"所有評論"這個tag')
                        try:
                            reviews_test = find_tags(driver, dic_tag['allreviews'])
                            print('fine~~~~~~~~~~')
                        except Exception as e:
                            print('error~~~~~~~~，except，開始儲存店家list')
                            print(e)
                            traceback.print_exc()
                            lst_store = save_csv(stores_path, lst_store)  # 儲存後回傳空的list
                            bError = True
                            bfinal = True

                        if len(allreviews) > 0:
                            for j in allreviews:
                                if '評論' in j.get_attribute(dic_tag['label']):
                                    j.click()
                                    print('已點擊"所有評論"，總共有:', j.get_attribute(dic_tag['label']))
                                    total_review = int(j.get_attribute(dic_tag['label']).split(' ')[0].replace(',','')) # 總共有幾則評論
                                    sort = find_tags(driver, dic_tag['ddl']) # 找到能依"最新日期, 相關度..."排序的下拉選單tag

                                    print('點擊選擇排序的下拉式選單:', sort[-1].is_displayed())
                                    sort[-1].click() # 第0個是"撰寫評論"，所以選第二個

                                    menuitem = find_tags(driver, dic_tag['sort_item']) # 下拉選單中的所有選項
                                    for item in menuitem:
                                        if item.text == '最新':
                                            item.click()
                                            print('點擊選擇依時間最新來排序')
                                            break

                                    print('開始找section-loading')
                                    time.sleep(2)
                                    loading = driver.find_elements_by_class_name(dic_tag['loading']) # 找到loading tag點擊，就等於將滾輪往下滑，可以載入新的評論
                                    time.sleep(2)
                                    loading_count = 0 # 紀錄目前往下滑的loading次數
                                    record_time = 0  # 每往下滑loading 30次，就儲存一次loading次數
                                    record_date_count = 0 # 每往下滑loading 30次，就儲存一次目前取得的評論筆數
                                    while len(loading) != 0:
                                        loading_count += 1
                                        print('loading評論第' + str(loading_count) + '次', end=',')
                                        loading = driver.find_elements_by_class_name(dic_tag['loading'])
                                        time.sleep(2)
                                        lstdate = find_tags(driver, dic_tag['review_date']) # 取得目前載入的評論數目

                                        if loading_count - record_time >= 30: # 目前loading次數 與 紀錄loading次數 相差 30次以上就更新紀錄
                                            if len(lstdate) > record_date_count: # 目前載入的評論數 > 紀錄的評論數-->就更新紀錄的評論數
                                                print('原本紀錄的loading次數:', record_time, ',更新為:', loading_count)
                                                print('原本紀錄的評論數:',record_date_count, ',更新為:', len(lstdate))
                                                record_date_count = len(lstdate)
                                                record_time = loading_count
                                            else:
                                                print('無法載入新的評論，Chrome 掛掉了，放棄載入新的評論', name)
                                                bError = True # 正常來說，每下滑一次就會取得新的評論，
                                                bfinal = True # 所以每下滑30次檢查一次，目前載入的評論數目會 > 已記錄的評論數才對
                                                break         # 若沒大於，代表它一直往下滑，但卻沒有載入新的評論數-->瀏覽器掛掉了
                                        loading_date = lstdate[-1].text

                                        print('saved_latest_date：',saved_latest_date, 'loading_date：', get_real_date(loading_date),', len(loading)：' ,len(loading), loading[-1].is_displayed())
                                        # if '年' in loading_date and  int(loading_date.split(' ')[0]) > 4:
                                        #     print('目前最後一個評論已超過五年，不需再往下滑了')
                                        #     break
                                        if saved_latest_date != '' and get_real_date(loading_date) < saved_latest_date:
                                            print('目前最後一個評論日期', get_real_date(loading_date), '已 < 最新儲存日期:', saved_latest_date, '，不需再往下滑了')
                                            break
                                        elif len(loading) == 0:
                                            print('沒有section-loading了，停止往下滑')
                                            break
                                        if not loading[-1].is_displayed(): # 若元素沒有出現在畫面上，但仍要對它做動作，會出現錯誤"element not interactable”
                                            print('loading[-1]還沒出現，等2秒')
                                            time.sleep(2)
                                            if not loading[-1].is_displayed():
                                                print('loading[-1]沒有顯示，放棄載入新的評論', name)
                                                break
                                        loading[-1].click()

                                    each_review = find_tags(driver, dic_tag['review_text'])

                                    print('開始顯示所有評論數量:', len(each_review))
                                    print('=========================================')

                                    stars = find_tags(driver, dic_tag['review_star']) # 找到評論的星星數
                                    publish_date = find_tags(driver, dic_tag['review_date']) # 找到評論發表日期
                                    for k in range(len(each_review)):
                                        word = each_review[k].text.split('(原始評論)')
                                        # ======= 每個評論的字典都要先清空，不然會連動到上一個塞進List的dict  =============
                                        dic_review = {}
                                        review_date = publish_date[k].text # '1 週前'
                                        review_star = stars[k].get_attribute(dic_tag['label']).split(' ')[1] #' 5 顆星 '
                                        dic_review['tmpid'] = k+1
                                        dic_review['date'] = get_real_date(review_date)
                                        dic_review['star'] = review_star
                                        review_text = ''
                                        if each_review[k].text != "":
                                            if len(word) > 1:
                                                review_text = word[0].replace('(由 Google 提供翻譯)', '') # 非中文的話只取google翻譯過後的中文
                                            else:
                                                review_text = each_review[k].text

                                        review_text = '"' + review_text.replace('\r', '').replace('\n', '，') + '"' # 評論裡的換行符號改成"，"
                                        print('第' + str(k + 1), end=',')
                                        # print('第' + str(k + 1) + '筆:', '日期:', review_date, '星等:', review_star, '評論:',review_text)
                                        dic_review['text'] = review_text

                                        # if '年' in publish_date[k].text and  int(publish_date[k].text.split(' ')[0]) > 3:
                                        #     print('超過四年的評論不使用，擷取評論結束')
                                        #     break
                                        if saved_latest_date != '' and get_real_date(review_date) == saved_latest_date and review_text == saved_latest_review:
                                            print('這個評論日期 == 最新儲存日期，且評論內容 == 最新儲存評論內容，擷取評論結束')
                                            break
                                        elif saved_latest_date != '' and get_real_date(review_date) < saved_latest_date:
                                            print('這個評論日期', get_real_date(review_date) , '已 < 最新儲存日期:', saved_latest_date, '，擷取評論結束')
                                            break
                                        elif saved_latest_date != '' and not '天' in review_date:
                                            print('只更新一週內的評論，超過的不更新，這個評論日期：', get_real_date(review_date))
                                            break
                                        elif review_text == '""':
                                            print('空白評論不儲存！', end=',')
                                            empty_review += 1
                                            continue
                                        lst_review.append(dic_review)
                                    break

                            # print('====== 將該店家的review list放進該店家資訊的dic_store ===============')
                            dic_store['review'] = len(lst_review)  # 紀錄已儲存的評論數
                            dic_store['empty_review'] = empty_review # 紀錄空白的評論數
                            if not os.path.exists(review_path):
                                lst_store.append(dic_store)  # 若該店家已存過就不重複更新stores.csv

                            print('\n開始儲存review：', review_path, '，總評論數：', total_review, '，儲存評論筆數：', len(lst_review),'、空白評論筆數：', empty_review)
                            lst_review = save_csv(review_path, lst_review) # 儲存後回傳空的list
                        else:
                            print('這個店家完全沒有評論, ', name)

                        if not bfinal:
                            back_store = find_tags(driver, dic_tag['back_store'])
                            back_store[0].click()
                            print('已點擊返回店家資訊:')

                    if not bfinal:
                        back_list = find_tags(driver, dic_tag['back_list'])
                        back_list[0].click()
                        print('已點擊返回搜尋列表')
                        time.sleep((2))

            print('目前這頁爬完了，換下一頁，目前在第', page, '頁，已點過的店家數:', count_store)
            print('開始儲存店家list')
            lst_store = save_csv(stores_path, lst_store) # 儲存後回傳空的list

            if bfinal:
                print('跳出while')
                break
            try:
                nextpage = driver.find_element_by_id(dic_tag['next_page']) # 找到可以點擊下一頁的tag
                count_store = 0
                if nextpage.get_attribute('disabled') != 'true':
                    print('已點擊下一頁')
                    nextpage.click()
                    time.sleep(2)
                else:
                    bfinal = True # 若真的是最後一頁，tag的屬性disabled="true"，無法點擊
                    print('最後一頁了，下一頁disabled="true"')
            except Exception as e:
                print(e)
                print('最後一頁了，找不到 next_page tag，except，開始儲存店家list')
                lst_store = save_csv(stores_path, lst_store) # 儲存後回傳空的list
                traceback.print_exc()
                bError = True
                bfinal = True
        except Exception as e:
            print(e)
            print('except，開始儲存店家list')
            lst_store = save_csv(stores_path, lst_store) # 儲存後回傳空的list
            traceback.print_exc()
            bError = True
            bfinal = True
print('結束了~~~~~~~~~~~~~~~~')
time.sleep(3)
end_time = time.time()
total_time = end_time-start_time

m, s = divmod(total_time, 60)
h, m = divmod(m, 60)
print ("花費時間，時:%02d, 分:%02d, 秒:%02d" % (h, m, s))
# print(time.strftime("%H:%M:%S", total_time))
# print('{:d}:{:02d}:{:02d}'.format(h, m, s)) # Python 3
# print(f'{h:d}:{m:02d}:{s:02d}') # Python 3.6+
# driver.close()