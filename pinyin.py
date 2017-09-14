# coding: utf-8
from pypinyin import lazy_pinyin
import pymysql

conn = pymysql.connect(host='', user='', passwd='', db='', charset='utf8')
cur = conn.cursor()

for i in range(1, 17960):
    cur.execute('select stu_name from student_album where id = {}'.format(i))
    results = cur.fetchone()
    temp = ""
    for each in lazy_pinyin(results):
        temp += each[0]
    sql = 'update student_album set stu_pinyin = "{}" where id = {}'.format(temp, i)
    cur.execute(sql)
    conn.commit()
