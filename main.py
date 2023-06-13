import sys
from PIL import Image, ImageChops
from mpmath import mp
 

if __name__ == '__main__':

    if len(sys.argv) == 3:
        flag_opt = False
    elif (len(sys.argv) == 4) and sys.argv[3].__eq__("--diff"):
        flag_opt = True
    else:
        print("ERROR: Invalid arguments!")
        print("Usage: python main.py <x> <y> --z(optional)")
        print("Necessities:")
        print("       <x> : info.")
        print("       <y> : info.")
        print("Optional Arguments:")
        print("       --z : info.")
        sys.exit(1)

    img_path = sys.argv[1]
    secretMessage = sys.argv[2]

    # Open the image with RGB mode
    img = Image.open(img_path).convert('RGB')



    # Compare the images
    if flag_opt:
        print("optional parameter selected")
