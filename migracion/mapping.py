import csv
import os
import re

from datetime import datetime


class Column:

    def __init__(self, index: int, name: str=None, datatype: str=None, nullable: bool=False, values: set=None):
        self.index = index
        self.name = name
        self.datatype = datatype
        self.nullable = nullable
        self.values = values
        self.primary_key = False

    def __repr__(self):
        is_null = '' if self.nullable else ' NOT NULL'
        is_pk = ' PRIMARY KEY' if self.index == 0 else ''
            
        return f'\n\t{self.name} {self.datatype}{is_null}{is_pk}'


class Table:

    def __init__(self, name=None, columns=[]):
        self.name = name
        self.columns = columns

    def __repr__(self):
        return f'CREATE TABLE {self.name} ({self.columns}\n);'.replace('[','').replace(']','')


def list_files(path):
    return os.listdir(path)


def has_nulls(values: list) -> bool:
    for val in values:
        if val == '' or val == 'null':
            return True
    return False

def set_nullability(column: Column) -> None:
    column.nullable = has_nulls(column.values)


def set_data_types(column: Column) -> None:
    date_pattern = re.compile("^\d{2}/\d{2}/\d{4}$")
    datetime_pattern = re.compile("^\d{2}/\d{2}/\d{4} \d{2}:\d{2} [ap]. m.$")
    time_pattern = re.compile("^\d{2}:\d{2}:\d{2}$")

    if len(column.values) == 1 and 'null' in column.values:
        if column.name.startswith('ID_'):
            column.datatype = "INTEGER"
        else:
            column.datatype = "VARCHAR(45)"
        return

    size = len(max(column.values, key=len))
    if size > 22:
        column.datatype = f"VARCHAR({size})"
    elif size == 0:
        column.datatype = f"VARCHAR(15)"
    else:
        for val in column.values:
            if len(val) > 1 and val[0] == '0' and val.isdecimal():
                column.datatype = f"CHAR({size})"
            elif val.lstrip('-').replace(",", "").replace(".00", "").isdecimal():
                column.datatype = "INTEGER"
            elif date_pattern.match(val):
                column.datatype = 'DATE'
            elif datetime_pattern.match(val):
                column.datatype = 'TIMESTAMP'
            elif time_pattern.match(val):
                column.datatype = 'TIMESTAMP'
            else:
                column.datatype = f"VARCHAR({size})"


def create_metadata(path: str, file: str, header: bool=True) -> Table:
    table = Table(file[:-4])
    index = 0

    with open(f'{path}{file}', encoding="ISO-8859-1") as csv_file:
        for row in csv.reader(csv_file, delimiter='\t'):
            if header:
                table.columns = [Column(i, r, values=set()) for i,r in enumerate(row)]
                header = False
            else:
                index += 1
                for index, c in enumerate(table.columns):
                    c.values.add(row[index])
            if index == 10:
                break

    return table

def generate_ddl(path, output):
    with open(output, "w", encoding='utf-8') as f:
        for file in sorted(list_files(path)):
            print(f"{file}...", end="")
            table = create_metadata(path, file)
        
            for column in table.columns:
                set_data_types(column)
                set_nullability(column)

            f.write(f"\n\n{table}")
            print(" processed!")


def clean_data(datatypes: list = None, row: list = None) -> None:
    if datatypes[0] == 'SERIAL':
        result = '0'
        datatypes.pop(0)
    else:
        result = ''

    for i, value in enumerate(row):
        new_value = ''
        value = '' if value == 'null' else value
        if datatypes[i] == 'INTEGER':
            new_value = value.lstrip('-').replace(",", "").replace(".00", "").strip()
        elif datatypes[i] == 'TIMESTAMP':
            if 'a. m.' in value:
                value = value.replace('a. m.', 'AM')
            else:
                value = value.replace('p. m.', 'PM')
            if value != '':
                value = datetime.strptime(value, '%d/%m/%Y %H:%M %p')
                new_value = value.strftime("%m/%d/%Y %H:%M:%S")
        else:
            if value == None or value == '':
                new_value = ''
            else:
                if len(value) > 0 and value[0] == '\'' or value[0] == '\"':
                    value = value[1:]
                if len(value) > 0 and value[-1] == '\'' or value[-1] == '\"':
                    value = value[:-1]
                value = value.strip()
                new_value = '' if value == 'null' else value
                new_value = new_value.replace('\n', '\\n').replace('"', "'")
        result += f',"{new_value}"'

    return result[1:]


def load_ddl(name_file: str) -> set:
    file = open(name_file, mode='r')
    ddl = file.read()
    file.close()

    tables = {}

    for sencence in [s.strip() for s in ddl.split(");\n")]:
        columns = sencence.split('\n')
        name = columns[0].replace('CREATE TABLE ', '')
        data_types = []
        for col in columns[1:]:
            col = col.strip('\b\t')
            type = col.split(' ')
            if len(type) == 2:
                data_types.append(type[1])
        tables[name[:-1]] = data_types 

    return tables


def load_data(metadata: dict, path: str, output: str) -> None:
   
    #for file in sorted(list_files(path)):
    for file in ['DETALLE_PROGRAMAS.csv']:
        name = file.replace('.csv', '')
        print(f"{name}...", end="")

        index = 0

        with open(f'{path}{file}', encoding="ISO-8859-1") as input, open(f'{output}{file}', "w", encoding="ISO-8859-1") as out:
            for row in csv.reader(input, delimiter='\t'):
                if index == 0:
                    headers = '"' + '","'.join(row).lower() + '"'
                    out.write(headers)
                    out.write("\n")
                else:
                    cleaned = clean_data(metadata[name], row)
                    out.write(cleaned)
                    out.write("\n")
                index += 1
        print(index, "lines written. File processed!")


if __name__ == '__main__':
    path = './resources/videoteca/'
    out_path = './resources/clean/'
    # generate_ddl(path, "tables.txt")
    metadata = load_ddl('metadata.txt')
    load_data(metadata, path, out_path)
    #for i, v in metadata.items():
    #    print(i, v)
    #load_data(path, out_path)
    