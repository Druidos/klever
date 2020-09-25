#
# Copyright (c) 2019 ISP RAS (http://www.ispras.ru)
# Ivannikov Institute for System Programming of the Russian Academy of Sciences
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import os
import re
import time
from datetime import datetime

from django.conf import settings
from django.db.models.base import ModelBase

from bridge.utils import BridgeException, logger
from tools.models import LockTable, CallLogs

# Waiting while other function try to lock with DB table + try to lock with DB table
# So maximum waiting time is (MAX_WAITING * 2) in seconds.
if settings.UNLOCK_FAILED_REQUESTS:
    MAX_WAITING = 30
else:
    MAX_WAITING = 300


def get_time():
    while True:
        try:
            return time.time()
        except Exception as e:
            logger.error(e)
            pass


class ExecLocker:
    lockfile = os.path.join(settings.BASE_DIR, 'media', '.lock')

    def __init__(self, name, groups):
        self.call_log = {
            'name': name,
            'enter_time': get_time()
        }
        self.names = self.__get_affected_models(groups)
        self.lock_ids = set()
        # wait1 and wait2
        self.waiting_time = [0, 0]

    def lock(self):
        if len(self.names) == 0:
            return
        # Lock with file while we locking with DB table
        while True:
            try:
                with open(self.lockfile, mode='x'):
                    break
            except FileExistsError:
                time.sleep(0.1)
                self.waiting_time[0] += 0.1
                if self.waiting_time[0] > MAX_WAITING:
                    if settings.UNLOCK_FAILED_REQUESTS:
                        try:
                            os.remove(self.lockfile)
                        except FileNotFoundError:
                            pass
                    else:
                        raise RuntimeError('Not enough time to lock execution of view')

        try:
            self.__lock_names()
        finally:
            try:
                os.remove(self.lockfile)
            except FileNotFoundError:
                pass

    def unlock(self, is_failed):
        self.call_log.update({
            'execution_delta': get_time() - self.call_log['execution_time'], 'is_failed': is_failed
        })

        if (not is_failed or settings.UNLOCK_FAILED_REQUESTS) and len(self.lock_ids) > 0:
            LockTable.objects.filter(id__in=self.lock_ids).update(locked=False)
        self.call_log['return_time'] = get_time()

    def save_exec_time(self):
        self.call_log.update({
            'execution_time': get_time(),
            'wait1': self.waiting_time[0],
            'wait2': self.waiting_time[1]
        })

    def __lock_names(self):
        can_lock = True
        names_in_db = set()
        # Get all created models in table with names in self.block
        for lt in LockTable.objects.filter(name__in=self.names):
            names_in_db.add(lt.name)
            self.lock_ids.add(lt.id)
            if lt.locked:
                can_lock = False

        # Are there models which aren't created yet?
        if len(names_in_db) < len(self.names):
            # Will be executed maximum 1 time per view function
            for l_name in set(self.names) - set(names_in_db):
                self.lock_ids.add(LockTable.objects.create(name=l_name).id)

        if not can_lock:
            while LockTable.objects.filter(id__in=self.lock_ids, locked=True).count() > 0:
                time.sleep(0.2)
                self.waiting_time[1] += 0.2
                if self.waiting_time[1] > MAX_WAITING:
                    if settings.UNLOCK_FAILED_REQUESTS:
                        break
                    raise RuntimeError('Not enough time to lock execution of view')
        # Lock
        LockTable.objects.filter(id__in=self.lock_ids).update(locked=True)

    def __get_affected_models(self, groups):
        block = set()
        for group in groups:
            if isinstance(group, ModelBase):
                block |= self.__affected_models(group, [])
            else:
                block.add(str(group))
        return block

    def __affected_models(self, model, parents):
        curr_name = getattr(model, '_meta').object_name
        related_models = {curr_name}
        parents.append(curr_name)
        for rel in [f for f in getattr(model, '_meta').get_fields()
                    if (f.one_to_one or f.one_to_many) and f.auto_created and not f.concrete]:
            rel_model_name = getattr(rel.field.model, '_meta').object_name
            if rel_model_name not in related_models and rel_model_name != curr_name and rel_model_name not in parents:
                related_models.add(rel_model_name)
                related_models |= self.__affected_models(rel.field.model, parents)
        parents.pop()
        return related_models


