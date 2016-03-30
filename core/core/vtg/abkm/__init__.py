#!/usr/bin/python3

import os
import re

from core.vtg import common


# This strategy is aimed at merging all bug kinds inside each rule scpecification
# and at checking each rule specification as a separated verification run
# until finding the first bug.
class ABKM(common.SequentialStrategy):
    def generate_verification_tasks(self):
        self.logger.info('Generate one verification task by merging all bug kinds')
        self.process_sequential_verification_task()

    main = generate_verification_tasks

    def prepare_bug_kind_functions_file(self):
        self.logger.info('Prepare bug kind functions file "bug kind funcs.c"')

        # Get all bug kinds.
        bug_kinds = self.get_all_bug_kinds()

        # Create bug kind function definitions that all call __VERIFIER_error() since this strategy doesn't distinguish
        # different bug kinds.
        with open('bug kind funcs.c', 'w') as fp:
            fp.write('/* http://sv-comp.sosy-lab.org/2015/rules.php */\nvoid __VERIFIER_error(void);\n')
            for bug_kind in bug_kinds:
                fp.write('void ldv_assert_{0}(int expr) {{\n\tif (!expr)\n\t\t__VERIFIER_error();\n}}\n'.format(
                    re.sub(r'\W', '_', bug_kind)))

        # Add bug kind functions file to other abstract verification task files.
        self.conf['abstract task desc']['extra C files'].append(
            {'C file': os.path.relpath('bug kind funcs.c', os.path.realpath(self.conf['source tree root']))})
