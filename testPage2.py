#!/usr/bin/python
# -*- coding: utf-8 -*-
# author ecalf

import sys
import urllib2
import urllib
from urllib2 import URLError, HTTPError 
import zlib
import codecs

# print "脚本  ", sys.argv[0]
# print '参数  ', sys.argv[1:]
# print '============'




def showMsg( msg='', isWarn=False):
	if isWarn:
		print '\033[1;91m '+msg+' \033[0m' 
	else:
		print '\033[1;0m '+msg+' \033[0m'	

def printReport(text='',reportFile=None):
	print text
	if reportFile and isinstance(reportFile,file):
		print >> reportFile, text

def getCmdParams(params):
	fileIn = ''
	fileOut = ''
	outPutConfig = {
		'printBodyLength':0,
		'printHeaders':False
	}
	


	if len(params)==1:
		fileIn = params[0]
		
	else:
		for i,param in enumerate(params):
			if param.lower() == '-f':
				if i+1>=len(params):
					showMsg('请指定url配置文件',True)
				else:
					fileIn = params[i+1]
			elif param.lower() == '-out':
				if i+1>=len(params):
					showMsg('请指定测试报告输出文件路劲',True)
				else:
					fileOut = params[i+1]
			elif param.lower() == '-print':
				if i+1>=len(params):
					showMsg('请指定打印数据的长度',True)
				else:
					try:
						outPutConfig['printBodyLength'] = int(params[i+1])
					except Exception,err:
						showMsg('指定打印请求返回的数据长度应该输入数字',True)
			elif param.lower()=='-headers':
				outPutConfig['printHeaders'] = True

	return fileIn,fileOut,outPutConfig



def getUrlList(fileIn):
	try:
		fileObj = open(fileIn,'r')
		fileContent = fileObj.read()
	except Exception,err:
		showMsg('无法读取文件:'+fileIn,True)
	finally:
		if fileObj:
			fileObj.close()


	if fileContent[0:3]==codecs.BOM_UTF8:
		fileContent = fileContent[3:]
		
	dataType = 'string'
	try:
		urlsConfig = eval(fileContent)
		if isinstance(urlsConfig,dict):
			dataType = 'list'

	except Exception,err:
		#showMsg('parse fileContent err>>>'+str(err),True)
		pass


	urls = []
	option = None
	try:
		if dataType=='string':
			lines = fileContent.split('\n')
			for url in lines:
				if url.replace(' ', ''):
					urls.append(url)

		elif dataType.lower()=='list':
			option = urlsConfig['option']
			urls = urlsConfig['urls']

	except Exception,err:
		showMsg('文件读取错误，请使用UTF8编码保存URL配置文件',True)

	return urls,option



def getCommonHeaders():
	headers = {
		'Connection':'keep-alive',  
		'Cache-Control':'max-age=0',  
		'Accept': 'text/html,application/xhtml+xml,application/xml,application/json;q=0.9,image/webp,image/apng,*/*;q=0.8',
		'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Safari/537.36',  
		'Pragma': 'no-cache',
		'Cache-Control': 'no-cache',
		'Accept-Encoding': 'gzip, deflate',  
		'Accept-Language': 'zh-CN,zh;q=0.9'  
	}

	return headers

def setHost(request,host):
	request.add_header('Host', host)

def setCookie(request,cookieStr):
	request.add_header('Cookie', cookieStr)

def initConfig(urlConfig,option):
	method = 'GET'
	headers = getCommonHeaders()
	data = {}

	#from option
	if isinstance(option,dict):
		if 'method' in option:
			method = option['method']

		if 'headers' in option and isinstance(option['headers'],dict):
			headers.update(option['headers'])

		if 'data' in option and isinstance(option['data'],dict):
			data.update(option['data'])

	#from urlConfig
	if 'method' in urlConfig:
			method = urlConfig['method']

	if 'headers' in urlConfig and isinstance(urlConfig['headers'],dict):
		headers.update(urlConfig['headers'])
	
	if 'data' in urlConfig and isinstance(urlConfig['data'],dict):
		data.update(urlConfig['data'])

	if len(data.keys())==0:
		data = None

	return  urlConfig['url'],method,headers,data


def initRequest(url,data=None,method='GET',headers=None):
	url =  urllib.quote(url.strip(),safe="$#&+;/:,=?@")
	if data:
		data = urllib.urlencode(data)

	if method.upper()=='GET':
		if data:
			searchStartIndex = url.find('?')
			if searchStartIndex>-1:
				url = url[0:searchStartIndex]+'?'+data+'&'+url[searchStartIndex+1:]
			else:
				anchorIndex = url.find('#')
				if anchorIndex>-1:
					url = url[0:anchorIndex]+'?'+data+url[anchorIndex:]
				else:
					url = url+'?'+data
		request = urllib2.Request(url,None,headers) 
	else:
		if not data:
			data = ''
		request = urllib2.Request(url,data,headers)

	return 	request,url


