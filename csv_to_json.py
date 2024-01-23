# CSV to Parameter Map in JSON converter
# Turns the provided table to VSlib-compatible Parameter map.

import sys
import json 

class Parameter:
    
    def __init__(self, name: str, parameter_type, unit=None, enum=None, limit_min=None, limit_max=None):
        self._name = name
        self._type = parameter_type
        self._unit = unit
        self._length = 1
        if enum is not None:
            self._enum = enum
            self._length = len(self._enum)
        else:
            self._enum = None
        self._limit_min = limit_min
        self._limit_max = limit_max

    def serialize(self):
        serialized_parameter = {
            "name": self._name,
            "type": self._type,
            "length": self._length,
            "unit": self._unit
        }
        if self._enum is not None:
            serialized_parameter['fields'] = self._enum
        if self._limit_min is not None:
            serialized_parameter['limit_min'] = self._limit_min
        if self._limit_max is not None:
            serialized_parameter['limit_max'] = self._limit_max
        return serialized_parameter

class Component:
    
    def __init__(self, component_type: str, name: str, parent):
        self._component_type = component_type
        self._name = name
        self._parent = parent
        if parent is not None:
            parent.add_child(self)
        self._children_list = []
        self._parameter_list = []
    
    def add_parameter(self, parameter: Parameter):
        self._parameter_list.append(parameter)

    def add_child(self, child):
        self._children_list.append(child)
    
    def has_parent(self):
        return self._parent != None

    def serialize(self):
        serialized_parameters = list()
        for parameter in self._parameter_list:
            serialized_parameters.append(parameter.serialize())

        serialized_children = list()
        for child in self._children_list:
            serialized_children.append(child.serialize())
        
        serialized_component = {
            "name": self._name,
            "type": self._component_type,
            "parameters": serialized_parameters,
            "components": serialized_children
        }
        return serialized_component

def _parse_file(file_path: str, component_dict: dict):
    with open(file_path, 'r') as file:
        current_component = None
        skip_line = True
        for line in file:
            if skip_line: # skip the header
                skip_line = False
                continue
            contents = line.split(',')
            component_type = contents[0]
            if component_type != '': # line defines new component
                parent_name = contents[1]
                if parent_name != "None" and parent_name in component_dict:
                    parent = component_dict[parent_name]
                else:
                    parent = None
                component_name = contents[2]
                component_dict[component_name] = Component(component_type, component_name, parent)
                current_component = component_dict[component_name]

            parameter_name = contents[3]
            parameter_type = contents[4]
            if parameter_type == 'Enum':
                enum_values = contents[5][1:-1].split(';')
            else:
                enum_values = None
            parameter_unit = contents[6]
            parameter_limit_min = float(contents[7]) if contents[7] not in ["", '\n'] else None 
            parameter_limit_max = float(contents[8]) if contents[8] not in ["", '\n'] else None 
            parameter = Parameter(parameter_name, parameter_type, parameter_unit, enum_values, parameter_limit_min, parameter_limit_max)
            current_component.add_parameter(parameter)

def _serialize_components(component_dict: dict):
    parameter_map = list()
    parameter_map.append({"version": [0, 2, 0]})
    for key in component_dict:
        component = component_dict[key]
        if component.has_parent():
            continue
        parameter_map.append(component.serialize())
    return parameter_map

def _write_output(output_file: str, parameter_map: json):
    with open(output_file, 'w') as file:
        file.write(json.dumps(parameter_map, indent=1))


def main(file_path: str, output_file: str):
    component_dict = dict()
    _parse_file(file_path, component_dict)
    parameter_map = _serialize_components(component_dict)
    _write_output(output_file, parameter_map)
                

if __name__ == '__main__':
    file_path = sys.argv[1]
    output_file = sys.argv[2]
    main(file_path=file_path, output_file=output_file)