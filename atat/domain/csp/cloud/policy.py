from glob import glob
import json
from dataclasses import dataclass
from os.path import join as path_join


class AzurePolicyManager:
    def __init__(self, static_policy_location):
        self._static_policy_location = static_policy_location

    @property
    def portfolio_definitions(self):
        if getattr(self, "_portfolio_definitions", None) is None:
            portfolio_files = self._glob_json("portfolios")
            self._portfolio_definitions = self._load_policies(portfolio_files)

        return self._portfolio_definitions

    @property
    def application_definitions(self):
        pass

    @property
    def environment_definitions(self):
        pass

    def _glob_json(self, path):
        return glob(path_join(self._static_policy_location, "portfolios", "*.json"))

    def _load_policies(self, json_policies):
        return [self._load_policy(pol) for pol in json_policies]

    def _load_policy(self, policy_file):
        with open(policy_file, "r") as file_:
            doc = json.loads(file_.read())
            return AzurePolicy(
                definition_point=doc["definitionPoint"],
                definition=doc["policyDefinition"],
                parameters=doc["parameters"],
            )


@dataclass
class AzurePolicy:
    definition_point: str
    definition: dict
    parameters: dict
