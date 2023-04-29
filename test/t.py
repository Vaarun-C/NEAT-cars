import cv2

def thinning(image):
    height, width = image.shape

    # Create a binary output image
    output = [[0 for x in range(width)] for y in range(height)]

    # Define a structuring element
    structuring_element = [
        [1, 1, 1],
        [1, 1, 1],
        [1, 1, 1]
    ]

    # Create a flag for stopping the iteration
    has_changed = True

    while has_changed:
        has_changed = False

        # Iterate over each pixel in the input image
        for y in range(1, height - 1):
            for x in range(1, width - 1):
                # Check if the pixel is black
                if image[y][x] == 0:
                    continue

                # Apply the structuring element
                neighbors = [
                    [image[y - 1][x - 1], image[y - 1][x], image[y - 1][x + 1]],
                    [image[y][x - 1], image[y][x], image[y][x + 1]],
                    [image[y + 1][x - 1], image[y + 1][x], image[y + 1][x + 1]]
                ]

                sum_neighbors = sum([sum(row) for row in neighbors])
                num_transitions = 0

                for j in range(3):
                    for i in range(3):
                        if i == j:
                            continue
                        if neighbors[j][i] == 0 and neighbors[j][i + 1] == 1:
                            num_transitions += 1

                if num_transitions == 1 and sum_neighbors >= 2 and sum_neighbors <= 6:
                    output[y][x] = 1
                    has_changed = True
                else:
                    output[y][x] = 0

        image = output

    return output


# Load the binary image
img = cv2.imread('1.png', cv2.IMREAD_GRAYSCALE)

# Apply thresholding to convert the image to binary
_, img = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY)

# Apply thinning algorithm
thinning = cv2.ximgproc.thinning(img, None, cv2.ximgproc.THINNING_ZHANGSUEN)

# Save the thinned image
cv2.imwrite('thinned_image.png', thinning)
