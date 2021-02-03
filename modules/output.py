#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
模块：将文字内容优化排版生成图片
"""

import re

try:
    from PIL import Image
    from PIL import ImageDraw
    from PIL import ImageFont
except ModuleNotFoundError:
    Image, ImageDraw, ImageFont = None, None, None

from modules import util


class Output(object):
    def __init__(self):
        self.__font_size = 16  # 主文本字体大小
        self.__font_size_2 = 14  # 次文本字体大小
        self.__margin = (24, 24, 24, 24)  # 页边距
        self.__margin_head = 20  # 页眉-正文间距
        self.__margin_foot = 20  # 正文-页脚间距
        self.__margin_line = 4  # 行距
        self.__margin_paragraph = 10  # 段距
        self.__margin_column = 80  # 列距
        self.__margin_tag = 16  # 标签色块占距
        self.__unit = 4
        self.__color_bg = '#2b2b2b'  # 背景色
        self.__color_fg = '#bbbbbb'  # 前景色（文本颜色）
        self.__color_fg_2 = '#555555'  # 次前景色
        self.__color_tags = {
            'skillFull': '#5394ec',
            'heroLost': '#cc666e',
            'heroUnknown': self.__color_fg,
            'normal': self.__color_fg_2
        }  # 各级色块标签

    def _draw_mark_margin(self, draw, margin, size_page):
        index_end = (size_page[0] - 1, size_page[1] - 1)
        index_rectangles = (
            (0, 0, margin[0] - 1, self.__unit - 1),
            (0, 0, self.__unit - 1, margin[1] - 1),
            (index_end[0] - margin[2] + 1, 0, index_end[0], self.__unit - 1),
            (index_end[0] - self.__unit + 1, 0, index_end[0], margin[1] - 1),
            (index_end[0] - margin[2] + 1, index_end[1] - self.__unit + 1,
             index_end[0], index_end[1]),
            (index_end[0] - self.__unit + 1, index_end[1] - margin[3] + 1,
             index_end[0], index_end[1]),
            (0, index_end[1] - self.__unit + 1, margin[0] - 1, index_end[1]),
            (0, index_end[1] - margin[3] + 1, self.__unit - 1, index_end[1])
        )
        for index in index_rectangles:
            draw.rectangle(index, fill=self.__color_fg_2)

    def _draw_mark_paragraph(self, draw, index_paragraphs):
        offset = 14
        for paragraph in index_paragraphs:
            index = paragraph['index']
            color_tag = self.__color_tags[paragraph['level']]
            draw.rectangle((index[0] - offset, index[1],
                            index[2] - offset + self.__unit - 1, index[3]),
                           fill=color_tag)

    def _size_column(self, font, content):
        height_line = sum(font.getmetrics())
        width_lines = []
        height = 0
        for i, paragraph in enumerate(content):
            if i > 0:
                height += self.__margin_paragraph
            for j, line in enumerate(paragraph):
                width_lines.append(font.getsize(line)[0])
                if j > 0:
                    height += self.__margin_line
                height += height_line
        return max(width_lines), height
    
    def _size_canvas(self, font, font_2, content, head, foot):
        height_line_2 = sum(font_2.getmetrics())
        
        width_main = 0
        height_main = 0
        for i, column in enumerate(content):
            size_column = self._size_column(font, column)
            if i > 0:
                width_main += self.__margin_column
            width_main += self.__margin_tag + size_column[0]
            height_main = max(height_main, size_column[1])
        if head:
            width_main = max(width_main,
                             self.__margin_tag + font_2.getsize(head)[0])
            height_main += height_line_2 + self.__margin_head
        if foot:
            width_main = max(width_main,
                             self.__margin_tag + font_2.getsize(foot)[0])
            height_main += self.__margin_foot + height_line_2
        return (width_main + self.__margin[0] + self.__margin[2],
                height_main + self.__margin[1] + self.__margin[3])

    def text2img(self, file_font, file_out, content, head=None, foot=None):
        font = ImageFont.truetype(file_font, size=self.__font_size)  # 主文本字体
        font_2 = ImageFont.truetype(file_font, size=self.__font_size_2)  # 次文本字体
        size_img = self._size_canvas(font, font_2, content, head, foot)  # 预计算图片大小
        image = Image.new('RGB', size_img, self.__color_bg)
        draw = ImageDraw.Draw(image)
        # 放弃通过 font.getsize('xx')[1] 计算行高
        height_line = sum(font.getmetrics())  # 主文本行高
        height_line_2 = sum(font_2.getmetrics())  # 次文本行高
        index_column_line = [[self.__margin[0] + self.__margin_tag,
                              self.__margin[1]]]  # 下一行索引
        index_paragraphs = []  # 段索引
        if head:  # 绘制页眉
            draw.text(index_column_line[0], head,
                      fill=self.__color_fg_2, font=font_2)
            index_column_line[0][1] += height_line_2 + self.__margin_head
        for column in content:
            size_column = self._size_column(font, column)
            index_column_line.append([
                index_column_line[-1][0] + size_column[0]
                + self.__margin_column + self.__margin_tag,
                index_column_line[0][1]
            ])
        for i, column in enumerate(content):
            index_line = index_column_line[i]
            for j, paragraph in enumerate(column):
                if j > 0:
                    index_line[1] -= self.__margin_line
                    index_line[1] += self.__margin_paragraph
                index_paragraph = [index_line[0], index_line[1],
                                   index_line[0], 0]
                tag_level = 'normal'
                for k, line in enumerate(paragraph):
                    if k == 0:
                        tag_level = _level_tag(line)
                    draw.text(index_line, line, fill=self.__color_fg, font=font)
                    index_line[1] += height_line + self.__margin_line
                index_paragraph[3] = index_line[1] - self.__margin_line - 1
                index_paragraphs.append({
                    'index': index_paragraph, 'level': tag_level
                })
        if foot:  # 绘制页脚
            index_line = [index_column_line[0][0],
                          max([index[1] for index in index_column_line])]
            index_line[1] -= self.__margin_line
            index_line[1] += self.__margin_foot
            draw.text(index_line, foot, fill=self.__color_fg_2, font=font_2)
            index_line[1] += height_line_2 + self.__margin_line
        # self._draw_mark_margin(draw, MARGIN, size_img)
        self._draw_mark_paragraph(draw, index_paragraphs)
        image.save(file_out, 'png')
        # image.show()  # 会导致主进程挂起


def _level_tag(line):
    obj = re.match(r'^.+ (.+?)(?:/(.+))?$', line)
    if not obj:
        return 'normal'
    if obj.group(1) == '???':  # 未知
        return 'heroUnknown'
    if obj.group(1) == '---':  # 式神未拥有
        return 'heroLost'
    if obj.group(2) and obj.group(1) == obj.group(2):  # 满技能
        return 'skillFull'
    return 'normal'


def _score_skill(skill):
    return sum([int(num) for num in skill])


def _data2text(data):
    data_x = [{**{'name': name}, **item}
              for name, item in data.items() if item['x']]
    data_not_x = [{**{'name': name}, **item}
                  for name, item in data.items() if not item['x']]

    data_columns = [sorted(
        data_x,
        key=lambda x: x['sort']
    )] if data_x else []
    rarities = sorted(list({item['rarity'] for item in data_not_x}),
                      reverse=True)
    for rarity in rarities:
        data_columns.append(sorted(
            [item for item in data_not_x if item['rarity'] == rarity],
            key=lambda x: x['sort']
        ))
        
    result = []
    for column in data_columns:
        result_columns = []
        for i, item in enumerate(column):
            if not item['all']:
                result_columns.append(['%s  %s%s' % (
                    item['name'],
                    '---' if item['all'] is None else '???',
                    ('/%s' % item['max']) if item['max'] else ''
                )])
                continue
            skill_all = sorted(item['all'],
                               key=lambda x: _score_skill(x),
                               reverse=True)
            lines = ['%s  %s' % (item['name'], skill)
                     for skill in skill_all[1:]]
            lines.insert(0, '%s  %s%s' % (
                item['name'],
                skill_all[0],
                ('/%s' % item['max']) if item['max'] else ''
            ))
            result_columns.append(lines)
        result.append(result_columns)
    return result


def enabled():
    try:
        import PIL
    except ModuleNotFoundError:
        return False
    return util.font_ok()


def text2img(file_out, data, head=None, foot=None):
    o = Output()
    o.text2img(util.font(), file_out, _data2text(data), head, foot)


if __name__ == '__main__':
    print('module: output')
