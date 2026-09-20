from array import array
from pathlib import Path
from datetime import datetime

MAX_WIDTH = 576
MAX_HIEGHT = 720
MACBINARY_LENGTH = 128
HEADER_LENGTH = 512

# Convert an array of bytes where each byte is 0 or 255
# to an array of bits where each byte that is 0 becomes a 1
# and each byte that is 255 becomes a 0

def byter_to_bits(original: array) -> array:
    bitsArray = array('B')

    for byteIndex in range(0, len(original), 8):
        nextByte = 0
        for bitIndex in range(8):
            index = byteIndex + bitIndex
            bit = original[index] & 1
            invertBit = 1 - bit
            shiftBit = invertBit << (7 - bitIndex)
            nextByte = nextByte | shiftBit

            if (index + 1) >= len(original):
                break

        bitsArray.append(nextByte)

    return bitsArray


# Convert the array of bytes into bits using the helper function.
# Pad any missing spots with white bits due to the original
# image having a smaller size than 576x720.

def prepare(data: array, width: int, height: int) -> array:
    bitsArray = array('B')
    for row in range(height):
        imageLocation = row * width
        imageBits = byter_to_bits(data[imageLocation:(imageLocation + width)])
        bitsArray += imageBits
        remainingWidth = MAX_WIDTH - width
        whiteWidthBits = array('B', [0] * (remainingWidth // 8))
        bitsArray += whiteWidthBits

    remainingHeight = MAX_HIEGHT - height
    whiteHeightBits = array('B', [0] * ((remainingHeight * MAX_WIDTH) // 8))
    bitsArray += whiteHeightBits

    return bitsArray


# MacPaint expects RLE to happen on a per-line basis (MAX_WIDTH).
# In other words there are line boundaries.

def run_length_encode(originalData: array) -> array:
    # Find how many of the same bytes are in a row from *start*
    def takeSame(source: array, start: int) -> int:
        count = 0
        while (start + count + 1 < len(source)
               and source[start + count] == source[start + count + 1]):
            count += 1
        return count + 1 if count > 0 else 0

    rleData = array('B')

    # Divide data into MAX_WIDTH size boundaries by line
    for lineStart in range(0, len(originalData), MAX_WIDTH // 8):
        data = originalData[lineStart:(lineStart + (MAX_WIDTH // 8))]
        index = 0
        while index < len(data):
            notSame = 0
            while(((same := takeSame(data, index + notSame)) == 0)
                  and (index + notSame < len(data))):
                notSame += 1

            if notSame > 0:
                rleData.append(notSame - 1)
                rleData += data[index:index + notSame]
                index += notSame

            if same > 0:
                rleData.append(257 - same)
                rleData.append(data[index])
                index += same
    return rleData

# UTF-8    -> Modern common encoding
#mac_roman  -> Classic Mac OS encoding
# Data fork length = 52,352 bytes
# The value is stored using 4 bytes.

def macBinaryHeader(outFile: str, dataSize: int) -> array:
    macBinary = array('B', [0] * MACBINARY_LENGTH)
    filename = Path(outFile).stem
    filename = filename[:63] if len(filename) > 63 else filename
    macBinary[1] = len(filename)
    macBinary[2:(2 + len(filename))] = array("B", filename.encode("mac_roman"))  # This converts a Python string into bytes using the MacRoman character encoding.
    macBinary[65:69] = array("B", "PNTG".encode("mac_roman"))       # file type
    macBinary[69:73] = array("B", "MPNT".encode("mac_roman"))       # file_creator
    macBinary[83:87] = array("B", dataSize.to_bytes(4, byteorder='big'))  # size og data fork
    timestamp = int((datetime.now() - datetime(1904, 1, 1)).total_seconds())  # Mac timestamp
    macBinary[91:95] = array("B", timestamp.to_bytes(4, byteorder="big"))   # creation stamp
    macBinary[95:99] = array("B", timestamp.to_bytes(4, byteorder="big"))   # modification stamp

    return macBinary


# macbinary format requires that there be padding of 0s up to a
# multiple of 128 bytes for the data fork

def writeMacPaintFile(data: array, outFile: str, width: int, height: int):
    bitsArray = prepare(data, width, height)
    rle = run_length_encode(bitsArray)
    dataSize = len(rle) + HEADER_LENGTH
    output = macBinaryHeader(outFile, dataSize) + array('B', [0] * HEADER_LENGTH) + rle
    output[MACBINARY_LENGTH + 3] = 2   # Data Fork Header Signature

    padding = 128 - (dataSize % 128)
    if padding > 0:
        output += array('B', [0] * padding)

    with open(outFile + ".bin", "wb") as fp:
        output.tofile(fp)


"""
Putting It All Together
To write our MacPaint file bundled as a MacBinary file, we need to take our 
pixel array from dither() and:
1. Call prepare() to convert it from bytes to bits and pad it with 0s.
2. Call run_length_encode() to run-length encode the bit array.
3. Call macbinary_header() to combine the result with a MacBinary  
header.
4. Add a 512-byte MacPaint header as well.
5. Pad the end result with 0s up to a multiple of 128 bytes to follow the 
MacBinary specification requiring this.
"""