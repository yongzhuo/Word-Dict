# !/usr/bin/python
# -*- coding: utf-8 -*-
# @time    : 2019/12/16 23:02
# @author  : Mo
# @function: count word freq for chinese word segnment


import json
import time
import os
import re


def txt_read(path_file, encode_type='utf-8'):
    """
        读取txt文件，默认utf8格式, 不能有空行
    :param file_path: str, 文件路径
    :param encode_type: str, 编码格式
    :return: list
    """
    list_line = []
    try:
        file = open(path_file, 'r', encoding=encode_type)
        while True:
            line = file.readline().strip()
            if not line:
                break
            list_line.append(line)
        file.close()
    except Exception as e:
        print(str(e))
    finally:
        return list_line


def save_json(json_lines, json_path):
    """
      保存json，
    :param json_lines: json 
    :param path: str
    :return: None
    """
    with open(json_path, 'w', encoding='utf-8') as fj:
        fj.write(json.dumps(json_lines, ensure_ascii=False))
    fj.close()


def cut_sentence(sentence):
    """
        分句
    :param sentence:str
    :return:list
    """
    re_sen = re.compile('[:;!?。：；？！\n\r]') #.不加是因为不确定.是小数还是英文句号(中文省略号......)
    sentences = re_sen.split(sentence)
    sen_cuts = []
    for sen in sentences:
        if sen and str(sen).strip():
            sen_cuts.append(sen)
    return sen_cuts


class WordCut:
    def __init__(self, path):
        self.dict_words = txt_read(path)
        self.dict_words_freq = {}
        for dw in self.dict_words:
            self.dict_words_freq[dw] = 0
        print("load words_1000w.txt ok!")

    def cut_search(self, sentence, len_word_max=105):
        """
            构建句子的词典概率有向图;
            jieba使用的是前缀字典替代前缀树,内存比前缀树小,且比前缀树快;
            基本思想是构建'大漠帝国:132','大漠帝','大漠:640','大':1024等，没有则置为0,
            搜索时候前缀不存在就跳出,不用继续下去了
        :param sentence: str, like '大漠帝国是谁'
        :param sentence: int, like 132
        :return: dict, like {0:[0,1], 1:[1]}
        """
        len_sen = len(sentence)
        dag_sen = []
        for i in range(len_sen):  # 前向遍历, 全切分
            enum_j = [sentence[i]]          # 单个字就是它本身
            for j in range(i+1, min(len_sen, len_word_max)):    # 遍历从当前字到句子末尾可能成词的部分, 当前的不取, 设置最大成词长度为105
                word_maybe = sentence[i:j+1]
                if word_maybe in self.dict_words_freq: # 字典dict比数组list快上百上千倍
                    enum_j.append(sentence[i:j+1])
            dag_sen += enum_j
        dag_sen = list(set(dag_sen))
        return dag_sen


path = "words_1000w.txt" # 超大词典, 接近一千万词语, 包括一般中/英文
path_dir = "corpus"
time_start = time.time()
# 获取一个目录下所有文件
path_files_all = []
for root,dirs,files in os.walk(path_dir):
    for file in files:
        path_files_all.append(os.path.join(root,file))
print("get file from corpus dir ok!")
# WordCut初始化
wc = WordCut(path)
words_dict = {}
for nf in path_files_all:
    if "__init__.py" not in nf:
        file = open(nf, 'r', encoding='utf-8')
        for line in file:
            line_st = line.strip()
            if line_st:
                sens = cut_sentence(line_st) # 切句,避免长句
                for sen in sens:
                    line_search = wc.cut_search(sen) #
                    for word in line_search:
                        if word not in words_dict:
                            words_dict[word] = 1
                        else:
                            words_dict[word] = words_dict[word] + 1
        save_json(words_dict, "words_dict.json") # 每处理玩一个文件保存一次,避免中断后重头跑起
        file.close()
        print(nf)
# 处理单个字, 解决单个字出现过多的问题
score_total = sum(words_dict.values())
nums = len(words_dict)
score_avg = int(score_total/nums)
for k,v in words_dict.items():
    if len(k) ==1:
        len_avg = len(str(score_avg))
        len_k = len(str(k))
        if len_k - len_avg > 0:
            words_dict[k] = int(words_dict[k]/((len_k-len_avg)*10))

save_json(words_dict, "words_dict.json")
print(time.time() - time_start)
gg = 0
