# 藏宝阁·阴阳师·技能图鉴

[![Beta](https://img.shields.io/badge/Beta-2.0-brightgreen.svg?style=flat-square)](https://github.com/nguaduot/yys-cbg-skill)
[![Release](https://img.shields.io/badge/Release-1.1-brightgreen.svg?style=flat-square)](https://github.com/nguaduot/yys-cbg-skill/releases)
[![Download](https://img.shields.io/badge/Download-EXE-brightgreen.svg?style=flat-square)](dist/%E6%8A%80%E8%83%BD%E5%9B%BE%E9%89%B41.1.exe)

[阴阳师藏宝阁](https://yys.cbg.163.com/)衍生小工具，一图速览商品号式神图鉴&技能。

一图包含了哪些信息？
+ **联动**、**SP**、**SSR**、**SR**、**R** 式神图鉴
+ 式神录可见全式神技能等级
+ 高亮标记 **SP**、**SSR** 缺失式神（已收录仍可能缺失）
+ 高亮标记满技能式神
+ 御行达摩保有量+消耗量（保守估计）

例：

商品页面：[阴阳师藏宝阁-夏之蝉-南瓜多糖](https://yys.cbg.163.com/cgi/mweb/equip/21/202102020901616-21-3S6GQUUH2DOUM)

生成图：[技能图鉴](sample/cbg_中国区-iOS_夏之蝉_南瓜多糖_20210222071008_skill.png)

> 「技能图鉴」同时发布到 NGA 论坛阴阳师板块，可回复交流：
> 
> [[心得交流] [02/26] [v1.1] 藏宝阁·技能图鉴：一图速览式神图鉴&技能](https://nga.178.com/read.php?tid=25428203&_ff=538)

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

v2.0.210301
+ 增加式神图鉴信息
+ 更精准识别SR、R阶联动拥有情况
+ 除藏宝阁链接，也支持解析本地藏宝阁JSON数据文件
+ 支持解析“痒痒熊快照”导出的JSON数据文件

v1.1.210226
+ 缺失式神增加碎片收集量显示
+ 增加黑蛋保有量显示

v1.0.210205
+ 第一版发布