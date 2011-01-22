yes <- read.table('yes.dat')
no <- read.table('no.dat')
t.test(yes, no)