def startTest(urls,option,fileOut,outPutConfig):
	if len(urls)==0:
		showMsg('url list is empty',True)
		return

	reportFile = ''
	if fileOut:
		try:
			reportFile = open(fileOut,'w')
		except Exception,err:
			showMsg('创建报告文件失败:'+str(err),True)



	counter = {
		'count200':[],
		'count401':[],
		'count404':[],
		'count500':[],
		'count502':[],
		'countURLError':[],
		'countException':[],
	}

	
	for i,urlConfig in enumerate(urls):
		i=i+1

		try:
			if isinstance(urlConfig,basestring):
				url = urlConfig
				urlConfig = {}
			else:
				url = urlConfig['url']


			method = 'GET'
			if 'method' in urlConfig:
				method = urlConfig['method']

			if url[:4].upper()=='POST':
				method = 'POST'
				url = url[4:]
			elif url[:3].upper()=='GET':
				method = 'GET'
				url = url[3:]

			urlConfig['method'] = method
			urlConfig['url'] = url.strip()

			url,method,headers,data = initConfig(urlConfig,option)
			request,url = initRequest(url,data,method,headers)
			response = urllib2.urlopen(request)
			


			body = response.read()
			gzipped = response.headers.get('Content-Encoding')
			if gzipped:
			    	body =zlib.decompress(body, 16+zlib.MAX_WBITS)
			    	#print 'zlib.decompress body'

			if outPutConfig['printHeaders']==True or outPutConfig['printBodyLength']>0:
				printReport('----------------------------------------------------------------',reportFile)
				

			if 	outPutConfig['printHeaders']==True:
				printReport(response.info(),reportFile)

			if outPutConfig['printBodyLength']>0:
				printReport(body[:outPutConfig['printBodyLength']],reportFile)


			statusCode = response.getcode()
			countKey = 'count'+str(statusCode)
			if countKey not in counter:
				counter[countKey] = []

			counter[countKey].append(i)
			msg = '['+str(i)+']'+'\t'+str(statusCode)+'\t\t'+method.upper()+' '+url

			if response.geturl()!=url:
				msg = msg+' redirect =>'+response.geturl()

			showMsg(msg)
			if reportFile and isinstance(reportFile,file):
				reportFile.write(msg+'\n')

		except HTTPError, err: 
			#print err,err.code,err.reason
			stateText = err.reason
			statusCode = err.code

			countKey = 'count'+str(statusCode)
			if countKey not in counter:
				counter[countKey] = []

			counter[countKey].append(i)
				
			#print err.reason
			msg = '['+str(i)+']'+'\t'+str(statusCode)+'\t\t'+method.upper()+' '+url
			showMsg(msg,True)
			if reportFile and isinstance(reportFile,file):
				reportFile.write(msg+'\n')
		except URLError, err: 
			counter['countURLError'].append(i)
			
			msg = '['+str(i)+']'+'\tURLError'+'\t'+method.upper()+' '+url
			showMsg(msg,True)
			if reportFile and isinstance(reportFile,file):
				reportFile.write(msg+'\n')

		except Exception,err:
			counter['countException'].append(i)

			msg = '['+str(i)+']'+'\tException:'+str(err)+'\t'+method.upper()+' '+url
			showMsg(msg,True)
			if reportFile and isinstance(reportFile,file):
				reportFile.write(msg+'\n')
				

		

	reportMsg = []
	reportMsg = reportMsg+['\n\n------------ test report,  Total:',str(i),' --------------','\n']
	reportMsg = reportMsg+['status   ','\t','count','\t','index','\n']

	countKeys = counter.keys()
	countKeys.sort()
	for i,key in enumerate(countKeys):
		statusColumn = key[len('count'):]+'         '
		statusColumn = statusColumn[:9]
		countColumn = str(len(counter[key]))
		if len(countColumn)<5:
			countColumn = countColumn+'     '
			countColumn = countColumn[:5]



		reportMsg = reportMsg+[statusColumn,'\t',countColumn,'\t',str(counter[key]),'\n']


	# reportMsg = reportMsg+['ok','\t',str(len(counter['countOk'])),'\t',str(counter['countOk']),'\n']
	# reportMsg = reportMsg+['40*','\t',str(len(count400)),'\t',str(count400),'\n']
	# reportMsg = reportMsg+['50*','\t',str(len(count500)),'\t',str(count500),'\n']
	# reportMsg = reportMsg+['err','\t',str(len(countErr)),'\t',str(countErr),'\n']
	# reportMsg = reportMsg+['??','\t',str(len(Exception)),'\t',str(Exception),'\n']
	reportMsg = reportMsg+['---------------------------------------------------','\n']
	reportMsg = reportMsg+['\n\n']
	reportMsg = ''.join(reportMsg)

	printReport(reportMsg,reportFile)
	if reportFile and isinstance(reportFile,file):
		reportFile.close()



params = sys.argv[1:]
fileIn,fileOut,outPutConfig = getCmdParams(params)
urls,option = getUrlList(fileIn)
startTest(urls,option,fileOut,outPutConfig)









	
