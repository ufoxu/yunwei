# !/usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = 'ufoxu'

"""date：2021.06.01
roles:  ansible
usage:
https://github.com/ansible/ansible/blob/v2.9.10/lib/ansible/inventory/manager.py
https://github.com/ansible/ansible/blob/v2.9.10/lib/ansible/plugins/callback/default.py
https://github.com/ansible/ansible/blob/v2.9.10/lib/ansible/cli/adhoc.py
https://docs.ansible.com/ansible/latest/dev_guide/developing_api.html
https://serversforhackers.com/c/running-ansible-2-programmatically
notice:
update: date：2021.06.01
"""
from ansible.plugins.callback import CallbackBase
from ansible.parsing.dataloader import DataLoader
from ansible.vars.manager import VariableManager
from ansible.inventory.manager import InventoryManager
from ansible.playbook.play import Play
from ansible.executor.task_queue_manager import TaskQueueManager
from ansible.errors import AnsibleError
from ansible.module_utils.common.collections import ImmutableDict
from ansible import context
import ansible.constants as C
import json

# Create a callback plugin so we can capture the output
class ResultsCollectorJSONCallback(CallbackBase):
    """A sample callback plugin used for performing an action as results come in.

    If you want to collect all results into a single object for processing at
    the end of the execution, look into utilizing the ``json`` callback plugin
    or writing your own custom callback plugin.
    """

    def __init__(self, *args, **kwargs):
        super(ResultsCollectorJSONCallback, self).__init__(*args, **kwargs)
        self.results_raw = dict(ok={}, failed={}, unreachable={}, skipped={}) #: 详细信息

    def gather_result(self, tag, result):
        self._clean_results(result._result, result._task.action) #:清理
        host = result._host.get_name()
        task_name = result.task_name
        task_result = result._result

        if self.results_raw[tag].get(host):
            self.results_raw[tag][host][task_name] = task_result
        else:
            self.results_raw[tag][host] = {task_name: task_result}

    def v2_runner_on_unreachable(self, result):
        return self.gather_result("unreachable", result)

    def v2_runner_on_ok(self, result, *args, **kwargs):
        return self.gather_result("ok", result)

    def v2_runner_on_failed(self, result, *args, **kwargs):
        return self.gather_result("failed", result)

    def v2_runner_on_skipped(self, result, *args, **kwargs):
        return self.v2_runner_on_skipped("skipped", result)


#：ansible ADHoc Runner接口
class AdHocRunner(object):
    def __init__(self, host_list, options=None):
        if options:
            self.passwords = options.get("passwords", None)
            self.forks = options.get("forks", 10)
        self.loader = DataLoader() #: 用来加载解析yaml文件或JSON内容,并且支持vault的解密

        self.host_list = host_list
        host_str = ','.join(self.host_list)
        if len(self.host_list) == 1:
            host_str += ','
        self.inventory = InventoryManager(loader=self.loader, sources=host_str)

        self.variable_manager = VariableManager(  # 初始话需要的类,用来管理变量，包括主机、组、扩展等变量，该类在之前的Inventory内置
            loader=self.loader, inventory=self.inventory
        )
        #: 声明全局变量CLIArgs
        context.CLIARGS = ImmutableDict(connection='smart', module_path=None, forks=self.forks, become=None,
                                    become_method=None, become_user=None, check=False, diff=False)
    #: 检查task语法
    @staticmethod
    def check_module_args(module_name, module_args=''):
        if module_name in C.MODULE_REQUIRE_ARGS and not module_args:
            err = "No argument passed to '%s' module." % module_name
            raise AnsibleError(err)

    #: 检查当前分组
    def check_pattern(self, pattern):
        if not pattern:
            raise AnsibleError("Pattern `{}` is not valid!".format(pattern))
        if not self.inventory.list_hosts("all"):
            raise AnsibleError("Inventory is empty.")
        if not self.inventory.list_hosts(pattern):
            raise AnsibleError(
                "pattern: %s  dose not match any hosts." % pattern
            )

    def get_task_list(self, tasks):
        cleaned_tasks = []
        for task in tasks:
            self.check_module_args(task['action']['module'], task['action'].get('args'))
            cleaned_tasks.append(task)
        return cleaned_tasks


    def run(self, tasks, pattern, play_name='Ansible Ad-hoc', gather_facts='no'):
        """
        :param tasks: [{'action': {'module': 'shell', 'args': 'ls'}, ...}, ]
        :param pattern: all, *, or others
        :param play_name: The play name
        :return:
        """
        self.check_pattern(pattern)
        results_callback = ResultsCollectorJSONCallback()

        play_source = dict(
            name=play_name,
            hosts=pattern, # 匹配host_list中的主机的正则表达式, 也可以是host_list
            gather_facts=gather_facts,
            tasks=self.get_task_list(tasks)
        )

        play = Play().load(
            play_source,
            variable_manager=self.variable_manager,
            loader=self.loader,
        )

        tqm = TaskQueueManager(
            inventory=self.inventory,  #: 由ansible.inventory模块创建，用于导入inventory文件
            variable_manager=self.variable_manager,  #:由ansible.vars模块创建，用于存储各类变量信息
            loader=self.loader,     #: 由ansible.parsing.dataloader模块创建，用于数据解析
            #options=self.options,   #: 存放各类配置信息的数据字典 ansible 2.9.10 取消
            stdout_callback=results_callback, #: 回调函数,使用我们的自定义回调，而不是打印到stdout的``default``回调插件
            passwords= self.passwords, #: 登录密码，可设置加密信息
            run_additional_callbacks=C.DEFAULT_LOAD_CALLBACK_PLUGINS,
            run_tree=False,
            forks= context.CLIARGS['forks'], #fork数量
        )
        try:
            tqm.run(play)
            return results_callback
        except Exception as e:
            raise AnsibleError(e)
        finally:
            tqm.cleanup()
            self.loader.cleanup_all_tmp_files()
        # shutil.rmtree(C.DEFAULT_LOCAL_TMP, True)