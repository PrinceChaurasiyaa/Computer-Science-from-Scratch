from PIL import Image
from array import array
from typing import NamedTuple

THRESHOLD = 127

"""NamedTuple = A tuple with named fields that is convenient for storing structured data."""

class Pattern(NamedTuple):
    deltaColumn: int
    deltaRow: int
    numerator: int
    denominator: int


BILL_ATKINSON = [Pattern(1, 0, 1, 8), Pattern(2, 0, 1, 8),
                 Pattern(-1, 1, 1, 8), Pattern(0, 1, 1, 8), Pattern(1, 1, 1, 8),
                 Pattern(0, 2, 1, 8)]

FLOYD_STEINBERG = [Pattern(1, 0, 7, 16),
                   Pattern(-1, 1, 3, 16), Pattern(0, 1, 5, 16), Pattern(1, 1, 1, 16)]

# Assumes we are working with a grayscale image (Mode "L" in Pillow)
# Returns an array of dithered pixels (255 for white, 0 for black)


def ditherAlgo(image: Image.Image) -> array:

    def errorDiffusion(c: int, r: int, error: int, pattern: list[Pattern]):
        for part in pattern:
            col = c + part.deltaColumn
            row = r + part.deltaRow
            if col < 0 or col >= image.width or row >= image.height:
                continue
            currentPixel: float = image.getpixel((col, row))
            errorPart = (error * part.numerator) // part.denominator
            image.putpixel((col, row), currentPixel + errorPart)

    """
    [0] * (image.width * image.height): Creates a flat list of zeros. The total number of zeros matches the total number of pixels in the image (Width × Height).
    array('B', ...): Converts that list into a memory-efficient sys array object from Python's built-in array module. 
    The 'B' type code specifies unsigned chars (bytes), meaning each element is an integer restricted to a value between 0 and 255.
    """
    result = array('B', [0] * (image.width * image.height))

    """ =========== in Pillow: image.getpixel((x, y)) ========  """
    """ =========== x -> Column (horizontal position) & y -> Row (vertical position) ==============="""

    for y in range(image.height):
        for x in range(image.width):
            oldPixel: float = image.getpixel((x, y))

            """ ======== Quantization Threshold ====== """

            newPixel = 255 if oldPixel > THRESHOLD else 0
            result[y * image.width + x] = newPixel

            """ ========== Error ==========="""

            error = int(oldPixel - newPixel)

            """ ============ Error Diffusion =========="""
            
            errorDiffusion(x, y, error, BILL_ATKINSON)

    return result