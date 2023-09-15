from PIL import Image
import csv
import re
import numpy as np
from wordcloud import WordCloud
import jieba
import matplotlib.pyplot as plt
import pandas as pd
import requests
import json
import multiprocessing
import time

plt.rcParams['font.sans-serif'] = ['SimHei']        # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False      # 用来正常显示符号

# 定义一个常量来存储文件名
danmu_file = 'danmu_data.csv'


def get_bvid(page, pos):
    try:

        # 构造搜索视频的API请求URL
        _url = 'https://api.bilibili.com/x/web-interface/search/all/v2?page=' + str(page + 1) + '&keyword=日本核污染水排海'

        # 构造请求头，包括用户代理信息和cookie
        _headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/116.0.0.0 Safari/537.36 Edg/116.0.1938.69',
            'cookie': "buvid3=84494823-6825-4308-FB2B-6A7A8368B42566066infoc; b_nut=1684242766; CURRENT_FNVAL=4048;"
                      " _uuid=21010568AE-754A-8159-C754-6D5C27F10107B866445infoc; buvid4=42FAC9B1-0422-0A2A-8A64-82F"
                      "43936FFA871340-022022019-H0Dgo27GdvKzjHRGWFdXiw%3D%3D; buvid_fp=b5f7b890d23b3c02c06cc18eaa6417"
                      "d3; rpdid=|(RYkm|~JJu0J'uY)RkRk~~|; i-wanna-go-back=-1; FEED_LIVE_VERSION=V8; header_theme_ver"
                      "sion=CLOSE; home_feed_column=5; DedeUserID=1460134606; DedeUserID__ckMd5=187e8dfdff780cc7; b_ut"
                      "=5; nostalgia_conf=-1; CURRENT_QUALITY=64; PVID=1; browser_resolution=1488-742; SESSDATA=587edd3"
                      "2%2C1709184545%2Cd3355%2A913IpTnXrMod4HMCSeYYRaYLOo9QDYXObvfOLMTnd7StvuIEF-hseEzI4HHTs0WmbXVblGz"
                      "gAABgA; bili_jct=9d23bd6f285f8004da547bbfbfa382f4"}

        req = requests.get(url=_url, headers=_headers).text  # 发起GET请求，获取响应结果的文本形
        json_dict = json.loads(req)  # 将获取的响应结果解析为Python字典对象
        return json_dict["data"]["result"][11]["data"][pos]["bvid"]  # 返回视频的bvid号

    # 异常处理
    except Exception as e:
        print("执行get_bvid报错：", e)       # 打印错误信息

def get_cid(bvid):
    try:
        # 构造API请求URL
        url = 'https://api.bilibili.com/x/player/pagelist?bvid=' + str(bvid) + '&jsonp=jsonp'
        res = requests.get(url).text  # 发起GET请求，获取响应结果的文本形式
        json_dict = json.loads(res)  # 将获取的网页json编码字符串转换为Python对象
        # print(json_dict)        # 打印整个转换后的结果，用于调试
        return json_dict["data"][0]["cid"]  # 返回获取到的视频信息的cid值

    # 异常处理
    except Exception as e:
        print("执行get_cid报错：", e)       # 打印错误信息


def get_data(cid):
    try:
        # 构造API请求URL
        final_url = "https://api.bilibili.com/x/v1/dm/list.so?oid=" + str(cid)
        final_res = requests.get(final_url)     # 发起GET请求获取数据
        final_res.encoding = 'utf-8'        # 设置编码为utf-8
        final_res = final_res.text          # 获取文本形式
        pattern = re.compile('<d.*?>(.*?)</d>')     # 使用正则表达式提取数据
        data = pattern.findall(final_res)
        return data     # 返回数据

    # 异常处理
    except Exception as e:
        print("执行get_data失败：", e)       # 打印错误信息


def save_to_file(data):
    try:
        # 打开 CSV 文件，以追加模式写入数据
        with open('danmu_data.csv', 'a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)       # 创建CSV writer对象
            # 遍历数据列表，逐行写入CSV文件
            for d in data:
                writer.writerow([d])

    # 异常处理
    except Exception as e:
        print("执行保存文件报错：", e)       # 打印错误信息


def ciyuntu():
    try:
        df = pd.read_csv(danmu_file)     # 使用pandas读取CSV文件
        txt = ''.join(df.astype(str).values.flatten())      # 将DataFrame转换为字符串
        txt_list = jieba.lcut(txt)      # 使用jieba进行中文分词
        string = ' '.join(txt_list)     # 将分词结果拼接为字符串
        mask_image = "protect.jpg"      # 读取自定义的图片作为词云图背景
        mask = np.array(Image.open(mask_image))
        # 创建词云图对象
        wc = WordCloud(background_color='blue',
                       font_path='C:/Windows/Fonts/SIMLI.TTF',
                       width=1000, height=700,
                       contour_width=1, contour_color='white',
                       mask=mask)
        wc.generate(string)     # 生成词云图
        wc.to_file('wordcloud.png')     # 保存词云图

    # 异常处理
    except Exception as e:
        print("执行词云图制作报错：", e)        # 打印错误信息


def print_danmu():
    try:
        # 读取csv文件，从第一列开始读取数据
        all_danmu = pd.read_csv(danmu_file, header=None, encoding='utf-8')
        counter = all_danmu.stack().value_counts()      # 统计每个弹幕出现的次数
        top_20 = counter.head(20).reset_index()     # 转换为DataFrame并重置索引
        top_20.columns = ['弹幕', '出现次数']     # 重命名列名
        print(top_20)
        counter.to_csv('danmu_counter.csv')     # 统计弹幕出现次数并存入csv

        top_20 = top_20.sort_values(by='出现次数', ascending=True)  # 按出现次数升序排序

        # 设置图表样式和布局
        plt.style.use('ggplot')
        plt.figure(figsize=(13, 6))

        # 绘制水平条形图
        plt.barh(top_20['弹幕'], top_20['出现次数'], color='steelblue')
        plt.xlabel('出现次数')
        plt.ylabel('弹幕')
        plt.title('Top 20 弹幕统计')
        plt.show()

    # 异常处理
    except Exception as e:
        print("执行输出弹幕报错：", e)       # 打印错误信息


def main(page):
    try:
        # 由于一页有20个视频,因此循环20次
        for j in range(20):
            save_to_file(get_data(get_cid(get_bvid(page, j))))  # 调用函数获取弹幕

    # 异常处理
    except Exception as e:
        print("执行main报错：", e)        # 打印错误信息


if __name__ == '__main__':
    try:
        # 记录开始时间
        start_time = time.time()

        pool = multiprocessing.Pool(15)  # 创建一个进程池，最大进程数为15
        # 循环创建15个进程，并指派给进程池执行
        for i in range(15):
            pool.apply_async(main(i), args=(i, danmu_file))  # main(i)表示爬取第i页弹幕数据
        pool.close()  # 关闭进程池，表示不再接受新的任务
        pool.join()  # 等待所有进程任务完成
        print("All workers finished")
        print_danmu()  # 输出数量前20的弹幕
        ciyuntu()  # 词云图制作


    # 异常处理
    except Exception as e:
        print("报错：", e)        # 打印错误信息
