from core.lkvog.strategies.strategy_utils import Module, Graph
from core.lkvog.strategies.abstract_strategy import AbstractStrategy


class Manual(AbstractStrategy):
    def __init__(self, logger, strategy_params, params):
        super().__init__(logger)
        self.groups = params.get('groups', {})

    def divide(self, module_name):
        ret = []

        if module_name in self.groups:
            for group in self.groups[module_name]:
                group_modules = []
                for module in group:
                    group_modules.append(Module(module))
                    for pred_module in group_modules[:-1]:
                        pred_module.add_successor(group_modules[-1])
                # Make module_name to root of the Graph
                root_module_pos = [module.id for module in group_modules].index(module_name)
                group_modules[0], group_modules[root_module_pos] = group_modules[root_module_pos], group_modules[0]

                ret.append(Graph(group_modules))
        else:
            ret.append(Graph([Module(module_name)]))

        return ret
