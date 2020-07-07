import requests, re, json, os, string, urllib.parse, operator
from bs4 import BeautifulSoup

import networkx as nx
import matplotlib.pyplot as plt


class Categorization(object):
	def __init__(self):
		self.files_dir = '../../files/'
		self.folder_data_name = self.files_dir + 'data'
		self.good_cs_filename = self.files_dir + 'good_name_links.json'

		self.categorization_json = self.files_dir + 'categorization.json'
		self.beautified_categories_json = self.files_dir + 'beautified_categorization.json'

		self.tmp_hits_file = 'tmp_hits.txt'

		self.category_hits = self.files_dir + 'hits_top_20_categories.txt'
		self.category_pagerank = self.files_dir + 'pagerank_top_20_categories.txt'

	def write_txt_file(self, file_name, content):
		file = open(file_name, 'w')
		file.write(content)
		file.close()

	def get_json_content(self, file_name):
		file = open(file_name)
		content = json.load(file)
		file.close()
		return content

	def get_all_cs_files(self):
		to_ret = []
		# for item in self.get_json_content(self.good_cs_filename)['name_links']:
		# 	to_ret.append(self.folder_data_name + '/' + list(item.keys())[0])
		# return to_ret
		for item in os.listdir(self.folder_data_name):
			to_ret.append(self.folder_data_name + '/' + item)
		return to_ret

	def get_html_content(self, file_name):
		file = open(file_name)
		content = file.read()
		file.close()
		return content

	def get_cs_name_from_filename(self, file_name):	return file_name.split('/')[-1]
	
	def clean_list(self, a_list):
		pass
	

	def get_fields(self, file_name):
		soup = BeautifulSoup(self.get_html_content(file_name), 'html.parser')
		infobox = soup.find('table', {'class':'infobox'})
		fields_list = []
		if infobox != None:
			for item in infobox.findAll('tr'):
				infobox_key = item.find('th')
				if infobox_key != None and infobox_key.get_text() == 'Fields':
					infobox_value = item.find('td')
					fields_list.append(infobox_value.get_text())
		this_name = self.get_cs_name_from_filename(file_name)
		return fields_list
		
	def clean_fields(self, fields_list):
		new_fields = []
		for item in fields_list:
			if '\n' in item:	new_fields = item.split('\n')
		new_fields = [x for x in new_fields if x]

		for item in fields_list:
			if ' and ' in item:
				new_fields.append(item.split(' and ')[0])
				new_fields.append(item.split(' and ')[1])

		to_ret = []
		for item in new_fields:
			if '[' in item:	to_ret.append(item.split('[')[0])
			else:
				if '\n' in item:
					if '\n\n\n' in item:
						to_ret.append(item.replace('\n\n\n', ''))
				else:	to_ret.append(item)

		new_to_ret = []
		for item in to_ret:
			if '\n' in item:
				new_to_ret = item.split('\n')
		to_ret = to_ret + new_to_ret
		return list(set(to_ret))

	def compute_categorization(self, all_cs_files_list):
		to_ret = []
		none = 0
		for file_name in all_cs_files_list:
			cs_name = self.get_cs_name_from_filename(file_name)
			his_fields = self.clean_fields(self.get_fields(file_name))

			new_fields = []
			for item in his_fields:	new_fields.append(item.capitalize())
			if new_fields != []:
				cs_name = urllib.parse.unquote(cs_name)	# from 'Philipp_Matth%C3%A4us_Hahn' ---> 'Philipp_Matthäus_Hahn'
				to_ret.append({cs_name:new_fields})
			else:
				none += 1
		return to_ret

	def write_categorization_json(self, categorization_list, file_name):
		to_write = {"categorized_cs": categorization_list}
		file = open(file_name, 'w')
		json.dump(to_write, file, indent = 4)
		file.close()


	def get_all_cs_categories(self):
		file_content = self.get_json_content(self.categorization_json)
		to_ret = []
		for item in file_content['categorized_cs']:
			for i in list(item.values()):
				for category in i:
					to_ret.append(category.capitalize())
		return list(set(to_ret))


	def make_tmp_txt_file(self):
		file_content = self.get_json_content(self.categorization_json)
		to_write = ''
		for item in file_content['categorized_cs']:
			for name in item:
				for category in item[name]:
					to_write = to_write + name + ',' + category + '\n'
		self.write_txt_file(self.tmp_hits_file, to_write)

	def compute_hits(self):
		G = nx.DiGraph()
		file = open(self.tmp_hits_file, 'r')
		for line in file:
			l = line.split(",")
			influenced = l[0].split("\n")[0]
			category = l[1].split("\n")[0]
			G.add_edge(influenced, category)

		pr = nx.hits(G)
		p1 = pr[0]
		sorted_p1 = sorted(p1.items(), key=operator.itemgetter(1))
		sorted_p1.reverse()

		p2 = pr[1]
		sorted_p2 = sorted(p2.items(), key=operator.itemgetter(1))
		sorted_p2.reverse()

		counter = 0
		to_write = ''
		for i in sorted_p2:
			#print(i)
			to_write = to_write + str(i) + '\n'
			if counter == 20:	break
			counter += 1

		self.write_txt_file(self.category_hits, to_write)

	def compute_pagerank(self):
		G = nx.DiGraph()
		file = open(self.tmp_hits_file, 'r')
		for line in file:
			l = line.split(",")
			influenced = l[0].split("\n")[0]
			category = l[1].split("\n")[0]
			G.add_edge(influenced, category)

		pr = nx.pagerank(G, alpha=0.85)
		sorted_pr = sorted(pr.items(), key=operator.itemgetter(1))
		sorted_pr.reverse()

		counter = 0
		to_write = ''
		for i in sorted_pr:
			#print(i)
			to_write = to_write + str(i) + '\n'
			if counter == 20:	break
			counter += 1
		self.write_txt_file(self.category_pagerank, to_write)

	
	def main(self):
		all_cs_files_list = self.get_all_cs_files()
		if not os.path.exists(self.categorization_json):
			categorization_list = self.compute_categorization(all_cs_files_list)
			self.write_categorization_json(categorization_list, self.categorization_json)
		else:
			categories = self.get_all_cs_categories()

			self.make_tmp_txt_file()
			self.compute_hits()
			self.compute_pagerank()
			os.remove(self.tmp_hits_file)



if __name__ == '__main__':
	Categorization_Obj = Categorization().main()