# from __future__ import print_function
import os,sys

print 'AAAAAAAAAAAAAAAAA',sys.argv
for dirname,dirnames,filenames in os.walk(sys.argv[1]):
    print(dirname)
    for subdirname in dirnames:
        print(os.path.join(dirname, subdirname))

    for filename in filenames:
        print(os.path.join(dirname, filename))
        
for dirname,dirnames,filenames in os.walk(sys.argv[2]):
    for subdirname in dirnames:
        print(os.path.join(dirname, subdirname))

    for filename in filenames:
        print(os.path.join(dirname, filename))
        
        
with open('invoice_adhoc.py') as f1, open('invoice_adhoc_1.py') as f2, open('outfile.txt', 'w') as outfile:
    for line1, line2 in zip(f1, f2):
        if line1 != line2:
	    line1=line1.rstrip('\n')
        outfile.write('File path '+f1.name+': Diff line '+line1)
