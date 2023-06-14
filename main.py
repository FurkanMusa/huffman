import sys

import numpy as np
from PIL import Image, ImageChops
from mpmath import mp

"""
# Huffman Coding
create a priority queue Q consisting of each unique character.
sort then in ascending order of their frequencies.
for all the unique characters:
    create a newNode
    extract minimum value from Q and assign it to leftChild of newNode
    extract minimum value from Q and assign it to rightChild of newNode
    calculate the sum of these two minimum values and assign it to the value of newNode
    insert this newNode into the tree
return rootNode
"""


def stash_to_pixel(img_width, img_height, stash):
    rgb_vector = stash % 3
    stash = (stash - rgb_vector) / 3
    width = stash % img_width
    stash = (stash - width) / img_width
    height = stash % img_height
    return int(width), int(height), int(rgb_vector)


def pixel_to_stash(img_width, img_height, height, width):
    stash = height * img_width + width
    return int(stash)


def compare_images(image_1_path, image_2_path):
    img1 = Image.open(image_1_path).convert('RGB')
    img2 = Image.open(image_2_path).convert('RGB')

    img_diff = ImageChops.difference(img1, img2)

    for x in range(img_diff.width):
        for y in range(img_diff.height):
            pixel = img_diff.getpixel((x, y))
            if pixel != (0, 0, 0):
                img_diff.putpixel((x, y), (0, 255, 0))

    path_to_save = image_1_path.split('.')[0] + "_diff." + image_1_path.split('.')[-1]
    img_diff.save(path_to_save)
    print("Difference image saved as \"" + path_to_save + "\"")

    # img_diff.show()

    return img_diff, path_to_save


# Creating tree nodes
class NodeTree(object):

    def __init__(self, left=None, right=None):
        self.left = left
        self.right = right

    def children(self):
        return self.left, self.right

    def nodes(self):
        return self.left, self.right

    def __str__(self):
        return '%s_%s' % (self.left, self.right)


# Main function implementing huffman coding
def huffman_code_tree(node, left=True, binString=''):
    if type(node) is int:
        return {node: binString}
    (l, r) = node.children()
    d = dict()
    d.update(huffman_code_tree(l, True, binString + '0'))
    d.update(huffman_code_tree(r, False, binString + '1'))
    return d


def encode(path_to_base_img):
    img = Image.open(path_to_base_img).convert('RGB')

    # Get the image szies
    width, height = img.size

    # Frequency of each character
    freq = {}
    for x in range(height):
        for y in range(width):
            pixel = img.getpixel((x, y))
            for rgb in range(3):
                if pixel[rgb] in freq:
                    freq[pixel[rgb]] += 1
                else:
                    freq[pixel[rgb]] = 1

    # Sort the frequency table
    freq = sorted(freq.items(), key=lambda x: x[1], reverse=True)
    nodes = freq

    # Huffman Tree
    while len(nodes) > 1:
        (key1, c1) = nodes[-1]
        (key2, c2) = nodes[-2]
        # print("key1, c1: " + str(key1) + ", " + str(c1) + "\n")
        # print("key2, c2: " + str(key2) + ", " + str(c2) + "\n")
        nodes = nodes[:-2]
        node = NodeTree(key1, key2)
        nodes.append((node, c1 + c2))
        nodes = sorted(nodes, key=lambda x: x[1], reverse=True)

    huffmanCode = huffman_code_tree(nodes[0][0])

    print('     Color |           | Huffman')
    print(' Intensity | Frequency | Code ')
    print('- - - - - -|- - - - - -|- - - - - - - -')
    min, max = 9999, 0
    for (stash, frequency) in freq:
        print(' %9r | %-9s | %s' % (stash, frequency, huffmanCode[stash]))
        if stash < min:
            min = stash
        if stash > max:
            max = stash

    print("\n Minimum and Maximum Color Intensities: (" + str(min) + ", " + str(max) + ")")


    # Encode the image
    encoded_str = ""
    for x in range(height):
        for y in range(width):
            pixel = img.getpixel((y, x))
            print("(" + str(x) + ", " + str(y) + ") : " + str(pixel))
            for rgb in range(3):
                encoded_str += huffmanCode[pixel[rgb]]

    print(" Number of bits in the encoded bit stream:", len(encoded_str))
    print(" Bit stream:", encoded_str)

    return encoded_str, huffmanCode


def get_key_from_value(dictionary, value):
    for key, val in dictionary.items():
        if val == value:
            return key
    return None  # Value not found in the dictionary


def decode(encoded_str, huffmanCode, width, height):

    # Create a new image with green screen
    image = Image.new("RGB", (width, height), "green")

    # Access the pixel data
    img_pixels = image.load()

    # Fill every pixel with a specific color
    for x in range(height):
        for y in range(width):
            # Set the color of each pixel (red, green, blue)
            img_pixels[y, x] = (x % 256, y % 256, (x + y) % 256)

    # Save the image
    image.save("generated_image.png")

    while encoded_str.__len__() != 0:
        flag = True
        key = ''
        while flag:
            key = key + encoded_str[0]
            encoded_str = encoded_str[1:]
            if key in huffmanCode.values():
                flag = False
                print("%10r : %r " % (key, get_key_from_value(huffmanCode, key)))



    # decoded_img = np.array(encoded_str).reshape(width, height)

    # return decoded_img
    return "decoded_img"








if __name__ == '__main__':

    if len(sys.argv) == 2:
        flag_diff = False
    elif (len(sys.argv) == 3) and sys.argv[2].__eq__("--diff"):
        flag_diff = True
    else:
        print("ERROR: Invalid arguments!")
        print("Usage: python main.py [image_path] --diff(optional)")
        print("Necessities:")
        print("       [image_path] : relevant path to image.")
        print("Optional Arguments:")
        print("       --diff : show the difference between the original image and the encoded image.")
        sys.exit(1)

    img_path = sys.argv[1]

    # Open image
    img = Image.open(img_path).convert('RGB')


    # Encode as huffman
    encoded_img, encoded_img_path = encode(img_path)

    img_decoded = decode(encoded_img, encoded_img_path, img.width, img.height)
    print("img_decoded" + img_decoded)


    if flag_diff:
        # Compare the original image with the encoded image
        diff_img, diff_img_path = compare_images(img_path, encoded_img_path)
