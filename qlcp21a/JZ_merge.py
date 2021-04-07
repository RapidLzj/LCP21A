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


def merge(
        cat_fits_lst=None,
        cat_table_txt_lst=None,
        cat_list_txt_lst=None,
        out_cat_fits=None,
        out_cat_table_txt=None,
        out_cat_list_txt=None,
    ):
    """
    Merge catalogs with same structure
    In this program, star id and file id will be handled, and the fits catalog will be processed
    A simple tool, so no log and ini be used
    210129: I do not remember why and where to use this??
    :param cat_fits_lst:
    :param cat_table_txt_lst:
    :param cat_list_txt_lst:
    :param out_cat_fits:
    :param out_cat_table_txt:
    :param out_cat_list_txt:
    :return:
    """

    # merge fits catalog
    if cat_fits_lst:
        cat_lst = []
        for f in cat_fits_lst:
            if not os.path.isfile(f):
                print("Catalog file NOT found: {}".format(f))
            else:
                cat1 = fits.getdata(f)
                if cat_lst and cat_lst[0].dtype != cat1.dtype:
                    print("Catalog columns NOT match: {}".format(f))
                else:
                    cat_lst.append(cat1)
        final_cat = np.hstack(cat_lst)
        final_hdul = fits.HDUList([
            fits.PrimaryHDU(),
            fits.BinTableHDU(data=final_cat)
        ])
        final_hdul.writeto(out_cat_fits)

    # merge table txt
    if cat_table_txt_lst:
        cat_lst = []
        cat_stru = ""
        for f in cat_table_txt_lst:
            if not os.path.isfile(f):
                print("Catalog file NOT found: {}".format(f))
            else:
                cat1 = open(f).readlines()
                cat_lst.extend(cat1[1:])
                cat_stru = cat1[0]
        with open(out_cat_table_txt, "w") as ff:
            ff.write(cat_stru)
            for f in cat_lst:
                ff.write(f)

    # merge list txt
    if cat_list_txt_lst:
        cat_lst = []
        cat_stru = ""
        for f in cat_list_txt_lst:
            if not os.path.isfile(f):
                print("Catalog file NOT found: {}".format(f))
            else:
                cat1 = open(f).readlines()
                cat_lst.extend(cat1[1:])
                cat_stru = cat1[0]
        with open(out_cat_list_txt, "w") as ff:
            ff.write(cat_stru)
            for f in cat_lst:
                ff.write(f)
