# -*- coding: utf-8 -*-
"""
    201901, Dr. Jie Zheng, Beijing & Xinglong, NAOC
    202101-? Dr. Jie Zheng & Dr./Prof. Linqiao Jiang
    Light_Curve_Pipeline
    v3 (2021A) Upgrade from former version, remove unused code
"""


import numpy as np
import astropy.io.fits as fits
import os
from .JZ_utils import loadlist, datestr, logfile, conf, meanclip
#from .QZ_plotting import plot_im_star, plot_magerr
from .J2_se import _se_


def phot(ini_file, file_lst,
         red_path="",
         overwrite=False,
         log=None,
         extra_config=None):
    """
    photometry
    :param ini_file:
    :param file_lst: list file of scientific fits files
    :param red_path: path of out files
    :param overwrite: over write result file or not if exists
    :param log:
    :param extra_config: 190619 额外的配置参数，临时覆盖配置文件中的信息
    :return:
    """
    ini = conf(ini_file, extra_config)
    lf = logfile(log, level=ini["log_level"])

    if not os.path.isfile(file_lst):
        lf.show("SKIP -- FILE NOT EXISTS: " + file_lst, logfile.ERROR)
        return

    # load list
    scif = loadlist(file_lst, suffix=ini["bf_mid"]+".fits", base_path=red_path,
                    separate_folder = ini["separate_folder"])
    catf = loadlist(file_lst, suffix=ini["cat_mid"]+".fits", base_path=red_path,
                    separate_folder=ini["separate_folder"])
    txtf = loadlist(file_lst, suffix=ini["cat_mid"]+".txt", base_path=red_path,
                    separate_folder=ini["separate_folder"])
    sef = loadlist(file_lst, suffix=ini["se_mid"]+".fits", base_path=red_path,
                    separate_folder=ini["separate_folder"])

    basename = [os.path.basename(f) for f in catf]

    if not overwrite:
        skiptag = [os.path.isfile(f) for f in catf]
    else:
        skiptag = [False for f in catf]

    _se_(ini, scif, sef, catf, txtf, skiptag, lf)

    lf.close()
