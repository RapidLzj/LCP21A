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
from .J1_imgproc import _imgproc_


def imgproc(ini_file, file_lst, bias_fits, flat_fits,
            obj_coord=None,
            raw_path="", red_path="",
            extra_hdr=None,
            overwrite=False,
            log=None,
            extra_config=None):
    """

    :param ini_file:
    :param file_lst: list file of scientific fits files
    :param bias_fits: merged flat fits files
    :param flat_fits: merged flat fits files
    :param obj_coord:
    :param raw_path: base path add to list
    :param red_path: path of out files, if provided, use this path
    :param extra_hdr: extra header, a dict
    :param overwrite: over write result file or not if exists
    :param log:
    :param extra_config: 190619 额外的配置参数，临时覆盖配置文件中的信息
    :return: nothing
    """
    ini = conf(ini_file, extra_config)
    lf = logfile(log, level=ini["log_level"])

    if not os.path.isfile(file_lst):
        lf.show("SKIP -- FILE NOT EXISTS: " + file_lst, logfile.ERROR)
        return

    # load list
    lst = loadlist(file_lst, base_path=raw_path)
    scif = loadlist(file_lst, suffix=ini["bf_mid"]+".fits",
                    base_path=red_path, separate_folder=ini["separate_folder"])

    if not overwrite:
        skiptag = [os.path.isfile(f) for f in scif]
    else:
        skiptag = [False for f in scif]

    _imgproc_(ini, lst, bias_fits, flat_fits, scif, obj_coord, skiptag, extra_hdr, lf)

    lf.close()
