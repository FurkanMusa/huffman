import sys
from PIL import Image, ImageChops

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


def count_different_pixels(image_1_path, image_2_path):
    img1 = Image.open(image_1_path).convert('RGB')
    img2 = Image.open(image_2_path).convert('RGB')

    img_diff = ImageChops.difference(img1, img2)

    counter = 0
    for x in range(img_diff.width):
        for y in range(img_diff.height):
            pixel = img_diff.getpixel((x, y))
            if pixel != (0, 0, 0):
                counter += 1

    return counter


def get_key_from_value(dictionary, value):
    for key, val in dictionary.items():
        if val == value:
            return key
    return None  # Value not found in the dictionary


def encode(path_to_base_img):
    img = Image.open(path_to_base_img).convert('RGB')

    # Get the image szies
    width, height = img.size

    # Frequency of each character
    freq = {}
    for x in range(height):
        for y in range(width):
            pixel = img.getpixel((y, x))
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
        nodes = nodes[:-2]
        node = NodeTree(key1, key2)
        nodes.append((node, c1 + c2))
        nodes = sorted(nodes, key=lambda x: x[1], reverse=True)

    huffmanCode = huffman_code_tree(nodes[0][0])

    print('     Color |           | Huffman ')
    print(' Intensity | Frequency | Code    ')
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
            # print("(" + str(x) + ", " + str(y) + ") : " + str(pixel))
            for rgb in range(3):
                encoded_str += huffmanCode[pixel[rgb]]

    print(" Number of bits in the encoded bit stream:", len(encoded_str))
    # print(" Bit stream:", encoded_str)

    return encoded_str, huffmanCode


def decode(encoded_str, huffmanCode, width, height):

    # Reverse the dictionary
    huffmanCode = {v: k for k, v in huffmanCode.items()}

    # Decode the image
    stash_of_stashes = []
    starting_index = 0
    while starting_index < encoded_str.__len__():
        flag = True
        key = ''
        index = 0
        while flag:
            key = key + encoded_str[starting_index + index]
            index += 1
            if key in huffmanCode:
                starting_index += index
                flag = False
                stash_of_stashes.append(huffmanCode[key])
                # print("%10s : %r " % (key, huffmanCode[key]))

    # print("Length of stash_of_stashes: " + str(stash_of_stashes.__len__()))
    # print("stash_of_stashes: " + str(stash_of_stashes))

    # generate image from stash of stashes
    # Create a new image with green screen
    image = Image.new("RGB", (width, height), "green")

    # Access the pixel data
    img_pixels = image.load()

    for x in range(height):
        for y in range(width):
            stash_start = 3 * (x * width + y)
            img_pixels[y, x] = (
                stash_of_stashes[stash_start], stash_of_stashes[stash_start + 1], stash_of_stashes[stash_start + 2])

    return image


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


if __name__ == '__main__':

    if len(sys.argv) == 2:
        img_path = sys.argv[1]
    else:
        print("ERROR: Invalid arguments!")
        print("Usage: python main.py [image_path] --diff(optional)")
        print("Necessities:")
        print("       [image_path] : relevant path to image.")
        sys.exit(1)

    # Open image
    img = Image.open(img_path).convert('RGB')

    # Get the image sizes
    width, height = img.size
    print(' Image size: %3s x %-3s \n' % (str(width), str(height)))

    # Encode as huffman
    encoded_img, encoded_img_path = encode(img_path)

    # Decode the encoded image
    img_decoded = decode(encoded_img, encoded_img_path, img.width, img.height)

    # Save the decoded image
    path_to_save = img_path.split('.')[0] + "_regenerated." + img_path.split('.')[-1]
    img_decoded.save(path_to_save)
    print("\n Regenerated image saved as \"" + path_to_save + "\"")

    # Compare the original image with the decoded image
    print("\nAnalysis of Huffman Encoding:")
    print("     Number of bits in the encoded bit stream: ", len(encoded_img))
    print("     Number of bits in the original bit stream:", width * height * 3 * 8)
    print("     Compression ratio:", (width * height * 3 * 8) / len(encoded_img))
    print("     Different pixels: ", count_different_pixels(img_path, path_to_save))
