import os
home='/home/'
names=''
cnt=''
if os.getcwd()=='/home/':
	user_names=[f for f in os.listdir('.') if os.path.isdir(f)]
	print 'Users ',user_names
	for o in user_names:
		names=[c for c in os.listdir(home+o+'/.')]
		if '.psql_history' not in names:
			cnt=cnt+o+','
	if cnt:
		print 'p is ',cnt
	a=os.popen("locate .psql_history").readlines()
	for i in a:
		i=i[:-1]
		f=open(i).readlines()
		for j in f:
			if 'update' in j.lower() and '12.36' in j.lower():
				print '\nCurrent File:',i
				print 'Name:',i.split('/')[-2]
				print 'Query:',j

	b=os.popen("locate .bash_history").readlines()
	for k in b:
		k=k[:-1]
		l=open(k).readlines()
		for m in l:
			if ('vim' in m.lower() and '.psql_history' in m.lower()) or ('rm' in m.lower() and '.psql_history' in m.lower()) or ('>' in m.lower() and '.psql_history' in m.lower()):
				print '\nCurrent File:',k
				print 'Name:',k.split('/')[-2]
				print 'Command:',m
