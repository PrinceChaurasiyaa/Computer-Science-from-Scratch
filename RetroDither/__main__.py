"""
What do you do when you need to show an image on a display with fewer colors than 
are in the image itself? 

Solving that problem is the realm of dithering algorithms, which 
strategically use a limited color palette to create the illusion of more colors.

Dithering algorithms purposely introduce noise into an image in a specific 
way that makes the image appear to have more color depth than it actually 
does.

Application:

If you’ve ever seen full-motion graphics on an early 1990s game con
sole or computer, then you probably have a sense of what dithering looks 
like. The technique is also prevalent in animated GIFs, since GIFs can only 
support 256 colors. (There’s a hacky way to get more than 256 colors in a 
GIF, but most export programs don’t support it.)

Another common use of dithering and techniques like it is to make a 
black-and-white image appear to be grayscale.

Most Amazon Kindle devices sup
port 16 levels of grayscale, so many book covers and photographs displayed on 
the Kindle must be approximated via dithering (albeit not 1-bit dithering).


The pipeline our project will follow is pretty straightforward:

1. Read an image from disk.

2. Resize it and convert it to grayscale.  

3. Dither it to black and white.

4. Write it to disk in MacPaint format.

"""

"""----------------Pillow-------------------"""

"""Pillow can read an image in any popular format in a single line of code, 
and it’s just a few more lines to resize an image and convert it to grayscale. """

from PIL import Image
from argparse import ArgumentParser