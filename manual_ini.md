<link rel="stylesheet" type="text/css" href="../../auto-number-title.css" />

# LCP-2021A 使用手册-附录B：配置项目说明

| 版本 | 作者 | 说明 |
|----|----|----|
| 2021G | 小林博士 | 初始版本 |

[toc]

## 附录B：配置项目说明

配置文件中的信息，用于控制程序运行。通常适用于所有数据处理过程。以下分类介绍参数。

### 配置文件优先级

在调用时，可以支持多个配置文件，按照优先级由低到高依次为：lcp21a目录下的`default.ini`，当前工作路径下的`default.ini`，通过`ini_file`参数指定的配置文件，如果有多个，后面的优先级比前面的高，通过`extra_config`参数指定的具体配置项。

当优先级更高的方式指定了低优先级方式中出现的配置项目时，以高优先级的为准，换句话说，按照优先级从低到高加载配置项，后加载的覆盖先加载的。

### 屏幕显示信息

```
log_level = "INFO"  # 用来指定处理时在屏幕上显示的信息数量，DEBUG全部信息, INFO常规信息, WARNING只显示警告, ERROR只显示错误
```

### 输出文件名

针对每一幅科学图像，处理之后输出的文件中间名，添加在原文件名的尾部，扩展名之前。
`separate_folder`表示是否为每一次处理的输出结果单独创建文件夹。

例如`J1836+3847_V_0001.fit`，经过本底平场改正之后的文件为`J1836+3847_V_0001/J1836+3847_V_0001.cat.fits`，最终测光结果文件为`J1836+3847_V/J1836+3847_V_0001.cat.fits`。

```
bf_mid  = "bf"
cat_mid = "cat"
se_mid  = "se"
separate_folder = True
```

以下部分则用于指定各步骤的输入、输出文件名的格式，包括列表、数据和图像、日志等，格式基本上为`{work}_{obj}_{band}.{format}`。若非特殊情况，例如希望不同处理模式结果输出到不同文件，否则不建议修改。

```
filename_bias_lst      = "bias.lst"
filename_flat_lst      = "flat_{band}.lst"
filename_file_lst      = "{obj}_{band}.lst"
filename_bias_fit      = "bias.fits"
filename_flat_fit      = "flat_{band}.fits"
filename_imgproc_log   = "imgproc_{obj}_{band}.log"
filename_wcs_txt       = "wcs_{obj}_{band}.fits"
filename_offset_txt    = "offset_{obj}_{band}.txt"
filename_pick_txt      = "pick_{obj}_{band}.txt"
filename_cat_fit       = "cat_{obj}_{band}.fits"
filename_cat_table_txt = "cattb_{obj}_{band}.txt"
filename_cat_list_txt  = "catls_{obj}_{band}.txt"
filename_finding_img   = "cat_{obj}_{band}.png"
filename_cali_fit      = "cali_{obj}_{band}.fits"
filename_cali_txt      = "cali_{obj}_{band}.txt"
filename_lc_png        = "lc_{obj}_{band}.png"
filename_bias_log      = "log/bias.log"
filename_flat_log      = "log/flat_{band}.log"
filename_phot_log      = "log/phot_{obj}_{band}.log"
filename_wcs_log       = "log/wcs_{obj}_{band}.log"
filename_offset_log    = "log/offset_{obj}_{band}.log"
filename_pick_log      = "log/pick_{obj}_{band}.log"
filename_cat_log       = "log/cat_{obj}_{band}.log"
filename_cali_log      = "log/cali_{obj}_{band}.log"
filename_lc_log        = "log/lc_{obj}_{band}.log"
```

### 本底平场合并参数

指定本底平场合并的函数，不过通常情况下选中值而非均值。此外，可以对平场进行选择。

```
bias_comb_function = "median"   #本底合并函数median或mean
flat_comb_function = "median"   #平场合并函数median或mean
flat_limit_low  =  5000         #用于合并的平场值的下限
flat_limit_high = 50000         #用于合并的平场值的上限
```

### 边缘处理

在选星作为定位、流量定标等工作时，删去距离边缘太近的星。

```
bf_border_cut = 0
```

### Source-Extractor相关

`se_cmd`用于指示Source-Extractor的命令名，不同系统、不同版本可能不一样。后面则是指定在SE输出的星表中，选用哪些列。如果在``default.sex`和default.param`中选择了不同的模式，那么这里要相应变更。

