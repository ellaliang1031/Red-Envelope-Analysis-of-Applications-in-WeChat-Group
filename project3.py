"""A program to analyse the red envelopes of different apps shared 
   in a Wechat Group, and give different types of apps their special 
   suggestion about the popular advertising words and suitable time to
   release more red envelopes.

   Author: Chen Liang
   Student ID: 46275313
   Date: May 2018
"""
from tkinter import *
from tkinter.ttk import * 
import datetime
import jieba 
import jieba.analyse 
import os
from scipy.misc import imread
import wordcloud as wc
import matplotlib.pyplot as plt 
import numpy as np
import pandas as pd
from collections import Counter

class Red():
    """Red represents the red envelope observation, 
    data attributes: time of the red envelope being sent,
                     advertising words on the envelope,
                     domain name of the app which the red envelope belongs to."""
    
    def __init__(self, time, adwords, domain):
        """create a new Red object with the special time, adwords and domain"""
        self.time = time
        self.apptype = 'Unknown'
        self.adwords = adwords
        self.domain = domain
        
    def gettype(self):
        """recognise the type of app from the domain name, this part is based on
        the analysis of the domain list which contain the apps appearing more than
        30 times in total"""
        n = 0
        takeoutlist = ['ele', 'meituan', 'waimai', 'dianping.com', 'kuaizi', 'band']
        for item in takeoutlist:
            if item in self.domain:
                n += 1
        if n != 0:
            self.apptype = 'Takeout'
        elif ('play' in self.domain)  or ('animal' in self.domain):
            self.apptype = 'Mobile Game'
        elif ('mobike' in self.domain) or ('ofo' in self.domain):
            self.apptype = 'OFO'
        elif 'xiaojukeji' in self.domain:
            self.apptype = 'Taxi'
        elif 'weixin.qq.com' in self.domain:
            self.apptype = 'Third Party APP'
        elif ('xuxian' in self.domain) or ('fresh' in self.domain):
            self.apptype = 'Fruit Takeout'
        n = 0
        shoppinglist = ['dpurl', 'xiaohong', 'kaola', 'jd']
        for item in shoppinglist:
            if item in self.domain:
                n += 1
        if n != 0:
            self.apptype = 'Online Shopping'
        elif 'tenpay' in self.domain:
            self.apptype = 'Finance'
        elif 'dianying' in self.domain:
            self.apptype = 'Movie'  
        return self.apptype
            
def string_code_identify(b: bytes):
    """find out the code for the Chinese characters in dataset"""
    CODES = ['UTF-8', 'UTF-16', 'GB18030', 'BIG5'] 
    UTF_8_BOM = b'\xef\xbb\xbf'      
    for code in CODES:  
        try:  
            b.decode(encoding=code)  
            if 'UTF-8' == code and b.startswith(UTF_8_BOM):  
                return 'UTF-8'  
            return code  
        except Exception:  
            continue  
    return 'Characters with code not in CODES'              

def get_domain_name(address):
    """get the domain name from the web address of the red envelope"""
    from urllib.parse import urlparse
    domain_name = urlparse(address).netloc
    return domain_name

def get_domain_list(data):
    """get the list of all the domain name of the dataset"""
    domain_list = []
    from urllib.parse import urlparse
    for item in data['content']:
        content_list = str(item).split(' ')
        for string in content_list:
            if string.startswith('http'):
                domain_list.append(get_domain_name(string))
    return domain_list
    
def get_time(datetimestr):
    """get time from datetime string"""
    import datetime
    datetimelist = datetimestr.strip().split(' ')
    return datetime.datetime.strptime(datetimelist[1], '%H:%M')

def get_words(sentence):
    """split the advertising sentence into Chinese words"""
    tagsw = ''
    words = []
    if len(sentence) > 0:
        tags = jieba.analyse.extract_tags(sentence)
        tagsw = ",".join(tags)    
        for word in tagsw.split(','):
            words.append(word)
    return words

def wordfrequency(word_list):
    """count the word in wordlist"""
    freq = []
    counter = Counter(word_list)
    for a in counter.most_common(100):
        freq.append((a[0], a[1]))
    return freq

