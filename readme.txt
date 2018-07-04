
testPage.py 简单版，只能测试无登录状态GET URL 配置写在 脚本里面,直接执行该脚本






testPage2.py 需要通过配置文件配置URL

1、使用参数 -f 指定url配置文件
2、url文件简单配置, 每行一条URL 下面三种格式都可以，如果不声明 GET、POST 默认为GET请求
	https://www.wmzy.com/api/rank/schList?sch_rank_type=QS2018
	get https://www.wmzy.com/api/rank/schList
	post https://www.wmzy.com/account/saveEduInfo

	调用命令: ./testPage2.py -f ./urls.txt

3、通过 list 配置带有参数和信息头的的URL
	配置文件是严格的 python 字典类型数据，包含 option 和 urls 两个 key
	option:字典类型, 可以配置 method,headers,data,	会被list 内 url的配置覆盖
	urls: list 类型, 每个元素配置一条url，格式如下
	
	简单的get请求可以是url字符串
	带有额外配置信息的URL使用字典配置
		url: url地址
		method:缺省认为GET
		headers：字段类型，请求头信息
		data:数据，缺省默认为 None 
		
	


	调用命令:  ./testPage2.py -f ./urls2.txt

4、使用参数 -out 输出测试报告文件
	调用命令:  ./testPage2.py -f ./urls2.txt -out ./report.txt

5、通过参数 -print 100 指定:请求测试通过时打印请求返回内容的前100个字符
6、通过参数 -headers 指定:请求测试通过时打印请求返回的头信息
	调用命令: ./testPage2.py -f ./ajaxTestUrls.txt -out ./report.txt  -print 200
