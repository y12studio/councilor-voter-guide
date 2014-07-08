# -*- coding: utf-8 -*-
import re
import codecs
import psycopg2
import json
from datetime import datetime


def SittingsAbbreviation(key):
    d = json.load(open('util.json'))
    return d.get(key)

def FileLog(c, sitting):
    c.execute('''
        INSERT into councilors_filelog(sitting, date)
        SELECT %s, %s
        WHERE NOT EXISTS (SELECT 1 FROM councilors_filelog WHERE sitting = %s) RETURNING id
    ''', (sitting, datetime.now(), sitting))

def GetDate(text):
    matchTerm = re.search(u'''
        (?P<year>[\d]+)[\s]*年[\s]*
        (?P<month>[\d]+)[\s]*月[\s]*
        (?P<day>[\d]+)
    ''', text, re.X)
    if matchTerm:
        return '%04d-%02d-%02d' % (int(matchTerm.group('year'))+1911, int(matchTerm.group('month')), int(matchTerm.group('day')))
    else:
        return None

def getId(c, name, ad, county):
    c.execute('''
        SELECT councilor_id
        FROM councilors_councilorsdetail
        WHERE name = %s and ad = %s and county = %s
    ''', (name, ad, county))
    r = c.fetchone()
    if r:
        return r[0]
    print name

def getDetailId(c, name, ad, county):
    c.execute('''
        SELECT id
        FROM councilors_councilorsdetail
        WHERE name = %s and ad = %s and county = %s
    ''', (name, ad, county))
    r = c.fetchone()
    if r:
        return r[0]
    print name

def getIdList(c, name_list, sitting_dict):
    c.execute('''
        SELECT id, councilor_id
        FROM councilors_councilorsdetail
        WHERE name IN %s and ad = %s and county = %s
    ''', (tuple(name_list), sitting_dict['ad'], sitting_dict['county']))
    r = c.fetchall()
    if r:
        return r
    print name_list
    return []

def getNameList(text):
    name_list, firstName = [], ''
    for name in text.split():
        if re.search(u'[）)。】」]$', name):   #立委名字後有標點符號
            name = name[:-1]
        #兩個字的立委中文名字中間有空白
        if len(name) < 2 and firstName == '':
            firstName = name
            continue
        if len(name) < 2 and firstName != '':
            name = firstName + name
            firstName = ''
        if len(name) > 4: #立委名字相連
            name = name[:3]
        name_list.append(name)
    return name_list

def AddAttendanceRecord(c, councilor_id, sitting_id, category, status):
    c.execute('''
        INSERT into councilors_attendance(councilor_id, sitting_id, category, status)
        SELECT %s, %s, %s, %s
        WHERE NOT EXISTS (SELECT 1 FROM councilors_attendance WHERE councilor_id = %s AND sitting_id = %s)
    ''', (councilor_id, sitting_id, category, status, councilor_id, sitting_id))

def Attendance(c, sitting_dict, text, category, status):
    for id, councilor_id in getIdList(c, getNameList(text), sitting_dict):
        AddAttendanceRecord(c, id, sitting_dict['uid'], category, status)

def InsertSitting(c, sitting_dict):
    complement = {"committee": '', "name": ''}
    complement.update(sitting_dict)
    c.execute('''
        UPDATE sittings_sittings
        SET name = %(name)s, ad = %(ad)s, session = %(session)s, date = %(date)s, county = %(county)s, committee = %(committee)s
        WHERE uid = %(uid)s
    ''', complement)
    c.execute('''
        INSERT into sittings_sittings(uid, name, ad, session, date, county, committee)
        SELECT %(uid)s, %(name)s, %(ad)s, %(session)s, %(date)s, %(county)s, %(committee)s
        WHERE NOT EXISTS (SELECT 1 FROM sittings_sittings WHERE uid = %(uid)s)
    ''', complement)

def UpdateSitting(c, uid, name):
    c.execute('''
        UPDATE sittings_sittings
        SET name = %s
        WHERE uid = %s
    ''', (name, uid))

def remote_newline_in_sittings(c):
    c.execute('''
        select uid, name
        from sittings_sittings
    ''')
    for uid, name in c.fetchall():
        UpdateSitting(c, uid, re.sub(u'[\s]', '', name))

def UpdateFileLog(c, id, sitting):
    c.execute('''
        UPDATE legislator_filelog
        SET sitting = %s
        WHERE id = %s
    ''', (sitting, id))

def remote_newline_in_filelog(c):
    c.execute('''
        select id, sitting
        from legislator_filelog
    ''')
    for id, sitting in c.fetchall():
        UpdateFileLog(c, id, re.sub(u'[\s]', '', sitting))