import csv

list1 = [1,2,3,4,5,6]
list2 = ["red", "orange", "yellow", "green", "blue", "purple"]
list3 = ['a', 'b', 'c', 'd', 'e', 'f']

with open('test.csv','w', newline='') as file:
    writer = csv.writer(file)
    for i in range(len(list1)):
        writer.writerow([str(list1[i])] + [list2[i]] + [list3[i]])