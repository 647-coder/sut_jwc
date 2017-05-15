#! /usr/bin/env python
#coding:utf-8

import sys
import re
import urllib2
import urllib
import cookielib
import urllib2
import Image
import cStringIO
#import pytesseract
import time
import MySQLdb
from PIL import Image

reload(sys)  
sys.setdefaultencoding("utf8")

loginurl = 'http://jwc.sut.edu.cn/ACTIONLOGON.APPPROCESS'

class SutJWC(object):
    
    def __init__(self, username, password, agnourl=None):
        self.name = username
        self.password = password
        self.agnomenUrl = 'http://jwc.sut.edu.cn/ACTIONVALIDATERANDOMPICTURE.APPPROCESS' if not agnourl else agnourl
        self.allclass = {}
        self.allstu = []
        self.allinfo = {}
        self.error = []
        self.cj = cookielib.LWPCookieJar()
        self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cj)) 
        urllib2.install_opener(self.opener)

    def login(self):
        img = cStringIO.StringIO(urllib2.urlopen(self.agnomenUrl).read())
        image = Image.open(img)
        image.show()
        vcode = raw_input('Agnomen > ')
        #vcode = pytesseract.image_to_string(image)
        loginparams = { 'WebUserNO' : self.name,
                        'Password' : self.password,
                        'Agnomen' : vcode,
                        'submit.x': '30' ,
                        'submit.y' : '20'
                        }
        #headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.57 Safari/537.36'}
        req = urllib2.Request(loginurl, urllib.urlencode(loginparams))
        response = urllib2.urlopen(req)
        page = response.read().decode("GBK")
        if page.find(u"错误的用户名或者密码<br>") > 0:
            print "Error username or password."
            return
        if page.find(u"请输入正确的附加码<br>") > 0:
            print "Error Agnomen."
            return
        print 'Login Sucess!'
    
    def getClass(self):
        url = 'http://jwc.sut.edu.cn/ACTIONCLASSZHSCORE.APPPROCESS'
        response = urllib2.urlopen(url)
        page = response.read().decode("GBK")
        reg = '([0-9]{7,8})\[(.+)\]'
        com = re.compile(reg)
        find = re.findall(com, page)
        for each in find:
            classid, classname = each[0], each[1]
            self.allclass[str(classid)] = str(classname)

    def getStudent(self, key=None, sleep=None):
        url = 'http://jwc.sut.edu.cn/ACTIONQUERYCLASSCET.APPPROCESS?mode=2&query=1'
        reg = '<td align="center" height="24" width="30" >([0-9L]{8,})</td>'
        com = re.compile(reg)
        for each in self.allclass:
            params = { 'DeptNO' : "",
                       'ComeYear' : "",
                       'MajorNO' : "-1",
                       'ClassNO': int(each),
                       'BystudentNO' : ""
                       }
            data = urllib.urlencode(params)
            req = urllib2.Request(url, data)
            page = urllib2.urlopen(req).read()
            find = re.findall(com, page)
            self.allstu += find
            if sleep:
                time.sleep(sleep)

    def getinfo(self, sleep=None):
        all = len(self.allstu)
        url = 'http://jwc.sut.edu.cn/ACTIONQUERYSTUDENTBYSTUDENTNO.APPPROCESS?mode=2'
        reg_id = u'<td width="17%" height="30" align="left" valign="middle" nowrap class="color-row">([0-9]{9}|[0-9]{9}L{0,})</td>'
        reg_year = u'<td width="17%" height="30" align="left" valign="middle" nowrap class="color-row">([0-9]{4})</td>'
        reg_sex = u'<td width="17%" height="30" align="left" valign="middle" nowrap class="color-row">(男|女)</td>'
        reg_name_nation = u'<td width="17%" height="30" align="left" valign="middle" nowrap class="color-row">([\u4e00-\u9fa5]{2,})</td>'
        reg_major = u'<td width="28%" height="30" align="left" valign="middle" nowrap class="color-row">([\u4e00-\u9fa5()]{2,})</td>'
        reg_class = u'<td height="31" height="30" align="left" valign="middle" nowrap class="color-row">([\u4e00-\u9fa5()]{2,}[0-9]{2,}班)</td>'
        reg_city = u'<td height="36" colspan="2" align="left" valign="middle" nowrap class="color-row">([\u4e00-\u9fa5]{2,})</td>'
        reg_sid = u'<td height="33" colspan="2" align="left" valign="middle" nowrap class="color-row">([0-9xX]{18})</td>'
        com_id = re.compile(reg_id)
        com_year = re.compile(reg_year)
        com_sex = re.compile(reg_sex)
        com_name_nation = re.compile(reg_name_nation)
        com_major = re.compile(reg_major)
        com_class = re.compile(reg_class)
        com_city = re.compile(reg_city)
        com_sid = re.compile(reg_sid)
        for index, each in enumerate(self.allstu):
            print "Start [" + str(index) + "/" + str(all) + "] " + str(each),
            params = { 'ByStudentNO' : str(each) }
            tempinfo = {}
            try:
                tempinfo['pic'] = urllib2.urlopen('http://jwc.sut.edu.cn/ACTIONQUERYSTUDENTPIC.APPPROCESS?ByStudentNO=' + str(each)).read()
                data = urllib.urlencode(params)
                req = urllib2.Request(url, data)
                response = urllib2.urlopen(req)
                page = response.read().decode("GBK")
                tempinfo['id'] = re.findall(com_id, page)[0]
                tempinfo['year'] = re.findall(com_year, page)[0]
                tempinfo['sex'] = re.findall(com_sex, page)[0]
                tempinfo['name'], tempinfo['nation'] = re.findall(com_name_nation, page)
                tempinfo['major'] = re.findall(com_major, page)[1]
                tempinfo['class'] = re.findall(com_class, page)[0]
                city = re.findall(com_city, page)
                tempinfo['city'] = city[0] if city else "None"
                tempinfo['sid'] = re.findall(com_sid, page)[0]
                self.allinfo[each] = tempinfo
                print 'success.'
            except Exception, e:
                print e
                self.error.append(each)
                print 'fail.'
            finally:
                if sleep:
                    time.sleep(sleep)
        print 'Error', self.error

    def savesql(self, localhost, name, passwd, data, table):
        db = MySQLdb.connect(localhost, name, passwd, data, charset="utf8")
        sql = u"insert into " + str(table) + u"(stu_id, stu_name, stu_sex, stu_year, stu_nation, stu_city, stu_sid, stu_school, stu_major) values('%s','%s','%s','%s','%s','%s','%s','%s','%s')"
        cursor = db.cursor()
        for each in self.allinfo:
            cursor.execute((sql % each['id'], each['name'],  each['sex'],  each['year'],  each['nation'],  each['city'],  each['sid'],  each['major'],  each['class']).encode("UTF-8"))
        db.close()

if __name__ == '__main__':
    username = '*****'
    password = '*****'
    userlogin = SutJWC(username, password)
    userlogin.login()
    userlogin.getClass()
    userlogin.getStudent()
    userlogin.getinfo()
