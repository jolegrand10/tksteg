import cv2 as cv
import logging
import sys

class Stegano:
    """ encode/decode a byte-msg in/from an image without visible difference"""

    INPICFILES = (('image files', '.jpg .png .bmp'),)
    OUTPICFILES = (('image files', '.jpg .png .bmp'),)
    TXTFILES = (('text files', '*.txt'),)

    def __init__(self):
        """ image is an np.ndarray as used in cv2 """
        self.image = None
        self.data = ""
        self.n = 0
        self.p = 0

    def read_image(self, path):
        logging.info(f"Read image from {path}")
        try:
            self.image = cv.imread(path)
        except Exception as e:
            logging.error(f"Failed to read cv2 image. Reason: {e}")
        if self.image is None:
            raise Exception("Failed to read cv2 image")
        else:
            self.n, self.p, _ = self.image.shape

    def read_data(self, path):
        with open(path, "rb") as f:
            self.data = f.read()
        logging.info(f"{len(self.data)} bytes read from {path}")

    def input_data(self):
        self.data=sys.stdin.read()

    def write_image(self, path):
        logging.info(f"Write image to {path}")
        cv.imwrite(path, self.image)

    def write_data(self, path):
        with open(path, "wb") as f:
            f.write(self.data)
            logging.info(f"{len(self.data)} bytes written")

    def output_data(self):
        sys.stdout.write(self.data)
        logging.info(f"{len(self.data)} bytes written")

    def output_image(self, dotext):
        sys.stdout.buffer.write(cv.imencode(dotext, img)[1].tobytes())

    def encode(self):
        """ message is a byte array """
        #
        # if length of message in bytes exceeds the count of bytes in the image
        # the message is truncated
        #
        maxlen = self.image.size // 8
        message = self.data
        if len(message) >= maxlen:
            message = message[:maxlen - 1]  # - 1 accounts for the termination mark
        #
        # Starting position in the image, where the message will be encoded
        #
        i = 0  # row index
        j = 0  # column index
        k = 0  # color index (or channel index, for R,G or B)
        #
        # message is processed byte by byte
        # a null byte is added as the end of message to mark its end
        #
        for c in message + bytearray((0,)):
            #
            # c is a byte, bs is its representation as a string of 8  1s or 0s
            #
            bs = format(int(c), '08b')
            #
            # for each bit in the current byte - bit string
            #
            for b in bs:
                b = int(b)
                if b:
                    #
                    # to set last bit while preserving the others : or with 1
                    #
                    self.image[i, j, k] |= 1
                else:
                    #
                    # to clear last bit while preserving the others : and with ~1
                    #
                    self.image[i, j, k] &= ~1
                #
                # move  next channel
                #
                k = (k + 1) % 3
                if k == 0:
                    #
                    # move next pixel in the line
                    #
                    j = (j + 1) % self.p
                    if j == 0:
                        #
                        # move  next line
                        #
                        i += 1
        return len(message)

    def decode(self):
        #
        # the message to be recovered from the image
        #
        message = bytearray()
        #
        # bit string - representing a byte
        #
        bs = ""
        #
        # loop on all bytes in the image, collecting 1 bit per byte,
        # assembling bits in bytes, appended one by one to the growing message
        # until a null byte is encountered
        #
        for i in range(self.n):
            for j in range(self.p):
                for k in range(3):
                    #
                    # collect low weight bit
                    #
                    b = self.image[i, j, k] & 1
                    #
                    # catenate to growing bitstring
                    #
                    bs += str(b)
                    #
                    # until a byte is assembled
                    #
                    if len(bs) == 8:
                        #
                        # convert 8 bit string to int
                        #
                        #
                        x = int(bs, 2)
                        if x == 0:
                            #
                            # null byte terminates the message
                            #
                            self.data = message
                            logging.info(f"{len(self.data)} bytes decoded")
                            return
                        else:
                            #
                            # catenate byte to the growing msg
                            #
                            message += bytearray((x,))

                            bs = ""


def main():
    pass


if __name__ == '__main__':
    main()
