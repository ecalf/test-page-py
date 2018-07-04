#!/usr/bin/python
# -*- coding: utf-8 -*-
# author ecalf

import urllib

pages = [
	"https://www.wmzy.com/api/rank/schList?sch_rank_type=QS2018",
	"https://www.wmzy.com/api/rank/schList",
	"https://www.wmzy.com/api/school/getSchList?prov_filter=44&type_filter=0&diploma_filter=0&flag_filter=0&page=2&page_len=20&_=1529798214101",
	"https://www.wmzy.com/api/school/3bzwryxx.html",
	"https://www.wmzy.com/api/school/getSchList?prov_filter=shenzhen&type_filter=0&diploma_filter=0&flag_filter=0&page=2&page_len=20&_=1529798214101",
	"https://www.wmzy.com/static/outer/js/aq_auth.js",
	"https://cloud.tenxasdasdcent.com/deasdasdasdvelopera/aasdasdsk/asd42279/answer/63957",
	"absdad"
]





count200 = []
count404 = []
count500 = []
countErr  = []

for i,pageurl in enumerate(pages):
	i=i+1
	try:
		reqInfo=urllib.urlopen(pageurl)
		status = reqInfo.code
		if status/100==2:
			count200.append(i)
		if status/100==4:
			count404.append(i)
		if status/100==5:
			count500.append(i)

		if status!=200:
			print '\033[1;91m '+'['+str(i)+']'+'\t'+str(status)+'\t'+pageurl+' \033[0m'
		else:
			print '\033[1;0m '+'['+str(i)+']'+'\t'+str(status)+'\t'+pageurl+' \033[0m'
	except Exception as err:  
		countErr.append(i)
		print '\033[1;91m '+'['+str(i)+']'+'\t'+'error'+'\t'+pageurl+' \033[0m' 

	


print '\n\n============ test result report ================'
print 'status','\t','count','\t','index'
print 200,'\t',len(count200),'\t',count200
print 404,'\t',len(count404),'\t',count404
print 500,'\t',len(count500),'\t',count500
print 'err','\t',len(countErr),'\t',countErr
print '\n\n'