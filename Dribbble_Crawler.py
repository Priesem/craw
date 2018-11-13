# coding=utf-8
import requests
import urllib2
import os
from lxml import html
import re
import wx
from threading import Thread
import time
from multiprocessing import Pool
from multiprocessing.dummy import Pool as ThreadPool
import logging

# 下载的页数
dribbble_page = 20
# 图片存储地址
global download_local_path
# 下载图片链接和title
images_titles_dataArr = []
# 需要下载的图片总数
total_images_count = 0
# 已下载图片数目
downloaded_images_count = 1
# 遗失的图片数目
missed_images_count = 0
# 信息返回窗口
contents = wx.TextCtrl
#主界面Frame
global mainApp
# pool数量
pool_number = 10

# 多线程
class mutiThread(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.start()
    def run(self):
        try:
            global contents
            dribbble_urls = []
            if dribbble_page == 1:
                dribbble_urls.append('https://dribbble.com/shots?page=1')
            else:
                for i in range(1,dribbble_page,1):
                    dribbble_urls.append('https://dribbble.com/shots?page=' + str(i))
            # 开始抓取
            contents.AppendText('Start crawling!!\nAffected by the network, this process requires a lot of time, please wait patiently !!')
            # 多线程池
            pool = ThreadPool(pool_number)
            response_bodys = map(self.get_responseData,dribbble_urls)
             # 获取到了所有的网页数据
            contents.AppendText('\n' + 'Get all html data, start getting the image_urls !!')
            pool.map(self.get_imageUrl_title,response_bodys)
            # 取到所需下载图片总数
            global total_images_count
            global images_titles_dataArr
            total_images_count = len(images_titles_dataArr)
            # 获取到了所有的图片链接
            contents.AppendText('\n' + 'Get all image_urls, start downloading the images !!')
            pool.map(self.download_images,images_titles_dataArr)
            # 下载完毕
            global mainApp
            mainApp.btnO.Enable(True)
            mainApp.btnS.Enable(True)
            contents.AppendText('Complete percent:  100.00000%')
            contents.AppendText('\n' + 'Downloading finished !! \nYou have %d images now!!'%(total_images_count))
            pool.close()
            pool.join()
        except:
            contents.AppendText('\n' + 'An exception error occurred. Please try again. ')
            mainApp.btnO.Enable(True)
            mainApp.btnS.Enable(True)

# 获得网页数据
    def get_responseData(self,dribbble_url):
        responseData = requests.get(dribbble_url)
        return responseData.text
# 获取图片下载链接和标题描述
    def get_imageUrl_title(self,response_body):
        try:
            parsed_body = html.fromstring(response_body)
            image_urls = parsed_body.xpath('//a[@class="dribbble-link"]/div/div[2]/@data-src')
            titles = parsed_body.xpath('//@data-alt')
            for image_url,title in zip(image_urls,titles):
                dataDic = {
                  'image_url' : image_url,
                  'title' : title
             }
                global images_titles_dataArr
                images_titles_dataArr.append(dataDic)
        except:
            print 'Miss one sigle url(Which means had missed one sigle images too)'
 # 正则过滤特殊字符
    def validateTitle(self,string):
        rstr = r"[\/\\\:\*\?\"\<\>\|]"
        new_title = re.sub(rstr, "", string)
        return new_title
# 获取图片的后缀
    def file_extension(self,path):
        return os.path.splitext(path)[1]
# 下载图片
    def download_images(self,dataDic):
        global contents
        global downloaded_images_count
        global total_images_count
        try:
            image_url = re.compile('_1x').sub('',dataDic['image_url'])
            image_name = self.validateTitle(dataDic['title']) + self.file_extension(image_url)
            os.chdir(download_local_path)
            os.getcwd()
            conn = urllib2.urlopen(image_url,timeout = 100).read()
            with open(image_name, "wb+") as f:
                f.write(conn)
            downloaded_images_count = downloaded_images_count + 1
            # 进度条
            percent = 1.0 * downloaded_images_count / total_images_count * 100
            if percent < 100:
                contents.AppendText('Complete percent:%10.8s%s'%(str(percent),'%') + str('\r'))
            time.sleep(0.1)
        except:
            contents.AppendText('An exception error occurred.Fixing......')
            downloaded_images_count = downloaded_images_count - 1
# 构建APP
class mainAppFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, -1, 'Dribbble crawler',
                size=(385, 280),style = wx.SYSTEM_MENU|wx.CAPTION|wx.CLOSE_BOX)

        panel = wx.Panel(self, -1)
        # 存储地址Label
        wx.StaticText(panel, -1, "PATH:",(10, 15),(35, -1),wx.ALIGN_LEFT)
        #地址栏
        self.TxtCfn = wx.TextCtrl(panel,pos=(50,10),size=(240,25),style = wx.TE_READONLY)
        #按钮
        self.btnO = wx.Button(panel, label="Select",pos=(300,10),size=(70,25))
        self.btnS = wx.Button(panel, label="Start",pos=(300,145),size=(70,100))
        self.btnO.Bind(wx.EVT_BUTTON, self.folderdialog,self.btnO)
        self.btnS.Bind(wx.EVT_BUTTON, self.start_crawling,self.btnS)
        # 下载页数选择
        wx.StaticText(panel, -1, "PAGE_NUMBER:",(10, 60),(120, -1),wx.ALIGN_LEFT)
        self.dribbble_page_slider = wx.Slider(panel, 1, 10, 1, 100, pos=(120, 45),size=(240, -1),style=wx.SL_HORIZONTAL | wx.SL_AUTOTICKS | wx.SL_LABELS )
        self.dribbble_page_slider.SetPageSize(1)
        self.Bind(wx.EVT_SLIDER,self.OnSlider_1,self.dribbble_page_slider)
        # 下载速度选择
        wx.StaticText(panel, -1, "POOL_NUMBER:",(10, 105),(120, -1),wx.ALIGN_LEFT)
        self.speed_slider = wx.Slider(panel, 2, 10, 1, 100, pos=(120, 90),size=(240, -1),style=wx.SL_HORIZONTAL | wx.SL_AUTOTICKS | wx.SL_LABELS )
        self.speed_slider.SetPageSize(1)
        self.Bind(wx.EVT_SLIDER,self.OnSlider_2,self.speed_slider)
        # 信息返回窗口
        global contents
        contents = wx.TextCtrl(panel,-1,pos=(10,145),size=(280,100),
                     style = wx.TE_AUTO_SCROLL | wx.TE_MULTILINE | wx.TE_READONLY)
        contents.SetForegroundColour('white')
        contents.SetBackgroundColour('black')
    #滑块选择方法（下载页数）
    def OnSlider_1(self,event):
        global dribbble_page
        dribbble_page = self.dribbble_page_slider.GetValue()
    #滑块选择方法（下载速度）
    def OnSlider_2(self,event):
        global pool_number
        pool_number = self.speed_slider.GetValue()
    # 选择文件目录
    def folderdialog(self,event):
     dialog = wx.DirDialog(None, "Choose a directory", style=1 )
     if dialog.ShowModal() == wx.ID_OK:
         chosepath = dialog.GetPath()
         if chosepath:
             self.TxtCfn.SetValue(chosepath)
             global download_local_path
             download_local_path = chosepath
     dialog.Destroy()
    # 开始爬取数据
    def start_crawling(self,event):
        if not self.TxtCfn.GetValue():
                dlg = wx.MessageDialog(None, u'Wrong directory!!', u'Erro',wx.ICON_ERROR)
                if dlg.ShowModal() == wx.ID_YES:
                    self.Close(True)
                    dlg.Destroy()
        else:
            contents.Clear()
            self.thread = mutiThread()
            self.btnO.Enable(False)
            self.btnS.Enable(False)

#主函数
if __name__ == '__main__':
        app = wx.App()
        global mainApp
        mainApp = mainAppFrame()
        mainApp.Show()
        mainApp.Center()
        app.MainLoop()
