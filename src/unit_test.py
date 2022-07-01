import unittest
from mock_data import valid_resources
from srctrueview import Input
from config import MAX_STR_LENGTH, PASSWORD_LENGTH, PROJECT_DESCRIPTION_MAX_LENGTH, PROJECT_VERSION_MAX_LENGTH, \
    MAX_RESOURCES_ALLOWED


def get_input_object():
    return {"resources": valid_resources}


def get_valid_and_invalid_str_input(max_length):
    invalid = "".join(["z" for _ in range(max_length + 1)])
    valid = "".join(["z" for _ in range(max_length)])
    return invalid, valid


class UnitTest(unittest.TestCase):

    def test_resources_initial_validation(self):
        too_many_resources = []
        duplicated_resources = []
        duplicated_resources.extend(valid_resources)
        duplicated_resources.extend(valid_resources)

        for _ in range(round(MAX_RESOURCES_ALLOWED / 4)):
            too_many_resources.extend(valid_resources)

        # no resources
        with self.assertRaises(ValueError):
            Input()

        # too many resources
        with self.assertRaises(ValueError):
            Input(**{"resources": too_many_resources})

        # less than maximum resources, but contains duplicates
        with self.assertRaises(ValueError):
            Input(**{"resources": duplicated_resources})

    def test_relationship_to_nonexistent_table(self):
        data = get_input_object()
        relationships = [
            {
                "type": "ONE-TO-MANY",
                "table": "nonexistent_table",
                "reference_field": "custid"
            }
        ]

        data["resources"][0]["relationships"] = relationships

        # relationship to non existent table
        with self.assertRaises(ValueError):
            Input(**data)

    def test_relationship_to_same_table(self):
        data = get_input_object()
        relationships = [
            {
                "type": "ONE-TO-MANY",
                "table": "Customers",
                "reference_field": "custid"
            }
        ]

        data["resources"][0]["relationships"] = relationships

        # relationship from a resource to itself
        with self.assertRaises(ValueError):
            Input(**data)

    def test_relationship_nonexistent_referenced_field(self):
        data = get_input_object()
        relationships = [
            {
                "type": "ONE-TO-MANY",
                "table": "Ord",
                "reference_field": "nonexistent_field"
            }
        ]
        data["resources"][0]["relationships"] = relationships

        # indicated field does not exist in the resource
        with self.assertRaises(ValueError):
            Input(**data)

    def test_relationship_m2m_with_ref_field(self):
        data = get_input_object()
        relationships = [
            {
                "type": "MANY-TO-MANY",
                "table": "Ord",
                "reference_field": "custid"
            }
        ]
        data["resources"][0]["relationships"] = relationships

        # many-to-many with referenced_field
        with self.assertRaises(ValueError):
            Input(**data)

    def test_relationship_o2m_with_no_ref_field(self):
        data = get_input_object()
        relationships = [
            {
                "type": "ONE-TO-MANY",
                "table": "Ord",
            }
        ]

        data["resources"][0]["relationships"] = relationships

        # one-to-many/one-to-one with no referenced_field
        with self.assertRaises(ValueError):
            Input(**data)

    def test_invalid_port(self):
        data = get_input_object()
        options = {
            "application_port": -1
        }
        data["options"] = options

        with self.assertRaises(ValueError):
            Input(**data)

        data["options"]["application_port"] = 65536

        with self.assertRaises(ValueError):
            Input(**data)

        data["options"]["application_port"] = 65535

        self.assertIsInstance(Input(**data), Input)

    def test_db_type_validation(self):
        data = get_input_object()
        options = {
            "database_options": {
                "db_type": "PostgreSQL"
            }
        }
        data["options"] = options

        with self.assertRaises(ValueError):
            Input(**data)

        data["options"]["database_options"]["db_type"] = "MariaDB"
        self.assertIsInstance(Input(**data), Input)

        data["options"]["database_options"]["db_type"] = "MongoDB"
        self.assertIsInstance(Input(**data), Input)

    def test_db_username_validation(self):
        long_string, valid_string = get_valid_and_invalid_str_input(MAX_STR_LENGTH)
        data = get_input_object()
        options = {
            "database_options": {
                "db_username": long_string
            }
        }
        data["options"] = options

        with self.assertRaises(ValueError):
            Input(**data)

        data["options"]["database_options"]["db_username"] = valid_string

        self.assertIsInstance(Input(**data), Input)

    def test_password_validation(self):
        long_password, valid_password = get_valid_and_invalid_str_input(PASSWORD_LENGTH)
        data = get_input_object()
        options = {
            "database_options": {
                "db_password": long_password
            }
        }
        data["options"] = options

        with self.assertRaises(ValueError):
            Input(**data)

        data["options"]["database_options"]["db_password"] = valid_password

        self.assertIsInstance(Input(**data), Input)

    def test_project_title_validation(self):
        invalid_title, valid_title = get_valid_and_invalid_str_input(MAX_STR_LENGTH)
        data = get_input_object()
        options = {
            "project_metadata": {
                "title": invalid_title
            }
        }
        data["options"] = options

        with self.assertRaises(ValueError):
            Input(**data)

        data["options"]["project_metadata"]["title"] = valid_title

        self.assertIsInstance(Input(**data), Input)

    def test_project_description_validation(self):
        invalid_description, valid_description = get_valid_and_invalid_str_input(PROJECT_DESCRIPTION_MAX_LENGTH)
        data = get_input_object()
        options = {
            "project_metadata": {
                "description": invalid_description
            }
        }
        data["options"] = options

        with self.assertRaises(ValueError):
            Input(**data)

        data["options"]["project_metadata"]["description"] = valid_description

        self.assertIsInstance(Input(**data), Input)

    def test_project_version_validation(self):
        invalid_version, valid_version = get_valid_and_invalid_str_input(PROJECT_VERSION_MAX_LENGTH)
        data = get_input_object()
        options = {
            "project_metadata": {
                "version": invalid_version
            }
        }
        data["options"] = options

        with self.assertRaises(ValueError):
            Input(**data)

        data["options"]["project_metadata"]["version"] = valid_version

        self.assertIsInstance(Input(**data), Input)


if __name__ == '__main__':
    unittest.main()
