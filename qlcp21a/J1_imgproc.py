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
from .JZ_utils import loadlist, datestr, logfile, conf, sex2dec, lst, hourangle, azalt, airmass, ra2hms, dec2dms, hdr_dt_jd
from astropy import time, coordinates as coord, units as u


def _imgproc_(ini, rawf, bias_fits, flat_fits, scif, obj_coord, skiptag, extra_hdr, lf):
    """

    :param ini:
    :param rawf:
    :param bias_fits:
    :param flat_fits:
    :param scif:
    :param obj_coord:
    :param skiptag:
    :param extra_hdr:
    :param lf:
    :return:
    """

    nf = len(rawf)

    lf.show("{:03d} files".format(nf), logfile.DEBUG)

    # load bias and flat
    lf.show("Loading Bias: {}".format(bias_fits), logfile.DEBUG)
    data_bias = fits.getdata(bias_fits)
    lf.show("Loading Flat: {}".format(flat_fits), logfile.DEBUG)
    data_flat = fits.getdata(flat_fits)

    # load header from extra header file or dict, if exists
    hdr_ex = {}
    if extra_hdr:
        if type(extra_hdr) is str:
            extra_hdr = (extra_hdr, )
        for f in extra_hdr:
            hdr_ex.update(conf(f, no_default=True).to_header())
    elif type(extra_hdr) is dict:
        hdr_ex.update(extra_hdr)

    # 标出复制字段，即该字段的值来自另外一个原先已有的字段
    hdr_mark = {}
    for k in hdr_ex:
        v = hdr_ex[k]
        if type(v) in (list, tuple):
            v = v[0]
        if type(v) is str and v.startswith("$"):
            hdr_mark[k] = v[1:]

    # observatory info, this is used in transfer JD to HJD
    site = coord.EarthLocation(lat=ini["site_lat"] * u.deg, lon=ini["site_lon"] * u.deg, height=ini["site_ele"] * u.m)
    # object
    hdr = fits.getheader(rawf[0])
    obj_ra = obj_coord[0] if obj_coord else hdr.get(ini["hdr_obj_ra"], "00:00:00")
    obj_dec = obj_coord[1] if obj_coord else hdr.get(ini["hdr_obj_dec"], "+00:00:00")
    obj = coord.SkyCoord(obj_ra, obj_dec, unit=(u.hour, u.deg), frame="icrs")

    # load images and process
    for f in range(nf):
        if not os.path.isdir(os.path.dirname(scif[f])):
            os.mkdir(os.path.dirname(scif[f]))
        if skiptag[f]:
            lf.show("SKIP    {:03d}/{:03d}: {:40s}".format(f + 1, nf, scif[f]), logfile.DEBUG)
            continue
        lf.show("Loading {:03d}/{:03d}: {:40s}".format(f + 1, nf, rawf[f]), logfile.DEBUG)

        # process data
        dat = (fits.getdata(rawf[f]) - data_bias) / data_flat

        # load and handle header
        hdr = fits.getheader(rawf[f])
        d_str = hdr[ini["date_key"]][ini["date_start"]:ini["date_end"]]
        t_str = hdr[ini["time_key"]][ini["time_start"]:ini["time_end"]]
        if d_str[2] == "/" and d_str[5] == "/":
            d_str = "20" + d_str[6:8] + "-" + d_str[3:5] + "-" + d_str[0:2]
        obs_dt = d_str + "T" + t_str
        obs_jd = time.Time(obs_dt, format='isot', scale='utc', location=site)
        # obs_dt, obs_jd = hdr_dt_jd(hdr, ini)
        obs_mjd = obs_jd.mjd
        ltt_bary = obs_jd.light_travel_time(obj)
        obs_bjd = (obs_jd.tdb + ltt_bary).jd
        obs_lst = coord.Angle(lst(obs_mjd, site.lon.deg), u.hour)
        obs_ha = obs_lst - obj.ra
        obs_az, obs_alt = azalt(site.lat.deg, obs_lst.hour, obj.ra.deg, obj.dec.deg)
        obs_am = airmass(site.lat.deg, obs_lst.hour, obj.ra.deg, obj.dec.deg)

        # add ra, dec, lst, jd, mjd, bjd, hjd, az, alt,
        hdr.update({
            "RA": ra2hms(obj.ra),
            "DEC": dec2dms(obj.dec),
            "LST": ra2hms(obs_lst),
            "HA": ra2hms(obs_ha),
            "JD": obs_jd.jd,
            "MJD": obs_mjd,
            "BJD": obs_bjd,
            "HJD": 0.0,
            "AZ": obs_az,
            "ALT": obs_alt,
            "AIRMASS": obs_am,
            "SITEELEV": site.height.value,
            "SITELAT": site.lat.deg,
            "SITELONG": site.lon.deg,
        })

        # add process time to header
        hdr.update(BZERO=0)
        hdr.append(('PROCTIME', datestr()))
        s = hdr.tostring()  # force check the header

        # copy marked fields from original header
        # 190619 重新启用
        hdr_ex2 = hdr_ex.copy()
        for k in hdr_mark:
            hdr_ex2.update({k:hdr.get(k, "")})
        # add extra fields to header
        hdr.update(hdr_ex2)

        # save new fits
        new_hdu = fits.PrimaryHDU(header=hdr, data=dat)
        new_fits = fits.HDUList([new_hdu])
        new_fits.writeto(scif[f], overwrite=True)
        lf.show("Writing {:03d}/{:03d}: {:40s}".format(f + 1, nf, scif[f]), logfile.DEBUG)

    lf.show("{} of {} files corrected".format(nf-sum(skiptag), nf), logfile.INFO)