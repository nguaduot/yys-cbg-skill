#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# 技能图鉴
# 一图速览式神图鉴&技能
#
# 了解更多请前往 GitHub 查看项目：https://github.com/nguaduot/yys-cbg-skill
#
# author: @nguaduot 痒痒鼠@南瓜多糖
# version: 1.0.210203
# date: 20210203

import datetime
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

from modules import output

PROG = 'yys-cbg-skill'
AUTH = 'nguaduot'
VER = '1.0'
VERSION = '1.0.210203'
REL = 'github.com/nguaduot/yys-cbg-skill'
COPYRIGHT = '%s v%s @%s %s' % (PROG, VERSION, AUTH, REL)
HELP = '''+ 选项：
  -h, --help     帮助
  -v, --version  程序版本
  -u, --url      藏宝阁商品链接
+ 若未指定 -u, 程序会读取未知参数, 若也无未知参数, 不启动程序'
+ 不带任何参数也可启动程序, 会有参数输入引导'''

HERO_RARITY = ['', 'N', 'R', 'SR', 'SSR', 'SP']  # 式神稀有度索引
HERO_ONMYOJI = {
    10: '晴明', 11: '神乐', 13: '源博雅', 12: '八百比丘尼',
    900: '神龙', 901: '白藏主', 903: '黑豹', 902: '孔雀'
}  # 阴阳师及其御灵稀有度均被设定为SSR, 即 item['rarity'] == 4

# TODO: 以下常量需留意随版本更新而检查更新
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
    '垢尝': '515'
}  # 式神技能等级上限, 使用 HERO_SKILL_MAX.get(x, x) 取值而非 HERO_SKILL_MAX[x]

USER_AGENT = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
              ' AppleWebKit/537.36 (KHTML, like Gecko)'
              ' Chrome/84.0.4147.89 Safari/537.36')

DATA_SOURCE_CONFIG = None
DATA_SOURCE_EQUIP = None


def save(data_equip, data_hero_book, damo_yx_own_cost):
    dir_cbg = path.join(path.dirname(path.abspath(sys.argv[0])), 'cbg')
    if not path.isdir(dir_cbg):
        os.mkdir(dir_cbg)
    if not data_equip:
        return
    # 删除 Windows 文件名中不允许出现的字符, 以及无法正常显示且会导致 IO 异常的控制字符
    # 使用当前卖家角色昵称 equip_name，而非 seller_name，其会随买家再次上架而改变
    seller = re.sub(
        r'[\\/:?"<>|\u0000-\u001F\u007F-\u009F]', '',
        data_equip['equip']['equip_name']
    )
    t = datetime.datetime.strptime(data_equip['equip']['create_time'],
                                   '%Y-%m-%d %H:%M:%S')
    file_base = path.join(dir_cbg, 'cbg_%s_%s_%s_%s' % (
        data_equip['equip']['area_name'], data_equip['equip']['server_name'],
        seller, t.strftime('%Y%m%d%H%M%S')
    ))
    file_source = '%s.json' % file_base
    file_result = '%s_skill.png' % file_base
    # if path.isfile(file_source):
    #     cio('源数据已存在 \'%s\'' % path.basename(file_source), 'info')
    with open(file_source, 'w', encoding='utf-8') as f:
        json.dump(data_equip, f)
    print(log('已保存源数据 \'%s\'' % path.basename(file_source), 'info'))
    if output.enabled():
        head = path.basename(file_result) + '  %d+%d' % damo_yx_own_cost
        output.text2img(file_result, data_hero_book,
                        head=head, foot=COPYRIGHT)
        print(log('已保存结果 \'*_%s\'' % file_result.rsplit('_', 1)[1], 'info'))
        view(file_result)
    else:
        print(log('\'PIL\'库或字体缺失, 未将结果生成图片 \'*_%s\''
                  % file_result.rsplit('_', 1)[1], 'warn'))


def get_damo_yx(data_equip):
    data_game = json.loads(data_equip['equip']['equip_desc'])
    data_damo = data_game['damo_count_dict']
    data_heroes = list(data_game['heroes'].values())
    data_sp_ssr = [item for item in data_heroes if (
        item['rarity'] == 5 or item['rarity'] == 4
    ) and item['heroId'] not in HERO_ONMYOJI]
    sum_own = sum([num for damoes in data_damo.values()
                   for damo, num in damoes.items()
                   if damo == '411'])
    sum_cost = sum([max(info[1] - 1, 0) for hero in data_sp_ssr
                    for info in hero['skinfo']])
    return sum_own, sum_cost


