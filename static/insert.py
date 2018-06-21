file_9 = open("9.tbl","r")
file_10 = open("10.tbl","r")
query = "insert into difficulty(unique_id, difficulty, difficulty_y, difficulty_x) values(%s, %d, %s, %s);"
for data in file_9.readlines():
    data = data.replace('\n','').split('\t')
    if len(data) == 3:
        unique_id = data[0]
        diff_y = data[1]
        diff_x = data[2]
        print query % (unique_id,9, diff_y, diff_x)

for data in file_10.readlines():
    data = data.replace('\n','').split('\t')
    if len(data) == 3:
        unique_id = data[0]
        diff_y = data[1]
        diff_x = data[2]
        print query % (unique_id,10, diff_y, diff_x)

