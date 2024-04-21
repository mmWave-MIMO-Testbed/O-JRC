import xml.etree.ElementTree as ET


class RamFile():
    def __init__(self, filename):
        self.filename = filename
        ram_tree = ET.parse(filename)
        self.ram_root = ram_tree.getroot()
        if self.ram_root.tag != 'RAM':
            raise Exception("File not a RAM file.")
        self.tables = self.ram_root.findall('TABLE')
        self.id_list = self._generate_table_id_list()

    def name(self):
        return self.ram_root.find('NAME').text

    def description(self):
        return self.ram_root.find('DESCRIPTION').text

    def module_types(self):
        return self.ram_root.find('MODULE_TYPES').text

    def table_id_list(self):
        return self.id_list

    def table_count(self):
        return len(self.tables)

    def table_tag_info(self, id, tag):
        tag = tag.upper()
        idx = self._id_to_idx(id)
        return self.tables[idx].find(tag).text.lstrip().rstrip()

    def table_row_data_by_index(self, id, index):
        row = self._find_row(id, index)
        data = row.find('DATA').text.lstrip().rstrip()
        data = data.split(',')
        data_format = self.table_tag_info(id, 'DATA_FORMAT').upper().lstrip().rstrip()
        data = self._conv_str_data_to_int(data, data_format)
        row_data = {index:{}}
        field_names = self._table_field_specs(id)
        for i in range(len(field_names)):
            row_data[index][field_names[i]] = data[i]
        return row_data

    def table_row_data_by_position(self, id, pos):
        idx = self._id_to_idx(id)
        row = self.tables[idx].findall('ROW')[pos]
        index = int(row.find('INDEX').text.lstrip().rstrip())
        data = row.find('DATA').text.lstrip().rstrip()
        data = data.split(',')
        data_format = self.table_tag_info(id, 'DATA_FORMAT').upper().lstrip().rstrip()
        data = self._conv_str_data_to_int(data, data_format)
        row_data = {index:{}}
        field_names = self._table_field_specs(id)
        for i in range(len(field_names)):
            row_data[index][field_names[i]] = data[i]
        return row_data

    def table_data(self, id):
        idx = self._id_to_idx(id)
        rows = self.tables[idx].findall('ROW')
        table = {}
        for row_pos in range(len(rows)):
            table.update(self.table_row_data_by_position(id, row_pos))
        return table

    def _generate_table_id_list(self):
        table_id_list = []
        for table in self.tables:
            table_id_list.append(table.find('ID').text.lstrip().rstrip())
        return table_id_list

    def _table_field_specs(self, id):
        idx = self._id_to_idx(id)
        fields = self.tables[idx].find('FIELD_SPECS').findall('FIELD')
        def field_name(f):
            return f.find('NAME').text.lower()
        return list(map(field_name, fields))

    def _find_row(self, id, index):
        idx = self._id_to_idx(id)
        rows = self.tables[idx].findall('ROW')
        for row in rows:
            if row.find('INDEX').text.lstrip().rstrip() == str(index):
                return row

    def _conv_str_data_to_int(self, data, data_format):
        def conv_str_to_int(s):
            if data_format == 'HEX':
                return int(s, 16)
            elif data_format == 'DEC':
                return int(s, 10)
            return int(s)

        return list(map(conv_str_to_int, data))

    def _id_to_idx(self, id):
        return self.id_list.index(id)
