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


def _se_(ini, scif, sef, catf, skiptag, lf):
    """
    Photometric working, this function is calling Source-Extractor,
    but other implementation can call pure python solution
    :param ini:
    :param scif:
    :param sef:
    :param catf:
    :param skiptag:
    :param lf:
    :return:
    """

    nf = len(scif)
    lf.show("{:03d} files".format(nf), logfile.DEBUG)

    # choose default sex config from working dir or program dir
    if os.path.isfile("default.sex"):
        def_sex = "default.sex"
    else:
        def_sex = os.path.split(__file__)[0] + "/default.sex"
    def_par = os.path.split(__file__)[0] + "/default.param"

    se_cmd_fmt1 = "{se} -c {st} -parameters_name {par} {{img}} -CATALOG_NAME {{se}}".format(
        se=ini["se_cmd"], st=def_sex, par=def_par)
    # se_cmd_fmt1 = ini["se_cmd"] + " -c " + def_sex + " -parameters_name " + def_par + " {img} -CATALOG_NAME {cat}"

    # load images and process
    for f in range(nf):
        if skiptag[f]:
            lf.show("SKIP: \"" + catf[f] + "\"" )
            continue
        lf.show("SE on {:03d}/{:03d}: {:40s}".format(f + 1, nf, scif[f]), logfile.DEBUG)

        # first, use auto
        se_cmd = se_cmd_fmt1.format(img=scif[f], se=sef[f])
        # following execution canceled, because real aperture is not so nice
        lf.show("    " + se_cmd, logfile.DEBUG)
        os.system(se_cmd)

        # 210329 generate the new catalog with LCP format from SE output
        secat = fits.getdata(sef[f], 2)
        ns = len(secat)
        mycat = np.empty(ns, [
            ("Num",   np.uint16 ),
            ("X",     np.float64),
            ("Y",     np.float64),
            ("Elong", np.float32),
            ("FWHM",  np.float32),
            ("Mag",   np.float32),
            ("Err",   np.float32),
            ("Flags", np.uint16 ),
            ("Alpha", np.float64),
            ("Delta", np.float64),
        ])
        mycat["Num"  ] = secat["NUMBER"]
        mycat["X"    ] = secat[ini["se_x"]]
        mycat["Y"    ] = secat[ini["se_y"]]
        mycat["Elong"] = secat[ini["elong"]]
        mycat["FWHM" ] = secat[ini["fwhm"]]
        mycat["Mag"  ] = secat[ini["se_mag"]]
        mycat["Err"  ] = secat[ini["se_err"]]
        mycat["Flags"] = secat["FLAGS"]
        mycat["Alpha"] = secat[ini["se_ra"]]
        mycat["Delta"] = secat[ini["se_de"]]

        hdr = fits.getheader(scif[f])
        hdr["IMNAXIS1"] = hdr["NAXIS1"]
        hdr["IMNAXIS2"] = hdr["NAXIS2"]

        pri_hdu = fits.PrimaryHDU(header=hdr)
        tb_hdu = fits.BinTableHDU(data=mycat)
        new_fits = fits.HDUList([pri_hdu, tb_hdu])
        new_fits.writeto(catf[f], overwrite=True)
        lf.show("SE result transfer to {}".format(catf[f]), logfile.DEBUG)

    lf.show("Photometry on {} of {} files".format(nf - sum(skiptag), nf), logfile.INFO)