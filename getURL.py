#!/usr/bin/python

'''
getURL reads URL from a external File sends a http 
request and writes the response inside the home_page folder which 
is created at the current active directory.

NOTE: Set MAXTHREADS to the number of CPU cores that your machine has for optimal performance
'''

import urllib2
import os
import thread

fname = 'myURL.txt' #File name which stores various URL's
dirname = 'home_page' #Name of the directory to be created
MAXTHREADS = 2 #Max number of threads to be created

writelock = thread.allocate_lock()
exitlock = [thread.allocate_lock() for i in range(MAXTHREADS)]


'''
Assigns Job to the threads that are created
'''
def assignJob(i, urlRange, urlList):
	#1. Split the urls into the range
	#2. Download the content for that range
	#3. If i is MAXTHREADS have to reconsider the last remaining URL's as well
	
	startPos = i * urlRange
	endPos = startPos + urlRange
		
	for pos in range(startPos, endPos):
		#Get the url and pass it to fetchContent()
		fetchContent(urlList[pos])		

	if(i == MAXTHREADS-1):
		for pos in range(endPos, len(urlList)):
			 fetchContent(urlList[pos])
			
			
	exitlock[i].acquire()


'''
Fetch the content of the individual URL's
'''
def fetchContent(url):
	writelock.acquire()
	print 'Fetching => ' + url
	writelock.release()	
	
	try:
		req = urllib2.Request(url)
		response = urllib2.urlopen(req)
		
		writeResponseToFile(response, url)
		
	except:
		writelock.acquire()
		print 'Unable to Fetch => ' + url
		writelock.release()
		
		
'''
Writing the HTTP response to the file
'''
def writeResponseToFile(response, url):
	filename = url.split('.')[1]
	global dirname
	
	writelock.acquire()
	try:
		fobj = open(os.path.join(dirname, filename), 'w+')
		fobj.write(response.read())
		fobj.close
	except:
		print 'Unable to Write to File'
	writelock.release()
	

'''
Creating Directory
'''
def createDir(dirname):	
	if not os.path.exists(dirname):
		try:
			os.makedirs(dirname)
		except:
			print 'Unable to create directory'
			sys.exit(0)



if(__name__ == "__main__"):
	
	try: 
		fobj = open(fname)
		urlList = [url.strip() for url in fobj.readlines()]
		fobj.close()
	except:
		print 'Unable to Open File, exiting'
		sys.exit(0)
		
	#Creating the home_page directory	
	createDir(dirname)
		
	#Finding the range to distribute the URL's to each of the threads
	urlRange = abs(len(urlList) / MAXTHREADS)
	
	for i in range(MAXTHREADS):
		thread.start_new_thread(assignJob, (i, urlRange, urlList))
		

	#Making sure the parent thread runs as long as the child threads are running
	
	for mutex in exitlock:
		while not mutex.locked(): pass
