# !/usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = 'ufoxu'

"""date：2021.06.01
roles:  model
usage:
notice:
update: date：2021.06.01
"""

import commands
import sys
import os
from operate.op_prefix import Utils

reload(sys)
sys.setdefaultencoding('utf8')


def start_():
    try:
        cmd = "pwd"
        (status, output) = commands.getstatusoutput(cmd)
        return 0
    except Exception as e:
        _log.outpu(e)
        _log.logging.exception(e, )
    return 1


if __name__ == "__main__":
    #: 脚本名, 脚本名前缀, 脚本路径
    script_name = os.path.basename(__file__)
    sub_name = script_name.split('.')[0]
    path_name = os.path.abspath(__file__)[:-len(script_name)]

    #: 配置文件路径
    conf_pwd = os.path.join(path_name, 'conf')
    conf_sub = os.path.join(conf_pwd, '%s.conf' % sub_name)

    #: 日志路径&日志处理 日志最好写绝对路径
    log_path = os.path.join(path_name, "logs", '%s.log' % (script_name,))
    script_info = ' '.join(sys.argv)
    _log = Utils(log_path)
    _log.logging.info('%s start' % script_info)
    _log.outpu('%s start' % script_info)

    last_code = 0
    #: 定义变量

    #: 功能函数
    last_code += start_()


    #: 确认脚本是否成功
    sys.stdout.write('\n')
    sys.stdout.flush()
    if last_code == 0:
        _log.logging.info("success end")
        _log.outpu("success end")
    else:
        _log.outpu("error end")
        _log.logging.warning("error end")
        sys.exit(2)
    _log.__del__()
