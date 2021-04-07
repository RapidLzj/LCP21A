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
from .J0_flatcomb import _flatcomb_


def flatcomb(ini_file, file_lst, bias_fits, out_flat_fits,
             raw_path="",
             overwrite=False,
             log=None,
             extra_config=None):
    """
    Combine bias fits files
    :param ini_file:
    :param file_lst: list file of bias fits files
    :param bias_fits: merged bias fits file
    :param out_flat_fits: merged flat fits file
    :param raw_path: base path add to list
    :param overwrite: over write result file or not if exists
    :param log:
    :param extra_config: 190619 额外的配置参数，临时覆盖配置文件中的信息
    :return: nothing
    """
    ini = conf(ini_file, extra_config)
    lf = logfile(log, level=ini["log_level"])

    if os.path.isfile(out_flat_fits) and not overwrite:
        lf.show("SKIP: " + out_flat_fits, logfile.ERROR)
        return

    if not os.path.isfile(file_lst):
        lf.show("SKIP -- FILE NOT EXISTS: " + file_lst, logfile.ERROR)
        return

    # load list
    lst = loadlist(file_lst, base_path=raw_path)

    _flatcomb_(ini, lst, bias_fits, out_flat_fits, lf)

    lf.close()
