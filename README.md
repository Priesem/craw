# DribbbleCrawler
A small crawler which has been addicted to the beauty of the designs!!
<center>![](http://i3.piimg.com/1fe7cb2e4735e154.png)</center>
##Windows平台应用程序
[点击获取](http://pan.baidu.com/s/1o88EH8Q)
## 使用
PATH:存储图片的地址

PAGE_NUMBER:抓取图片的网页页数

POOL_NUMBER:下载图片时候使用的线程池个数，建议不要过大，防止IP封杀。
## 废话
本虫，第一步使用多线程防止堵塞主UI。第二步使用map多线程队列下载，就算是国外的网站图片也还是抓取的很快。

#####后面会拓展出其他功能。
## 继续说废话
 >一般来说的话，写爬虫的话，少有连界面一起写出来的，但python的依赖安装并不十分友好，所以打包成exe文件也是为了更多的方便使用。

