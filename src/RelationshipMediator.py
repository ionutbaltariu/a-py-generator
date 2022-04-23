from view import Input
from networkx import DiGraph


class RelationshipMediator:
    relationships: DiGraph

    def __init__(self, app_input: Input):
        self.app_input = app_input

    def check_for_cycles_in_relationship(self) -> bool:
        pass

    def compute_relationships_graph(self) -> DiGraph:
        pass

    def change_resources_based_on_relationships(self) -> None:
        pass
