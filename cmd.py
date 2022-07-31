import argparse
import os.path
from fullog import Full_Log
import logging
import sys
from stegano import Stegano

def is_valid_pic(parser,arg):
    if not os.path.isfile(arg):
        parser.error(f'Picture file {arg} does not exist')
    else:
        return arg

def is_valid_txt(parser,arg):
    #TODO check folder name and file name syntax
    if not isinstance(arg,str):
        parser.error(f'Wrong text file path: {arg}')
    else:
        return arg

def main():
    parser = argparse.ArgumentParser(description=""" Two way steganography.
    
    'encode' starts from an image and a text to produce an output image.
    
    'decode' retrieves the text contained in an encoded image.
    """)
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-d', '--decode', help='Reveal the invisible text',
                        action='store_true', default=False)
    group.add_argument('-e', '--encode', help='Hide text in an image',
                        action='store_true', default=False)
    parser.add_argument('--pic', dest='picfile', required=True,
                        help='path to the picture file', metavar='PIC',
                        type=lambda x: is_valid_pic(parser,x))
    parser.add_argument('infile', nargs='?', type=argparse.FileType('r'),
                        help='path to the text file',
                        default=sys.stdin)
    parser.add_argument('-o', '--output', help='Output file. Pic or text. Default is stdout.')

    args = parser.parse_args()
    #https://stackoverflow.com/questions/7862987/consistent-way-to-redirect-both-stdin-stdout-to-files-in-python-using-optparse
    #
    #
    Full_Log("tksteg")
    logging.info("CLI args:")
    #
    # check parsed args
    #
    for k in dir(args):
        if not k.startswith('_'):
            logging.info(f"  {k}: {eval('args.'+k)}")
    stegano = Stegano()
    #
    #
    #
    try:
        stegano.read_image(args.picfile)
        #
        #
        #
        if args.decode:
            stegano.decode()
            stegano.output_data()
        elif args.encode:
            stegano.input_data()
            stegano.encode()
            outfile = args.picfile
            filetype  = args.picfile[-4:].lower()
            if outfile[-3:].lower() == 'jpg':
                logging.warning("Cannot save to jpg. Will save to png instead.")
                #
                # replace JPG by PNG in output image
                #
                filetype = '.png'
            stegano.output_image(filetype)
    except Exception as e:
        logging.error(str(e))

main()
