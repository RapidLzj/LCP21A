# -*- coding: utf-8 -*-
"""
    201901, Dr. Jie Zheng, Beijing & Xinglong, NAOC
    202101-? Dr. Jie Zheng & Dr./Prof. Linqiao Jiang
    Light_Curve_Pipeline
    v3 (2021A) Upgrade from former version, remove unused code
"""


import os
import numpy as np
import astropy.io.fits as fits
from .JZ_utils import loadlist, datestr, logfile, conf


def _imgproc_(ini, lst, bias_fits, flat_fits, scif, skiptag, extra_hdr, lf):
    """

    :param ini:
    :param lst:
    :param bias_fits:
    :param flat_fits:
    :param scif:
    :param skiptag:
    :param extra_hdr:
    :param lf:
    :return:
    """

    nf = len(lst)

    lf.show("{:03d} files".format(nf), logfile.DEBUG)

    # load bias and flat
    lf.show("Loading Bias: {}".format(bias_fits), logfile.DEBUG)
    data_bias = fits.getdata(bias_fits)
    lf.show("Loading Flat: {}".format(flat_fits), logfile.DEBUG)
    data_flat = fits.getdata(flat_fits)

    # load header from extra header file or dict, if exists
    hdr_ex = {}
    if extra_hdr:
        if type(extra_hdr) is str:
            extra_hdr = (extra_hdr, )
        for f in extra_hdr:
            hdr_ex.update(conf(f, no_default=True).to_header())
    elif type(extra_hdr) is dict:
        hdr_ex.update(extra_hdr)

    # 标出复制字段，即该字段的值来自另外一个原先已有的字段
    hdr_mark = {}
    for k in hdr_ex:
        v = hdr_ex[k]
        if type(v) in (list, tuple):
            v = v[0]
        if type(v) is str and v.startswith("$"):
            hdr_mark[k] = v[1:]

    # load images and process
    for f in range(nf):
        if not os.path.isdir(os.path.dirname(scif[f])):
            os.mkdir(os.path.dirname(scif[f]))
        if skiptag[f]:
            lf.show("SKIP    {:03d}/{:03d}: {:40s}".format(f + 1, nf, scif[f]), logfile.DEBUG)
            continue
        lf.show("Loading {:03d}/{:03d}: {:40s}".format(f + 1, nf, lst[f]), logfile.DEBUG)
        hdr = fits.getheader(lst[f])
        dat = (fits.getdata(lst[f]) - data_bias) / data_flat

        # add process time to header
        hdr.update(BZERO=0)
        hdr.append(('PROCTIME', datestr()))
        s = hdr.tostring()  # force check the header

        # copy marked fields from original header
        # 190619 重新启用
        hdr_ex2 = hdr_ex.copy()
        for k in hdr_mark:
            hdr_ex2.update({k:hdr.get(k, "")})
        # add extra fields to header
        hdr.update(hdr_ex2)

        # save new fits
        new_hdu = fits.PrimaryHDU(header=hdr, data=dat)
        new_fits = fits.HDUList([new_hdu])
        new_fits.writeto(scif[f], overwrite=True)
        lf.show("Writing {:03d}/{:03d}: {:40s}".format(f + 1, nf, scif[f]), logfile.DEBUG)

    lf.show("{} of {} files corrected".format(nf-sum(skiptag), nf), logfile.INFO)