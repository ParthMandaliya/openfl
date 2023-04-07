import importlib
import yaml
from yaml.loader import SafeLoader
from typing import Dict, Any


class Participant:
    def __init__(self, name: str = ""):
        self.private_attributes = {}
        self._name = name

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name: str):
        self._name = name

    def private_attributes(self, attrs: Dict[str, Any]) -> None:
        self.private_attributes = attrs


class Collaborator(Participant):
    """
    Defines a collaborator participant
    """
    def __init__(self, collab_config, **kwargs):
        super().__init__(**kwargs)
        self.__collaborator_config_file = collab_config


    def initialize_private_attributes(self):
        with open(self.__collaborator_config_file, "r") as f:
            config = yaml.load(f, Loader=SafeLoader)

        filepath, class_name = config["shard_descriptor"]["template"].split(".")

        shard_descriptor_module = importlib.import_module(filepath)
        ShardDescriptor = getattr(shard_descriptor_module, class_name)

        shard_descriptor = ShardDescriptor(self.__collaborator_config_file)

        self.private_attributes = shard_descriptor.get()
        print (f"Initializing Private attributes for Collaborator {self.name}")

    def exec(self, task=None, cln=None, func=None):
        return func(self, cln)
