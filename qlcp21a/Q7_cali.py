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
import astropy.io.ascii as ascii
from .JZ_utils import loadlist, datestr, logfile, conf, meanclip, basefilename, unmatched,subset
from matplotlib import pyplot as plt
from .J7_cali import _cali_


def cali(ini_file,
          cat_fits,
          out_cali_fits,
          out_cali_txt,
          tgt_id=0,
          ref_id=None,
          chk_id=None,
          overwrite=False,
          log=None,
          extra_config=None):
    """
    plot light curve, calibration with giving data
    :param ini_file:
    :param cat_fits:
    :param out_cali_fits:
    :param out_cali_txt:
    :param tgt_id: id of target in mags, if None, use 1st (0)
    :param ref_id: id of reference, if None, use all but 0
    :param chk_id: id of checkers, as above
    :param overwrite:
    :param log:
    :param extra_config:
    :return:
    """

    ini = conf(ini_file, extra_config)
    lf = logfile(log, level=ini["log_level"])

    if os.path.isfile(out_cali_fits) and not overwrite:
        lf.show("SKIP: " + out_cali_fits + "")
        return

    if not os.path.isfile(cat_fits):
        lf.show("SKIP -- FILE NOT EXISTS: " + cat_fits, logfile.ERROR)
        return

    _cali_(ini, cat_fits, tgt_id, ref_id, chk_id, out_cali_fits, out_cali_txt, lf)

    lf.close()
