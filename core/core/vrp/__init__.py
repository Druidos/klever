#
# Copyright (c) 2018 ISP RAS (http://www.ispras.ru)
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

import glob
import json
import os
import queue
import re
import time
import traceback
import xml.etree.ElementTree as ElementTree
import zipfile
import multiprocessing

from clade import Clade

from core.vrp.et import import_error_trace

import core.components
import core.session
import core.utils
from core.coverage import LCOV


@core.components.before_callback
def __launch_sub_job_components(context):
    context.mqs['VRP common prj attrs'] = multiprocessing.Queue()
    context.mqs['VRP source paths'] = multiprocessing.Queue()
    context.mqs['processing tasks'] = multiprocessing.Queue()


@core.components.after_callback
def __submit_project_attrs(context):
    context.mqs['VRP common prj attrs'].put(context.common_prj_attrs)
    context.mqs['VRP source paths'].put(context.source_paths)


class VRP(core.components.Component):

    def __init__(self, conf, logger, parent_id, callbacks, mqs, vals, id=None, work_dir=None, attrs=None,
                 separate_from_parent=False, include_child_resources=False):
        # Requirement specification descriptions were already extracted when getting VTG callbacks.
        self.__downloaded = dict()
        self.__workers = None

        # Read this in a callback
        self.verdict = None
        self.requirement = None
        self.program_fragment = None

        # Common initialization
        super(VRP, self).__init__(conf, logger, parent_id, callbacks, mqs, vals, id, work_dir, attrs,
                                  separate_from_parent, include_child_resources)

    def process_results(self):
        self.__workers = core.utils.get_parallel_threads_num(self.logger, self.conf, 'Results processing')
        self.logger.info("Going to start {} workers to process results".format(self.__workers))

        # Do result processing
        core.utils.report(self.logger,
                          'attrs',
                          {
                              'id': self.id,
                              'attrs': self.__get_common_prj_attrs()
                          },
                          self.mqs['report files'],
                          self.vals['report id'],
                          self.conf['main working directory'])

        subcomponents = [('RPL', self.__result_processing)]
        for i in range(self.__workers):
            subcomponents.append(('RPWL', self.__loop_worker))
        self.launch_subcomponents(False, *subcomponents)

        self.clean_dir = True
        # Finalize
        self.finish_task_results_processing()

    def finish_task_results_processing(self):
        """Function has a callback at Job.py."""
        self.logger.info('Task results processing has finished')

    main = process_results

    def __result_processing(self):
        pending = dict()
        # todo: implement them in GUI
        solution_timeout = 10
        generation_timeout = 5

        source_paths = self.mqs['VRP source paths'].get()
        self.mqs['VRP source paths'].close()
        self.logger.info('Source paths to be trimmed file names: {0}'.format(source_paths))

        def submit_processing_task(status, t):
            task_data, tryattempt = pending[t]
            self.mqs['processing tasks'].put([status, task_data, tryattempt, source_paths])

        receiving = True
        session = core.session.Session(self.logger, self.conf['Klever Bridge'], self.conf['identifier'])
        try:
            while True:
                # Get new tasks
                if receiving:
                    if len(pending) > 0:
                        number = 0
                        try:
                            while True:
                                data = self.mqs['pending tasks'].get_nowait()
                                if not data:
                                    receiving = False
                                    self.logger.info("Expect no tasks to be generated")
                                else:
                                    pending[data[0][0]] = data
                                number += 1
                        except queue.Empty:
                            self.logger.debug("Fetched {} tasks".format(number))
                    else:
                        try:
                            data = self.mqs['pending tasks'].get(block=True, timeout=generation_timeout)
                            if not data:
                                receiving = False
                                self.logger.info("Expect no tasks to be generated")
                            else:
                                pending[data[0][0]] = data
                        except queue.Empty:
                            self.logger.debug("No tasks has come for last 30 seconds")

                # Plan for processing new tasks
                if len(pending) > 0:
                    tasks_statuses = session.get_tasks_statuses(list(pending.keys()))
                    for task in list(pending.keys()):
                        if task in tasks_statuses['finished']:
                            submit_processing_task('finished', task)
                            del pending[task]
                        elif task in tasks_statuses['error']:
                            submit_processing_task('error', task)
                            del pending[task]
                        elif task not in tasks_statuses['processing'] and task not in tasks_statuses['pending']:
                            raise KeyError("Cannot find task {!r} in either finished, processing, pending or erroneus "
                                           "tasks".format(task))

                if not receiving and len(pending) == 0:
                    # Wait for all rest tasks, no tasks can come currently
                    self.mqs['pending tasks'].close()
                    for _ in range(self.__workers):
                        self.mqs['processing tasks'].put(None)
                    self.mqs['processing tasks'].close()
                    break

                time.sleep(solution_timeout)
        finally:
            session.sign_out()
        self.logger.debug("Shutting down result processing gracefully")

    def __loop_worker(self):
        self.logger.info("VRP fetcher is ready to work")

        # First get QOS resource limitations
        qos_resource_limits = core.utils.read_max_resource_limitations(self.logger, self.conf)
        self.vals['task solution triples'] = multiprocessing.Manager().dict()

        while True:
            element = self.mqs['processing tasks'].get()
            if element is None:
                break

            status, data, attempt, source_paths = element
            pf = data[2]['id']
            requirement = data[3]
            attrs = [
                {
                    "name": "Requirement",
                    "value": requirement,
                    "compare": True,
                    "associate": True
                }
            ]
            if attempt:
                new_id = "{}/{}/{}/RP".format(pf, requirement, attempt)
                workdir = os.path.join(pf, requirement, str(attempt))
                attrs.append(
                    {
                        "name": "Rescheduling attempt",
                        "value": str(attempt),
                        "compare": False,
                        "associate": False
                    }
                )
            else:
                new_id = "{}/{}/RP".format(pf, requirement)
                workdir = os.path.join(pf, requirement)
            self.vals['task solution triples']['{}:{}'.format(pf, requirement)] = [None, None, None]
            try:
                rp = RP(self.conf, self.logger, self.id, self.callbacks, self.mqs, self.vals, new_id,
                        workdir, attrs, separate_from_parent=True, qos_resource_limits=qos_resource_limits,
                        source_paths=source_paths, element=[status, data])
                rp.start()
                rp.join()
            except core.components.ComponentError:
                self.logger.debug("RP that processed {!r}, {!r} failed".format(pf, requirement))
            finally:
                solution = list(self.vals['task solution triples'].get('{}:{}'.format(pf, requirement)))
                del self.vals['task solution triples']['{}:{}'.format(pf, requirement)]
                self.mqs['processed tasks'].put((pf, requirement, solution))

        self.logger.info("VRP fetcher finishes its work")

    def __get_common_prj_attrs(self):
        self.logger.info('Get common project atributes')

        common_prj_attrs = self.mqs['VRP common prj attrs'].get()

        self.mqs['VRP common prj attrs'].close()

        return common_prj_attrs


