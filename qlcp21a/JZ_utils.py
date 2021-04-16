# -*- coding: utf-8 -*-
"""
    201901, Dr. Jie Zheng, Beijing & Xinglong, NAOC
    202101-? Dr. Jie Zheng & Dr./Prof. Linqiao Jiang
    Light_Curve_Pipeline
    v3 (2021A) Upgrade from former version, remove unused code
"""


import numpy as np
from scipy import stats as st
import time
import os
from astropy.time import Time


def loadlist(listfile, base_path="", suffix="", separate_folder=False):
    """
    Load file list from list file, add base path and suffix to each filename
    :param listfile:
    :param base_path: add base path to filenames in list
    :param suffix: if filename not ends with fits/fit/gz, then .fits will be append
    :param separate_folder: make a separate folder for each file
    :return: a list of filename
    """

    def get_ext(f):
        # a inner function gto split base name and ext
        # if the last ext is gz, then the former section is also part of the ext
        # 4x: xx.fits.gz xx.tar.gz
        sp = os.path.splitext(f)
        base = sp[0]
        ext = sp[1]
        if ext == ".gz":
            spsp = os.path.splitext(base)
            ext = spsp[1] + ext
            base = spsp[0]
        return os.path.basename(base), ext

    lstname = os.path.basename(os.path.splitext(listfile)[0])
    lst = open(listfile, "r").readlines()
    lst = [f.strip() for f in lst]
    nlst = len(lst)

    # a special mark for list of list
    if len(lst[0].split()) > 1:
        return loadlistlist(listfile, base_path, suffix, separate_folder)

    if suffix is not None and suffix != "" and not suffix.startswith("."):
        suffix = "." + suffix

    ori_path = [os.path.dirname(f) + "/" for f in lst]  # with ending /
    base_name = [get_ext(f)[0] for f in lst]  # pure name
    ori_ext = [get_ext(f)[1] for f in lst]  # ext with .

    # new suffix if provided
    if suffix is None or suffix.strip() == "":
        new_ext = ori_ext.copy()
    elif suffix in ('.fit', '.fits', '.fit.gz', '.fits.gz', ):
        # if new and ori suffix are both aliases of fits, keep original
        # different to last version, middle-fix is now a part of new suffix
        new_ext = [f if f in ('.fit', '.fits', '.fit.gz', '.fits.gz', ) else suffix for f in ori_ext]
    else:
        new_ext = [suffix] * len(ori_ext)

    if base_path is not None and base_path != "":
        new_path = [base_path] * nlst
    else:
        new_path = ori_path.copy()

    if separate_folder:
        # 210404 use new style folder, with lst name but not base filename
        # new_lst = [p + f + "/" + f + e for p, f, e in zip(new_path, base_name, new_ext)]
        new_lst = [p + lstname + "/" + f + e for p, f, e in zip(new_path, base_name, new_ext)]
    else:
        new_lst = [p + f + e for p, f, e in zip(new_path, base_name, new_ext)]

    return np.array(new_lst)


def loadlistlist(
        listlistfile,
        base_path="",
        suffix="",
        separate_folder=False):
    """
    191106 add
    Load list of lists of files
    :param listlistfile:
    :param base_path:
    :param suffix:
    :param separate_folder:
    :return:
    """
    # load lists and then split each line into base path, new path, and list name
    lstlst = open(listlistfile, "r").readlines()
    lstlst = [f.strip().split() for f in lstlst]

    # load each list
    all_lst = []
    for f in lstlst:
        lst_one = loadlist(
            listfile=f[1],
            suffix=suffix,
            base_path=base_path + f[0],
            separate_folder=separate_folder)
        all_lst.extend(lst_one)

    return np.array(all_lst)


def datestr():
    """
    Generate a string of current time
    :return:
    """
    return time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime())


class logfile(object):
    """
    Log file generator
    """

    # log level
    DEBUG = 10
    INFO = 20
    WARNING = 30
    ERROR = 90

    LEVEL_CODE={DEBUG:">", INFO:"|", WARNING:"!", ERROR:"X"}
    LEVEL_STR = {"DEBUG":DEBUG, "INFO":INFO, "WARNING":WARNING, "ERROR":ERROR}

    def __init__(self,
                 filename=None,
                 filemode="w",
                 filefmt="{time} {level} {message}",
                 scrfmt="{message}",
                 level=INFO):
        """
        Create a log object
        :param filename:
        :param filemode:
        :param filefmt:
        :param scrfmt:
        :param level:
        """
        self.filefmt = filefmt + "\n"
        self.scrfmt = scrfmt
        # 210404 检查是否存在目录，不存在则创建
        if filename:
            os.makedirs(os.path.dirname(filename), exist_ok=True)
        self._file_ = (None if filename is None or filename == "" else
                   open(filename, filemode))
        if type(level) in (int, float):
            self.level = level
        elif type(level) is str:
            self.level = self.LEVEL_STR[level.upper()]
        else:
            self.level = self.INFO

    def show(self, message, level=INFO):
        """
        Show message
        :param message:
        :param level:
        :return:
        """
        if level >= self.level:
            print(self.scrfmt.format(
                time=datestr(), level=self.LEVEL_CODE[level], message=message))
        if self._file_ is not None:
            self._file_.write(self.filefmt.format(
                time=datestr(), level=self.LEVEL_CODE[level], message=message))

    def close(self):
        if self._file_:
            self._file_.close()
            self._file_ = None

    def __del__(self):
        if self:
            self.close()


