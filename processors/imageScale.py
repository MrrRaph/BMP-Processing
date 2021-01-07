#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from utils import helpers as hp
import numpy as np

def scale(image, nR, nC):
    nR0 = len(image)
    nC0 = len(image[0])
    return [
        [
            image[int(nR0 * r / nR)][int(nC0 * c / nC)] for c in range(nC)
        ] for r in range(nR)
    ]

def imageScale(bmp, nR, nC):
    return np.array(scale(bmp.imageData, nR, nC)).astype(float)