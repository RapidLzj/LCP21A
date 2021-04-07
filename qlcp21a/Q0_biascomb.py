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
from .J0_biascomb import _biascomb_


def biascomb(ini_file, file_lst, out_bias_fits, raw_path="",
             overwrite=False,
             log=None,
             extra_config=None):
    """
    Combine bias fits files
    :param ini_file:
    :param file_lst: list file of bias fits files
    :param out_bias_fits: merged bias fits files
    :param raw_path: base path add to list
    :param overwrite: over write result file or not if exists
    :param log: log
    :param extra_config: 190619 额外的配置参数，临时覆盖配置文件中的信息
    :return: nothing
    """
    ini = conf(ini_file, extra_config)
    lf = logfile(log, level=ini["log_level"])

    if os.path.isfile(out_bias_fits) and not overwrite:
        lf.show("SKIP: " + out_bias_fits, logfile.ERROR)
        return

    if not os.path.isfile(file_lst):
        lf.show("SKIP -- FILE NOT EXISTS: " + file_lst, logfile.ERROR)
        return

    # load list
    lst = loadlist(file_lst, base_path=raw_path)

    # call thee working part
    _biascomb_(ini, lst, out_bias_fits, lf)

    lf.close()
