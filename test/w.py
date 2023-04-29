import math

# Open the image file
with open('1.png', 'rb') as f:
    data = f.read()

# Extract image dimensions
width = int.from_bytes(data[16:20], byteorder='big')
height = int.from_bytes(data[20:24], byteorder='big')

# Convert image data to binary list
image_binary = []
for y in range(height):
    row = []
    for x in range(width):
        pixel = data[24 + y*width + x]
        row.append(1 if pixel != 0 else 0)
    image_binary.append(row)

# Initialize distance matrix with large values
distance = [[0 for x in range(width)] for y in range(height)]

# Compute distance for each row
for y in range(height):
    d = 0
    for x in range(width):
        if image_binary[y][x] == 0:
            d = 0
        else:
            d += 1
        distance[y][x] = math.sqrt(d**2 + min(distance[max(y-1, 0)][x], distance[max(y-1, 0)][max(x-1, 0)], distance[y][max(x-1, 0)]))

# Compute distance for each column
for y in range(height):
    for x in range(width-2, -1, -1):
        distance[y][x] = min(distance[y][x], math.sqrt(1 + min(distance[y][x+1], distance[max(y-1, 0)][x+1], distance[max(y-1, 0)][max(x, 1)])))

    for x in range(width-1):
        distance[y][x] = min(distance[y][x], math.sqrt(1 + min(distance[y][x+1], distance[min(y+1, height-1)][x+1], distance[min(y+1, height-1)][max(x, 1)])))

# Save distance map to file
with open('distance_map.txt', 'w') as f:
    for row in distance:
        f.write(' '.join([str(d) for d in row]))
        f.write('\n')
