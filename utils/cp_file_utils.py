# -*- coding: utf-8 -*-
# !/usr/bin/env python
"""
-------------------------------------------------
   File     : cp_file_utils.py
   Author   : CoderPig
   date     : 2021-11-08 10:40 
   Desc     : 自用文件操作类
-------------------------------------------------
"""
import os
import shutil
import threading
import hashlib

lock = threading.RLock()


def is_dir_existed(file_path, mkdir=True, is_recreate=False):
    """ 判断目录是否存在，不存在则创建

    Args:
        file_path (str): 文件路径
        mkdir (bool): 不存在是否新建
        is_recreate (bool): 存在是否删掉重建

    Returns:
        默认返回None，如果mkdir为False返回文件是否存在
    """
    if mkdir:
        if not os.path.exists(file_path):
            os.makedirs(file_path)
        else:
            if is_recreate:
                delete_file(file_path)
                os.makedirs(file_path)
    else:
        return os.path.exists(file_path)


def delete_file(file_path):
    """ 根据传入的文件路径删除文件

    Args:
        file_path (str): 文件路径

    Returns:
        None
    """
    del_list = os.listdir(file_path)
    for f in del_list:
        file_path = os.path.join(file_path, f)
        if os.path.isfile(file_path):
            os.remove(file_path)
        elif os.path.isdir(file_path):
            shutil.rmtree(file_path)


def fetch_all_file_list(file_dir=os.getcwd()):
    """ 获取目录下所有文件路径列表

    Args:
        file_dir (str): 文件目录

    Returns:
        list (str): 文件路径列表
    """
    return list(map(lambda x: os.path.join(file_dir, x), os.listdir(file_dir)))


def filter_file_type(file_dir=os.getcwd(), file_suffix=''):
    """ 获取目录下特定后缀的文件路径列表

    Args:
        file_dir (str): 文件目录
        file_suffix (str): 文件后缀

    Returns:
        list (str): 文件路径列表
    """
    result_list = []
    file_path_list = fetch_all_file_list(file_dir)
    for file_path in file_path_list:
        if file_path.endswith(file_suffix):
            result_list.append(file_path)
    return result_list


# 获取目录下包含字符串的文件路径列表
def filter_file_by_string(file_dir, content):
    """ 获取目录下包含字符串的文件路径列表

    Args:
        file_dir (str): 文件目录
        content (str): 特定字符串

    Returns:
        list: 文件路径列表
    """
    result_list = []
    file_path_list = fetch_all_file_list(file_dir)
    if len(file_path_list) > 0:
        for file_path in file_path_list:
            if file_path.find(content) != -1:
                result_list.append(file_path)
    return result_list


def search_all_file(file_dir=os.getcwd(), target_suffix_tuple=()):
    """ 递归遍历文夹与子文件夹中的特定后缀文件

    Args:
        file_dir (str): 文件目录
        target_suffix_tuple (str): 文件目录

    Returns:
        list : 文件路径列表
    """
    file_list = []
    # 切换到目录下
    os.chdir(file_dir)
    file_name_list = os.listdir(os.curdir)
    for file_name in file_name_list:
        # 获取文件绝对路径
        file_path = "{}{}{}".format(os.getcwd(), os.path.sep, file_name)
        # 判断是否为目录，是往下递归
        if os.path.isdir(file_path):
            print("[-]", file_path)
            file_list.extend(search_all_file(file_path, target_suffix_tuple))
            os.chdir(os.pardir)
        elif target_suffix_tuple is not None and file_name.endswith(target_suffix_tuple):
            print("[!]", file_path)
            file_list.append(file_path)
        else:
            print("[+]", file_path)
    return file_list


def read_file_text_content(file_path):
    """ 以文本形式读取文件内容

    Args:
        file_path (str): 文件路径

    Returns:
        str: 文件内容
    """
    if not os.path.exists(file_path):
        return None
    else:
        with open(file_path, 'r+', encoding='utf-8') as f:
            return f.read()


def write_text_to_file(content, file_path, mode="w+"):
    """ 将文字写入到文件中

    Args:
        content (str): 文字内容
        file_path (str): 写入文件路径
        mode (str): 文件写入模式，w写入、a追加、+可读写

    Returns:
        None
    """
    with lock:
        try:
            with open(file_path, mode, encoding='utf-8') as f:
                f.write(content + "\n", )
        except OSError as reason:
            print(str(reason))


def write_text_list_to_file(content_list, file_path, mode="w+"):
    """ 将文字列表写入到文件中

    Args:
        content_list (list): 文字列表
        file_path (str): 写入文件路径
        mode (str): 文件写入模式，w写入、a追加、+可读写

    Returns:
        None
    """
    try:
        with open(file_path, mode, encoding='utf-8') as f:
            for content in content_list:
                f.write(content + "\n", )
    except OSError as reason:
        print(str(reason))


def get_file_md5(file_path):
    """ 计算文件md5

    Args:
        file_path (str): 文件路径

    Returns:
        str: 文件md5
    """
    m = hashlib.md5()
    try:
        with lock:
            with open(file_path, 'rb') as f:
                while True:
                    data = f.read(4096)
                    if not data:
                        break
                    m.update(data)
            return m.hexdigest()
    except OSError as reason:
        print(str(reason))


def get_str_md5(content):
    """ 计算字符串md5

    Args:
        content (str): 字符串内容

    Returns:
        str: 文件md5
    """
    m = hashlib.md5(content.encode('utf-8'))
    return m.hexdigest()


def copy_file(src_file, dst_file):
    f_path, f_name = os.path.split(dst_file)
    is_dir_existed(f_path)
    shutil.copyfile(src_file, dst_file)


if __name__ == '__main__':
    print(get_str_md5('test'))
