import requests, re, os
import urllib.request
import urllib.parse


class Check_Influences(object):
	def __init__(self):
		self.folder_data_name = '../../files/data'

	def get_all_files(self):
		return os.listdir(self.folder_data_name)



	def main(self):
		all_files = self.get_all_files()
		influenze_l = []
		influenzati_l = []
		for file in all_files:
			file_name = self.folder_data_name + '/' + file
			file = open(file_name)
			file_content = file.read()
			file.close()
			paragraphs = re.findall(r'<table(.*?)</table>', str(file_content))
			for eachP in paragraphs:
				if "Influences" or "Influenced" in eachP:
					r = re.findall(r'Influences(.*?)Influenced', str(eachP))
					for e in r:
						influenze = re.findall(r'title="(.*?)"', str(e))
						influenze_l.append(influenze)

					p = re.findall(r'Influenced(.*?)colspan="2"', str(eachP))
					for el in p:
						influenzati = re.findall(r'title="(.*?)"', str(el))
						influenze_l.append(influenzati)

		print(influenzati)
		print()
		print(influenze_l)



if __name__ == '__main__':
	Check_Influences_Obj = Check_Influences()
	Check_Influences_Obj.main()