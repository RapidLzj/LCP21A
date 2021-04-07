# -*- coding: utf-8 -*-
"""
    201901, Dr. Jie Zheng, Beijing & Xinglong, NAOC
    202101-? Dr. Jie Zheng & Dr./Prof. Linqiao Jiang
    Light_Curve_Pipeline
    v3 (2021A) Upgrade from former version, remove unused code
    Qx_xxxx_ is the working part of the step, while Qx_xxxx is the shell
"""


import numpy as np
import astropy.io.fits as fits
from .JZ_utils import loadlist, datestr, logfile, conf


def _flatcomb_(ini, lst, bias_fits, out_flat_fits, lf):
    nf = len(lst)

    # get size of images
    hdr = fits.getheader(lst[0])
    nx = hdr['NAXIS1']
    ny = hdr['NAXIS2']
    lf.show("{:02d} flat files, image sizes {:4d}x{:4d}".format(nf, nx, ny), logfile.DEBUG)

    # load bias
    lf.show("Loading Bias: {}".format(bias_fits), logfile.DEBUG)
    data_bias = fits.getdata(bias_fits)

    # load images
    data_cube = np.empty((nf, ny, nx), dtype=np.float32)
    for f in range(nf):
        data_tmp = fits.getdata(lst[f]) - data_bias
        data_tmp_med = np.median(data_tmp)
        if ini["flat_limit_low"] < data_tmp_med < ini["flat_limit_high"]:
            data_cube[f, :, :] = data_tmp / data_tmp_med
            lf.show("Loading {:02d}/{:02d}: {:40s} / Scaled by {:7.1f}".format(
                f + 1, nf, lst[f], data_tmp_med), logfile.DEBUG)
        else:
            data_cube[f, :, :] = np.nan
            lf.show("Ignore  {:02d}/{:02d}: {:40s} / XXX MED = {:7.1f}".format(
                f + 1, nf, lst[f], data_tmp_med), logfile.DEBUG)

    # get median
    data_med = np.nanmedian(data_cube, axis=0)

    # add process time to header
    hdr.append(('COMBTIME', datestr()))
    s = hdr.tostring()  # force check the header

    # save new fits
    new_fits = fits.HDUList([
        fits.PrimaryHDU(header=hdr, data=data_med),
    ])
    new_fits.writeto(out_flat_fits, overwrite=True)
    lf.show("Writing to: {}".format(out_flat_fits), logfile.INFO)
