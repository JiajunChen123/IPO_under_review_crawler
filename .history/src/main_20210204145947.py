#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   main.py
@Time    :   2021/02/04 14:06:31
@Author  :   Jiajun Chen 
@Version :   1.0
@Contact :   554001000@qq.com
@License :   (C)Copyright 2017-2018, Liugroup-NLPR-CASIA
'''



from szcyb_crawler import szcyb_check_update
from shkcb_crawler import shkcb_check_update
from east-money import update_eastmoneyData

if __name__ == '__main__':
    szcyb_check_update()
    shkcb_check_update()

update_eastmoneyData