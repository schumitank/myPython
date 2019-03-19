
# coding: utf-8

# ## 小象学院课程
# ## Pyhton数据分析
# ## 爬取PM2.5(细颗粒物)及空气质量指数(AQI)数据
# http://www.pm25.in/
# 提供PM2.5(细颗粒物)及空气质量指数(AQI)实时查询的网站，同时开放PM2.5监测数据查询的API给开发者使用！

# > **提示**：<br>
# 1、这样的文字将会指导你如何使用 jupyter Notebook 来完成项目。<br>
# 2、你可以通过单击代码区域，然后使用键盘快捷键 Shift+Enter 或 Shift+Return 来运行代码。或者在选择代码后使用执行（run cell）按钮执行代码。Markdown的文字区域也同样可以如此操作。<br>
# 3、在如下有# TODO 提示的地方，将代码补全，实现注释中所要求的功能。<br>
# 4、在有"** 回答：**" 提示的地方，回答其上所提出的问题。<br>

# ### 分析流程
# * 爬取url的网页数据：url可以是一级网址，也可以是二级网址
# * 依据二级网址获得城市指数
# * 依据一级网址获得热门城市的城市名称、城市链接（根据城市链接【二级网址】获得城市的指数数据）
# * 写入json文件
# * 主函数

# ### 项目分析
# 对网址http://www.pm25.in/ 进行分析，获得热门城市的名称和链接（二级网址），然后依据二级网址获得该城市的各种指数，以下对各种指数【AQI、PM2.5/1h、PM10/1h、CO/1h、NO2/1h、O3/1h、O3/8h、SO2/1h】进行说明<br>
# * city_name：热门城市名称
# * city_link：城市链接（二级网址）
# * AQI：空气质量指数(AQI)，即air quality index，是定量描述空气质量状况的无纲量指数
# * PM2.5/1h：颗粒物（粒径小于等于2.5μm）1小时平均
# * PM10/1h：颗粒物（粒径小于等于10μm）1小时滑动平均
# * CO/1h：一氧化碳1小时平均
# * NO2/1h：二氧化氮1小时平均
# * O3/1h：臭氧1小时平均
# * O3/8h：臭氧8小时滑动平均
# * SO2/1h：二氧化硫1小时平均<br>
# #### 对指数更详细说明的网址是：http://www.pm25.in/api_doc

# 导入需要的库

# In[52]:

import requests
from bs4 import BeautifulSoup
import json


# 爬取url的源代码，使用"html.parser"对源代码进行解析，该url可以是一级网址，也可以是二级网址

# In[83]:

def get_soup_obj(url):
    url_obj = requests.get(url)
    soup = BeautifulSoup(url_obj.content, 'html.parser')
    return soup


# 依据city_aqi_item['city_link']二级网址获得该城市的各种指数

# In[84]:

def get_secondpage(city_aqi_item):
    """
    功能：
        通过二级网址获得城市的一些指数
    参数：
        city_aqi_item：可以是字典，通过该字典可以获得二级网址，或者直接是二级网址，这个参数主要是为了能把二级网址传入方法中
    返回值：
        通过城市对应的链接（二级网址）获得该城市的各种指数
    """
#     TODO
#     通过城市对应的链接（二级网址）获得该城市的各种指数
    #print('papa...', city_aqi_item['city_name'])
    print(city_aqi_item)
    soup = get_soup_obj(city_aqi_item)
    
    data_div = soup.find('div', class_='span12 data')
    value_div_lst = data_div.find_all('div', class_='value')
    #print(value_div_lst)
    #print(value_div_lst[0])
    #print(value_div_lst[0].text)

    city_aqi_item={}
    city_aqi_item['aqi'] = float(value_div_lst[0].text)
    city_aqi_item['pm25'] = float(value_div_lst[1].text)
    city_aqi_item['pm10'] = float(value_div_lst[2].text)
    city_aqi_item['co'] = float(value_div_lst[3].text)
    city_aqi_item['no2'] = float(value_div_lst[4].text)
    city_aqi_item['o3_1h'] = float(value_div_lst[5].text)
    city_aqi_item['o3_8h'] = float(value_div_lst[6].text)
    city_aqi_item['so2'] = float(value_div_lst[7].text)

    return city_aqi_item




# 依据'http://www.pm25.in/' 网址获得热门城市下的所有城市名称，以及该城市对应的链接，以及该城市的各种指数【AQI、PM2.5/1h、PM10/1h、CO/1h、NO2/1h、O3/1h、O3/8h、SO2/1h】数据

# In[85]:

def get_fistpage_and_secondpage(url,soup):
    """
    功能：
        通过一级网址获得城市名称和对应的链接（二级网址），然后通过对应的链接（二级网址）得到该城市的一些指数，
        这个方法可以通过传参二级网址调用get_secondpage方法获得城市对应的各种指数
    参数：
        url:一级网址
        soup:需要分析的一级网址的源代码数据
    返回值：
        返回一个列表，列表的元素是字典，字典的元素是城市名称、城市对应的链接、城市的各种指数
    """
#     需要返回的列表
    city_aqi_list = []
    
#     TODO
#     对soup的源代码数据进行分析，获得城市名称，城市链接，然后根据城市链接获得该城市的各种指数

    bottom_div = soup.find('div', class_='hot')
    #print(bottom_div)
    city_lst = bottom_div.find_all('li')
    #print(city_lst)

    for city in city_lst:
        #print(city)
        row={}
        row['city_name'] = city.find('a').text
        city_link = url + city.find('a')['href']
        row['city_link'] = city_link
        row['city_items'] = get_secondpage(city_link)
        city_aqi_list.append(row)

    return city_aqi_list


# 将查询得到的数据下入json数据文件

# In[86]:

def write_city_aqi(city_aqi_data):
    file_path = './dataFile/city_aqi.json'
#     TODO
#     将得到的city_aqi_data数据存入json文件

    with open(file_path, mode='w',encoding='utf-8') as f_obj:
        json.dump(city_aqi_data, f_obj, ensure_ascii=False)



# 使用main函数执行以上方法

# In[87]:

if __name__=="__main__":
    
#     需要分析的url
    url = 'http://www.pm25.in/'
    
#     获得url的解析数据
    soup = get_soup_obj(url)
    
#     获得从一级网址和二级网址获得的结果数据综合
    city_aqi_list = get_fistpage_and_secondpage(url,soup)
    
#     对爬取到的热门城市名称、城市链接、城市的各种指数数据进行遍历
    for city_aqi in city_aqi_list:
        print(city_aqi)

    
#     将得到的数据写入json文件
    write_city_aqi(city_aqi_list)


# In[ ]:




# In[ ]:




# In[ ]:



