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
    hero_rarity = {5: 'sp', 4: 'ssr', 3: 'sr', 2: 'r', 1: 'n'}  # 式神稀有度索引
    file_attach = None  # 所依附文件, 据此决定结果文件路径
    data_src = None
    rarity_visible = ['x', 'sp', 'ssr', 'sr', 'r']  # 设定显示的稀有度, 其他则不显示(X为联动)

    def __init__(self, file_attach, data_src, rarity_visible=None):
        self.file_attach = file_attach
        self.data_src = data_src
        if rarity_visible:
            self.rarity_visible = rarity_visible

    def generate_path_base(self):
        return None

    def get_title(self):
        return None

    def get_feet(self):
        return tuple()

    def parse(self, data_hero_book):
        return None


class CbgParser(Parser):
    hero_onmyoji = {
        10: '晴明', 11: '神乐', 13: '源博雅', 12: '八百比丘尼',
        900: '神龙', 901: '白藏主', 903: '黑豹', 902: '孔雀'
    }  # 阴阳师及其御灵稀有度均被设定为SSR, 即 item['rarity'] == 4
    rarity_fragment = {5: 60, 4: 50, 3: 40, 2: 30, 1: 25}  # 各稀有度碎片合成量
    data_equip = None

    def __init__(self, file_attach, data_src, rarity_visible=None):
        Parser.__init__(self, file_attach, data_src, rarity_visible)

        self.data_equip = json.loads(data_src['equip']['equip_desc'])

    def _get_hero_x(self):
        return {item[0]: item[1] == 1
                for item in self.data_equip['hero_history']['x'].values()
                if type(item) is list}

    def _get_hero_own(self):
        data_heroes = [item for item in self.data_equip['heroes'].values()
                       if item['heroId'] not in self.hero_onmyoji]

        result = {}
        for item in data_heroes:
            skills = sorted(item['skinfo'], key=lambda x: x[0])
            skills = ''.join([str(one[1]) for one in skills if one[1] > 0])
            if item['name'] in result:
                result[item['name']]['all'].append(skills)
            else:
                result[item['name']] = {'all': [skills]}
        return result

    def _get_hero_fragment(self):
        # 仅 SP、SSR 有数据
        return {item['name']: item['num']
                for item in self.data_equip['hero_fragment'].values()}

    def _get_damo_yx(self):
        """获取黑蛋保有量+消耗量
        注: 两者均为保守估计，前者未包含碎片合成量，后者无法统计到浪费在非SP/SSR的量
        """
        data_damo = self.data_equip['damo_count_dict']
        data_hero = list(self.data_equip['heroes'].values())
        data_sp_ssr = [item for item in data_hero if (
                item['rarity'] == 5 or item['rarity'] == 4
        ) and item['heroId'] not in self.hero_onmyoji]
        sum_own = sum([num for damoes in data_damo.values()
                       for damo, num in damoes.items()
                       if damo == '411'])
        sum_cost = sum([max(info[1] - 1, 0) for hero in data_sp_ssr
                        for info in hero['skinfo']])
        return '御行达摩保有/消耗量: %d+/%d+' % (sum_own, sum_cost)

    def _get_hero_history(self, rarity_target):
        rarity_readable = {'x': '联动', 'sp': 'SP', 'ssr': 'SSR', 'sr': 'SR',
                           'r': 'R', 'gua': '呱'}
        data_history = self.data_equip['hero_history']
        result = '式神图鉴:'
        for key, name in rarity_readable.items():
            if key in rarity_target and key in data_history:
                result += ' %s %d/%d' % (
                    rarity_readable[key],
                    data_history[key]['got'],
                    data_history[key]['all']
                )
        return result

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
        hero_history = self._get_hero_history(self.rarity_visible)

        return damo_yx, hero_history

    def parse(self, data_hero_book: dict):
        data_new = copy.deepcopy(data_hero_book)

        # 识别联动式神
        data_hero_x = self._get_hero_x()
        for name, item in data_new.items():
            item['x'] = name in data_hero_x

        # 合并式神录
        data_hero_own = self._get_hero_own()
        for name, item in data_new.items():
            if name in data_hero_own:
                item['all'] = data_hero_own[name]['all']
            elif item['rarity'] >= 4:
                item['all'] = None  # 式神缺失置 None
            elif item['x']:
                item['all'] = [] if data_hero_x.get(name, False) else None
            else:
                item['all'] = []  # 式神未知置空

        # 加入碎片存量
        data_fragment = self._get_hero_fragment()
        for name, item in data_new.items():
            item['fragment'] = {
                'own': data_fragment.get(
                    name, 0 if item['rarity'] >= 4 else None
                ),
                'max': self.rarity_fragment[item['rarity']]
            }

        # 稀有度过滤
        for name in list(data_new.keys()):
            item = data_new[name]
            if item['x']:
                if 'x' not in self.rarity_visible:
                    del data_new[name]
            elif self.hero_rarity[item['rarity']] not in self.rarity_visible:
                del data_new[name]

        return data_new


class YyxParser(Parser):
    # map_rarity = {'SP': 5, 'SSR': 4, 'SR': 3, 'R': 2, 'N': 1}  # 稀有度索引映射
    heroes_x = (
        '奴良陆生',
        '卖药郎',
        '鬼灯', '阿香', '蜜桃&芥子',
        '犬夜叉', '杀生丸', '桔梗',
        '黑崎一护', '朽木露琪亚',
        '灶门炭治郎', '灶门祢豆子'
    )  # TODO: 联动式神(需维护, 痒痒熊导出数据并非标记联动)
    data_equip = None

    def __init__(self, file_attach, data_src, rarity_visible=None):
        Parser.__init__(self, file_attach, data_src, rarity_visible)

        self.data_equip = data_src['data']

    def _get_hero_own(self):
        data_heroes = self.data_equip['heroes']

        result = {}
        for item in data_heroes:
            skills = sorted(item['skills'], key=lambda x: x['id'])
            skills = ''.join([str(one['level']) for one in skills])
            if item['hero_id'] in result:
                result[item['hero_id']]['all'].append(skills)
            else:
                result[item['hero_id']] = {'all': [skills]}
        return result

    def _get_hero_fragment(self):
        data_fragment = self.data_equip['hero_book_shards']
        return {item['hero_id']: {
            'own': item['shards'],
            'max': item['book_max_shards']
        } for item in data_fragment}

    def _get_damo_yx(self):
        """获取黑蛋保有量+消耗量
        注: 两者均为保守估计，前者未包含碎片合成量，后者无法统计到浪费在非SP/SSR的量
        """
        data_hero = self.data_equip['heroes']
        data_fragment = self._get_hero_fragment()
        data_sp_ssr = [item for item in data_hero
                       if item['rarity'] == 'SP' or item['rarity'] == 'SSR']
        sum_own = len([item for item in data_hero if item['hero_id'] == 411])
        sum_own_f = data_fragment[411]['own'] // data_fragment[411]['max']
        sum_cost = sum([info['level'] - 1 for hero in data_sp_ssr
                        for info in hero['skills']])
        return '御行达摩保有/消耗量: %d+%d/%d+' % (sum_own, sum_own_f, sum_cost)

    def generate_path_base(self):
        return path.splitext(self.file_attach)[0]

    def get_title(self):
        username = self.data_equip['player']['name']
        return '阴阳师·技能图鉴: @%s' % username

    def get_feet(self):
        # 获取黑蛋保有量+消耗量
        damo_yx = self._get_damo_yx()

        return (damo_yx,)

    def parse(self, data_hero_book):
        data_new = copy.deepcopy(data_hero_book)

        # 识别联动式神
        for name, item in data_new.items():
            item['x'] = name in self.heroes_x

        # 合并式神录
        data_hero_own = self._get_hero_own()
        for name, item in data_new.items():
            if item['sort'] in data_hero_own:
                item['all'] = data_hero_own[item['sort']]['all']
            else:
                item['all'] = None  # 式神缺失置 None

        # 加入碎片存量
        data_fragment = self._get_hero_fragment()
        for name, item in data_new.items():
            item['fragment'] = data_fragment.get(item['sort'], 0)

        # 稀有度过滤
        for name in list(data_new.keys()):
            item = data_new[name]
            if item['x']:
                if 'x' not in self.rarity_visible:
                    del data_new[name]
            elif self.hero_rarity[item['rarity']] not in self.rarity_visible:
                del data_new[name]

        return data_new


if __name__ == '__main__':
    print('module: parser')
