with open('dblp/dblp.xml') as content_file:
    content = content_file.read()

count = 0
with open('dblp/htmllatin1.txt') as key_file:
    for line in key_file:
        count = count + 1
        trans_from = line.split()[0]
        trans_to = line.split()[1]
        print(count, trans_from, trans_to)
        content = content.replace(trans_from, trans_to)


with open('dblp/utf8.xml', 'w') as out_file:
    out_file.write(content)
