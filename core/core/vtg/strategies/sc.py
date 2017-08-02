#!/usr/bin/python3

from core.vtg.libraries.common import create_task, submit_task, wait_for_submitted_tasks, process_result, update_task
from core.vtg.strategies import Strategy
from core.vtg.data_structures import VerificationResults

SEQUENTIAL_COMBINATION_TAG = "sequential combination"
UNITE_ASSERTIONS = 1
SEPARATE_ASSERTIONS = 0
SEPARATION_PARAMETER = 3


class SC(Strategy):
    """
    This strategy represents sequential combination of tools launches.
    Each launch is determined by its tool configuration and the given resources.
    """
    long_name = "sequential combination"
    name = "SC"

    def execute(self):
        launches = self.__get_launches_information()
        verification_task = None
        verification_result = VerificationResults()
        for launch in launches:
            (launch_config, assertions_handling, factor) = self._select_config(launch, verification_result)

            if not verification_task:
                verification_task = create_task(self, predefined_config=launch_config, limitations_factor=factor)[0]
            else:
                verification_task = update_task(self, verification_task, verification_result, launch_config, factor)

            submitted_tasks = []
            if assertions_handling == UNITE_ASSERTIONS:
                verification_task.assemble_task_files(verification_task.get_assertions())
                verification_task.execute_cil()
                submitted_tasks.append(submit_task(verification_task, self))
            else:
                for assertion in verification_task.get_assertions():
                    verification_task.assemble_task_files([assertion])
                    verification_task.execute_cil()
                    submitted_tasks.append(submit_task(verification_task, self))
            verification_result.update(wait_for_submitted_tasks(submitted_tasks, self))
            if verification_result.is_solved():
                break
        process_result(verification_result, self, verification_task)

    def _select_config(self, launch_information, verification_result: VerificationResults):
        """
        Provides new configuration for each new launch based on the given results.
        This function can be overridden in child strategies.
        :param launch_information: information from base config.
        :param verification_result: previous results (or None in case of the first launch).
        :return: tuple <tool config>, <unite / separate properties>, <resource limitation factor>.
        """
        primary = launch_information["primary config"]  # mandatory item
        secondary = launch_information.get("secondary config")  # aux config
        factor = launch_information.get("limitations factor") or 1.0  # base resource limitation factor
        if not secondary or verification_result.is_empty():
            config = (primary, UNITE_ASSERTIONS)
        else:
            if len(verification_result.get_checked_assertions()) < SEPARATION_PARAMETER:
                config = (secondary, SEPARATE_ASSERTIONS)
                factor = 1.0 / len(verification_result.verdicts)
            else:
                config = (primary, UNITE_ASSERTIONS)
                factor = len(verification_result.get_checked_assertions()) / len(verification_result.verdicts)
        return config + (factor, )

    def __get_launches_information(self):
        if SEQUENTIAL_COMBINATION_TAG not in self.conf['VTG strategy']['verifier']:
            raise RuntimeError("Tag {0} must present for strategy {1}".format(SEQUENTIAL_COMBINATION_TAG, self.name))
        return self.conf['VTG strategy']['verifier'][SEQUENTIAL_COMBINATION_TAG]
