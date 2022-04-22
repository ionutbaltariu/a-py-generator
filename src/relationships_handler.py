from networkx import DiGraph, find_cycle
from networkx.exception import NetworkXNoCycle
from view import Field, Resource, Unique, ForeignKey


def check_relationships_and_adapt(resources):
    relationships_graph = DiGraph()
    tables_names = [x.table_name for x in resources]

    for table_name in tables_names:
        relationships_graph.add_node(table_name)

    for resource in resources:
        for relation in resource.relationships:
            relationships_graph.add_edge(resource.table_name,
                                         relation.table,
                                         rel_type=relation.type,
                                         referenced_field=relation.reference_field)

    try:
        cycle = find_cycle(relationships_graph)
        cycle = ' -> '.join([f"({x[0]}, {x[1]})" for x in cycle])
        raise ValueError(f"There are circular relationships in the given list of resources. Please revise: {cycle}")
    except NetworkXNoCycle:
        # there were no cycles and the list of resources can be updated to contain the new foreign keys and eventual
        # link tables (many-to-many)
        adapt_entities(relationships_graph, resources)


def adapt_entities(relationships_graph, resources):
    for table1, table2, data in relationships_graph.edges(data=True):
        rel_type = data["rel_type"]
        referenced_field = data["referenced_field"]

        if referenced_field is not None and rel_type == "MANY-TO-MANY":
            raise ValueError(f"There should not be a referenced field"
                             f" when the relationship type is 'MANY-TO-MANY'")
        if referenced_field is None and rel_type != "MANY-TO-MANY":
            raise ValueError(f"Please introduce a referenced field in the child table.")

        table1 = list(filter(lambda x: x.table_name == table1, resources))[0]
        table2 = list(filter(lambda x: x.table_name == table2, resources))[0]
        table1_field = list(filter(lambda x: x.name == referenced_field, table1.fields))

        if len(table1_field) == 0:
            raise ValueError(f"The referenced field should exist in '{table1.table_name}'!")

        if rel_type == "MANY-TO-MANY":
            fields = [Field(name=f"id", type="integer", nullable=False),
                      Field(name=f"{table1.primary_key}", type="integer", nullable=False),
                      Field(name=f"{table2.primary_key}", type="integer", nullable=False)]
            table_name = f"{table1.table_name}_{table2.table_name}"
            # TODO: when support for composite primary keys will be added, also change here
            link_table = Resource(name=table_name, table_name=table_name, fields=fields, primary_key="id")
            resources.append(link_table)
            create_fk_many_to_many(link_table, table1, fields[1].name)
            create_fk_many_to_many(link_table, table2, fields[2].name)
        elif rel_type == "ONE-TO-ONE":
            create_fk(master=table2, slave=table1, reference_field=referenced_field)
            if not table1.uniques:
                table1.uniques = []
            table1.uniques.append(Unique(name='one_to_one_constr', unique_fields=[referenced_field]))
        elif rel_type == "ONE-TO-MANY":
            create_fk(master=table2, slave=table1, reference_field=referenced_field)


def create_fk_many_to_many(master, slave, already_existent_field=None):
    fk_name = already_existent_field
    fk = ForeignKey(field=fk_name, references=slave.table_name, reference_field=slave.primary_key)

    if not master.foreign_keys:
        master.foreign_keys = []

    master.foreign_keys.append(fk)


# theoretically bad design, changing variables passed by reference.. there should be another way
def create_fk(master, slave, reference_field):
    fk_name = f"{slave.table_name}_fk"
    fk = ForeignKey(field=fk_name, references=slave.table_name, reference_field=reference_field)

    fk_field = Field(name=f"{slave.table_name}_fk", type="integer", nullable=False)
    master.fields.append(fk_field)

    if not master.foreign_keys:
        master.foreign_keys = []

    master.foreign_keys.append(fk)