class conf(object):
    """
    Configuration file loader
    """

    def __init__(self, ini_filenames, ext_conf=None, no_default=False):
        """
        Load ini file
        :param ini_filenames: 配置文件名，字符串或者列表、元组
        :param ext_conf: 额外的配置，在加载文件之后额外补充
        :param no_default: 是否允许默认值文件，对于用来读fits头，是没有默认值的
        """
        self.data = {}
        self.comment = {}
        # 190619 允许设置多个配置文件，如果只给一个名字，那么自动升级为元组
        if type(ini_filenames) is str:
            ini_filenames = [ini_filenames, ]

        # 不论其他配置如何，必须先读default.ini，确保每个字段有默认值
        if not no_default and "default.ini" not in ini_filenames:
            ini_filenames.insert(0, "default.ini")
            # 200103 新增读程序所在路径的default.ini
            def_ini_0 = os.path.split(__file__)[0] + "/default.ini"
            ini_filenames.insert(0, def_ini_0)

        self.load(ini_filenames, ext_conf)

    @staticmethod
    def _check_type_(v):
        """
        transfer v to int, float, or bool if possible
        :param v:
        :return:
        """
        try:
            a = int(v)
        except ValueError:
            try:
                a = float(v)
            except ValueError:
                if v.upper() in ("T", "TRUE", "Y", "YES"):
                    a = True
                elif v.upper() in ("F", "FALSE", "N", "NO"):
                    a = False
                else:
                    a = v
        return a

    def load(self, ini_filenames, ext_conf):
        """
        Real loading operation
        :param ini_filenames:
        :param ext_conf:
        :return:
        """
        for fn in ini_filenames:
            # lines = open(ini_filename, "r").readlines()
            # 先检查文件名是否存在，不存在就跳过去
            if not os.path.isfile(fn):
                continue
            # print("Loading INI: {}".format(fn))
            lines = open(fn, "r").readlines()
            for l in lines:
                p1 = l.find("#")
                # 200102改，增加整行都是注释的处理
                line_ok = l[:p1].strip() if p1 > -1 else l.strip()
                c = l[p1+1:]
                p0 = line_ok.find("=")
                if p0 > 0:
                    k = line_ok[:p0].strip()
                    v = eval(line_ok[p0+1:])
                    self.data[k] = v
                    self.comment[k] = c

        # 190619 如果有额外覆盖，那么就更新，没有就算了
        if ext_conf is not None:
            self.data.update(ext_conf)

    def __getitem__(self, item, default_value=None):
        """
        enable visit conf by conf["prop"]
        :param item: item name
        :param default_value: default value if item is not exists
        :return:
        """
        return self.data.get(item, default_value)

    def to_header(self):
        hdr = {k:(v, self.comment.get(k, "")) for k, v in self.data.items()}
        return hdr


def meanclip(dat, nsigma=3.0, func=np.median):
    """
    Compute clipped median and sigma of dat
    :param dat: data, can be list, tuple or np array, 1-d or n-d,
                but if use checking, n-d array will be flattened
    :param nsigma: how many sigma used in clipping
    :param func: method used to evaluate the median/mean
    :return:
    """
    if len(dat) == 0:
        m, s = np.nan, np.nan
        ix = []
    elif len(dat) == 1:
        m, s = dat[0], np.nan
        ix = [0]
    else:
        dat1 = dat.flatten()
        dat1 = dat1[np.isfinite(dat1)]
        c, l, u = st.sigmaclip(dat1, nsigma, nsigma)
        m = func(c)
        s = np.std(c)
    return m, s


def hdr_dt_jd(hdr, ini):
    d_str = hdr[ini["date_key"]][ini["date_start"]:ini["date_end"]]
    if d_str[2] == "/" and d_str[5] == "/":
        d_str = "20" + d_str[6:8] + "-" + d_str[3:5] + "-" + d_str[0:2]
    t_str = hdr[ini["time_key"]][ini["time_start"]:ini["time_end"]]
    dt_str = d_str + "T" + t_str
    dt_jd = Time(dt_str, format='isot', scale='utc')
    return dt_str, dt_jd


