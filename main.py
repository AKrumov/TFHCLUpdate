import argparse
import json
from ast import literal_eval

import hcl


class HCLUpdate:
    def __init__(self):
        self.args = self._load_arguments()
        self.file_name = self.args.file
        self.data = self._load_file()

        if self.args.data:
            self.update_variable(self.args.variable, self.args.data)
        else:
            self.get_variable_as_dict(self.args.variable)

    @staticmethod
    def _load_arguments():
        parser = argparse.ArgumentParser(description='HCLUpdate CLI tool for variable files.')
        parser.add_argument('--file', help='Full path to the HCL file', required=True)
        parser.add_argument('--variable', help='Variable name to retrieve or update', required=True)
        parser.add_argument('--data', help='New data for the variable (optional)')

        return parser.parse_args()

    @staticmethod
    def _reformat_dict(data, indent):
        result = "[\n"
        items = literal_eval(data)

        for item in items:
            result += indent + "  {\n"
            for key, value in item.items():
                result += f'{indent}    {key} = "{value}"\n'
            result += indent + ('  }\n' if item == items[-1] else '  },\n')

        result += indent + ']\n'
        return result

    def _load_file(self):
        try:
            with open(self.file_name, 'r') as f:
                return hcl.load(f).get('variable', {})
        except (FileNotFoundError, hcl.HCLError) as e:
            raise ValueError(f"Error loading file: {e}")

    def _update_file(self):
        try:
            with open(self.file_name, 'w') as f:
                f.write(self._dict_to_hcl2(self.data))
        except IOError as e:
            raise ValueError(f"Error writing to file: {e}")

    def _to_hcl2(self, data, level=0):
        indent = "  " * level
        hcl2_str = ""

        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, dict):
                    if level == 0:
                        hcl2_str += f'{indent}variable "{key}" {{\n'
                    else:
                        hcl2_str += f'{indent}{key} = {{\n'
                    hcl2_str += self._to_hcl2(value, level + 1)
                    hcl2_str += f'{indent}}}\n'
                else:
                    value = value.replace('"', "") if key == 'type' else json.dumps(value)
                    if "[{" in value:
                        value = self._reformat_dict(value, indent)
                    hcl2_str += f'{indent}{key} = {value}\n'
        elif isinstance(data, list):
            hcl2_str += f"{indent}[\n"
            for item in data:
                hcl2_str += self._to_hcl2(item, level + 1)
            hcl2_str += f"{indent}]\n"
        else:
            hcl2_str += f'{indent}{json.dumps(data)}\n'

        return hcl2_str

    def _dict_to_hcl2(self, data):
        return "\n".join([self._to_hcl2({key: value}) for key, value in data.items()])

    def get_variable_as_dict(self, name):
        variable = self.data.get(name)
        if not variable:
            raise ValueError(f"No variable named '{name}' found in {self.file_name}.")
        print(json.dumps(variable['default'], indent=2))
        return variable['default']

    def update_variable(self, name, variable_data):
        if name not in self.data:
            raise ValueError(f"No variable named '{name}' found in {self.file_name}.")

        try:
            self.data[name]['default'] = literal_eval(variable_data)
        except (ValueError, SyntaxError):
            self.data[name]['default'] = variable_data

        self._update_file()


if __name__ == "__main__":
    HCLUpdate()
