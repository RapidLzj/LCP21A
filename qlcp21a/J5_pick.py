# -*- coding: utf-8 -*-
"""
    201901, Dr. Jie Zheng, Beijing & Xinglong, NAOC
    202101-? Dr. Jie Zheng & Dr./Prof. Linqiao Jiang
    Light_Curve_Pipeline
    v3 (2021A) Upgrade from former version, remove unused code
"""


import os
import numpy as np
from astropy.io import fits, ascii
from .JZ_utils import loadlist, datestr, logfile, conf, meanclip, hdr_dt_jd
from .JZ_cata import match


def _pick_(ini, catf, offset_file, base_img_id, base_cat_file, out_pick_txt, lf):
    """

    :param ini:
    :param catf:
    :param offset_file:
    :param base_img_id:
    :param base_cat_file:
    :param out_pick_txt:
    :param lf:
    :return:
    """
    nf = len(catf)
    lf.show("{:03d} files".format(nf), logfile.DEBUG)

    # load offset result
    offset = ascii.read(offset_file)

    # base x/y  200118
    # the xy in k-th image is xy - base_offset + k_offset
    x_base = 0 if base_img_id == -1 else offset[base_img_id]["X_Med"]
    y_base = 0 if base_img_id == -1 else offset[base_img_id]["Y_Med"]

    # load control number from ini
    pick_err = ini["pick_err"]
    pick_star = ini["pick_star"]

    # check base file
    base_cat_file = base_cat_file if base_img_id < 0 else catf[base_img_id]
    if not os.path.isfile(base_cat_file):
        raise FileExistsError("Base catalog {} NOT exists".format(base_cat_file))

    # load base catalog
    cat_b = fits.getdata(base_cat_file)
    nx = fits.getval(base_cat_file, "IMNAXIS1")
    ny = fits.getval(base_cat_file, "IMNAXIS2")
    border_cut = ini["border_cut"]
    gix = np.argsort(cat_b["Err"])[:pick_star]
    gix = gix[cat_b[gix]["Err"] < pick_err]
    ng = len(gix)  # number of good stars
    lf.show("List {:4d} stars from base image".format(ng), logfile.DEBUG)
    x_b = cat_b[gix]["X"]
    y_b = cat_b[gix]["Y"]
    m_b = cat_b[gix]["Mag"]
    e_b = cat_b[gix]["Err"]
    mags = np.empty((nf, ng), float) + np.nan
    magc = np.empty((nf, ng), float) + np.nan
    errs = np.empty((nf, ng), float) + np.nan
    if base_img_id > -1:
        mags[base_img_id] = m_b
        magc[base_img_id] = m_b
        errs[base_img_id] = e_b
    cali_cst = np.empty(nf, float)
    cali_std = np.empty(nf, float)

    # load choices one by one, match with 1st, keep matched
    for k in range(nf):
        if k == base_img_id:
            continue
        cat_k = fits.getdata(catf[k])
        x_k = cat_k["X"] + offset[k]["X_Med"] - x_base
        y_k = cat_k["Y"] + offset[k]["Y_Med"] - y_base
        ix_b, ix_k, dd = match(x_b, y_b, None, x_k, y_k, None, ini["cali_dis_limit"], None, multi=True)
        mags[k, ix_b] = cat_k[ix_k]["Mag"]
        errs[k, ix_b] = cat_k[ix_k]["Err"]
        cali_cst[k], cali_std[k] = meanclip(mags[k] - m_b)
        magc[k] = mags[k] - cali_cst[k]
        lf.show("Match {:3d}/{:3d}: N={:4d}->{:4d}  Cali-Const={:+7.3}+-{:6.3f}".format(
            k, nf, len(cat_k), len(ix_k), cali_cst[k], cali_std[k]), logfile.DEBUG)

    pick_var_std = ini["pick_var_std"]
    pick_var_dif = ini["pick_var_dif"]
    pick_var_rad = ini["pick_var_rad"]
    pick_ref_std = ini["pick_ref_std"]
    pick_ref_dif = ini["pick_ref_dif"]
    pick_ref_n   = ini["pick_ref_n"]

    # calc std of all stars, and then find the good enough stars
    magstd = np.nanstd(magc, axis=0)  # std of each star between all images
    magdif = np.nanmax(magc, axis=0) - np.nanmin(magc, axis=0)  # diff between min and max of each star
    magbad = np.sum(np.isnan(magc), axis=0) / nf  # percent of bad (nan) of each star

    # pick variable stars, by mag std, and distance to center
    ix_var = np.where((magstd > pick_var_std) & (magdif > pick_var_dif)
                      & (np.abs(x_b - nx / 2) < nx * pick_var_rad)
                      & (np.abs(y_b - ny / 2) < ny * pick_var_rad)
                      )[0]

    # pick reference stars, by a error limit or a number limit or both
    ix_ref = np.where((magstd < pick_ref_std) & (magdif < pick_ref_dif) & (magbad < 0.1))[0]
    ix_ref = ix_ref[np.argsort(magstd[ix_ref])][:pick_ref_n]

    lf.show("Pick {:3d} ref stars and {:3d} var stars".format(
        len(ix_ref), len(ix_var)), logfile.INFO)

    for i, k in enumerate(ix_var):
        lf.show("  VAR {i:2d}: [{k:3d}] ({x:6.1f} {y:6.1f})  {m:5.2f}+-{e:5.3f}".format(
            i=i, k=k, x=x_b[k], y=y_b[k], m=m_b[k], e=e_b[k], ), logfile.INFO)
    for i, k in enumerate(ix_ref):
        lf.show("  REF {i:2d}: [{k:3d}] ({x:6.1f} {y:6.1f})  {m:5.2f}+-{e:5.3f}".format(
            i=i, k=k, x=x_b[k], y=y_b[k], m=m_b[k], e=e_b[k], ), logfile.INFO)

    xy_ref = [(x_b[k], y_b[k]) for k in ix_ref]
    xy_var = [(x_b[k], y_b[k]) for k in ix_var]

    with open(out_pick_txt, "w") as ff:
        ff.write("{:3}  {:7} {:7}  {:5}  {:7} {:6}  {:3} {:3}\n".format(
            "GNo", "X", "Y", "Mag", "Std", "Dif", "Var", "Ref",
        ))
        for k in range(ng):
            ff.write("{k:3d}  {x:7.2f} {y:7.2f}  {m:5.2f}  {s:7.3f} {d:7.3f}  {v:3s} {r:3s}\n".format(
                k=k, x=x_b[k], y=y_b[k], m=m_b[k], s=magstd[k], d=magdif[k],
                v="var" if k in ix_var else "---",
                r="ref" if k in ix_ref else "---",
            ))
    lf.show("Pick result save to {}".format(out_pick_txt), logfile.INFO)

    return xy_var, xy_ref
