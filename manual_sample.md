<link rel="stylesheet" type="text/css" href="../auto-number-title.css" />

# LCP-2021A 使用手册-附录

| 版本 | 作者 | 说明 |
|----|----|----|
| 2021G | 小林博士 | 初始版本 |

[toc]

## 附录A：调用示例

这里给出一些调用示例，并说明其适用性，供参考。

### 通用的import段

导入本程序，这里使用的是相对路径，实际应用中建议使用绝对路径。先将qlcp21a程序所在的上层目录添加到系统搜索路径sys.path中，然后再引入qlcp21a。

注意执行时可能给出警告，由于本机的天体运行相关数据未能更新，会对最终的精度造成一定影响。最后两句是取消自动下载。在后续程序运行中，将不会去试图去更新。如果网络条件允许，建议更新。如果无法更新又没有取消，那么部分步骤将会长时间等待直到网络超时。

```
import sys
sys.path.append("..")
import qlcp21a

from astropy.utils import iers
iers.conf.auto_download = False
```

### 一步式调用

```
base_dir = "/data/"  # the base dir of data
qlcp21a.do_all(
    ini_file="xl60.ini", 
    raw_dir=base_dir+"raw/20210404_60/",
    lst_dir=base_dir+"lst/20210404_60/", 
    red_dir=base_dir+"red/20210404_60/",
)
```

该调用法全部采用默认参数，仅需要指定数据所在路径。最终将在屏幕显示部分操作消息，以及最终输出的各波段证认图和光变曲线，目标星和参考星自动从数据中选取。

### 自动调用的补充

全自动识别目标星和参考星可能并不可靠，尤其是有已知的参考星的时候，往往需要手工指定。下面的调用中，跳过了前面的步骤直接执行后面的cdg部分。并且指定了找星时的中心点误差为5.0像素（默认10.0）。另外，这里指定了具体要处理的目标，而不是处理所有图像。

```
qlcp21a.do_all(
    ini_file="xl60.ini", 
    raw_dir=base_dir+"raw/20210404_60/",
    lst_dir=base_dir+"lst/20210404_60/", 
    red_dir=base_dir+"red/20210404_60/",
    obj="Vega", band="BVRI",
    steps="cdg",
    starxy=[
        (1079,  977),
        ( 143, 1986),
        ( 171, 1887),
        (  40,  112),
        ( 691,  988),
        ( 988,  845),
        ( 148, 1224),
        (1737, 1709),
    ],
    extra_config={"cali_dis_limit": 5.0},
    overwrite=True
)
```

### 使用其它日期的参考数据

处理完第一天的数据后，其它日期对同一个目标的观测数据可以直接套用此前处理的结果作为指定目标的参考，不需要重新去当天的数据中找目标星、参考星的中心。

```
qlcp21a.do_all(
    ini_file="xl60.ini", 
    raw_dir=base_dir+"raw/20210405_60/",
    lst_dir=base_dir+"lst/20210405_60/", 
    red_dir=base_dir+"red/20210405_60/",
    obj="Vega", band="BVRI",
    steps="lbfipocdg",
    base_img_id=-1,
    base_cat_file=base_dir+"red/20210404_60/Vega_V/Vega_V_001.cat.fits",
    base_fits_file=base_dir+"red/20210404_60/Vega_V/Vega_V_001.bf.fits",,
    starxy=[
        (1079,  977),
        ( 143, 1986),
        ( 171, 1887),
        (  40,  112),
        ( 691,  988),
        ( 988,  845),
        ( 148, 1224),
        (1737, 1709),
    ],
    extra_config={"cali_dis_limit": 5.0},
)
```

### 针对兴隆85厘米望远镜的处理

由于兴隆85厘米望远镜数据头部暂时不包括目标赤经、赤纬信息，因此需要手工提供，对于整晚单目标和多目标，多目标时可以这样做：

```
qlcp21a.do_all(
    ini_file="xl85.ini", 
    raw_dir=base_dir+"raw/20210303_85/",
    lst_dir=base_dir+"lst/20210303_85/", 
    red_dir=base_dir+"red/20210303_85/",
    obj_coord = {
        "Vega" : ("18:36:56.34", "+38:47:01.3"),
        "Sirius" : ("06:45:08.92","-16:42:58.0"),
    },
)
```

如果是单目标，那么可以直接只给一组坐标：

```
qlcp21a.do_all(
    ini_file="xl85.ini", 
    raw_dir=base_dir+"raw/20210303_85/",
    lst_dir=base_dir+"lst/20210303_85/", 
    red_dir=base_dir+"red/20210303_85/",
    obj_coord = ("18:36:56.34", "+38:47:01.3"),
)
```

### 针对自建列表的数据

在一些情况下，可能我们会对自动创建的列表进行一些调整，例如从中剔除一些质量不好的数据，或者是有些望远镜的文件名并不带有目标和波段信息，需要我们手工建立列表。此时我们不需要执行`l`步骤，直接指定目标和波段即可。

```
qlcp21a.do_all(
    ini_file="xl60.ini", 
    raw_dir=base_dir+"raw/20210404_60/",
    lst_dir=base_dir+"lst/20210404_60/", 
    red_dir=base_dir+"red/20210404_60/",
    bandobj = {
        "B": ["Vega", "Sirius", "flat"],
        "V": ["Sirius", "flat"],
        "": ["bias"],
    },
    steps="bfipocdg",
)
```

