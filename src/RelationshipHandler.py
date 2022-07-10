from view import Resource, ForeignKey, ResourceField, Unique, Relationship
from typing import List
from networkx import DiGraph, find_cycle, exception


# Command Pattern
class RelationshipHandler:
    relationships: DiGraph

    def __init__(self, app_input: List[Resource]):
        self.resources = app_input
        self.table_names = [x.table_name for x in app_input]
        self.relationships = DiGraph()

    def check_for_cycles_in_relationships(self) -> None:
        """
        Checks for cycles in the relationship graph of the current generation.
        """
        try:
            cycle = find_cycle(self.relationships)
            cycle = ' -> '.join([f"({x[0]}, {x[1]})" for x in cycle])
            raise ValueError(f"There are circular relationships in the given list of resources. Please revise: {cycle}")
        except exception.NetworkXNoCycle:
            pass

    def compute_relationships_graph(self) -> None:
        """
        Creates the relationship graph that contains all links between the given resources.
        """
        for table_name in self.table_names:
            self.relationships.add_node(table_name)
        for resource in self.resources:
            # guard for the resources that do not have relationship
            if not resource.relationships:
                continue

            for relation in resource.relationships:
                child = list(filter(lambda x: x.table_name == relation.table, self.resources))[0]
                fk_name = f"{resource.name}_fk".lower() if relation.type != "MANY-TO-MANY" else None
                reference_field = [x for x in resource.fields if x.name == relation.reference_field][0] \
                    if relation.type != "MANY-TO-MANY" else None

                self.relationships.add_edge(resource.table_name, relation.table, rel_type=relation.type,
                                            foreign_key_name=fk_name, parent=resource, child=child,
                                            referenced_field=reference_field)

    def change_resources_based_on_relationships(self) -> None:
        """
        Modifies the existing resources based on the detected relationships. Creates foreign keys, unique keys and
        eventually join tables.
        """
        for parent, child, data in self.relationships.edges(data=True):
            rel_type = data["rel_type"]
            fk_name = data["foreign_key_name"]
            referenced_field = data["referenced_field"]
            parent_table = data["parent"]
            child_table = data["child"]

            if rel_type == "MANY-TO-MANY":
                self.handle_many_to_many(child_table, parent_table)
            elif rel_type == "ONE-TO-ONE":
                create_fk_one_to_one(parent_table, child_table, referenced_field, fk_name)
            elif rel_type == "ONE-TO-MANY":
                create_fk_one_to_many(parent_table, child_table, referenced_field, fk_name)

    def handle_many_to_many(self, child_table, parent_table):
        """
        Method dedicated to the handling of the many-to-many relationship type.
        """
        parent_table_fields = [x for x in parent_table.fields if x.name == parent_table.primary_key]
        if parent_table_fields[0].type == "string":
            params = {
                "type": "string",
                "length": parent_table_fields[0].length
            }
        else:
            params = {
                "type": parent_table_fields[0].type
            }

        child_table_fields = [x for x in child_table.fields if x.name == child_table.primary_key]
        if child_table_fields[0].type == "string":
            params2 = {
                "type": "string",
                "length": child_table_fields[0].length
            }
        else:
            params2 = {
                "type": child_table_fields[0].type
            }
        fields = [ResourceField(name=f"id", type="integer", nullable=False),
                  ResourceField(name=f"{parent_table.primary_key}", nullable=False, **params),
                  ResourceField(name=f"{child_table.primary_key}", nullable=False, **params2)]
        table_name = f"{parent_table.table_name}_{child_table.table_name}"

        relationships = [Relationship(type="MANY-TO-MANY",
                                      table=parent_table.table_name,
                                      reference_field=parent_table.primary_key,
                                      role="Child"),
                         Relationship(type="MANY-TO-MANY",
                                      table=child_table.table_name,
                                      reference_field=child_table.primary_key,
                                      role="Child")]
        uniques = [Unique(name=f"{table_name}_un",
                          unique_fields=["id", parent_table.primary_key, child_table.primary_key])]

        link_table = Resource(name=table_name,
                              table_name=table_name,
                              fields=fields,
                              primary_key="id",
                              relationships=relationships,
                              uniques=uniques)
        self.resources.append(link_table)
        create_fk_many_to_many(link_table, parent_table, fields[1].name)
        create_fk_many_to_many(link_table, child_table, fields[2].name)

    def generate_mirror_relationships(self):
        """
        Creates corresponding members in the resources referred in relationships.
        """
        for parent, _, data in self.relationships.edges(data=True):
            rel_type = data["rel_type"]
            referenced_field = data["referenced_field"]
            child_table = data["child"]

            if not child_table.relationships:
                child_table.relationships = []

            if rel_type != "MANY-TO-MANY":
                ref_field = referenced_field.name
            else:
                ref_field = None

            child_table.relationships.append(Relationship(type=rel_type,
                                                          table=parent,
                                                          reference_field=ref_field,
                                                          role="Child"))

    def execute(self):
        """
        Trigger method. Executes all needed steps in the context of the relationship handler.
        """
        self.compute_relationships_graph()
        self.check_for_cycles_in_relationships()
        self.change_resources_based_on_relationships()
        self.generate_mirror_relationships()


def create_fk_many_to_many(parent, child, field):
    """
    Creates a foreign key in the context of many-to-many relationships.

    :param parent: the parent resource
    :param child: the child resource
    :param field: the field that is the foreign key
    """
    fk = ForeignKey(field=field, references=child.table_name, reference_field=child.primary_key)

    if not parent.foreign_keys:
        parent.foreign_keys = []

    parent.foreign_keys.append(fk)


def create_fk_one_to_many(parent, child, reference_field, fk_name):
    """
    Creates a foreign key in the context of one-to-many relationships.

    :param parent: the parent resource
    :param child: the child resource
    :param reference_field: the field that will be referenced by the foreign key in the child resource.
    :param fk_name: the name of the foreign key
    """
    fk = ForeignKey(field=fk_name, references=parent.table_name, reference_field=reference_field.name)

    length = reference_field.length if reference_field.type == "string" else None
    # it remains to have a dynamic type, not only integer but the type of the referenced field
    fk_field = ResourceField(name=fk_name, type=reference_field.type, length=length, nullable=False)
    child.fields.append(fk_field)

    if not child.foreign_keys:
        child.foreign_keys = []

    child.foreign_keys.append(fk)


def create_fk_one_to_one(parent, child, reference_field, fk_name):
    """
    Creates a foreign key in the context of one-to-one relationships (includes a unique constraint).

    :param parent: the parent resource
    :param child: the child resource
    :param reference_field: the field that will be referenced by the foreign key in the child resource.
    :param fk_name: the name of the foreign key
    """
    if not child.uniques:
        child.uniques = []
    child.uniques.append(Unique(name=f"{fk_name}_one_to_one", unique_fields=[fk_name]))

    create_fk_one_to_many(parent, child, reference_field, fk_name)
