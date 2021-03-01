#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# 阴阳师·技能图鉴：一图速览式神图鉴&技能
#
# 了解更多请前往 GitHub 查看项目：https://github.com/nguaduot/yys-cbg-skill
#
# author: @nguaduot 痒痒鼠@南瓜多糖
# version: 2.0
# date: 20210301

import getopt
import json
import os
import subprocess
import urllib
from os import path
import re
import sys
from threading import Thread
from urllib import request
from urllib import parse

from modules import output
from modules import parser

PROG = 'yys-cbg-skill'
AUTH = 'nguaduot'
VER = '2.0'
VERSION = VER + '.210301'
REL = 'github.com/nguaduot/yys-cbg-skill'
COPYRIGHT = '%s v%s @%s %s' % (PROG, VERSION, AUTH, REL)
HELP = '''参数文档:
-u, --url        藏宝阁商品号链接/本地数据文件路径
-d, --dark       暗色输出(默认)
-l, --light      亮色输出
-v, --version    程序版本
-h, --help       帮助'''

# TODO: 可自行调整
RARITY_VISIBLE = (
    'x', 'sp', 'ssr', 'sr', 'r'
)  # 可见稀有度, 合法值: sp, ssr, sr, r, n, x (n: N+呱, x: 联动)
PALETTE_DARK = True  # 暗色输出(True: 暗色, False: 亮色)

# TODO: 以下常量需留意随版本更新而检查更新
HERO_DAMO = {
    410: '招福达摩',
    411: '御行达摩',
    412: '奉为达摩',
    413: '大吉达摩',
    499: '鬼武达摩'
}  # 素材
HERO_SKILL_MAX = {
    # 联动
    '奴良陆生': '515',
    '卖药郎': '515',
    '鬼灯': '515',
    '阿香': '515',
    '蜜桃&芥子': '515',
    '犬夜叉': '515',
    '杀生丸': '515',
    '桔梗': '515',
    '朽木露琪亚': '555',
    '黑崎一护': '515',
    '灶门炭治郎': '555',
    '灶门祢豆子': '555',
    # SP
    '少羽大天狗': '515',
    '炼狱茨木童子': '555',
    '稻荷神御馔津': '555',
    '苍风一目连': '555',
    '赤影妖刀姬': '555',
    '御怨般若': '555',
    '骁浪荒川之主': '555',
    '烬天玉藻前': '555',
    '鬼王酒吞童子': '555',
    '天剑韧心鬼切': '555',
    '聆海金鱼姬': '515',
    '浮世青行灯': '555',
    '缚骨清姬': '555',
    '待宵姑获鸟': '515',
    '麓铭大岳丸': '555',
    '初翎山风': '555',
    '夜溟彼岸花': '555',
    # SSR
    '大天狗': '555',
    '酒吞童子': '515',
    '荒川之主': '515',
    '阎魔': '555',
    '两面佛': '555',
    '小鹿男': '555',
    '茨木童子': '515',
    '青行灯': '555',
    '妖刀姬': '515',
    '一目连': '555',
    '花鸟卷': '555',
    '辉夜姬': '535',
    '荒': '555',
    '彼岸花': '555',
    '雪童子': '515',
    '山风': '555',
    '玉藻前': '555',
    '御馔津': '515',
    '面灵气': '555',
    '鬼切': '515',
    '白藏主': '555',
    '八岐大蛇': '555',
    '不知火': '555',
    '大岳丸': '555',
    '泷夜叉姬': '555',
    '云外镜': '515',
    '鬼童丸': '555',
    '缘结神': '515',
    '铃鹿御前': '555',
    '紧那罗': '555',
    '千姬': '555',
    # SR
    '桃花妖': '555',
    '雪女': '555',
    '鬼使白': '555',
    '鬼使黑': '515',
    '孟婆': '555',
    '犬神': '555',
    '骨女': '515',
    '鬼女红叶': '555',
    '跳跳哥哥': '555',
    '傀儡师': '515',
    '海坊主': '515',
    '判官': '555',
    '凤凰火': '515',
    '吸血姬': '515',
    '妖狐': '555',
    '妖琴师': '555',
    '食梦貘': '515',
    '清姬': '615',
    '镰鼬': '555',
    '姑获鸟': '515',
    '二口女': '515',
    '白狼': '515',
    '樱花妖': '555',
    '惠比寿': '534',
    '络新妇': '515',
    '般若': '515',
    '青坊主': '515',
    '万年竹': '515',
    '夜叉': '555',
    '黑童子': '555',
    '白童子': '515',
    '烟烟罗': '555',
    '金鱼姬': '515',
    '鸩': '555',
    '以津真天': '555',
    '匣中少女': '515',
    '小松丸': '555',
    '书翁': '555',
    '百目鬼': '555',
    '追月神': '545',
    '日和坊': '515',
    '薰': '555',
    '弈': '515',
    '猫掌柜': '515',
    '人面树': '555',
    '於菊虫': '555',
    '一反木绵': '555',
    '入殓师': '555',
    '化鲸': '555',
    '海忍': '555',
    '久次良': '515',
    '蟹姬': '555',
    '纸舞': '555',
    '星熊童子': '555',
    '风狸': '555',
    '蝎女': '555',
    # R
    '三尾狐': '656',
    '座敷童子': '533',
    '鲤鱼精': '555',
    '九命猫': '515',
    '狸猫': '555',
    '河童': '545',
    '童男': '551',
    '童女': '554',
    '饿鬼': '555',
    '巫蛊师': '555',
    '鸦天狗': '545',
    '食发鬼': '515',
    '武士之灵': '555',
    '雨女': '514',
    '跳跳弟弟': '555',
    '跳跳妹妹': '515',
    '兵俑': '555',
    '丑时之女': '555',
    '独眼小僧': '555',
    '铁鼠': '515',
    '椒图': '543',
    '管狐': '545',
    '山兔': '545',
    '萤草': '555',
    '蝴蝶精': '555',
    '山童': '515',
    '首无': '515',
    '觉': '515',
    '青蛙瓷器': '515',
    '古笼火': '535',
    '兔丸': '555',
    '数珠': '555',
    '小袖之手': '555',
    '虫师': '515',
    '天井下': '555',
    '垢尝': '515',
    # N卡
    '灯笼鬼': '534',
    '提灯小僧': '55',
    '赤舌': '555',
    '盗墓小鬼': '5',
    '寄生魂': '5',
    '唐纸伞妖': '55',
    '天邪鬼绿': '55',
    '天邪鬼赤': '51',
    '天邪鬼黄': '51',
    '天邪鬼青': '51',
    '帚神': '55',
    '涂壁': '51',
    # 呱
    '大天狗呱': '55',
    '酒吞呱': '55',
    '荒川呱': '55',
    '阎魔呱': '55',
    '两面佛呱': '55',
    '小鹿男呱': '55',
    '茨木呱': '55',
    '青行灯呱': '55',
    '妖刀姬呱': '55',
    '一目连呱': '55',
    '花鸟卷呱': '55',
    '辉夜姬呱': '55',
    '荒呱': '55',
    '彼岸花呱': '55'
}  # 式神技能等级上限, 使用 ?.get(?, ?) 取值而非 ?[?]

