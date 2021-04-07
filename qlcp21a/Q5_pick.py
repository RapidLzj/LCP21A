# -*- coding: utf-8 -*-
"""
    201901, Dr. Jie Zheng, Beijing & Xinglong, NAOC
    202101-? Dr. Jie Zheng & Dr./Prof. Linqiao Jiang
    Light_Curve_Pipeline
    v3 (2021A) Upgrade from former version, remove unused code
    210330 add this section, pick out good reference
"""


import os
import numpy as np
import astropy.io.fits as fits
from .JZ_utils import loadlist, datestr, logfile, conf, meanclip, hdr_dt_jd
from .JZ_cata import match
from .J5_pick import _pick_


def pick(ini_file, file_lst,
         offset_file,
         out_pick_txt,
         base_img_id=0,
         base_cat_file=None,
         red_path="",
         overwrite=False,
         log=None,
         extra_config=None):
    """
    Pick good reference stars from image, the criteria is
    :param ini_file:
    :param file_lst: list file of scientific fits files
    :param offset_file: offset file
    :param base_img_id:
    :param base_cat_file:
    :param red_path: path of out files
    :param overwrite: overwrite result file or not if exists
    :param log:
    :param extra_config: 190619 额外的配置参数，临时覆盖配置文件中的信息
    :return: star_xy_list
    """

    ini = conf(ini_file, extra_config)
    lf = logfile(log, level=ini["log_level"])

    if os.path.isfile(out_pick_txt) and not overwrite:
        lf.show("SKIP: " + out_pick_txt + "")
        return

    if not os.path.isfile(file_lst):
        lf.show("SKIP -- FILE NOT EXISTS: " + file_lst, logfile.ERROR)
        return

    # load list
    catf = loadlist(file_lst, suffix=ini["cat_mid"] + ".fits", base_path=red_path,
                    separate_folder=ini["separate_folder"])

    xy_var, xy_ref = _pick_(ini, catf, offset_file, base_img_id, base_cat_file, out_pick_txt, lf)

    lf.close()

    return xy_var, xy_ref