def get_hero_book(data_config):
    result = {}
    for item in data_config['hero_list']:
        # [200, '桃花妖', 3, 'taohuayao']
        # 200: 式神 ID
        # 3: 稀有度索引(5 SP 4 SSR 3 SR 2 R 1 N + 呱 + 素材)
        if item[2] < 2:  # 跳过 N + 呱 + 素材
            continue
        result[item[1]] = {
            'rarity': item[2],
            'sort': item[0],
            'x': False,
            'max': None,
            'all': []
        }
    return result


def get_hero_x(data_equip):
    data_game = json.loads(data_equip['equip']['equip_desc'])
    return [item[0] for item in data_game['hero_history']['x'].values()
            if type(item) is list]


def get_hero_own(data_equip):
    data_game = json.loads(data_equip['equip']['equip_desc'])
    data_heroes = [item for item in data_game['heroes'].values()
                   if item['rarity'] >= 2
                   and item['heroId'] not in HERO_ONMYOJI]

    result = {}
    for item in data_heroes:
        skills = sorted(item['skinfo'], key=lambda x: x[0])
        skills = ''.join([str(max(one[1], 1)) for one in skills])
        if item['name'] in result:
            result[item['name']]['all'].append(skills)
        else:
            result[item['name']] = {
                'rarity': item['rarity'],
                'sort': item['heroId'],
                'x': False,
                'max': None,
                'all': [skills]
            }
    return result


def fetch_config():
    global DATA_SOURCE_CONFIG
    print(log('正在读取式神图鉴数据...', 'info'))
    url_heroes = 'https://cbg-yys.res.netease.com/js/game_auto_config.js'
    req = request.Request(url=url_heroes, headers={
        'User-Agent': USER_AGENT
    })
    data = request.urlopen(req, timeout=4).read().decode('utf-8')
    r = re.search(r'({.+})', data)
    if not r:
        return
    DATA_SOURCE_CONFIG = json.loads(r.group(1))


def fetch_equip(url_equip):
    global DATA_SOURCE_EQUIP
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
    DATA_SOURCE_EQUIP = json.loads(result)


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
    try:
        opts, args = getopt.getopt(
            args,
            'hvu:',
            ['help', 'version', 'url=']
        )
    except getopt.GetoptError:
        opts, args = [('-h', '')], []
    url_equip, helped = None, False
    for opt, value in opts:
        if opt in ('-h', '--help'):
            print(COPYRIGHT)
            print(HELP)
            helped = True
        elif opt in ('-v', '--version'):
            print(VERSION)
            helped = True
        elif opt in ('-u', '--url'):
            url_equip = value
    if not url_equip and args:
        url_equip = args[0]
    if not helped and not url_equip:
        print(COPYRIGHT)
        print(HELP)
    return url_equip


def run_as_exe():
    """判断本程序运行环境

    判断本程序是否已被封装为 EXE 执行，若如此可实现一些特性，如控制台进度条效果。
    IDE 中执行原生 .py 一般无法实现此效果。

    Returns:
        bool: True 为 Windows EXE，False 视为原生 .py 脚本
    """
    return path.splitext(sys.argv[0])[1] == '.exe'


def main():
    if len(sys.argv) > 1:
        url_equip = parse_args(sys.argv[1:])
        if not url_equip:
            return
        print(COPYRIGHT)
    else:
        print(COPYRIGHT)
        url_equip = input('藏宝阁链接: ')

    # data_config = fetch_config()
    # data_equip = fetch_equip(url_equip)
    thread_fetch_config = Thread(target=fetch_config)
    thread_fetch_equip = Thread(target=fetch_equip, args=(url_equip,))
    thread_fetch_config.start()
    thread_fetch_equip.start()
    thread_fetch_config.join()
    thread_fetch_equip.join()
    if not DATA_SOURCE_CONFIG or not DATA_SOURCE_EQUIP:
        print(log('抓取数据过程出错', 'error'))
        return

    data_hero_book = get_hero_book(DATA_SOURCE_CONFIG)

    data_hero_x = get_hero_x(DATA_SOURCE_EQUIP)
    for name, item in data_hero_book.items():
        item['x'] = name in data_hero_x

    for name, item in data_hero_book.items():
        item['max'] = HERO_SKILL_MAX.get(name, None)

    data_hero_own = get_hero_own(DATA_SOURCE_EQUIP)
    for name, item in data_hero_book.items():
        if name in data_hero_own:
            item['all'] = data_hero_own[name]['all']
        else:  # 式神未拥有置 None，未知置空
            item['all'] = None if item['rarity'] >= 4 else []

    damo_yx_own_cost = get_damo_yx(DATA_SOURCE_EQUIP)
    print(log('黑蛋拥有量+推测已消耗量: %d+%d' % damo_yx_own_cost, 'info'))

    save(DATA_SOURCE_EQUIP, data_hero_book, damo_yx_own_cost)


if __name__ == '__main__':
    try:
        main()
    except Exception:
        raise
    finally:
        if run_as_exe():  # 避免窗口一闪而逝
            os.system('pause')