USER_AGENT = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
              ' AppleWebKit/537.36 (KHTML, like Gecko)'
              ' Chrome/84.0.4147.89 Safari/537.36')

data_src_config: dict = None
data_parser: parser.Parser = None


def save(data_hero_book, title, feet, path_base):
    for foot in feet:
        print(foot)
    file_result = '%s_skill.png' % path_base
    if output.enabled():
        feet_all = feet + (path.basename(file_result), COPYRIGHT)
        output.text2img(file_result, data_hero_book,
                        title=title, feet=feet_all,
                        palette_dark=PALETTE_DARK)
        print(log('已保存结果 \'*_%s\'' % file_result.rsplit('_', 1)[1], 'info'))
        view(file_result)
    else:
        print(log('\'PIL\'库或字体缺失, 未将结果生成图片 \'*_%s\''
                  % file_result.rsplit('_', 1)[1], 'warn'))


def get_hero_book(data_config: dict):
    """
    e.g. [200, '桃花妖', 3, 'taohuayao']
    式神 ID, 式神名, 稀有度索引, 式神名拼音
    """
    result = {}
    for item in data_config['hero_list']:
        if item[0] in HERO_DAMO:  # 剔除被算作N阶稀有度的"素材"
            continue
        result[item[1]] = {
            'rarity': item[2],
            'fragment': None,
            'sort': item[0],
            'x': False,
            'max': HERO_SKILL_MAX.get(item[1], None),
            'all': []
        }
    return result


def fetch_cbg_config():
    global data_src_config
    print(log('正在读取式神图鉴数据...', 'info'))
    url_heroes = 'https://cbg-yys.res.netease.com/js/game_auto_config.js'
    req = request.Request(url=url_heroes, headers={
        'User-Agent': USER_AGENT
    })
    data = request.urlopen(req, timeout=4).read().decode('utf-8')
    r = re.search(r'({.+})', data)
    if not r:
        return
    data_src_config = json.loads(r.group(1))


def fetch_cbg_equip(url_equip):
    global data_parser
    url_player = urllib.parse.unquote(url_equip, encoding='utf-8')
    parsed = urllib.parse.urlparse(url_player)
    # queries = urllib.parse.parse_qs(parsed.query)  # 参数可省略
    m = re.match(r'/cgi/mweb/equip/(\d+)/(.+)', parsed.path)
    if not m:
        print(log('非法藏宝阁商品详情链接', 'warn'))
        return
    print(log('正在读取式神录数据...', 'info'))
    url = 'https://yys.cbg.163.com/cgi/api/get_equip_detail'
    headers = {
        'User-Agent': USER_AGENT
    }
    params = {
        'serverid': m.group(1),
        'ordersn': m.group(2)
    }
    req = request.Request(
        url=url,
        data=urllib.parse.urlencode(params).encode('utf-8'),
        headers=headers,
        method='POST'
    )
    result = request.urlopen(req, timeout=8).read().decode('utf-8')
    data_src = json.loads(result)
    data_parser = parser.CbgParser(sys.argv[0], data_src, RARITY_VISIBLE)
    # 保存源文件
    file_src = '%s.json' % data_parser.generate_path_base()
    with open(file_src, 'w', encoding='utf-8') as f:
        json.dump(data_src, f)
    print(log('已保存源数据 \'%s\'' % path.basename(file_src), 'info'))