```
se_cmd = "sex"          # source extractor在mac下的名称
                        # 在Linux一般为sextractor
se_x   = "x_image_dbl"  # SE输出的x坐标所用的列名称
se_y   = "y_image_dbl"  # 同上
se_ra  = "alpha_j2000"  # SE输出的ra坐标所用的列名称
se_de  = "delta_j2000"  # 同上
se_mag = "mag_auto"     # 选用的仪器星等列名
se_err = "magerr_auto"  # 选用的测光误差列名
fwhm   = "fwhm_image"   # 半高全宽列名
elong  = "elongation"   # 伸长率
```

### 孔径测光参数（未来版本使用）

测光孔径，天光孔径的内径和宽度。当前版本未使用这些参数。

```
phot_aper   = 12.5
phot_iann   = 25.0
phot_wann   = 10.0
```

### 证认图绘制

绘制证认图时的scale设置。

```
plot_img_lowsigma  = 1.0
plot_img_highsigma = 5.0
```

### 场星匹配

```
offset_tri_nstar    = 5 # 用于三角形匹配的点源个数，建议5-10个，太多了反而不好
offset_tri_matcherr = 0.0005 # 三角形匹配时边长比例误差

offset_err_limit = 0.1   # 用来做offset的星所需要达到的测光精度
offset_count     = 30    # 满足精度用来做offset的星的个数（按亮度顺序）
offset_max       = 40.0  # 做offset时进行每一幅图与参考星图的匹配时，
    # 两颗星判定为同一颗星的初始距离，此后根据匹配结果开始迭代，求出两图之间的偏移量
offset_min       = 3.0   #当偏移量的标准差小于min值时，则得到最终偏移量
offset_iter      = 8     #最多迭代次数，如果超过该迭代次数还未收敛，则认为迭代失败
offset_factor    = 2.0   #第二次迭代的容错值，为上一次匹配偏移量标准差的2倍
```

### 猜测目标星与参考星

```
pick_err     = 0.1    # 第一轮选择，误差上限
pick_star    = 100    # 第一轮最多不超过多少颗
pick_var_std = 0.1    # 最终选定时目标变星，在全部图像中的定标后标准差下限
pick_var_dif = 0.25   # 目标变星亮度最大、最小值之差下限
pick_ref_std = 0.025  # 最终选定的参考星，在全部图像中的定标后标准差上限
pick_ref_dif = 0.1    # 参考星亮度最大、最小值之差上限
pick_ref_n   = 20     # 最多找几颗参考星
```

### 给定坐标匹配目标时的误差容许值

```
cali_dis_limit = 10.0    # 提取所需目标星的坐标误差容错值，单位像元
cali_sky_limit =  2.5     # 同上，采用天球坐标，单位角秒
```

### 观测站地理位置

本节为望远镜所在观测站地理位置，其中纬度北为正，南为负，经度东为正，西为负，或者从本初子午线向东按0°-360°计。海拔以米为单位，精确度要求较低。

```
site_lon = 117.57722  # 117:34:38      # 兴隆观测站的经度
site_lat = 40.395833  # +40:23:45      # 兴隆观测站的纬度
site_ele = 900                         # 兴隆观测站的高度
```

### fits头中观测时间日期关键字和片段起止

本节内容与望远镜输出的fits文件头有关，不同望远镜配置可能不同。以下配置针对`DATE-OBS='2021-02-12T12:34:56.78'`这样的格式。

```
date_key   = "DATE-OBS"    # 观测日期头文件关键字
date_start = 0             # 开始字符
date_end   = 10            # 结束字符
time_key   = "DATE-OBS"    # 观测时间头文件关键字
time_start = 11            # 开始字符
time_end   = 19            # 结束字符
```

### 自动识别文件名模板

本节与望远镜输出文件名有关，不同望远镜配置不同。若无法正确写出正则表达式，可以考虑跳过自动识别，手工编制列表。下面给的格式分别针对两种不同情况，前者是`J1836+3847_0001V.fit `，后者是`J1836+3847_V_0001.fit`。

```
filename_temp = "(?P<obj>[^_]*)_(?P<sn>[0-9]{4})(?P<band>[a-zA-Z]{0,1}).fit"
```

```
filename_temp = "(?P<obj>[^_]*)_(?P<band>[a-zA-Z]{0,1})_(?P<sn>[0-9]{4}).fit"
```

