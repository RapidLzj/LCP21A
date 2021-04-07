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


def _curve_(ini_file, cali_fits, fig_set, noplot, out_lc_png, lf):
    """

    :param ini_file:
    :param cali_fits:
    :param fig_set:
    :param noplot:
    :param out_lc_png:
    :param lf:
    :return:
    """

    # extract settings from fig_set
    step_tgt_chk = fig_set["step_tgt_chk"]
    step_chk_chk = fig_set["step_chk_chk"]
    marker_tgt = fig_set["marker_tgt"]
    marker_chk = fig_set["marker_chk"]
    xlim = fig_set["xlim"]
    ylim = fig_set["ylim"]
    bjd_0 = fig_set["bjd_0"]
    figsize = fig_set["figsize"]

    # load catalog and get n_files and n_object
    cat = fits.getdata(cali_fits, 1)
    n_chk = len(cat[0]["Magchk"])
    tgt_mag_cali = cat["CaliTgt"]
    chk_mag_cali = cat["CaliChk"]

    if cat[0]["BJD"] == 0:
        bjd = cat["JD"] - fig_set["bjd_0"]
        jd_label = "JD"
    else:
        bjd = cat["BJD"] - fig_set["bjd_0"]
        jd_label = "BJD"

    # if steps not provided, use std
    if step_tgt_chk is None:
        step_tgt_chk = np.nanstd(tgt_mag_cali) * 2 + np.nanstd(chk_mag_cali) * 4
    if step_chk_chk is None:
        step_chk_chk = np.nanstd(chk_mag_cali) * 5

    # start plotting
    fig, ax = plt.subplots(1, 1, figsize=figsize)

    b = 0.0  # base y of each curve
    ax.plot(bjd, tgt_mag_cali + b, marker_tgt,
            label="Target")
            # label="Target (#{})".format(tgt_id))

    if type(marker_chk) is str:
        marker_chk = (marker_chk, )
    for i in range(n_chk):
        b = step_tgt_chk + step_chk_chk * i
        ax.plot(bjd, chk_mag_cali[:, i] + b, marker_chk[i % len(marker_chk)],
                # label="Check {} (#{}) $\\sigma$={:.3f}".format(i+1, chk_id[i], np.nanstd(chk_mag_cali[:, i])))
                label="Check {} $\\sigma$={:.3f}".format(i+1, np.nanstd(chk_mag_cali[:, i])))

    if xlim is not None:
        ax.set_xlim(*xlim)
    if ylim is not None:
        # if ylim given, use this, no checking
        ax.set_ylim(*ylim)
    else:
        # reverse auto y-lim
        ylim = ax.get_ylim()
        ax.set_ylim(ylim[1], ylim[0])

    ax.legend()
    if bjd_0 == 0:
        ax.set_xlabel(jd_label)
    else:
        ax.set_xlabel("{} - {}".format(jd_label, bjd_0))
    ax.set_ylabel("Differential Mag (mag)")

    ti = os.path.basename(os.path.splitext(os.path.split(cali_fits)[1])[0])
    ax.set_title("Light-Curve: " + ti)

    if out_lc_png:
        fig.savefig(out_lc_png)
        lf.show("Light-Curve save to {}".format(out_lc_png), logfile.INFO)

    if noplot:
        plt.close(fig)
