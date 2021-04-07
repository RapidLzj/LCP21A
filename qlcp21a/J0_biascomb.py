# -*- coding: utf-8 -*-
"""
    201901, Dr. Jie Zheng, Beijing & Xinglong, NAOC
    202101-? Dr. Jie Zheng & Dr./Prof. Linqiao Jiang
    Light_Curve_Pipeline
    v3 (2021A) Upgrade from former version, remove unused code
    Qx_xxxx_ is the working part of the step, while Qx_xxxx is the shell
"""


import os
import numpy as np
import astropy.io.fits as fits
from .JZ_utils import loadlist, datestr, logfile, conf


def _biascomb_(ini, lst, out_bias_fits, lf):
    """
    working part of bias combine
    :param ini:
    :param lst: list of bias files
    :param out_bias_fits:
    :param lf: log-file
    :return:
    """

    nf = len(lst)

    # get size of images
    hdr = fits.getheader(lst[0])
    nx = hdr['NAXIS1']
    ny = hdr['NAXIS2']
    lf.show("{:02d} bias files, image sizes {:4d}x{:4d}".format(nf, nx, ny), logfile.DEBUG)

    # load images
    data_cube = np.empty((nf, ny, nx), dtype=np.float32)
    for f in range(nf):
        lf.show("Loading {:02d}/{:02d}: {:40s}".format(f+1, nf, lst[f]), logfile.DEBUG)
        data_cube[f, :, :] = fits.getdata(lst[f])

    # get median
    data_med = np.median(data_cube, axis=0)

    # add process time to header
    hdr.append(('COMBTIME', datestr()))
    s = hdr.tostring()  # force check the header

    # save new fits
    new_fits = fits.HDUList([
        fits.PrimaryHDU(header=hdr, data=data_med),
    ])
    new_fits.writeto(out_bias_fits, overwrite=True)
    lf.show("Writing to: {}".format(out_bias_fits), logfile.INFO)
