#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# 阴阳师·技能图鉴：一图速览式神图鉴&技能
#
# 了解更多请前往 GitHub 查看项目：https://github.com/nguaduot/yys-cbg-skill
#
# author: @nguaduot 痒痒鼠@南瓜多糖
# version: 2.0
# date: 20210304

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
VERSION = VER + '.210304'
REL = 'github.com/nguaduot/yys-cbg-skill'
COPYRIGHT = '%s v%s @%s %s' % (PROG, VERSION, AUTH, REL)
HELP = '''参数文档:
-u, --url        藏宝阁商品号链接/本地数据文件路径
-r, --rarity     可见稀有度(6:联动 5:SP 4:SSR 3:SR 2:R 1:N 0:呱, 默认"65432")
-l, --light      亮色输出(默认暗色)
-v, --version    程序版本
-h, --help       帮助'''

# TODO: 可按需调整
HERO_RARITY2 = {
    6: {'name': '联动', 'visible': True},
    5: {'name': 'SP', 'visible': True},
    4: {'name': 'SSR', 'visible': True},
    3: {'name': 'SR', 'visible': True},
    2: {'name': 'R', 'visible': True},
    1: {'name': 'N', 'visible': False},
    0: {'name': '呱', 'visible': False},
    -1: {'name': '素材', 'visible': False}
}  # 式神稀有度索引, 名称, 输出可见性 (官方仅 5 4 3 2 1, 6 0 -1 为自定)
PALETTE_DARK = True  # 暗色输出(True: 暗色, False: 亮色)

USER_AGENT = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
              ' AppleWebKit/537.36 (KHTML, like Gecko)'
              ' Chrome/84.0.4147.89 Safari/537.36')

data_src_config: dict = None
data_parser: parser.Parser = None


def save(data_hero_book: dict, title: str, feet: tuple, path_base: str):
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
    依次为: 式神ID, 式神名, 稀有度索引, 式神名拼音
    注意: 稀有度索引中, "呱"和"素材"均被归到"N"，即1
    """
    result = {}
    for item in data_config['hero_list']:
        result[item[1]] = {
            'id': item[0],  # ID
            'rarity': item[2],  # 稀有度
            'rarity2': item[2],  # 稀有度v2
            'fragment': None,  # 碎片存量, 未知置None
            'skill': {
                'max': None,  # 满技能等级, 未知置None
                'all': None  # 已有技能等级, 缺失置[], 未知置None
            },  # 技能
            'colored': None,  # True: 图鉴已点亮, False: 未点亮, None: 未知
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
        print(log('非法藏宝阁商品号链接', 'warn'))
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
    data_parser = parser.CbgParser(sys.argv[0], data_src, HERO_RARITY2)
    # 保存源文件
    file_src = '%s.json' % data_parser.generate_path_base()
    with open(file_src, 'w', encoding='utf-8') as f:
        json.dump(data_src, f)
    print(log('已保存源数据 \'%s\'' % path.basename(file_src), 'info'))


def read_data(path_data):
    global data_parser
    print(log('正在读取式神录数据...', 'info'))
    try:
        with open(path_data, 'r', encoding='utf-8') as f:
            obj = json.loads(f.read())
            if check_data_fluxxu(obj):  # 按「痒痒熊快照」数据处理
                data_parser = parser.YyxParser(path_data, obj, HERO_RARITY2)
            elif check_data_cbg(obj):  # 按藏宝阁数据处理
                data_parser = parser.CbgParser(sys.argv[0], obj, HERO_RARITY2)
            else:
                print(log('无法识别数据文件内容', 'error'))
    except (FileNotFoundError, UnicodeDecodeError,
            json.decoder.JSONDecodeError) as e:
        print(log('非法数据文件或不存在', 'error'))
        print(e)


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


def set_palette(light: bool):
    global PALETTE_DARK
    if light:
        PALETTE_DARK = False


def set_rarity2(code_input: str):
    global HERO_RARITY2
    valid = False
    for index, item in HERO_RARITY2.items():
        visible = str(index) in code_input
        item['visible'] = visible
        valid |= visible
    return valid


def parse_args(args):
    global PALETTE_DARK
    try:
        opts, args = getopt.getopt(
            args,
            'hvlr:u:',
            ['help', 'version', 'light', 'rarity=', 'url=']
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
        elif opt in ('-l', '--light'):
            set_palette(True)
        elif opt in ('-r', '--rarity'):
            if not set_rarity2(value):
                print(log('稀有度指定无效', 'error'))
                do_not_run = True
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
    print(log('可见稀有度: %s, 不可见: %s' % (
        ' '.join([
            v['name'] for v in HERO_RARITY2.values() if v['visible']
        ]),
        ' '.join([
            v['name'] for v in HERO_RARITY2.values() if not v['visible']
        ])
    ), 'info'))
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
