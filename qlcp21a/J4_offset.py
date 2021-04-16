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


def _offset_(ini, basef, catf, base_img_id, base_cat_file, out_offset_file, lf):
    """

    :param ini:
    :param basef:
    :param catf:
    :param base_img_id:
    :param base_cat_file:
    :param out_offset_file:
    :param lf:
    :return:
    """

    nf = len(catf)
    lf.show("{:03d} files".format(nf), logfile.DEBUG)

    # prepare an empty catalog cube
    xy_off = np.zeros((6, nf))
    n_off = np.zeros(nf, dtype=int)
    r_off = np.zeros(nf, dtype=int)
    jd = np.zeros(nf)

    # base catalog
    # cat_base = fits.getdata(catf[base_img_id], 2) 200118
    # 200118 add extra template catalog, can be a catalog not in the list
    base_cat_file = base_cat_file if base_img_id < 0 else catf[base_img_id]
    if not os.path.isfile(base_cat_file):
        raise FileExistsError("Base catalog {} NOT exists".format(base_cat_file))

    cat_base = fits.getdata(base_cat_file)
    # nx = fits.getval(catf[0], "IMNAXIS1")
    # ny = fits.getval(catf[0], "IMNAXIS2")
    nx = fits.getval(base_cat_file, "IMNAXIS1")
    ny = fits.getval(base_cat_file, "IMNAXIS2")
    border_cut = ini["border_cut"]
    # 190609 remove border stars
    x_base = cat_base["X"]  # [ini["se_x"]]
    y_base = cat_base["Y"]  # [ini["se_y"]]
    cat_base = cat_base[
        (border_cut < x_base) & (x_base < nx - border_cut) &
        (border_cut < y_base) & (y_base < ny - border_cut)
    ]

    # goodix = np.where(cat_base[ini["se_err"]] < ini["offset_err_limit"])[0]
    # 190604 use brightest 10 stars
    # goodix = np.argsort(cat_base[ini["se_mag"]])[:ini["offset_count"]]
    goodix = np.argsort(cat_base["Mag"])[:ini["offset_count"]]
    x_base = cat_base[goodix]["X"]    # [ini["se_x"]]
    y_base = cat_base[goodix]["Y"]    # [ini["se_y"]]
    m_base = cat_base[goodix]["Mag"]  # [ini["se_mag"]]

    # tr_base = {}
    # for n_tri_star in range(5, 16):
    #     tri_goodix = np.argsort(m_base)[:n_tri_star]
    #     tr_base[n_tri_star] = make_tri(x_base, y_base, tri_goodix)
    # 200103 fixed count
    tri_goodix = np.argsort(m_base)[:ini["offset_tri_nstar"]]
    tr_base = make_tri(x_base, y_base, tri_goodix)

    lf.show("Load {:03d}/{:03d}: N={:4d}/{:4d} Base Image {}".format(
        base_img_id, nf, len(goodix), len(cat_base), catf[base_img_id]), logfile.DEBUG)

    # load images and process
    for f in range(nf):
        # jd[f] = hdr_dt_jd(fits.getheader(catf[f]), ini) - 2458000.0
        jd[f] = fits.getval(catf[f], "MJD") - 58000
        if f != base_img_id:
            # load n_th catalog
            cat_k = fits.getdata(catf[f])
            # 190609 remove border stars
            x_k = cat_k["X"]  # [ini["se_x"]]
            y_k = cat_k["Y"]  # [ini["se_y"]]
            cat_k = cat_k[
                (border_cut < x_k) & (x_k < nx - border_cut) &
                (border_cut < y_k) & (y_k < ny - border_cut)
                ]
            goodix = np.argsort(cat_k["Mag"])[:ini["offset_count"]]
            # goodix = np.argsort(cat_k[ini["se_mag"]])[:ini["offset_count"]]
            x_k = cat_k[goodix]["X"]    # [ini["se_x"]]
            y_k = cat_k[goodix]["Y"]    # [ini["se_y"]]
            m_k = cat_k[goodix]["Mag"]  # [ini["se_mag"]]
            lf.show("Load {:3d}/{:3d}: N={:4d}/{:4d} {}".format(
                f, nf, len(goodix), len(cat_k), catf[f]), logfile.DEBUG)

            for n_tri_star in range(5, 16):
                tri_goodix = np.argsort(m_k)[:n_tri_star]
                tr_k = make_tri(x_k, y_k, tri_goodix)

                # ix_b, ix_k = match_triangle(tr_base, tr_k, ini["offset_tri_matcherr"])

                # 开始匹配三角形
                mix_b, mix_k, dis = match(
                    tr_base["fac1"], tr_base["fac2"], None,
                    tr_k["fac1"], tr_k["fac2"], None,
                    dis_limit=ini["offset_tri_matcherr"])
                lf.show("{} Triangles matched with {} stars".format(len(mix_b), n_tri_star), logfile.DEBUG)

                # 根据匹配到的三角形，找出他们的三个顶点的序列，这是真正的匹配到的点
                pp1 = np.concatenate((tr_base[mix_b]["p0"], tr_base[mix_b]["p1"], tr_base[mix_b]["p2"]))
                pp2 = np.concatenate((tr_k[mix_k]["p0"], tr_k[mix_k]["p1"], tr_k[mix_k]["p2"]))

                # 去重。根据第一个序列找到每个重复点的第一次出现，纪录下标
                ix_b, ix_k = argunique(pp1, pp2)

                dx = x_base[ix_b] - x_k[ix_k]
                dy = y_base[ix_b] - y_k[ix_k]
                dm = m_base[ix_b] - m_k[ix_k]
                dr = np.sqrt(dx * dx + dy * dy)
                dxm, dxs = meanclip(dx, func=np.mean)
                dym, dys = meanclip(dy, func=np.mean)
                dmm, dms = meanclip(dm)
                drm, drs = meanclip(dr)
                n = len(ix_b)

                r = 0
                lf.show("  K={:1d} N={:4d} X={:7.3f}+-{:7s} Y={:7.3f}+-{:7s} R={:7.3f}+-{:7s} Mag={:7.3f}+-{:7s}".format(
                    r, n, dxm, "", dym, "", drm, "", dmm, ""), logfile.DEBUG)

                lim = ini["offset_max"]
                for r in (1,2):
                    ix_b, ix_k, dis = match(x_base, y_base, m_base, x_k + dxm, y_k + dym, m_k, lim)
                    dx = x_base[ix_b] - x_k[ix_k]
                    dy = y_base[ix_b] - y_k[ix_k]
                    dm = m_base[ix_b] - m_k[ix_k]
                    dr = np.sqrt(dx * dx + dy * dy)
                    dxm, dxs = meanclip(dx, func=np.mean)
                    dym, dys = meanclip(dy, func=np.mean)
                    dmm, dms = meanclip(dm)
                    drm, drs = meanclip(dr)
                    n = len(ix_b)
                    lim = drs * ini["offset_factor"]
                    lf.show("  K={:1d} N={:4d} X={:7.3f}+-{:7.4f} Y={:7.3f}+-{:7.4f} "
                            "R={:7.3f}+-{:7.4f} Mag={:7.3f}+-{:7.4f}".format(
                        r, n, dxm, dxs, dym, dys, drm, drs, dmm, dms), logfile.DEBUG)

                if n >= 3 and not np.isnan(drs) and drs < 5.0:
                    break # success in offset
            # end of n_tri_star


            xy_off[:, f] = dxm, dxs, dym, dys, dmm, dms
            n_off[f] = n
            r_off[f] = r

    with open(out_offset_file, "w") as ff:
        ff.write("{:3} {:20} {:4} {:2} {:8} {:7}  {:8} {:7}  {:7} {:7}  {:10}\n".format(
            "No", "Filename", "Cnt", "It", "X_Med", "X_Std", "Y_Med", "Y_Std", "Mag_Med", "Mag_Std", "MJD"
        ))
        for f in range(nf):
            ff.write("{:3d} {:20s} {:4d} {:2d} {:+8.3f} {:7.4f}  {:+8.3f} {:7.4f}  {:+7.3f} {:7.4f}  {:10.6f}\n".format(
                f, basef[f], n_off[f], r_off[f],
                xy_off[0, f], xy_off[1, f],
                xy_off[2, f], xy_off[3, f],
                xy_off[4, f], xy_off[5, f],
                jd[f],
            ))
    lf.show("Report save to {}".format(out_offset_file), logfile.INFO)
