# !/usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = 'ufoxu'

"""date：2021.06.01
roles:  ansible
usage:
notice:
update: date：2021.06.01
"""

import commands
import sys
import os
from operate.op_prefix import Utils
from operate.op_ansible import AdHocRunner

reload(sys)
sys.setdefaultencoding('utf8')


#: 获取服务器硬件信息
def ansible_get_setup(linux_hosts):

    _options = {
        'forks': 500,
        'passwords': dict(conn_pass='123456', become_pass='123456'), #: 定义默认的密码连接，主机未定义密码的时候才生效，conn_pass指连接远端的密码，become_pass指提升权限的密码
    }

    runner = AdHocRunner(linux_hosts, _options)
    tasks = [
        {"action": {"module": "setup"}, "name": "run_setup"},
    ]
    ret = runner.run(tasks, "all")
    datastructure = ret.results_raw

    #: 处理结果信息
    # ansible_result = run_setup_result(datastructure)
    # _log.logging.info(ansible_result)
    return datastructure


if __name__ == "__main__":
    #: 脚本名, 脚本名前缀, 脚本路径
    script_name = os.path.basename(__file__)
    sub_name = script_name.split('.')[0]
    path_name = os.path.abspath(__file__)[:-len(script_name)]

    #: 配置文件路径
    conf_pwd = os.path.join(path_name, 'conf')
    conf_sub = os.path.join(conf_pwd, '%s.conf' % sub_name)

    #: 日志路径&日志处理
    log_path = os.path.join(path_name, "logs", '%s.log' % (script_name,))
    script_info = ' '.join(sys.argv)
    _log = Utils(log_path)
    _log.logging.info('%s start' % script_info)
    _log.outpu('%s start' % script_info)

    last_code = 0
    #: 定义变量
    server_list = ['10.0.0.1']
    #: 功能函数

    host_info = ansible_get_setup(server_list)

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
