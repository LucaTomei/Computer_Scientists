import requests, re, os, json
import urllib.request
import urllib.parse
from bs4 import BeautifulSoup

import pprint
def bio_table(page):
    # open url with bs
    file = open(page)
    page = file.read()
    file.close()
    soup = BeautifulSoup(page, "html.parser")
    # get biography table
    table = soup.find('table', class_='infobox biography vcard')
    #print(len(table.find_all('ul', class_='NavContent')))
    try:
        # get influencers unordered list
        influencers = table.find_all('ul', class_='NavContent')[0]
    except:
        influencers = []
    try:
        # get influenced unordered list
        influenced = table.find_all('ul', class_='NavContent')[1]
    except:
        influenced = []
    #print(influenced)
    final_influencers = []
    final_influenced = []
    # We want a list of titles of wikipedia pages
    if influencers != []:
        for a in influencers.find_all('a'):
            try:
                # extract the title
                final_influencers.append(a.get('title'))
            except:
                pass
    # We want a list of titles of wikipedia pages
    if influenced != []:
        for a in influenced.find_all('a'):
            try:
                # extract the title
                final_influenced.append(a.get('title'))
            except:
                pass

    return final_influencers,final_influenced

class Check_Influences(object):
	def __init__(self):
		self.folder_data_name = '../../files/data'
		self.json_name_link = '../../files/name_links.json'
		self.good_json_file_name = '../../files/good_name_links.json'
		self.wiki_base_url = 'https://en.wikipedia.org'

	def get_all_files(self):
		return os.listdir(self.folder_data_name)

	def get_content_of_file(self):
		file = open(self.good_json_file_name)
		content = json.load(file)
		file.close()
		return content

	def has_infobox_table(self, file_name):
		file = open(file_name)
		file_content = file.read()
		file.close()
		if len(re.findall(r'infobox biography vcard', file_content)) != 0:	return True
		return False

	def write_json_file(self, lista):
		content = {"name_links":lista}
		file = open(self.good_json_file_name, 'w')
		json.dump(content, file, indent = 4)
		file.close()

	def get_good_cs(self):
		all_files = self.get_all_files()
		good_cs = []
		for file_name in all_files:
			file_name = self.folder_data_name + '/' + file_name
			if self.has_infobox_table(file_name):	good_cs.append(file_name)
		return good_cs

	def make_good_cs(self, good_cs):
		to_write = []
		for item in good_cs:
			item_name = item.rsplit('/', 1)[-1]
			item_link = self.wiki_base_url + '/' + item_name
			to_write.append({item_name:item_link})
		self.write_json_file(to_write)


	def get_good_cs_files(self):
		json_content = self.get_content_of_file()
		name_file_list = []
		for item in json_content['name_links']:
			name = list(item.keys())[0]
			name_file_list.append(self.folder_data_name + '/' + name)
		return name_file_list

	def check_influences(self, good_cs_filenames):
		count = 0
		
		for file_name in good_cs_filenames:
			print(file_name)
			#req = urllib.request.Request(, data)
			file = open(file_name)
			respData = file.read()
			file.close()
			paragraphs = re.findall(r'<table class="infobox(.*?)</table>', str(respData))

			for eachP in paragraphs:
				if "Influences" or "Influenced" in eachP:
					r = re.findall(r'Influence(.*?)Influenced', str(eachP))
					for e in r:
						influenze = re.findall(r'title="(.*?)"', str(e))
						for i in influenze:
							print(file_name + "," + i)

					p = re.findall(r'Influenced(.*?)colspan="2"', str(eachP))
					for el in p:
						influenzati = re.findall(r'title="(.*?)"', str(el))
						for inf in influenzati:
							print(inf + "," + file_name)
		print(count)

	def main(self):
		all_files = self.get_all_files()
		good_cs = self.get_good_cs()

		print("Good Computer Scientists: %d" % len(good_cs))
		self.make_good_cs(good_cs)
		good_cs_filenames = self.get_good_cs_files()
		
		self.check_influences(good_cs_filenames)
		# for i in good_cs_filenames:
		# 	print(bio_table(i))
		




if __name__ == '__main__':
	Check_Influences_Obj = Check_Influences()
	Check_Influences_Obj.main()