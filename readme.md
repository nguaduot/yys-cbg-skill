# 藏宝阁·阴阳师·技能图鉴

[![Release](https://img.shields.io/badge/Release-1.0-brightgreen.svg?style=flat-square)](https://github.com/nguaduot/yys-cbg-skill)
[![Download](https://img.shields.io/badge/Download-EXE-brightgreen.svg?style=flat-square)](dist/%E6%8A%80%E8%83%BD%E5%9B%BE%E9%89%B41.0.exe)

[阴阳师藏宝阁](https://yys.cbg.163.com/)衍生小工具，用于生成商品号的式神图鉴&技能速览图。

一图包含了哪些信息？
+ **联动** & **SP** & **SSR** & **SR** & **R** 五类式神完整图鉴
+ **SP**、**SSR** 阶稀有度式神未拥有标记（红色）
+ 式神技能等级
+ 多号机情况
+ SP&SSR技能升级次数统计

例：

商品页面：[阴阳师藏宝阁-夏之蝉-南瓜多糖](https://yys.cbg.163.com/cgi/mweb/equip/21/202101152201616-21-VTG7H9VQQFVSG)

生成图：[技能图鉴](sample/cbg_中国区-iOS_夏之蝉_南瓜多糖_20210201095612_skill.png)

> 「技能图鉴」同时发布到 NGA 论坛阴阳师板块，可回复交流：
> 
> [[心得交流] [01/28] [v1.6] 号来：藏宝阁辅助看号工具](https://nga.178.com/read.php?tid=23005018)

### 依赖

「技能图鉴」使用 Python3 编写，依赖的第三方库：

```
pip install pillow
```

### 文档

```
python cbg_skill.py -h
```

```
+ 选项：
  -h, --help     帮助
  -v, --version  程序版本
  -u, --url      藏宝阁商品链接
+ 若未指定 -u, 程序会读取未知参数, 若也无未知参数, 不启动程序'
+ 不带任何参数也可启动程序, 会有参数输入引导
```

### 作者

> “不会在记事本用 Python 写小工具的程序猿的不是好痒痒鼠！”
>
> —「夏之蝉」区@**南瓜多糖**

痒痒鼠相关问题欢迎来找我讨论，代码改进或漏洞也欢迎一起交流。

### 更新日志

v1.0.210205
+ 第一版发布