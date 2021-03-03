#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
模块：数据解析器：藏宝阁数据、痒痒熊导出数据
"""

import copy
import datetime
import json
import os
import re
from os import path


class Parser(object):
    hero_rarity2 = {
        6: {'name': '联动', 'visible': True},
        5: {'name': 'SP', 'visible': True},
        4: {'name': 'SSR', 'visible': True},
        3: {'name': 'SR', 'visible': True},
        2: {'name': 'R', 'visible': True},
        1: {'name': 'N', 'visible': False},
        0: {'name': '呱', 'visible': False},
        -1: {'name': '素材', 'visible': False}
    }  # 式神稀有度索引, 名称, 输出可见性 (官方仅 5 4 3 2 1, 6 0 -1 为自定)
    hero_gua = {
        414: '大天狗呱',
        415: '酒吞呱',
        416: '荒川呱',
        417: '阎魔呱',
        418: '两面佛呱',
        419: '小鹿男呱',
        420: '茨木呱',
        421: '青行灯呱',
        422: '妖刀姬呱',
        423: '一目连呱',
        424: '花鸟卷呱',
        425: '辉夜姬呱',
        426: '荒呱',
        427: '彼岸花呱'
    }  # 呱
    hero_sc = {
        410: '招福达摩',
        411: '御行达摩',
        412: '奉为达摩',
        413: '大吉达摩',
        499: '鬼武达摩'
    }  # 素材
    hero_skill_max = {
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
    # TODO: 以上常量需留意随版本更新而检查更新
    file_attach = None  # 所依附文件, 据此决定结果文件路径
    data_src = None

    def __init__(self, file_attach, data_src, hero_rarity2=None):
        self.file_attach = file_attach
        self.data_src = data_src
        if hero_rarity2:
            self.hero_rarity2 = hero_rarity2

    def parse(self, data_hero_book: dict):
        return None

    def generate_path_base(self):
        return None

    def get_title(self):
        return None

    def get_feet(self):
        return tuple()


class CbgParser(Parser):
    hero_onmyoji = {
        10: '晴明', 11: '神乐', 13: '源博雅', 12: '八百比丘尼',
        900: '神龙', 901: '白藏主', 903: '黑豹', 902: '孔雀'
    }  # 阴阳师及其御灵稀有度均被设定为SSR, 即 ?['rarity'] == 4
    data_equip = None

    def __init__(self, file_attach, data_src, hero_rarity2=None):
        Parser.__init__(self, file_attach, data_src, hero_rarity2)

        self.data_equip = json.loads(data_src['equip']['equip_desc'])

    def _get_damo_yx(self):
        """获取黑蛋保有量+消耗量
        注: 两者均为保守估计，前者未包含碎片合成量，后者无法统计到浪费在非SP/SSR的量
        """
        data_damo = self.data_equip['damo_count_dict']
        data_hero = list(self.data_equip['heroes'].values())
        data_sp_ssr = [item for item in data_hero if (
                item['rarity'] in (5, 4)
                and item['heroId'] not in self.hero_onmyoji
        )]
        sum_own = sum([num for damoes in data_damo.values()
                       for damo, num in damoes.items()
                       if damo == '411'])
        sum_cost = sum([max(info[1] - 1, 0) for hero in data_sp_ssr
                        for info in hero['skinfo']])
        return '御行达摩保有/消耗量: %d+/%d+' % (sum_own, sum_cost)

    def _get_hero_history(self):
        rarity2_index_to_key = {
            6: 'x', 5: 'sp', 4: 'ssr', 3: 'sr', 2: 'r', 1: 'n', 0: 'gua'
        }
        data_history = self.data_equip['hero_history']
        result = '图鉴收录:'
        for index, item in self.hero_rarity2.items():
            if (item['visible'] and index in rarity2_index_to_key
                    and rarity2_index_to_key[index] in data_history):
                result += ' %s %d/%d' % (
                    item['name'],
                    data_history[rarity2_index_to_key[index]]['got'],
                    data_history[rarity2_index_to_key[index]]['all']
                )
        return result

    def _fix_rarity(self, data_hero_book: dict):
        hero_x = {
            int(k): v[0]
            for k, v in self.data_equip['hero_history']['x'].items()
            if type(v) is list
        }
        for name, item in data_hero_book.items():
            if item['id'] in hero_x:
                item['rarity2'] = 6
            elif item['id'] in self.hero_gua:
                item['rarity2'] = 0
            elif item['id'] in self.hero_sc:
                item['rarity2'] = -1

    def _filter_rarity(self, data_hero_book: dict):
        for name in list(data_hero_book.keys()):
            rarity2 = data_hero_book[name]['rarity2']
            if not self.hero_rarity2[rarity2]['visible']:
                del data_hero_book[name]

    def _check_reel(self, data_hero_book: dict):
        hero_history = {
            v2[0]: v2[1]
            for v1 in self.data_equip['hero_history'].values()
            for v2 in v1.values() if type(v2) is list
        }  # 仅包含 SP, SSR, 联动
        for name, item in data_hero_book.items():
            item['colored'] = (hero_history[name] == 1
                               if name in hero_history else None)

    def _load_skill(self, data_hero_book: dict):
        data_hero = [item for item in self.data_equip['heroes'].values()
                     if item['heroId'] not in self.hero_onmyoji]
        data_skill = {}
        for item in data_hero:
            skills = sorted(item['skinfo'], key=lambda x: x[0])
            skills = ''.join([str(one[1]) for one in skills if one[1] > 0])
            if item['name'] in data_skill:
                data_skill[item['name']]['all'].append(skills)
            else:
                data_skill[item['name']] = {'all': [skills]}
        for name, item in data_hero_book.items():
            item['skill']['max'] = self.hero_skill_max.get(name, None)
            if name in data_skill:
                item['skill']['all'] = data_skill[name]['all']
            elif item['rarity'] in (5, 4):
                item['skill']['all'] = []  # 式神缺失置[]
            elif item['rarity2'] == 6 and item['colored'] is False:
                item['skill']['all'] = []  # 式神缺失置[]
            else:
                item['skill']['all'] = None  # 式神未知置None

    def _load_fragment(self, data_hero_book: dict):
        data_fragment = {
            item['name']: item['num']
            for item in self.data_equip['hero_fragment'].values()
        }  # 仅 SP、SSR 有数据
        for name, item in data_hero_book.items():
            item['fragment'] = data_fragment.get(
                name, 0 if item['rarity'] in (5, 4) else None
            )

    def parse(self, data_hero_book: dict):
        data_new = copy.deepcopy(data_hero_book)

        # 完善稀有度
        self._fix_rarity(data_new)

        # 稀有度过滤
        self._filter_rarity(data_new)

        # 检查图鉴点亮情况
        self._check_reel(data_new)

        # 装载式神录式神技能
        self._load_skill(data_new)

        # 装载碎片存量
        self._load_fragment(data_new)

        return data_new

    def generate_path_base(self):
        dir_cbg = path.join(path.dirname(path.abspath(self.file_attach)), 'cbg')
        if not path.isdir(dir_cbg):
            os.mkdir(dir_cbg)
        # 使用当前卖家角色昵称 equip_name，而非 seller_name，其会随买家再次上架而改变
        seller = self.data_src['equip']['equip_name']
        # 删除 Windows 文件名中不允许出现的字符, 以及无法正常显示且会导致 IO 异常的控制字符
        seller2 = re.sub(r'[\\/:?"<>|\u0000-\u001F\u007F-\u009F]', '', seller)
        t = datetime.datetime.strptime(self.data_src['equip']['create_time'],
                                       '%Y-%m-%d %H:%M:%S')
        return path.join(dir_cbg, 'cbg_%s_%s_%s_%s' % (
            self.data_src['equip']['area_name'],
            self.data_src['equip']['server_name'],
            seller2, t.strftime('%Y%m%d%H%M%S')
        ))

    def get_title(self):
        # 使用当前卖家角色昵称 equip_name，而非 seller_name，其会随买家再次上架而改变
        seller = self.data_src['equip']['equip_name']
        return '藏宝阁·阴阳师·技能图鉴: @%s' % seller

    def get_feet(self):
        # 获取黑蛋保有量+消耗量
        damo_yx = self._get_damo_yx()

        # 获取式神图鉴
        hero_history = self._get_hero_history()

        return damo_yx, hero_history


class YyxParser(Parser):
    hero_x = {
        294: '奴良陆生',
        305: '卖药郎',
        308: '鬼灯', 309: '阿香', 310: '蜜桃&芥子',
        313: '犬夜叉', 314: '杀生丸', 319: '桔梗',
        337: '黑崎一护', 336: '朽木露琪亚',
        359: '灶门炭治郎', 360: '灶门祢豆子'
    }  # TODO: 联动式神(需维护, 痒痒熊导出数据并非标记联动)
    data_equip = None

    def __init__(self, file_attach, data_src, hero_rarity2=None):
        Parser.__init__(self, file_attach, data_src, hero_rarity2)

        self.data_equip = data_src['data']

    def _get_damo_yx(self):
        """获取黑蛋保有量+消耗量
        注: 两者均为保守估计，前者未包含碎片合成量，后者无法统计到浪费在非SP/SSR的量
        """
        data_hero = self.data_equip['heroes']
        data_fragment = self.data_equip['hero_book_shards']
        data_sp_ssr = [item for item in data_hero
                       if item['rarity'] in ('SP', 'SSR')]
        id_damo_yx = 411
        sum_own = len([item for item in data_hero if item['hero_id'] == id_damo_yx])
        sum_own_f = 0
        for item in data_fragment:
            if item['hero_id'] == id_damo_yx:
                sum_own_f = item['shards'] // item['book_max_shards']
                break
        sum_cost = sum([info['level'] - 1 for hero in data_sp_ssr
                        for info in hero['skills']])
        return '御行达摩保有/消耗量: %d+%d/%d+' % (sum_own, sum_own_f, sum_cost)

    def _fix_rarity(self, data_hero_book: dict):
        for name, item in data_hero_book.items():
            if item['id'] in self.hero_x:
                item['rarity2'] = 6
            elif item['id'] in self.hero_gua:
                item['rarity2'] = 0
            elif item['id'] in self.hero_sc:
                item['rarity2'] = -1

    def _filter_rarity(self, data_hero_book: dict):
        for name in list(data_hero_book.keys()):
            rarity2 = data_hero_book[name]['rarity2']
            if not self.hero_rarity2[rarity2]['visible']:
                del data_hero_book[name]

    def _check_reel(self, data_hero_book: dict):
        for name, item in data_hero_book.items():
            item['colored'] = None  # 未知

    def _load_skill(self, data_hero_book: dict):
        data_hero = self.data_equip['heroes']
        data_skill = {}
        for item in data_hero:
            skills = sorted(item['skills'], key=lambda x: x['id'])
            skills = ''.join([str(one['level']) for one in skills])
            if item['hero_id'] in data_skill:
                data_skill[item['hero_id']]['all'].append(skills)
            else:
                data_skill[item['hero_id']] = {'all': [skills]}
        for name, item in data_hero_book.items():
            item['skill']['max'] = self.hero_skill_max.get(name, None)
            if item['id'] in data_skill:
                item['skill']['all'] = data_skill[item['id']]['all']
            else:
                item['skill']['all'] = []  # 式神缺失置[]

    def _load_fragment(self, data_hero_book: dict):
        data_fragment = self.data_equip['hero_book_shards']
        data_fragment = {item['hero_id']: item['shards']
                         for item in data_fragment}
        for name, item in data_hero_book.items():
            item['fragment'] = data_fragment.get(item['id'], 0)

    def parse(self, data_hero_book):
        data_new = copy.deepcopy(data_hero_book)

        # 完善稀有度
        self._fix_rarity(data_new)

        # 稀有度过滤
        self._filter_rarity(data_new)

        # 检查图鉴点亮情况
        self._check_reel(data_new)

        # 装载式神录式神技能
        self._load_skill(data_new)

        # 装载碎片存量
        self._load_fragment(data_new)

        return data_new

    def generate_path_base(self):
        return path.splitext(self.file_attach)[0]

    def get_title(self):
        username = self.data_equip['player']['name']
        return '阴阳师·技能图鉴: @%s' % username

    def get_feet(self):
        # 获取黑蛋保有量+消耗量
        damo_yx = self._get_damo_yx()

        return (damo_yx,)


if __name__ == '__main__':
    print('module: parser')
