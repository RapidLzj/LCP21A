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
from astropy import time, coordinates as coord, units as u
from .JZ_utils import loadlist, datestr, logfile, conf, meanclip, basefilename, unmatched, subset, sex2dec
from .JZ_cata import match
from .JZ_plotting import plot_im_obj


def _catalog_(ini, scif, catf, offset_file, starxy,
              # obj_coord,
              base_img_id, base_fits_file,
              out_cat_fits, out_cat_table_txt, out_cat_list_txt, out_finding_img, noplot, lf):

    # 210415, move to imgproc
    # observatoey and object info, this is used in transfer JD to HJD
    # site = coord.EarthLocation(lat=ini["site_lat"] * u.deg, lon=ini["site_lon"] * u.deg, height=ini["site_ele"] * u.m)
    # ct_ra = sex2dec(obj_coord[0], 15.0) if obj_coord else None
    # ct_dec = sex2dec(obj_coord[1]) if obj_coord else None
    # if obj_coord:
    #     obj = coord.SkyCoord(ct_ra, ct_dec, unit=(u.deg, u.deg), frame="icrs")
    # else:
    #     # if none, no jd-bjd transfer
    #     obj = None

    nf = len(catf)
    lf.show("{:03d} files".format(nf), logfile.DEBUG)
    # star x, y, and number
    ns = len(starxy)
    if type(starxy) is not np.ndarray:
        starxy = np.array(starxy)
    starx = starxy[:, 0]
    stary = starxy[:, 1]

    # load offset result
    offset = ascii.read(offset_file)

    # base x/y  200118
    # the xy in k-th image is xy - base_offset + k_offset
    # if an extra base image is used, this must be the same as offset base
    x_base = 0 if base_img_id == -1 else offset[base_img_id]["X_Med"]
    y_base = 0 if base_img_id == -1 else offset[base_img_id]["Y_Med"]

    # the array of the image info
    band = np.empty(nf, (str, 10))
    expt = np.empty(nf, float)
    obs_dt = np.empty(nf, (str, 22))
    obs_jd = np.empty(nf, float)  # from header
    # obs_jd = np.empty(nf, object)  # type=time.Time
    obs_bjd = np.zeros(nf, float)  # from header // transfer result
    obs_hjd = np.zeros(nf, float)  # from header

    # array of stars
    all_id   = np.zeros((nf, ns), int) -1
    all_x    = np.zeros((nf, ns), float) -1.0
    all_y    = np.zeros((nf, ns), float) -1.0
    all_mag  = np.zeros((nf, ns), float) -1.0
    all_err  = np.zeros((nf, ns), float) -1.0
    all_elon = np.zeros((nf, ns), float) -1.0
    all_fwhm = np.zeros((nf, ns), float) -1.0

    # load stars from images into the array, by matching x,y
    for k in range(nf):
        hdr = fits.getheader(catf[k])
        d_str = hdr[ini["date_key"]][ini["date_start"]:ini["date_end"]]
        t_str = hdr[ini["time_key"]][ini["time_start"]:ini["time_end"]]
        obs_dt[k] = d_str + "T" + t_str
        band[k] = hdr["FILTER"]
        expt[k] = hdr["EXPTIME"]
        # t = obs_jd[k] = time.Time(obs_dt[k], format='isot', scale='utc', location=site)
        # if obj is not None:
        #     ltt_bary = t.light_travel_time(obj)
        #     obs_bjd[k] = (t.tdb + ltt_bary).jd
        obs_jd[k] = hdr["JD"]
        obs_bjd[k] = hdr["BJD"]
        obs_hjd[k] = hdr["HJD"]

        cat_k = fits.getdata(catf[k])
        x_k = cat_k["X"] + offset[k]["X_Med"] - x_base
        y_k = cat_k["Y"] + offset[k]["Y_Med"] - y_base
        ix_s, ix_k, dd = match(starx, stary, None, x_k, y_k, None, ini["cali_dis_limit"], None, multi=True)
        all_id[k, ix_s] = ix_k
        all_x   [k, ix_s] = cat_k[ix_k]["X"]      # [ini["se_x"]]
        all_y   [k, ix_s] = cat_k[ix_k]["Y"]      # [ini["se_y"]]
        all_mag [k, ix_s] = cat_k[ix_k]["Mag"]    # [ini["se_mag"]]
        all_err [k, ix_s] = cat_k[ix_k]["Err"]    # [ini["se_err"]]
        all_fwhm[k, ix_s] = cat_k[ix_k]["FWHM"]   # [ini["fwhm"]]
        all_elon[k, ix_s] = cat_k[ix_k]["Elong"]  # [ini["elong"]]
        lf.show("Add {:3d}/{:3d}: N={:4d}->{:4d} {}".format(
            k, nf, len(cat_k), len(ix_k), catf[k]), logfile.DEBUG)

    # the final catalog structure
    cat_final = np.empty(nf, [
        ("File",  offset["Filename"].dtype),
        ("Band",  (str, 10),),
        ("Expt",  np.float32,),
        ("DT",    (str, 22),),
        ("JD",    np.float64),
        ("BJD",   np.float64),
        ("HJD",   np.float64),
        ("X",     np.float64, (ns,)),
        ("Y",     np.float64, (ns,)),
        ("Mag",   np.float32, (ns,)),
        ("Err",   np.float32, (ns,)),
        ("FWHM",  np.float32, (ns,)),
        ("Elong", np.float32, (ns,)),
        ("Idx",   int, (ns,)),
    ])

    cat_final["File"]  = offset["Filename"]
    cat_final["Band"]  = band
    cat_final["Expt"]  = expt
    cat_final["DT"]    = obs_dt
    cat_final["JD"]    = obs_jd
    cat_final["BJD"]   = obs_bjd
    cat_final["HJD"]   = obs_hjd
    cat_final["Mag"]   = all_mag
    cat_final["Err"]   = all_err
    cat_final["X"]     = all_x
    cat_final["Y"]     = all_y
    cat_final["FWHM"]  = all_fwhm
    cat_final["Elong"] = all_elon
    cat_final["Idx"]   = all_id

    pri_hdu = fits.PrimaryHDU()
    tb_hdu = fits.BinTableHDU(data=cat_final)
    new_fits = fits.HDUList([pri_hdu, tb_hdu])
    new_fits.writeto(out_cat_fits, overwrite=True)
    lf.show("Result save to {}".format(out_cat_fits), logfile.INFO)

    with open(out_cat_table_txt, "w") as ff:
        ff.write("File Band ExpTime DT JD BJD  ")
        for k in range(ns):
            ff.write("  ID{k:02d} X{k:02d} Y{k:02d}  Mag{k:02d} Err{k:02d}".format(k=k))
        ff.write("\n")

        for s in cat_final:
            ff.write("{f}  {s[Band]:5s}  {s[Expt]:5.1f}  {s[DT]:22s}  {s[JD]:15.7f}  {s[BJD]:15.7f}".format(
                f=basefilename(s["File"]), s=s))
            for k in range(ns):
                ff.write("   {i:4d}  {x:6.1f} {y:6.1f}   {mag:7.4f} {err:6.4f}".format(
                    i=s["Idx"][k], x=s["X"][k], y=s["Y"][k],
                    #ra=s["Alpha"][k], dec=s["Delta"][k],
                    mag=s["Mag"][k], err=s["Err"][k],
                ))
            ff.write("\n")
    lf.show("Result save to {}".format(out_cat_table_txt), logfile.INFO)

    with open(out_cat_list_txt, "w") as ff:
        ff.write("DT  Mag  ExpTime Band  File  BJD  Err  No  FWHM Elongation  JD  ID  X Y\n")
        for s in cat_final:
            for k in range(ns):
                ff.write("{dt:22s} {mag:7.4f} {t:5.1f} {b:5s} {f} {bjd:15.7f} {err:6.4f} {k:2d} {fwhm:5.2f} {elong:5.3f} {jd:15.7f} "
                         "{i:4d} {x:6.1f} {y:6.1f}\n".format(
                    f=basefilename(s["File"]),
                    b=s["Band"], t=s["Expt"],
                    dt=s["DT"], jd=s["JD"], bjd=s["BJD"], k=k+1,
                    i=s["Idx"][k],
                    x=s["X"][k], y=s["Y"][k],
                    # ra=s["Alpha"][k], dec=s["Delta"][k],
                    fwhm=s["FWHM"][k], elong=s["Elong"][k],
                    mag=s["Mag"][k], err=s["Err"][k],
                ))
    lf.show("Result save to {}".format(out_cat_list_txt), logfile.INFO)

    # 200103 恢复，画证认图
    # img = fits.getdata(scif[base_img_id])  200118
    base_fits_file = base_fits_file if base_img_id < 0 else scif[base_img_id]
    if os.path.isfile(base_fits_file):
        img = fits.getdata(base_fits_file)
        imtitle = os.path.basename(base_fits_file)
        plot_im_obj(ini, img, starx, stary, imtitle, out_finding_img, noplot=noplot)
        lf.show("Finding Chart save to {}".format(out_finding_img), logfile.INFO)
    else:
        lf.show("Finding Chart NOT plotted due to missing {}".format(base_fits_file), logfile.INFO)
