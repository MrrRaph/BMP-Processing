#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse, os, sys, numpy as np, colorama
from utils import helpers as hp, colourers, gaussianKernel, gaborKernel
from processors import printers as Printers, transformers as Transformers, filters as Filters
from middlewares import required_length
from formats import BMP, PNG

# Initialization of colorama
colorama.init(autoreset=True)

def imageProcessing():
    """
        Process a given image in parameter (BMP or PNG)
    """

    # Parser initialization
    parser = argparse.ArgumentParser(description=colourers.toCyan('Image processor for reading/writing images into BMP/PNG formats and applying transformations on it.'))
    
    # Formats Parser
    group = parser.add_argument_group(colourers.toGreen('formats'))
    formatParser = group.add_mutually_exclusive_group(required=True)
    formatParser.add_argument('--bmp',
                               type=str,
                               metavar=colourers.toRed('<bmp file name>'), 
                               help=colourers.toMagenta('bmp file to parse'))
    formatParser.add_argument('--png',
                              type=str,
                              metavar=colourers.toRed('<png file name>'),
                              help=colourers.toMagenta('png file to parse'))

    # Printers Parser
    group = parser.add_argument_group(colourers.toYellow('printers'))
    printers = group.add_mutually_exclusive_group()
    printers.add_argument('--header',
                       help=colourers.toMagenta('print the file format header'),
                       action='store_true')
    printers.add_argument('--print-color',
                       '-pc',
                       type=int,
                       nargs=2,
                       metavar=(colourers.toRed('<width>'), colourers.toRed('<height>')),
                       help=colourers.toMagenta('pixel to print'))
    printers.add_argument('--histogram',
                       action='store_true',
                       help=colourers.toMagenta('print histogram associated'))
    printers.add_argument('--output',
                        '-o',
                        type=str,
                        metavar=colourers.toRed('<output file>'),
                        help=colourers.toMagenta('image output file'))

    # Transformers Parser
    transformers = parser.add_argument_group(colourers.toBlue('transformers'))
    transformers.add_argument('--half',
                              action='store_true',
                              help='applying the filter on one half of the image')
    transformers.add_argument('--rotate',
                        '-r',
                        type=int,
                        choices=[90, 180, 270],
                        metavar=colourers.toRed('<degree of rotation>'),
                        help=colourers.toMagenta('rotate the image'))
    transformers.add_argument('--scale',
                        '-s',
                        type=int,
                        nargs='+',
                        action=required_length(1, 2),
                        metavar=(colourers.toRed('<scaleRatio> | [<width>'), colourers.toRed('<height>')),
                        help=colourers.toMagenta('scale/shrink the image'))
    transformers.add_argument('--contrast',
                        '-c',
                        type=float,
                        metavar=colourers.toRed('<contrast factor>'),
                        help=colourers.toMagenta('apply a factor contrast'))
    transformers.add_argument('--grayscale',
                        '-gs',
                        action='store_true',
                        help=colourers.toMagenta('to grayscale image'))
    transformers.add_argument('--binary',
                        '-b',
                        action='store_true',
                        help=colourers.toMagenta('to binary image'))
    transformers.add_argument('--invert',
                        '-i',
                        action='store_true',
                        help=colourers.toMagenta('to inverted image, equivalent to --contrast -1'))
    transformers.add_argument('--channel',
                        type=str,
                        choices=['blue', 'green', 'red'],
                        metavar=colourers.toRed('<channel>'),
                        nargs='+',
                        action=required_length(1, 2),
                        help=colourers.toMagenta('to the specified channel'))
    
    # Filters Parser
    filters = parser.add_argument_group(colourers.toCyan('filters'))
    filters.add_argument('--edge-detection',
                         '-ed',
                         type=str,
                         choices=['canny', 'sobel', 'prewitt', 'roberts', 'kirsch'],
                         metavar=colourers.toRed('<filter name>'),
                         help=colourers.toMagenta('perform an edge detection'))
    filters.add_argument('--retrieve-color',
                         '-rv',
                         action='store_true',
                         help=colourers.toMagenta('retrieve the colors of a grayscale image'))
    filters.add_argument('--edge-enhancement',
                         '-ee',
                         action='store_true', 
                         help=colourers.toMagenta('applying increased edge enhancement filter'))
    filters.add_argument('--sharpen',
                         action='store_true',
                         help=colourers.toMagenta('sharpening the image'))
    filters.add_argument('--unsharp',
                        action='store_true',
                        help=colourers.toMagenta('unsharp the image'))       
    filters.add_argument('--denoise',
                         action='store_true',
                         help=colourers.toMagenta('denoise the image'))
    filters.add_argument('--texture-detection',
                         '-td',
                         action='store_true',
                         help=colourers.toMagenta('applying texture detection (Gabor Filter)'))
    filters.add_argument('--blur',
                         type=str,
                         choices=['simple', 'more', 'average', 'gaussian', 'motion'],
                         metavar=colourers.toRed('<type of blur>'),
                         help=colourers.toMagenta('perform the selected blur'))
    filters.add_argument('--blur-iteration',
                         '-bi',
                         type=int,
                         default=1,
                         metavar=colourers.toRed('<number of iteration>'),
                         help=colourers.toMagenta('apply N times the blur function'))
    filters.add_argument('--emboss',
                         action='store_true',
                         help=colourers.toMagenta('perform an embossing filter'))
    filters.add_argument('--overlap',
                         type=str,
                         nargs='+',
                         metavar=colourers.toRed('<image to overlap>'),
                         help=colourers.toMagenta('overlap an image given on the selected image'))

    # Args parsing
    args = parser.parse_args()

    filename = ""
    # BMP Block
    if args.bmp:
        filename = args.bmp

        if not os.path.isfile(filename):
            colourers.error('"{}" does not exist !'.format(filename))
            sys.exit(-1)
        colourers.success('Success Opening {}...'.format(filename))

        bmp = BMP(filename)
        half = args.half

        if args.print_color:
            width, height = args.print_color
            colourers.info(f'Printing pixel color of ({width}, {height})')
            Printers.printPixel(bmp, width, height)
            sys.exit(0)
        
        elif args.header:
            colourers.info(f'Printing BMP header of {bmp.filename}')
            Printers.printHeader(bmp)
            sys.exit(0)
        
        elif args.histogram:
            colourers.info(f'Printing color histogram of {bmp.filename}')
            Printers.printHistogram(bmp)
            sys.exit(0)
        
        if (args.rotate or args.scale or args.contrast or args.grayscale or 
            args.binary or args.channel or args.edge_detection or args.retrieve_color or
            args.edge_enhancement or args.blur or args.emboss or args.overlap or args.texture_detection or
            args.denoise or args.sharpen or args.unsharp):
            if not hp.atLeastOne(args.output, (
                args.rotate,
                args.scale,
                args.contrast,
                args.grayscale,
                args.binary,
                args.channel,
                args.edge_detection,
                args.retrieve_color,
                args.edge_enhancement,
                args.blur,
                args.emboss,
                args.overlap,
                args.texture_detection,
                args.denoise,
                args.sharpen,
                args.unsharp
            )):
                parser.error('--rotate/--scale/--contrast/--grayscale/--binary/--channel/--edge-detection/--retrieve-color/--edge-enhancement/--blur/--emboss/--overlap/--texture-detection/--denoise/--sharpen/--unsharp and --output must be given together')
        
        if args.rotate:
            degree = args.rotate
            colourers.info(f'Rotating image to {degree} degree')
            bmp.imageData = Transformers.rotate(bmp, degree)

        if args.scale:
            if len(args.scale) == 2:
                width, height = args.scale
                colourers.info(f'Scaling image to {width}x{height} pixels')
                bmp.imageData = Transformers.scale(bmp, height, width)
            else:
                scaleRatio = args.scale[0]

                colourers.info(f'Scaling image to {scaleRatio} scale ratio')

                height = int(hp.readLittleEndian(bmp.height))
                width = int(hp.readLittleEndian(bmp.width))

                bmp.imageData = Transformers.scale(bmp, height * scaleRatio, width * scaleRatio)
        
        if args.contrast:
            factor = args.contrast
            colourers.info(f'Applying a factor contrast of {factor}')
            bmp.imageData = Transformers.contrast(bmp, factor)
        
        if args.grayscale:
            colourers.info(f'Applying grayscale mask to the image')
            bmp.imageData = Transformers.grayscale(bmp, half)
        
        if args.binary:
            colourers.info(f'Applying binary mask to the image')
            bmp.imageData = Transformers.binary(bmp, half)
        
        if args.invert:
            colourers.info(f'Inverting image colours')
            bmp.imageData = Transformers.invert(bmp, half)
        
        if args.channel:
            if len(args.channel) == 2:
                c1, c2 = args.channel
                colourers.info(f'Keeping only {c1} and {c2} channels of the image')
                bmp.imageData = Transformers.toChannel(bmp, [c1, c2], half)
            else:
                channel = args.channel[0]
                colourers.info(f'Keeping only {channel} channel of the image')
                bmp.imageData = Transformers.toChannel(bmp, channel, half)
        
        if args.denoise:
            colourers.info(f'Denoising the image')
            bmp.imageData = Filters.wienerFilter(bmp.imageData, gaussianKernel(9, sigma=0.33), K=10)
        
        if args.texture_detection:
            colourers.info(f'Applying texture detection (Gabor Filter)')
            bmp.imageData = Filters.gaborFilter(bmp.imageData, gaborKernel(0))
        
        if args.edge_enhancement:
            colourers.info(f'Applying increased edge enhancement filter')
            bmp.imageData = Filters.iee(bmp.imageData)

        if args.edge_detection:
            filterName = args.edge_detection
            if filterName == 'canny':
                colourers.info(f'Performing Canny filter for edge detection')
                bmp.imageData = Filters.ced(bmp.imageData, sigma=0.33, kernelSize=9, weakPix=50)
            if filterName == 'sobel':
                colourers.info(f'Performing Sobel filter for edge detection')
                bmp.imageData = Filters.sed(bmp.imageData, sigma=0.33, kernelSize=9)
            if filterName == 'prewitt':
                colourers.info(f'Performing Prewitt filter for edge detection')
                bmp.imageData = Filters.ped(bmp.imageData, sigma=0.33, kernelSize=9)
            if filterName == 'roberts':
                colourers.info(f'Performing Roberts filter for edge detection')
                bmp.imageData = Filters.red(bmp.imageData, sigma=0.33, kernelSize=9)
            if filterName == 'kirsch':
                colourers.info(f'Performing Kirsch filter for edge detection')
                bmp.imageData = Filters.ked(bmp.imageData, sigma=0.33, kernelSize=9)

        if args.sharpen:
            colourers.info(f'Sharpening the image')
            bmp.imageData = Filters.sharpen(bmp.imageData)
        
        if args.unsharp:
            colourers.info(f'Unsharpening the image')
            bmp.imageData = Filters.unsharp(bmp.imageData)

        if args.retrieve_color:
            colourers.info(f'Retrieving color')
            bmp.imageData = Filters.retrieveColor(bmp.imageData)
        
        if args.blur:
            blurType = args.blur
            colourers.info(f'Performing a {blurType} blur')
            for _ in range(args.blur_iteration):
                blurFunc = Filters.blur.switcher.get(blurType)
                bmp.imageData = blurFunc(bmp.imageData)
        
        if args.emboss:
            colourers.info(f'Performing emboss filter')
            bmp.imageData = Filters.emboss(bmp.imageData)
        
        if args.overlap:
            overlappers = []
            for ov in args.overlap:
                overlappers.append(BMP(ov).imageData)
            colourers.info(f'Performing an overlapping between {bmp.filename} and {args.overlap}')
            bmp.imageData = Filters.overlap(bmp.imageData, overlappers)
       
        if args.output:
            outputFile = args.output
            hp.saveBMP(bmp, bmp.imageData, outputFile)
            colourers.success(f'Succesfully saved into {outputFile}')
            sys.exit(0)
        
        parser.error('Give at least one more argument')
        
    # PNG Block
    else:
        filename = args.png

        if not os.path.isfile(filename):
            print('"{}" does not exist'.format(filename), file=sys.stderr)
            sys.exit(-1)
        print('Success Opening {}...'.format(filename))
        
        png = PNG(filename)

# Main function
if __name__ == '__main__':
    imageProcessing()
    sys.exit(0)