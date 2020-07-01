import os, re, requests, time, json
from urllib.request import urlretrieve
from bs4 import BeautifulSoup
import urllib.request
import urllib.parse

class RetrieveCS(object):
	def __init__(self):
		self.wiki_url = 'https://en.wikipedia.org/wiki/List_of_computer_scientists'
		self.wiki_base_url = 'https://en.wikipedia.org'
		self.folder_data_name = '../../files/data'

		self.json_name_link = '../../files/name_links.json'


	def myfilter(self, tag):
		""" 
			Find <a> tags like [ <li><a href='/wiki/' ]that are inside of A-Z headings.
		"""
		def tryparent(tag):
		 	try:
		 		return re.match('[A-Z]', tag.parent.parent.previous_sibling.previous_sibling.span.text)
		 	except:	False
		return tag and tag.name == 'a' and tag.parent.name == 'li' and tag.get('href').startswith('/wiki/') and not tag.previous_sibling and tryparent(tag)

	def get_links(self, soup):
		return [l.get('href') for l in soup.find_all(self.myfilter)]


	def write_json_file(self, lista):
		content = {"name_links":lista}
		file = open(self.json_name_link, 'w')
		json.dump(content, file, indent = 4)
		file.close()
	
	def main(self):
		soup = BeautifulSoup(requests.get(self.wiki_url).text, "html.parser")

		links = self.get_links(soup)

		print('found %d links' % len(links))
		if not os.path.exists(self.folder_data_name):
			os.makedirs(self.folder_data_name, exist_ok=True)
			lista = []
			for link in links:
				url = self.wiki_base_url + link
				print('fetching %s' % url)
				lista.append({link[6:]:url})
				urlretrieve(url, self.folder_data_name + '/' + link[6:])

				time.sleep(.6)
			self.write_json_file(lista)
		

		# comprimi i files html in data



if __name__ == '__main__':
	RetrieveCS_Obj = RetrieveCS()
	RetrieveCS_Obj.main()