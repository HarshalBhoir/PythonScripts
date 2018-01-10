import sys,os
import fnmatch

print "Addons dir",sys.argv[1]
print '''Please select operation to perform
1.Update
2.Insert'''

update_log_file='/update.log'
insert_log_file='/insert.log'
file_log='/filenames.log'

exluded_filenames=['old_files','offline_sync.py','account_31jan','ir','bkp','backup','old','bckup','scheduling_jobs.py','write_job.py','stock.py']
exclude_lines=['main_query_inspection','main_query_services','write_date','write_uid','create_date','create_uid','select * from phone_m2m_create','get_accounting_val','ir_']
with open("."+file_log,'a') as file_names:
	file_names.write("################################### Updated File Names ###################################\n")


op=raw_input()
if op=='1':
	path=sys.argv[1]
	with open("."+update_log_file,'a') as lg:
		for root, dirnames, filenames in os.walk(path):
			for j in fnmatch.filter(filenames,'*.py'):
				file_edited=False
				if not any(a in root+j for a in exluded_filenames) and not any(char.isdigit() for char in root+j):
					with open(root+"/"+j,'r') as file:
						f= file.readlines()
						for line,k in enumerate(f):
							if "update " in f[line].lower() and "set" in f[line].lower() and f[line].lower().find("update")<f[line].lower().find("set") and not any(a in f[line].lower() for a in exclude_lines):
								lg.write("Current File: "+root+"/"+j+" :"+str(line))
								lg.write("\n")
								lg.write("BEFORE UPDATE: "+f[line].lstrip())
								index_of=f[line].lower().find('set ')
								if "cr.execute" in f[line].lower():
									cur_line=f[line].lower()
									temp_str=cur_line[cur_line.find('cr.execute'):cur_line.find('update')]
									start_char=temp_str[temp_str.find('(')+1:len(temp_str)].strip()

									if start_char.lstrip('(') =="'":
										updated_line=f[line][:index_of+4]+r" write_date=(now() at time zone \'UTC\'),write_uid=1,"+f[line][index_of+4:]
									else:
										updated_line=f[line][:index_of+4]+" write_date=(now() at time zone 'UTC'),write_uid=1,"+f[line][index_of+4:]
								else:
									updated_line=f[line][:index_of+4]+" write_date=(now() at time zone 'UTC'),write_uid=1,"+f[line][index_of+4:]
								f[line]=updated_line
								lg.write("AFTER UPDATE : "+updated_line.lstrip())
								lg.write("\n")
								file_edited=True
					if file_edited:
						with open("."+file_log,'r') as file_names_read:
							file_names_read_list=file_names_read.readlines()
							if root+"/"+j not in file_names_read_list:
								with open("."+file_log,'a') as file_names:
									file_names.write(root+"/"+j+"\n")
						with open(root+"/"+j, 'w') as file1:
							file1.writelines(f)

elif op=='2':
	print 'insert'
	path=sys.argv[1]
	with open("."+insert_log_file,'a') as lg:
		for root, dirnames, filenames in os.walk(path):
			for j in fnmatch.filter(filenames,'*.py'):
				file_edited=False
				if not any(a in root+j for a in exluded_filenames) and not any(char.isdigit() for char in root+j):
					with open(root+"/"+j,'r') as file:
						f= file.readlines()
						for line,k in enumerate(f):
							if "insert" in f[line].lower() and "values" in f[line].lower() and f[line].lower().find("insert")<f[line].lower().find("values") and not any(a in f[line].lower() for a in exclude_lines):
								lg.write("Current File: "+root+"/"+j+" :"+str(line))
								lg.write("\n")
								lg.write("BEFORE UPDATE: "+f[line].lstrip())
								lg.write("\n")
								index_of=f[line].lower().find('(',f[line].lower().find('insert'))
								updated_line=f[line][:index_of+1]+"create_date,create_uid,"+f[line][index_of+1:]
								f[line]=updated_line
								index_of_values=f[line].lower().find('(',f[line].lower().find('values'))
								if 'cr.execute' in f[line].lower():
									updated_line_values=f[line][:index_of_values+1]+"(now() at time zone 'UTC'),uid,"+f[line][index_of_values+1:]
								else:
									updated_line_values=f[line][:index_of_values+1]+"(now() at time zone 'UTC'),1,"+f[line][index_of_values+1:]
								lg.write("AFTER UPDATE : "+updated_line_values.lstrip())
								lg.write("\n")
								f[line]=updated_line_values
								file_edited=True
					if file_edited:
						with open("."+file_log,'r') as file_names_read:
							file_names_read_list=file_names_read.readlines()
							if root+"/"+j not in file_names_read_list:
								with open("."+file_log,'a') as file_names:
									file_names.write(root+"/"+j+"\n")
						with open(root+"/"+j, 'w') as file1:
							file1.writelines(f)
					
else:
	print 'invalid input'


lg.close()
file.close()
file_names_read.close()
file_names.close()
file1.close()