class RP(core.components.Component):

    def __init__(self, conf, logger, parent_id, callbacks, mqs, vals, id=None, work_dir=None, attrs=None,
                 separate_from_parent=False, include_child_resources=False, qos_resource_limits=None, source_paths=None,
                 element=None):
        # Read this in a callback
        self.element = element
        self.verdict = None
        self.requirement = None
        self.program_fragment = None
        self.task_error = None
        self.verification_coverage = None
        self.source_paths = source_paths
        self.__exception = None
        self.__qos_resource_limit = qos_resource_limits
        # Common initialization
        super(RP, self).__init__(conf, logger, parent_id, callbacks, mqs, vals, id, work_dir, attrs,
                                 separate_from_parent, include_child_resources)

        self.clean_dir = True
        self.session = core.session.Session(self.logger, self.conf['Klever Bridge'], self.conf['identifier'])

        # Obtain file prefixes that can be removed from file paths.
        self.storage = Clade(self.conf['build base'])
        self.search_dirs = core.utils.get_search_dirs(self.conf['main working directory'], abs_paths=True)

    def fetcher(self):
        self.logger.info("VRP instance is ready to work")
        element = self.element
        status, data = element
        task_id, opts, program_fragment, requirement, verifier = data
        self.program_fragment = program_fragment['id']
        self.requirement = requirement
        self.results_key = '{}:{}'.format(self.program_fragment, self.requirement)
        self.logger.debug("Prcess results of task {}".format(task_id))

        files_list_file = 'files list.txt'
        with open(files_list_file, 'w', encoding='utf8') as fp:
            fp.writelines('\n'.join(sorted(f for grp in program_fragment['grps'] for f in grp['files'])))
        core.utils.report(self.logger,
                          'attrs',
                          {
                              'id': self.id,
                              'attrs': [
                                  {
                                      "name": "Program fragment",
                                      "value": program_fragment['id'],
                                      "data": files_list_file,
                                      "compare": True,
                                      "associate": True
                                  }
                              ]
                          },
                          self.mqs['report files'],
                          self.vals['report id'],
                          self.conf['main working directory'],
                          data_files=[files_list_file])

        # Update solution status
        data = list(self.vals['task solution triples'][self.results_key])
        data[0] = status
        self.vals['task solution triples'][self.results_key] = data

        try:
            if status == 'finished':
                self.process_finished_task(task_id, opts, verifier)
                # Raise exception just here sinse the method above has callbacks.
                if self.__exception:
                    self.logger.warning("Raising the saved exception")
                    raise self.__exception
            elif status == 'error':
                self.process_failed_task(task_id)
                # Raise exception just here sinse the method above has callbacks.
                raise RuntimeError('Failed to decide verification task: {0}'.format(self.task_error))
            else:
                raise ValueError("Unknown task {!r} status {!r}".format(task_id, status))
        finally:
            self.session.sign_out()

    main = fetcher

    def process_witness(self, witness):
        error_trace = import_error_trace(self.logger, witness)
        sources = self.__trim_file_names(error_trace['files'])
        error_trace['files'] = [sources[file] for file in error_trace['files']]

        # Distinguish multiple witnesses and error traces by using artificial unique identifiers encoded within witness
        # file names.
        match = re.search(r'witness\.(.+)\.graphml', witness)
        if match:
            error_trace_file = 'error trace {0}.json'.format(match.group(1))
        else:
            error_trace_file = 'error trace.json'

        self.logger.info('Write processed witness to "{0}"'.format(error_trace_file))
        with open(error_trace_file, 'w', encoding='utf8') as fp:
            json.dump(error_trace, fp, ensure_ascii=False, sort_keys=True, indent=4)

        return sources, error_trace_file

    def report_unsafe(self, sources, error_trace_files, attrs):
        core.utils.report(self.logger,
                          'unsafe',
                          {
                              'id': "{}/verification/unsafe".format(self.id),
                              'parent id': "{}/verification".format(self.id),
                              'attrs': attrs,
                              'sources': core.utils.ReportFiles(list(sources.keys()), arcnames=sources),
                              'error traces': [core.utils.ReportFiles([error_trace_file],
                                                                      arcnames={error_trace_file: 'error trace.json'})
                                               for error_trace_file in error_trace_files]
                          },
                          self.mqs['report files'],
                          self.vals['report id'],
                          self.conf['main working directory'])

    def process_single_verdict(self, decision_results, opts, log_file):
        """The function has a callback that collects verdicts to compare them with the ideal ones."""
        # Parse reports and determine status
        benchexec_reports = glob.glob(os.path.join('output', '*.results.xml'))
        if len(benchexec_reports) != 1:
            raise FileNotFoundError('Expect strictly single BenchExec XML report file, but found {}'.
                                    format(len(benchexec_reports)))

        # Expect single report file
        with open(benchexec_reports[0], encoding="utf8") as fp:
            result = ElementTree.parse(fp).getroot()

            run = result.findall("run")[0]
            for column in run.iter("column"):
                name, value = [column.attrib.get(name) for name in ("title", "value")]
                if name == "status":
                    decision_results["status"] = value

        # Check that we have set status
        if "status" not in decision_results:
            raise KeyError("There is no solution status in BenchExec XML report")

        self.logger.info('Verification task decision status is "{0}"'.format(decision_results['status']))

        # Do not fail immediately in case of witness processing failures that often take place. Otherwise we will
        # not upload all witnesses that can be properly processed as well as information on all such failures.
        # Necessary verificaiton finish report also won't be uploaded causing Bridge to corrupt the whole job.
        if re.search('true', decision_results['status']):
            core.utils.report(self.logger,
                              'safe',
                              {
                                  'id': "{}/verification/safe".format(self.id),
                                  'parent id': "{}/verification".format(self.id),
                                  'attrs': []
                                  # TODO: at the moment it is unclear what are verifier proofs.
                                  # 'proof': None
                              },
                              self.mqs['report files'],
                              self.vals['report id'],
                              self.conf['main working directory'])
            self.verdict = 'safe'
        else:
            witnesses = glob.glob(os.path.join('output', 'witness.*.graphml'))
            self.logger.info("Found {} witnesses".format(len(witnesses)))

            # Create unsafe reports independently on status. Later we will create unknown report in addition if status
            # is not "unsafe".
            if "expect several witnesses" in opts and opts["expect several witnesses"] and len(witnesses) != 0:
                self.verdict = 'unsafe'
                # Collect all sources referred by all error traces. Different error traces can refer almost the same
                # sources, so reporting them separately is redundant.
                sources = {}
                error_trace_files = []
                for witness in witnesses:
                    try:
                        error_trace_sources, error_trace_file = self.process_witness(witness)
                        sources.update(error_trace_sources)
                        error_trace_files.append(error_trace_file)
                    except Exception as e:
                        self.logger.warning('Failed to process a witness:\n{}'.format(traceback.format_exc().rstrip()))
                        self.verdict = 'non-verifier unknown'

                        if self.__exception:
                            try:
                                raise e from self.__exception
                            except Exception as e:
                                self.__exception = e
                        else:
                            self.__exception = e

                # Do not report unsafe if processing of all witnesses failed.
                if error_trace_files:
                    self.report_unsafe(sources, error_trace_files, [])
            if re.search('false', decision_results['status']) and \
                    ("expect several witnesses" not in opts or not opts["expect several witnesses"]):
                self.verdict = 'unsafe'
                try:
                    if len(witnesses) != 1:
                        NotImplementedError('Just one witness is supported (but "{0}" are given)'.
                                            format(len(witnesses)))

                    sources, error_trace_file = self.process_witness(witnesses[0])
                    self.report_unsafe(sources, [error_trace_file], [])
                except Exception as e:
                    self.logger.warning('Failed to process a witness:\n{}'.format(traceback.format_exc().rstrip()))
                    self.verdict = 'non-verifier unknown'
                    self.__exception = e
            elif not re.search('false', decision_results['status']):
                self.verdict = 'unknown'

                # Prepare file to send it with unknown report.
                os.mkdir('verification')
                verification_problem_desc = os.path.join('verification', 'problem desc.txt')

                # Check resource limitiations
                if decision_results['status'] in ('OUT OF MEMORY', 'TIMEOUT'):
                    if decision_results['status'] == 'OUT OF MEMORY':
                        msg = "memory exhausted"
                    else:
                        msg = "CPU time exhausted"

                    with open(verification_problem_desc, 'w', encoding='utf8') as fp:
                        fp.write(msg)

                    data = list(self.vals['task solution triples'][self.results_key])
                    data[2] = decision_results['status']
                    self.vals['task solution triples'][self.results_key] = data
                else:
                    os.symlink(os.path.relpath(log_file, 'verification'), verification_problem_desc)

                core.utils.report(self.logger,
                                  'unknown',
                                  {
                                      'id': "{}/verification/unknown".format(self.id),
                                      'parent id': "{}/verification".format(self.id),
                                      'attrs': [],
                                      'problem desc': core.utils.ReportFiles(
                                          [verification_problem_desc],
                                          {verification_problem_desc: 'problem desc.txt'})
                                  },
                                  self.mqs['report files'],
                                  self.vals['report id'],
                                  self.conf['main working directory'],
                                  'verification')

    def process_failed_task(self, task_id):
        """The function has a callback at Job module."""
        self.task_error = self.session.get_task_error(task_id)
        # We do not need task and its files anymore.
        self.session.remove_task(task_id)

        self.verdict = 'non-verifier unknown'

    def process_finished_task(self, task_id, opts, verifier):
        """Function has a callback at Job.py."""
        self.session.download_decision(task_id)

        with zipfile.ZipFile('decision result files.zip') as zfp:
            zfp.extractall()

        with open('decision results.json', encoding='utf8') as fp:
            decision_results = json.load(fp)

        # TODO: specify the computer where the verifier was invoked (this information should be get from BenchExec or VerifierCloud web client.
        log_files_dir = glob.glob(os.path.join('output', 'benchmark*logfiles'))[0]
        log_files = os.listdir(log_files_dir)

        if len(log_files) != 1:
            raise NotImplementedError('Exactly one log file should be outputted (but "{0}" are given)'
                                      .format(len(log_files)))

        log_file = os.path.join(log_files_dir, log_files[0])

        # Send an initial report
        report = {
            'id': "{}/verification".format(self.id),
            'parent id': self.id,
            # TODO: replace with something meaningful, e.g. tool name + tool version + tool configuration.
            'attrs': [],
            'name': verifier,
            'resources': decision_results['resources'],
        }

        # Get coverage
        coverage_info_dir = os.path.join('total coverages',
                                         self.conf['sub-job identifier'],
                                         self.requirement.replace('/', '-'))
        os.makedirs(os.path.join(self.conf['main working directory'], coverage_info_dir), exist_ok=True)

        self.coverage_info_file = os.path.join(coverage_info_dir,
                                               "{0}_coverage_info.json".format(task_id.replace('/', '-')))

        # Update solution progress. It is necessary to update the whole list to sync changes
        data = list(self.vals['task solution triples'][self.results_key])
        data[1] = decision_results['resources']
        self.vals['task solution triples'][self.results_key] = data

        if not self.logger.disabled and log_file:
            report['log'] = core.utils.ReportFiles([log_file], {log_file: 'log.txt'})

        if self.conf['upload input files of static verifiers']:
            report['task identifier'] = task_id

        # Remember exception and raise it if verdict is not unknown
        exception = None
        try:
            self.verification_coverage = LCOV(self.logger, os.path.join('output', 'coverage.info'),
                                              self.storage, self.source_paths,
                                              self.search_dirs, self.conf['main working directory'],
                                              opts.get('coverage'),
                                              os.path.join(self.conf['main working directory'],
                                                           self.coverage_info_file),
                                              os.path.join(self.conf['main working directory'], coverage_info_dir),
                                              opts.get('collect function names'))
        except Exception as err:
            exception = err
        else:
            if os.path.isfile('coverage.json'):
                report['coverage'] = core.utils.ReportFiles(['coverage.json'] +
                                                            list(self.verification_coverage.arcnames.keys()),
                                                            arcnames=self.verification_coverage.arcnames)
                self.vals['coverage_finished'][self.conf['sub-job identifier']] = False

        # todo: This should be cheked to guarantee that we can reschedule tasks
        core.utils.report(self.logger,
                          'verification',
                          report,
                          self.mqs['report files'],
                          self.vals['report id'],
                          self.conf['main working directory'])

        try:
            # Submit a verdict
            self.process_single_verdict(decision_results, opts, log_file)
        finally:
            # Submit a closing report
            core.utils.report(self.logger,
                              'verification finish',
                              {'id': report['id']},
                              self.mqs['report files'],
                              self.vals['report id'],
                              self.conf['main working directory'])

        # Check verdict
        if exception and self.verdict != 'unknown':
            raise exception
        elif exception:
            self.logger.exception('Could not parse coverage')

    def __trim_file_names(self, file_names):
        arcnames = {}

        for file_name in file_names:
            # Remove storage from file names if files were put there.
            new_file_name = core.utils.make_relative_path([self.storage.storage_dir], file_name)

            # Try to make paths relative to source paths or standard search directories.
            new_file_name = core.utils.make_relative_path(self.source_paths + self.search_dirs, new_file_name,
                                                          absolutize=True)
            arcnames[file_name] = new_file_name

        return arcnames