def count_domain(domain_list, countdomainfile):
    """count the number of domain in the domainlist and get the domain names
    which appeared more than 30 times in the data set, save the list in the 
    countdomainfile for later app type analysis"""
    domain_dic = {}
    domain_main = {}
    for item in domain_list:
        if item in domain_dic:
            domain_dic[item] += 1
        else:
            domain_dic[item] = 1
    for key,values in domain_dic.items():
        if values > 30:
            domain_main[key] = values
    output2 = open(countdomainfile, 'w')
    output2.write(str(sorted(domain_main.items(), key=lambda x:x[1],reverse = True)))
    output2.close()
    return domain_main  

def draw_bar(domain_main):
    """draw bar charts of the top five domain name in the frequency list and 
    save the figure"""
    domain_main1 = sorted(domain_main.items(),key = lambda x:x[1],reverse = True)
    domain_name = []
    domain_count = []
    for i in range(0, 5):
        domain_name.append(domain_main1[i][0])
        domain_count.append(domain_main1[i][1])
    y_pos = np.arange(len(domain_name))
    plt.bar(domain_name, domain_count, align='center', alpha=0.5)
    plt.xticks(y_pos, domain_name, rotation=12, fontsize = 6)
    plt.ylabel('Number')
    plt.savefig('domain_barchart.jpg')
    plt.close()

def draw_wordcloud(freq, n):    
    """draw the wordcloud plot based on the word count"""
    font = r'SourceHanSansSC-Bold.otf'
    back_figure = imread('timg.jpg')
    cloudplot = wc.WordCloud(background_color = 'white', 
                             max_words=8000, min_font_size = 10, 
                             font_path=font, mask = back_figure,max_font_size=150, 
                             random_state=42).generate_from_frequencies(dict(freq))
    image_colors = wc.ImageColorGenerator(back_figure)
    plt.imshow(cloudplot.recolor(color_func=image_colors))
    plt.axis("off")
    plt.savefig("wordcloud{}.jpg".format(n))
    plt.close()
     
def process_data(data, domain_main):
    """remove the useless observation which are not in the domain list"""
    remove_list = []
    appear = 0
    for index,row in data.iterrows():
        for key in domain_main.keys():
            if str(key) in str(row['content']):
                appear += 1
        if appear == 0:
            remove_list.append(index)
        appear = 0
    data = data.drop(remove_list)
    return data

def red_define(): 
    """turn the observations in the dataset into Red class and get the Red data list"""   
    with open('wechat.csv', 'rb') as f:
        print(string_code_identify(f.read()))  #UTF-8
    file = pd.read_csv('wechat.csv')
    data = pd.DataFrame(file)
    domain_list = get_domain_list(data)
    domain_main = count_domain(domain_list, 'countdomain.txt')
    draw_bar(domain_main)
    data = process_data(data, domain_main)
    #create Red dictionary
    data1 = []
    for _,row in data.iterrows():
        wordlist = []
        domain = ''
        try:
            wordlist = get_words(row['content'][0:(row['content'].index('http'))])
        except:
            wordlist = []
            continue
        domain = get_domain_name(row['content'][(row['content'].index('http')):])
        value = Red(get_time(row['time']), wordlist, domain)
        value.apptype = value.gettype()
        data1.append(value)
    return data1

def wordcloud_type(data):
    """seperate the observations into different types and get the 
    advertising words count and word cloud plot for each type"""  
    typelist = ['Takeout', 'Mobile Game', 'OFO', 'Taxi', 'Third Patry APP', 
                'Friut Takeout', 'Online Shopping', 'Finance', 'Movie']
    typeword = {}
    for red in data:
        for typename in typelist:
            if red.apptype == typename:
                if red.apptype in typeword:
                    typeword[red.apptype] += red.adwords
                else:
                    typeword[red.apptype] = red.adwords
    for key,value in typeword.items():
        typeword[key] = wordfrequency(value)
        draw_wordcloud(typeword[key], key)

def timeseries_dic(data):
    """get the time of all obervations for each type""" 
    typelist = ['Takeout', 'Mobile Game', 'OFO', 'Taxi', 'Third Patry APP', 
                'Friut Takeout', 'Online Shopping', 'Finance', 'Movie']    
    timetype = {}
    for red in data:
        for typename in typelist:
            if red.apptype == typename:
                if red.apptype in timetype:
                    timetype[red.apptype] += [red.time]
                else:
                    timetype[red.apptype] = [red.time]   
    return timetype

def todate(time, formattime):
    """turn the time string into datetime type"""
    return datetime.datetime.strptime(time, formattime)