def basefilename(fullname):
    return os.path.basename(fullname).split(".")[0]


def unmatched(nall, matched):
    """
    选出未匹配到的目标
    :param nall:
    :param matched:
    :return:
    """
    # tag = np.ones(nall, bool)
    # tag[matched] = False
    # return np.where(tag)[0]
    return np.array(list( set(range(nall)) - set(matched) ))


def subset(ixall, matched):
    """
    选出未匹配到的目标
    :param ixall:
    :param matched:
    :return:
    """
    # nall = np.max(ixall + matched) + 1
    # tag = np.zeros(nall, bool)
    # tag[ixall] = True
    # tag[matched] = False
    # return np.where(tag)[0]
    return np.array(list( set(ixall) - set(matched) ))


def sex2dec(s, fac=1.0):
    """
    将六十进制表达的数值转换成十进制表达（hms不负责乘15）
    :param s: 字符串形式，可以是空格分隔或者冒号分隔，如果不是字符串不转换，包括None
    :param fac: 倍率，如果是字符串转浮点数，需要乘倍率
    :return:
    """
    if type(s) not in (str, np.str_):
        d = s
    else:
        s1 = s.replace(":", " ").split()
        d = float(s1[0]) + float(s1[1]) / 60.0 + float(s1[2]) / 3600.0
        d *= fac
    return d


# functions from survey codes
def lst (mjd, lon) :
    """ get local sidereal time for longitude at mjd, no astropy
    args:
        mjd: mjd
        lon: longitude, in degrees
    returns:
        lst: in hours
    """
    mjd0 = np.floor(mjd)
    ut = (mjd - mjd0) * 24.0
    t_eph = (mjd0 - 51544.5) / 36525.0
    return (6.697374558 + 1.0027379093 * ut +
            (8640184.812866 + (0.093104 - 0.0000062 * t_eph) * t_eph) * t_eph / 3600.0 +
            lon / 15.0) % 24.0


def hourangle (lst, ra) :
    """ Calculate hourangle of specified ra, -12 to +12
    args:
        lst: local sidereal time, in hours
        ra: ra of object, in degrees
    returns:
        hourangle, in hours, -12 to +12
    """
    return (lst - ra / 15.0 + 12.0) % 24.0 - 12.0


def airmass (lat, lst, ra, dec) :
    """ Calculate airmass
        Use simplified formula from old obs4, unknown source
    args:
        lat: latitude of site, in degrees
        lst: local sidereal time, in hours
        ra: ra of target, in degrees, scrlar or ndarray
        dec: dec of target, same shape as ra
    returns:
        airmass, same shape as ra/dec
    """
    lat = np.deg2rad(lat)
    lst = np.deg2rad(lst * 15.0)
    ra  = np.deg2rad(ra)
    dec = np.deg2rad(dec)

    x1 = np.sin(lat) * np.sin(dec)
    x2 = np.cos(lat) * np.cos(dec)
    ha = lst - ra
    x = 1.0 / (x1 + x2 * np.cos(ha))
    if type(x) == np.ndarray :
        x[np.where((x < 0.0) | (x > 9.99))] = 9.99
    else :
        if (x < 0.0) or (x > 9.99) :
            x = 9.99
    return x


def azalt (lat, lst, ra, dec) :
    """ Convert RA/Dec of object to Az&Alt
        Use formular from hadec2altaz of astron of IDL
    args:
        lat: latitude of site, in degrees
        lst: local sidereal time, in hours
        ra: ra of target, in degrees, scrlar or ndarray
        dec: dec of target, same shape as ra
    returns:
        az, alt
    """
    lat = np.deg2rad(lat)
    lst = np.deg2rad(lst * 15.0)
    ra  = np.deg2rad(ra)
    dec = np.deg2rad(dec)
    ha = lst - ra

    sh = np.sin(ha)
    ch = np.cos(ha)
    sd = np.sin(dec)
    cd = np.cos(dec)
    sl = np.sin(lat)
    cl = np.cos(lat)

    x = - ch * cd * sl + sd * cl
    y = - sh * cd
    z = ch * cd * cl + sd * sl
    r = np.sqrt(x * x + y * y)

    az  = np.rad2deg(np.arctan2(y, x)) % 360.0
    alt = np.rad2deg(np.arctan2(z, r))

    return az, alt


def ra2hms(x):
    """
    from coord.ra to hms format
    """
    xx = x.hms
    return "{h:02d}:{m:02d}:{s:05.2f}".format(h=int(xx.h), m=int(xx.m), s=xx.s)


def dec2dms(x):
    """
    from coord.dec to signed dms format
    """
    xx = x.signed_dms
    return "{p:1s}{d:02d}:{m:02d}:{s:04.1f}".format(p="+" if xx.sign>0 else "-", d=int(xx.d), m=int(xx.m), s=xx.s)
