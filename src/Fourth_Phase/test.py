fields_list = ['Computer Science and Engineering', 'Pattern Recognition', 'Machine Learning', 'Computer Science', 'Engineering\nPattern Recognition\nMachine Learning']

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
		if '\n' in item:	pass
		else:
			to_ret.append(item)


print(to_ret)