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



数据保存在/data/文件夹，项目详细数据以python字典的形式保存在/saved_config/文件夹的.pkl文件中。