def timeseries_draw(timetype):
    """plot the count of app for each type changing with time during a day"""  
    timecount = {}
    timerec = {}
    for key,value in timetype.items():
        for time in value:
            for i in range(1, 24):
                if ((todate('{}:30'.format(i - 1),'%H:%M') < time) and 
                    (todate('{}:30'.format(i),'%H:%M') > time)):
                    if i in timecount:
                        timecount[i] += 1
                    else:
                        timecount[i] = 1
            if ((todate('{}:30'.format(i),'%H:%M') < todate('0:30','%H:%M')) 
                or (todate('{}:30'.format(i),'%H:%M') > todate('23:30','%H:%M'))):
                if 24 in timecount:
                    timecount[24] += 1
                else:
                    timecount[24] = 1        
        timecountlist = sorted(timecount.items())
        timerec[key] = [timecountlist[0][0], timecountlist[1][0]]
        xlab = []
        ylab = []
        xtick = []
        for item in timecountlist:
            xlab.append(item[0])
            ylab.append(item[1])
        for i in range(0, 25, 2):
            xtick.append('{}:00'.format(i))
        plt.plot(xlab,ylab)
        plt.xticks(np.arange(0, 25, 2), xtick)
        plt.xlabel('Time')
        plt.ylabel('Count')        
        plt.savefig("timeseries{}.jpg".format(key))    
        plt.close()      
        timecount = {}


class recword():
    """Define the interface"""
    def __init__(self, window, wordrec): 
        self.wordrec = wordrec
        self.window = window
        self.window.title('APP Red Envelope in Wechat')
        labeltext = "Choose the Type of Your App, We will Surpprise You"
        self.header = Label(window, text=labeltext, font = ('Lucida Handwriting', 12))  
        self.header.grid(row=0, column=0, columnspan=2, pady=10)
        self.default = Label(window, text = '', font = ('Lucida Handwriting', 10))
        self.default.grid(row=1, column=1, rowspan=2)
        chosenlist = ['Not Sure', 'Takeout', 'Online Shopping', 'Taxi', 'OFO']
        self.typechosen = Combobox(window, width=20, values=chosenlist)
        self.typechosen.grid(column=0, row=1, padx=20)    
        self.typechosen.bind('<<ComboboxSelected>>', self.update_word)
        self.typechosen.current(0)        
        self.window.columnconfigure(0, minsize=150, weight=1)
        self.window.columnconfigure(1, minsize=150, weight=1)
        self.window.columnconfigure(2, minsize=150, weight=1)
        self.window.rowconfigure(1, minsize=100)        
        self.update_word(None)    
        
    def update_word(self, event):    
        """define """
        self.default['text']= self.wordrec[self.typechosen.get()]  
        self.typechosen.selection_clear()
    
                                       
def main():
    """the main function of the project, which contains three parts, data cleaning,
    words count and time series"""  
    """"""
    #process the data
    data1 = red_define()
    #word count
    wordcloud_type(data1)
    #time series
    timetype = timeseries_dic(data1)
    timeseries_draw(timetype)   
    #interface: the wordrec list below is obtained by analysing the wordcloud plot
    #and time series instead just using the word with high frequency, because the 
    #plot for some type with less observation is none sense, so just keep 4 types
    wordrec = {}
    wordrec['Not Sure'] = 'Suitable for All:\n red envelope(红包),\
    sending red envelope(发红包), the name of your app(app名称)'
    wordrec['OFO'] = 'Popular words:\nofo, yellow bicycle(黄车), low carbon(低碳),\
    riding(骑行), for free(免费), awards(有奖)\nGood Time:\n13:00~14:00, 17:00~19:00'
    wordrec['Online Shopping'] = 'Popular words:\nreceive(领取), household(家居),\
    finance(金融), skin care production(护肤品), discount ticket(直降券)\nGood Time:\n11:00~12:00'
    wordrec['Takeout'] = 'Popular words:\ndelicious(美味), rich food(美食),\
    sale(特惠), highest(最高), million(百万)\nGood Time:\n11:00~12:00, 17:00~18:00'
    wordrec['Taxi'] = 'Popular words:\npay the bill(买单), one touch(一触),\
    pick up(接驾), share(分享), minutes and seconds(分秒)\nGood Time:\n14:00~16:00, 18:00~20:00'    
    window = Tk()    
    worreccoment = recword(window, wordrec)
    mainloop()          
                
main()
        
    