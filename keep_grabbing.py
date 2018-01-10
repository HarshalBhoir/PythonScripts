import os
from subprocess import Popen
locate=os.popen("ls /home/nevpro/Desktop | grep '/\|pdf$'")
lines=locate.readlines()
print lines
dest='/home/nevpro/pdf/.'
for i in lines:
    print i.rstrip('\n')
    p = Popen(['scp','-p','--preserve','/home/nevpro/Desktop'+str(i.rstrip('\n')),dest])
    #p = Popen(['rsync',str(i.rstrip('\n')),dest])
    p.wait()
