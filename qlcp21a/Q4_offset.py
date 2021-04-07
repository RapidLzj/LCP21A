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
from .JZ_utils import loadlist, datestr, logfile, conf, meanclip, hdr_dt_jd
from .JZ_cata import match
from .JZ_trimatch import make_tri, match_triangle, argunique
from .J4_offset import _offset_


def offset(ini_file, file_lst,
           out_offset_file,
           base_img_id=0,
           base_cat_file=None,
           red_path="",
           overwrite=False,
           log=None,
           extra_config=None):
    """
    x/y offset finding
    :param ini_file:
    :param file_lst: list file of scientific fits files
    :param out_offset_file: offset file
    :param base_img_id: the file chosen as the reference base
    :param base_cat_file: template catalog file, if base < 0, use this
    :param red_path: path of out files
    :param overwrite: over write result file or not if exists
    :param log:
    :param extra_config: 190619 额外的配置参数，临时覆盖配置文件中的信息
    :return:
    """

    ini = conf(ini_file, extra_config)
    lf = logfile(log, level=ini["log_level"])

    if os.path.isfile(out_offset_file) and not overwrite:
        lf.show("SKIP: " + out_offset_file + "")
        return

    if not os.path.isfile(file_lst):
        lf.show("SKIP -- FILE NOT EXISTS: " + file_lst, logfile.ERROR)
        return

    # load list
    basef = loadlist(file_lst)
    catf = loadlist(file_lst, suffix=ini["cat_mid"] + ".fits", base_path=red_path,
                    separate_folder=ini["separate_folder"])

    _offset_(ini, basef, catf, base_img_id, base_cat_file, out_offset_file, lf)

    lf.close()
