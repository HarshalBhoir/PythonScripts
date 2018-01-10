import os
from subprocess import Popen
locate=os.popen("locate  /home/nevpro/Desktop/*.pdf")
lines=locate.readlines()

dest='/home/nevpro/pdf/.'
for i in lines:
    #print i.rstrip('\n')
    p = Popen(['scp','-p','--preserve','/'+str(i.rstrip('\n')),dest])
    #p = Popen(['rsync',str(i.rstrip('\n')),dest])
    p.wait()