class LoggedCallMixin:
    unparallel = []

    def get_unparallel(self, request):
        return self.unparallel

    def dispatch(self, request, *args, **kwargs):
        if not hasattr(super(), 'dispatch'):
            # This mixin should be used together with View based class
            raise BridgeException()

        unparallel = self.get_unparallel(request)

        # If request can be executed in parallel and call logs are disabled then just normal view execution
        if not settings.ENABLE_CALL_LOGS and not unparallel:
            return getattr(super(), 'dispatch')(request, *args, **kwargs)

        locker = ExecLocker(type(self).__name__, unparallel)
        try:
            locker.lock()
        except Exception:
            CallLogs.objects.create(**locker.call_log)
            raise
        try:
            locker.save_exec_time()
            response = getattr(super(), 'dispatch')(request, *args, **kwargs)
        except BridgeException:
            locker.unlock(False)
            raise
        except Exception:
            locker.unlock(True)
            raise
        else:
            locker.unlock(False)
        finally:
            CallLogs.objects.create(**locker.call_log)
        return response

    def is_not_used(self, *args, **kwargs):
        pass


class ProfileData:
    default_around_seconds = 300

    def get_statistic_around(self, date, delta_seconds):
        if not isinstance(delta_seconds, int):
            delta_seconds = self.default_around_seconds
        date = self.__date_stamp(date)
        assert date is not None, 'Wrong date format'
        return self.__collect_statistic(date - delta_seconds, date + delta_seconds, None)

    def get_statistic(self, date1=None, date2=None, func_name=None):
        date1 = self.__date_stamp(date1)
        date2 = self.__date_stamp(date2)
        return self.__collect_statistic(date1, date2, func_name)

    def get_log_around(self, date, delta_seconds):
        if not isinstance(delta_seconds, int):
            delta_seconds = self.default_around_seconds
        date = self.__date_stamp(date)
        assert date is not None, 'Wrong date format'
        return self.get_log(date - delta_seconds, date + delta_seconds, None)

    def get_log(self, date1, date2, func_name):
        filters = {}
        date1 = self.__date_stamp(date1)
        if isinstance(date1, float):
            filters['enter_time__gt'] = date1
        date2 = self.__date_stamp(date2)
        if isinstance(date2, float):
            filters['enter_time__lt'] = date2
        if func_name:
            filters['name'] = func_name
        logdata = []
        for call_data in CallLogs.objects.filter(**filters).exclude(return_time=None).order_by('id'):
            logdata.append({
                'name': call_data.name,
                'wait1': (call_data.wait1, call_data.wait1 >= MAX_WAITING),
                'wait2': (call_data.wait2, call_data.wait2 >= MAX_WAITING),
                'wait_total': call_data.wait1 + call_data.wait2,
                'enter': datetime.fromtimestamp(call_data.enter_time),
                'exec': datetime.fromtimestamp(call_data.execution_time),
                'return': datetime.fromtimestamp(call_data.return_time),
                'exec_time': '%0.3f' % call_data.execution_delta,
                'failed': call_data.is_failed
            })
        return logdata

    def processing(self):
        data = []
        for cl in CallLogs.objects.filter(return_time=None).order_by('id'):
            data.append({
                'name': cl.name, 'enter': datetime.fromtimestamp(cl.enter_time),
                'wait1': cl.wait1, 'wait2': cl.wait2,
                'exec': datetime.fromtimestamp(cl.execution_time) if cl.execution_time else None
            })
        return data

    def __collect_statistic(self, date1, date2, func_name):
        data = {}
        filters = {}
        if isinstance(date1, float):
            filters['enter_time__gt'] = date1
        if isinstance(date2, float):
            filters['enter_time__lt'] = date2
        if func_name:
            filters['name'] = func_name

        for call_data in CallLogs.objects.filter(**filters).order_by('id'):
            if call_data.name not in data:
                data[call_data.name] = {
                    'name': call_data.name,
                    'total_exec': call_data.execution_delta,
                    'max_exec': call_data.execution_delta,
                    'waiting': call_data.wait1 + call_data.wait2,
                    'max_wait1': call_data.wait1,
                    'max_wait2': call_data.wait2,
                    'calls': 1,
                    'failed': 1 if call_data.is_failed else 0
                }
            else:
                data[call_data.name]['total_exec'] += call_data.execution_delta
                data[call_data.name]['waiting'] += call_data.wait1 + call_data.wait2
                data[call_data.name]['max_exec'] = max(data[call_data.name]['max_exec'], call_data.execution_delta)
                data[call_data.name]['max_wait1'] = max(data[call_data.name]['max_wait1'], call_data.wait1)
                data[call_data.name]['max_wait2'] = max(data[call_data.name]['max_wait2'], call_data.wait2)
                data[call_data.name]['calls'] += 1
                if call_data.is_failed:
                    data[call_data.name]['failed'] += 1
        for func in data:
            data[func]['average_exec'] = data[func]['total_exec'] / data[func]['calls']
        return list(data[fname] for fname in sorted(data))

    def __date_stamp(self, date):
        if isinstance(date, datetime):
            date = date.timestamp()
        elif isinstance(date, time.struct_time):
            date = time.mktime(date)
        elif not isinstance(date, float):
            date = None
        return date


