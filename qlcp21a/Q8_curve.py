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
from .J8_curve import _curve_


def curve(ini_file,
          cali_fits,
          out_lc_png=None,
          fig_set=None,
          noplot=False,
          overwrite=False,
          log=None,
          extra_config=None):
    """
    plot light curve, calibration with giving data
    :param ini_file:
    :param cali_fits:
    :param out_lc_png: if None, plot only
    :param fig_set: figure settings
    :param noplot: if True, no online plot, only save, if out none, do nothing
    :param overwrite:
    :param log:
    :param extra_config:
    :return:
    """

    ini = conf(ini_file, extra_config)
    lf = logfile(log, level=ini["log_level"])

    if out_lc_png and os.path.isfile(out_lc_png) and not overwrite:
        lf.show("SKIP: " + out_lc_png + "")
        return
    if not out_lc_png and noplot:
        lf.show("NO Plot and NO Save, Do Nothing!")
        return

    if not os.path.isfile(cali_fits):
        lf.show("SKIP -- FILE NOT EXISTS: " + cali_fits, logfile.ERROR)
        return

    # init fig_set, if given key not provided, use default value
    if fig_set is None:
        fig_set = {}

    def_fig_set = {
        "step_tgt_chk": None,  # steps between target curve and 1st checker
        "step_chk_chk": None,  # steps between checkers
        "marker_tgt": "rs",  # color and marker of target
        "marker_chk": ("b*", "g*", "m*", "c*"),  # color and marker of checker
        "xlim": None,  # if None, use default
        "ylim": None,  # if None, use reversed default
        "bjd_0": 0, # subtract BJD with this, if 0, use original
        "figsize": (20, 10),  # figure size
    }
    for k in def_fig_set:
        if k not in fig_set:
            fig_set[k] = def_fig_set[k]

    _curve_(ini, cali_fits, fig_set, noplot, out_lc_png, lf)

    lf.close()
