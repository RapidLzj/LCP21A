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


def _cali_(ini, cat_fits, tgt_id, ref_id, chk_id, out_cali_fits, out_cali_txt, lf):
    """

    :param ini:
    :param cat_fits:
    :param tgt_id:
    :param ref_id:
    :param chk_id:
    :param out_cali_fits:
    :param out_cali_txt:
    :param lf:
    :return:
    """

    # load catalog and get n_files and n_object
    cat = fits.getdata(cat_fits, 1)
    mags = cat["Mag"]
    errs = cat["Err"]
    nf, n_obj = mags.shape
    mags[mags < 0] = np.nan

    # if reference is not provided, use all stars except [0]
    if ref_id is None:
        ref_id = [i for i in range(n_obj) if i != tgt_id]
    n_ref = len(ref_id)
    # same for checkers
    if chk_id is None:
        chk_id = [i for i in range(n_obj) if i != tgt_id]
    n_chk = len(chk_id)

    # extract mags and BJD
    tgt_mag = mags[:, tgt_id]
    ref_mag = mags[:, ref_id]
    chk_mag = mags[:, chk_id]
    tgt_err = errs[:, tgt_id]
    ref_err = errs[:, ref_id]
    chk_err = errs[:, chk_id]

    # calibration reference mean
    ref_mag_m = np.mean(ref_mag, axis=1)
    # calibration
    tgt_mag_cali = tgt_mag - ref_mag_m
    chk_mag_cali = np.empty_like(chk_mag)
    for i in range(n_chk):
        chk_mag_cali[:, i] = chk_mag[:, i] - ref_mag_m
    # normalize to 0
    tgt_mag_cali -= np.nanmedian(tgt_mag_cali)
    for i in range(n_chk):
        chk_mag_cali[:, i] -= np.nanmedian(chk_mag_cali[:, i])

    # the final catalog structure
    cat_final = np.empty(nf, [
        ("File",  cat["File"].dtype),
        ("DT",    (str, 22),),
        ("JD",    np.float64),
        ("BJD",   np.float64),
        ("CaliCst", np.float32,),
        ("MagTgt",  np.float32,),
        ("CaliTgt", np.float32,),
        ("ErrTgt",  np.float32,),
        ("MagRef",  np.float32, (n_ref,)),
        ("ErrRef",  np.float32, (n_ref,)),
        ("MagChk",  np.float32, (n_chk,)),
        ("CaliChk", np.float32, (n_chk,)),
        ("ErrChk",  np.float32, (n_chk,)),
    ])

    cat_final["File"] = cat["File"]
    cat_final["DT"  ] = cat["DT"]
    cat_final["JD"  ] = cat["JD"]
    cat_final["BJD" ] = cat["BJD"]
    cat_final["CaliCst"] = ref_mag_m
    cat_final["MagTgt" ] = tgt_mag
    cat_final["CaliTgt"] = tgt_mag_cali
    cat_final["ErrTgt" ] = tgt_err
    cat_final["MagRef" ] = ref_mag
    cat_final["ErrRef" ] = ref_err
    cat_final["MagChk" ] = chk_mag
    cat_final["CaliChk"] = chk_mag_cali
    cat_final["ErrChk" ] = chk_err

    pri_hdu = fits.PrimaryHDU()
    tb_hdu = fits.BinTableHDU(data=cat_final)
    new_fits = fits.HDUList([pri_hdu, tb_hdu])
    new_fits.writeto(out_cali_fits, overwrite=True)
    lf.show("Result save to {}".format(out_cali_fits), logfile.INFO)

    with open(out_cali_txt, "w") as ff:
        ff.write("File DT JD BJD  CaliCst MagTgt  CaliTgt  ErrTgt")
        for k in range(n_ref):
            ff.write("  MagRef{k:02d} ErrRef{k:02d}".format(k=k+1))
        for k in range(n_chk):
            ff.write("  MagChk{k:02d} CaliChk{k:02d} ErrChk{k:02d}".format(k=k+1))
        ff.write("\n")

        for s in cat_final:
            ff.write("{s[File]}  {s[DT]:22s}  {s[JD]:15.7f}  {s[BJD]:15.7f}  {s[CaliCst]:6.3f}  "
                     "{s[MagTgt]:6.3f}  {s[CaliTgt]:6.3f}  {s[ErrTgt]:6.3f}".format(s=s))
            for k in range(n_ref):
                ff.write("   {m:6.3f}  {e:6.3f}".format(
                    m=s["MagRef"][k], e=s["ErrRef"][k],
                ))
            for k in range(n_chk):
                ff.write("   {m:6.3f} {c:6.3f} {e:6.3f}".format(
                    m=s["MagChk"][k], c=s["CaliChk"][k], e=s["ErrChk"][k],
                ))
            ff.write("\n")
    lf.show("Result save to {}".format(out_cali_txt), logfile.INFO)