def read_data(path_data):
    global data_parser
    print(log('正在读取式神录数据...', 'info'))
    with open(path_data, 'r', encoding='utf-8') as f:
        obj = json.loads(f.read())
        if check_data_fluxxu(obj):  # 按「痒痒熊快照」数据处理
            data_parser = parser.YyxParser(path_data, obj, RARITY_VISIBLE)
        elif check_data_cbg(obj):  # 按藏宝阁数据处理
            data_parser = parser.CbgParser(sys.argv[0], obj, RARITY_VISIBLE)
        else:
            print(log('无法识别数据文件内容', 'error'))


def check_data_fluxxu(data):
    """检查 JSON 数据是否为「痒痒熊快照」数据

    Args:
        data (dict): JSON 数据

    Returns:
        bool: 合法返回 True
    """
    return (data and isinstance(data, dict)
            and 'data' in data and 'hero_equips' in data['data'])


def check_data_cbg(data):
    """检查 JSON 数据是否为藏宝阁数据

    Args:
        data (dict): JSON 数据

    Returns:
        bool: 合法返回 True
    """
    return (data and isinstance(data, dict)
            and 'equip' in data and 'equip_desc' in data['equip'])


def log(content, level):
    """封装单行日志内容

    Args:
        content (str): 日志内容
        level (str): 日志等级 ['info', 'warn', 'error', 'input']

    Returns:
        str: 返回封装好的日志
    """
    log_prefix = {
        'info': '[日志]',
        'warn': '[警告]',
        'error': '[出错]',
        'input': '[输入]'
    }
    return '{} {}'.format(log_prefix[level], content)


def view(file):
    if run_as_exe() and path.exists(file):
        # subprocess.run(['start', file])
        subprocess.run(['explorer', file])


def parse_args(args):
    global PALETTE_DARK
    try:
        opts, args = getopt.getopt(
            args,
            'hvdlu:',
            ['help', 'version', 'dark', 'light', 'url=']
        )
    except getopt.GetoptError:
        opts, args = [('-h', '')], []
    url_or_path, do_not_run = None, False
    for opt, value in opts:
        if opt in ('-h', '--help'):
            print(COPYRIGHT)
            print(HELP)
            do_not_run = True
        elif opt in ('-v', '--version'):
            print(VERSION)
            do_not_run = True
        elif opt in ('-d', '--dark'):
            PALETTE_DARK = True
        elif opt in ('-l', '--light'):
            PALETTE_DARK = False
        elif opt in ('-u', '--url'):
            url_or_path = value
    if not url_or_path and args:
        url_or_path = args[0]
    return url_or_path, do_not_run


def run_as_exe():
    """判断本程序运行环境

    判断本程序是否已被封装为 EXE 执行，若如此可实现一些特性，如控制台进度条效果。
    IDE 中执行原生 .py 一般无法实现此效果。

    Returns:
        bool: True 为 Windows EXE，False 视为原生 .py 脚本
    """
    return path.splitext(sys.argv[0])[1] == '.exe'


def main():
    url_or_path, do_not_run = None, False
    if len(sys.argv) > 1:  # 带参启动
        url_or_path, do_not_run = parse_args(sys.argv[1:])
    if do_not_run:  # 无须启动
        return
    print(COPYRIGHT)
    print(log('暗色输出' if PALETTE_DARK else '亮色输出', 'info'))
    if not url_or_path:
        url_or_path = input(log('链接/路径: ', 'input')).strip('"\'')

    # 读取/抓取数据&解析数据
    thread1 = Thread(target=fetch_cbg_config)
    thread1.start()
    if path.isfile(url_or_path):
        thread2 = Thread(target=read_data, args=(url_or_path,))
        thread2.start()
    else:
        thread2 = Thread(target=fetch_cbg_equip, args=(url_or_path,))
        thread2.start()
    thread1.join()
    thread2.join()
    if not data_src_config or not data_parser:
        return
    
    # 解析式神图鉴
    data_hero_book = get_hero_book(data_src_config)

    # 生成结果图片
    save(data_parser.parse(data_hero_book),
         data_parser.get_title(),
         data_parser.get_feet(),
         data_parser.generate_path_base())


if __name__ == '__main__':
    try:
        main()
    except Exception:
        raise
    finally:
        if run_as_exe():  # 避免窗口一闪而逝
            os.system('pause')
