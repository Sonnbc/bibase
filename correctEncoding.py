contentFile = open('dblp/dblp.xml')
keyFile = open('dblp/htmllatin1.txt')
out = open('dblp/utf8.xml', 'w')

content = contentFile.read()
count = 0

for line in keyFile:
	count = count + 1
	transFrom = line.split()[0]
	transTo = line.split()[1]
	print(count, transFrom, transTo)
	content = content.replace(transFrom, transTo)


out.write(content)
