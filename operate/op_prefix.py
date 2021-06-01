# !/usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = 'ufoxu'

"""date：2021.06.01
roles:  日志
usage:
notice: logging.getLogger('log_name')都会返回同一个logger实例
        logging.basicConfig(**kwargs)日志记录器已经为其配置了处理程序，则此函数不执行任何操作
update: date：2021.06.01
"""

import logging, logging.handlers
import os
import re
import sys
import time

reload(sys)
sys.setdefaultencoding('utf8')


class Utils(object):

    def __init__(self, path):
        self.filename = path

    _LOG_LEVEL = "DEBUG"

    __logger = None

    file_ha = None

    @property
    def logging(self):

        if self.__logger:
            return self.__logger

        if not os.path.exists(os.path.dirname(self.filename)):
            os.makedirs(os.path.dirname(self.filename))

        formatter = logging.Formatter('%(asctime)s %(filename)s[line:%(lineno)d] '
                                      '%(levelname)s %(message)s', "%Y-%m-%d %H:%M:%S")

        log_fileter = "LOG:{0}".format(self.filename)

        self.__logger = logging.getLogger(log_fileter)

        self.__logger.setLevel(getattr(logging, self._LOG_LEVEL, logging.DEBUG))

        #: 开一个FileHandler日志输出通道
        try:
            self.file_ha = logging.handlers.RotatingFileHandler(self.filename, maxBytes=1000000000, backupCount=10)
        except Exception as e:
            sys.stdout.write(e)
            self.file_ha = logging.FileHandler(self.filename, "a", encoding='utf-8')

        self.file_ha.setLevel(getattr(logging, self._LOG_LEVEL, logging.DEBUG))

        self.file_ha.setFormatter(formatter)

        self.__logger.addHandler(self.file_ha)

        return self.__logger

    @staticmethod
    def outpu(message):
        sys.stdout.write(str(message))
        sys.stdout.write("\n")
        sys.stdout.flush()
        sys.stderr.flush()
        return 0

    def __del__(self):
        self.__logger.removeHandler(self.file_ha)