class DBLogsAnalizer:
    results_file = 'db-stat.json'

    def __init__(self):
        self.data = {}

    @property
    def _log_file(self):
        file_name = os.path.join('logs', 'db.log')
        assert os.path.isfile(file_name), 'DB log file does not exist'
        return file_name

    def analize(self, max_cnt=None):
        with open(self._log_file, mode='r', encoding='utf-8') as fp:
            cnt = 0
            for line in fp:
                m = re.match(r'^\[.*?]\s\((.*?)\)\s(.*)$', line)
                if m:
                    try:
                        exec_time = float(m.group(1))
                    except ValueError:
                        logger.error('Call log ValueError: {}, {}, {}'.format(m.group(1), line, m.groups()))
                        raise
                    query_sql = m.group(2)
                    if query_sql:
                        query_sql = self.parse_sql(query_sql)
                    if not query_sql:
                        query_sql = 'UPDATE report TREE'
                    self.__save_data(query_sql, exec_time)
                    cnt += 1
                    if max_cnt and cnt > max_cnt:
                        break

    def __save_data(self, query_sql, exec_time):
        if query_sql not in self.data:
            # 0 <= x0 < 0.005 <= x1 < 0.01 <= x2 < 0.05 <= x3 < 0.1 <= x4, total_number, total_execution
            self.data[query_sql] = [0, 0, 0, 0, 0, 0, 0.000]

        save_index = 4
        if exec_time < 0.005:
            save_index = 0
        elif exec_time < 0.01:
            save_index = 1
        elif exec_time < 0.05:
            save_index = 2
        elif exec_time < 0.1:
            save_index = 3
        self.data[query_sql][save_index] += 1
        self.data[query_sql][5] += 1
        self.data[query_sql][6] += exec_time

    def parse_sql(self, value):
        if value.startswith('SELECT'):
            m = re.match(r'^SELECT(.*)FROM(.*)WHERE(.*)$', value)
            if m:
                return 'SELECT ({}) FROM ({}) WHERE ({})'.format(
                    self.__parse_fields(m.group(1)),
                    self.__parse_from(m.group(2)),
                    self.__parse_where(m.group(3))
                )
            m = re.match(r'^SELECT(.*)FROM(.*)$', value)
            if m:
                return 'SELECT ({}) FROM ({})'.format(self.__parse_fields(m.group(1)), self.__parse_from(m.group(2)))
        elif value.startswith('UPDATE'):
            m = re.match(r'^UPDATE\s"(.*)"\sSET.*WHERE(.*)$', value)
            if m:
                return 'UPDATE {} WHERE ({})'.format(m.group(1), self.__parse_where(m.group(2)))
        elif value.startswith('INSERT'):
            m = re.match(r'^INSERT\sINTO\s"(.*?)"\s\(.*$', value)
            if m:
                return 'INSERT INTO {}'.format(m.group(1))
        elif value.startswith('DELETE'):
            m = re.match(r'^DELETE\sFROM\s"(.*)"\sWHERE\s(.*)$', value)
            if m:
                return 'DELETE FROM {} WHERE ({})'.format(m.group(1), self.__parse_where(m.group(2)))
        return value

    def __parse_fields(self, fields_str):
        fields_list = []
        for field_name in fields_str.split(', '):
            if fields_str.startswith('(1)'):
                fields_list.append('(1)')
            m = re.search(r'\."(\w+)"', field_name)
            if m:
                fields_list.append(m.group(1))
            else:
                fields_list.append(field_name.strip())
        return ', '.join(list(sorted(fields_list)))

    def __parse_where(self, value_str):
        fields_list = []
        m = re.match(r'^\s*(.*?)\s*(ORDER.*)?;.*$', value_str)
        if m:
            for field_name in m.group(1).split():
                m = re.match(r'^.*\S+\."(\w+)".*$', field_name)
                if m:
                    fields_list.append(m.group(1))
        return ', '.join(list(sorted(fields_list)))

    def __parse_from(self, value_str):
        return ', '.join(list(sorted(re.findall(r'\s"(\w+)"\s', value_str))))

    def print_results(self):
        import json
        with open(os.path.join('logs', self.results_file), mode='w', encoding='utf-8') as fp:
            json.dump(self.data, fp, sort_keys=True, indent=2, ensure_ascii=False)
