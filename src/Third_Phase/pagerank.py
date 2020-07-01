from bs4 import BeautifulSoup
from sortedcontainers import SortedList, SortedSet, SortedDict
from collections import Counter
from collections import defaultdict
import glob, os, re, requests
from urllib.request import urlretrieve
import tarfile


class Page_Rank(object):
	def __init__(self):
		self.folder_data_name = '../../files/data'
		self.file_folder_dir = '../../files/'
		self.dropbox_data_tar = 'https://www.dropbox.com/s/ut477x665aobz7e/data.tar.gz?dl=0'
		self.dropbox_headers = {'user-agent': 'Wget/1.16 (linux-gnu)'}
		self.this_dir = os.getcwd()

	def write_tar_file(self, response_content):
		tar_file_name = 'data.tar.gz'
		file = open(tar_file_name, 'wb')
		file.write(response_content)
		file.close()
		tar = tarfile.open(tar_file_name)
		tar.extractall()
		tar.close()


	"""	def compute_pagerank(self, urls, inlinks, outlinks, b=.85, iters=20)

		Return a dictionary mapping each url to its PageRank.
			Formula ---->	 R(u) = (1/N)(1-b) + b * (sum_{w in B_u} R(w) / (|F_w|)

		Initialize all scores to 1.0.

		Params:
			urls.......SortedList of urls (names)
			inlinks....SortedDict mapping url to list of in links (backlinks)
			outlinks...Sorteddict mapping url to list of outlinks
		Returns:
			A SortedDict mapping url to its final PageRank value (float)
	"""
	def compute_pagerank(self, urls, inlinks, outlinks, b=.85, iters=20):
		rw = defaultdict(lambda:0.0)
		pageRank = defaultdict(lambda:1.0)

		for outlink in outlinks:	rw[outlink]=len(outlinks[outlink])

		#initialize page ranks scores to 1
		for url in urls:	pageRank[url] = 1.0

		for i in range(iters):
			for url in urls:
				summ = 0.0
				for link in inlinks[url]:	summ += 1.0 * pageRank[link]/rw[link]
				pageRank[url] = (1/len(urls))* (1.0-b)+b*summ
		return SortedDict(dict(pageRank))


	def get_top_pageranks(self, inlinks, outlinks, b, n=50, iters=20):
		#get all the urls from the inlinks
		goturls = SortedList(dict(inlinks).keys())
		#do the compute page rank
		pageRank = self.compute_pagerank(goturls, inlinks, outlinks, b, iters)
		#sort the pageRank 
		topNPage = sorted(pageRank.items(), key=lambda x: x[1],reverse= True)
		#get only the top N pages
		finalTopNPage = topNPage[:n]
		return finalTopNPage



	def read_names(self, path):	#	Returns a SortedSet of names in the data directory.
		return SortedSet([os.path.basename(n) for n in glob.glob(path + os.sep + '*')])


	"""	def get_links(self, names, html)
		Return a SortedSet of computer scientist names that are linked from this
		html page. The return set is restricted to those people in the provided
		set of names.  The returned list should contain no duplicates.

		Params:
			names....A SortedSet of computer scientist names, one per filename.
			html.....A string representing one html page.

		Returns:
			A SortedSet of names of linked computer scientists on this html page, 
			restricted to elements of the set of provided names.	
	"""
	def get_links(self, names, html):
		listofHrefs = []
		listofHrefTexts = []
		FinalSortedSet = SortedSet()
		splice_char = '/'

		for i in range(0,len(listofHrefs)):
			value = listofHrefs[i][6:]
			listofHrefTexts.append(value)

		listofHrefTexts = re.findall(r'href="([^"]*)', html)

		for i in listofHrefTexts:
			value = i[6:]
			listofHrefs.append(value)
		listofHrefs = list(set(listofHrefs))

		for href in listofHrefs:
			for name in names:
				if(name == "Guy_L._Steele,_Jr"):
					names.remove(name)
					names.add("Guy_L._Steele,_Jr.")
				if(href == name):	FinalSortedSet.add(name)

		return FinalSortedSet

	
	"""	def read_links(self, path)
		Read the html pages in the data folder. Create and return two SortedDicts:
			-	inlinks: maps from a name to a SortedSet of names that link to it.
			-	outlinks: maps from a name to a SortedSet of names that it links to.
		
		For example:
			inlinks['Ada_Lovelace'] = SortedSet(['Charles_Babbage', 'David_Gelernter'], key=None, load=1000)
			outlinks['Ada_Lovelace'] = SortedSet(['Alan_Turing', 'Charles_Babbage'], key=None, load=1000)

		Returns:
			A (inlinks, outlinks) tuple(i.e., two SortedDicts)
	"""
	def read_links(self, path):
		# Define output dict
		inlinks = SortedDict() 
		outlinks = SortedDict()

		SetofNames = SortedSet()

		#reading all the folders from the path and creating a set of Computer Scientists names
		for name in self.read_names(path):
			if name == "Guy_L._Steele,_Jr":	name = "Guy_L._Steele,_Jr."

			SetofNames.add(name)

			#creating an empty inlinks of names as sortedSet
			inlinks[name] = SortedSet()

		#reading their inlinks and outlinks
		for name in SetofNames:
			SetOfInLinks = SortedSet()
			fp = open(path + "/"+ name,'r',encoding = "utf-8")
			soup = BeautifulSoup(fp.read(),"html.parser")
			linksFound = []
			linksFound = soup.findAll('a', href=re.compile("/wiki/"))

			HTML = ""
			for link in linksFound:
				HTML = HTML + str(link)
				HTML = HTML + " and "

			#get All the outlinks by calling get_links
			outlinks[name] = self.get_links(SetofNames,HTML)

			if name in outlinks[name]:	outlinks[name].remove(name)

			for outlink in outlinks[name]:
				SetOfInLinks.add(name)
				inlinks[outlink].update(SetOfInLinks)
		return (inlinks,outlinks)

	
	def main(self):
		if not os.path.exists(self.folder_data_name):
			print("Downloading wikipedia CS Pages")
			os.chdir(self.file_folder_dir)
			response = requests.get(self.dropbox_data_tar, stream=True, headers=self.dropbox_headers)
			response_content = response.content
			self.write_tar_file(response_content)

		print('Before calling read_links')
		(inlinks, outlinks) = self.read_links(self.folder_data_name)

		print('Read %d people with a total of %d inlinks' % (len(inlinks), sum(len(v) for v in inlinks.values())))
		print('Read %d people with a total of %d outlinks' % (len(outlinks), sum(len(v) for v in outlinks.values())))


		topn = self.get_top_pageranks(inlinks, outlinks, b=.8, n=20, iters=10)

		print('\nTop page ranks:\n%s' % ('\n'.join('%s\t%.5f' % (u, v) for u, v in topn)))

		os.chdir(self.this_dir)




if __name__ == '__main__':
	Page_Rank_Obj = Page_Rank()
	Page_Rank_Obj.main()