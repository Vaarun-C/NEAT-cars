#Library Imports
import math
import time

#matrix creation
matrix = [	[0, 0, 0, 0, 0, 0, 0, 0, 0],
			[0, 1, 1, 1, 1, 1, 1, 1, 0],
			[0, 1, 1, 1, 1, 1, 1, 1, 0],
			[0, 1, 1, 1, 1, 1, 1, 1, 0],
			[0, 1, 1, 1, 0, 1, 1, 1, 0],
			[0, 1, 1, 1, 1, 1, 1, 1, 0],
			[0, 1, 1, 1, 1, 1, 1, 1, 0],
			[0, 1, 1, 1, 1, 1, 1, 1, 0],
			[0, 0, 0, 0, 0, 0, 0, 0, 0]
		]
size = len(matrix)


for r in matrix:
	print(r)

#neighbours
def neighbours(x,y,image):
	img = image
	x_1, y_1, x1, y1 = x-1, y-1, x+1, y+1
	return [ img[x_1][y], img[x_1][y1], img[x][y1], img[x1][y1], img[x1][y], img[x1][y_1], img[x][y_1], img[x_1][y_1] ]

#transitions
def transitions(neighbours):
	n = neighbours + neighbours[0:1]
	return sum( (n1, n2) == (0, 1) for n1, n2 in zip(n, n[1:]) )

#zhang suen
def zhangSuen(image):
	changing1 = changing2 = 1
	while changing1 or changing2:

		changing1 = []
		rows, columns = len(matrix), len(matrix[0])
		for x in range(1, rows - 1):
			for y in range(1, columns - 1):

				P2,P3,P4,P5,P6,P7,P8,P9 = n = neighbours(x, y, matrix)
				if ((matrix[x][y] == 1) and (2 <= sum(n) <= 6) and (transitions(n) == 1) and (P2 * P4 * P6 == 0) and (P4 * P6 * P8 == 0)):         # Condition 4
					
					changing1.append((x,y))
		for x, y in changing1: 
			matrix[x][y] = 0

		changing2 = []
		for x in range(1, rows - 1):
			for y in range(1, columns - 1):
				P2,P3,P4,P5,P6,P7,P8,P9 = n = neighbours(x, y, matrix)
				if ((matrix[x][y] == 1) and (2 <= sum(n) <= 6) and (transitions(n) == 1) and (P2 * P4 * P8 == 0) and (P2 * P6 * P8 == 0)):            # Condition 4
					changing2.append((x,y))    
		
		for x, y in changing2: 
			matrix[x][y] = 0

#zhang suen
zhangSuen(matrix)
print("*"*100)
for r in matrix:
	print(r)
