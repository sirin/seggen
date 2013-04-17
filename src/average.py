import sys
res = []
for i in xrange(10):
    ins = open( "/Users/sirinsaygili/workspace/seggen/terminal/results/mut_cross_T30_"+str(i)+".txt", "r" )
    lines = []
    for line in ins:
        a = line.split("], ")
        b = a[1].split("]")
        if int(b[0]) < 100:
            lines.append(int(b[0]))
    res.append(sum(lines)/len(lines))
print res