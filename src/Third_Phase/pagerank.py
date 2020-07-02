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
		self.top_20_file = self.file_folder_dir + 'top_20.txt'
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


	def tabular_print_pagerank(self, list_of_tuples):
		new_list = []
		max_length_column = []
		element_in_tuple = 2

		for name, value in list_of_tuples:	new_list.append((name, str('%.5f' % value)))

		for i in range(element_in_tuple):	max_length_column.append(max(len(e[i])+6 for e in new_list))

		print("\nTop 20 Page Ranks with 10 iterations")
		for e in new_list:
			for i in range(element_in_tuple):	print(e[i].ljust(max_length_column[i]), end='')
			print()

		print("\nWrite pagerank output in %s" % self.top_20_file)
		self.write_pagerank_in_file(new_list)

	def write_pagerank_in_file(self, list_of_tuples):
		file = open(self.top_20_file,'w+')
		for tupla in list_of_tuples:	file.write(str(tupla) + '\n')
		file.close()


	def draw_graph(self, outlinks):
		to_write = ""
		for item in outlinks:
			if outlinks[item] ==  SortedSet([]):	pass
			else:
				for out in outlinks[item]:	to_write += item + ',' + out + '\n'

		temp_file = 'tmp.txt'
		file = open(temp_file, 'w')
		file.write(to_write)
		file.close()

		file = open(temp_file, 'r')
		import networkx as nx
		import matplotlib.pyplot as plt
		import operator
		from matplotlib import pylab

		G = nx.DiGraph()

		for line in file:
			l = line.split(",")
			influenced = l[0].split("\n")[0]
			cs_ist = l[1].split("\n")[0]
			G.add_edge(influenced, cs_ist)

		def save_graph(graph,file_name):
		 	plt.figure(num=None, figsize=(20, 20), dpi=80)
		 	plt.axis('off')
		 	fig = plt.figure(1)
		 	pos = nx.spring_layout(graph)
		 	nx.draw_networkx_nodes(graph,pos)
		 	nx.draw_networkx_edges(graph,pos)
		 	nx.draw_networkx_labels(graph,pos)
		 	cut = 0
		 	xmax = cut * max(xx for xx, yy in pos.values())
		 	ymax = cut * max(yy for xx, yy in pos.values())
		 	plt.xlim(0, xmax)
		 	plt.ylim(0, ymax)
		 	plt.savefig(file_name,bbox_inches="tight")
		 	pylab.close()
		 	del fig

		graph_name = self.file_folder_dir + "my_graph.pdf"
		save_graph(G,graph_name)
		os.remove(temp_file)

	
	def main(self):
		if not os.path.exists(self.folder_data_name):
			print("Downloading wikipedia CS Pages")
			os.chdir(self.file_folder_dir)
			response = requests.get(self.dropbox_data_tar, stream=True, headers=self.dropbox_headers)
			response_content = response.content
			self.write_tar_file(response_content)

		print('Before calling read_links')
		(inlinks, outlinks) = self.read_links(self.folder_data_name)
		print(outlinks)
		print('Read %d people with a total of %d inlinks' % (len(inlinks), sum(len(v) for v in inlinks.values())))
		print('Read %d people with a total of %d outlinks' % (len(outlinks), sum(len(v) for v in outlinks.values())))


		topn = self.get_top_pageranks(inlinks, outlinks, b=.8, n=20, iters=10)

		self.tabular_print_pagerank(topn)

		# print("I'm drawing directed graph")
		# self.draw_graph(outlinks)

		os.chdir(self.this_dir)




if __name__ == '__main__':
	Page_Rank_Obj = Page_Rank().main()