# 在审IPO项目的爬取与处理



**功能：**

此项目使用python爬虫爬取深交所、上交所、证监会及东方财富网的数据，获取了创业板、科创板、主板、中小板的IPO在审项目的详细信息。



此项目依赖的第三库包括**requests**, **BeautifulSoup**, **pickle**, **pandas**, **csv**需要提前安装：

```bash
pip install requests
pip install bs4
pip install pickle
pip install pandas
pip install csv
```



**使用方法：**

```bash
python ./src/main.py
```



文件数据保存在/data/文件夹中
/data/EastMoney/ 保存东方财富网源数据
/data/证监会文件/ 保存项目反馈意见
/data/IPO/ 为各项目单独的数据和文件（pdf文件暂未下载）

项目详细数据以python字典的形式保存在/saved_config/文件夹的.pkl文件中。
szcyb_stocksInfo.pkl 为创业板所有在审项目详细信息
shkcb_stocksInfo.pkl 为科创板所有在审项目详细信息
zb_zxb_stocksInfo.pkl 为主板中小板所有项目详细信息（待核对）


**待完成：**
1. 目前科创板和创业板数据能完整获取，也做了简单的静态html展示页面，主板中小板的数据比较分撒，仍无法很好处理，还是半成品，也没有设计相应的html展示页面，等待后续添加
2. 目前数据以pyhthon dict格式保存，不易管理， 需设计数据库存储数据

