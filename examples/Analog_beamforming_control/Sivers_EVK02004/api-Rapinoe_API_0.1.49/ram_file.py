import xml.etree.ElementTree as ET

import evk_logger

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

    def find_index_by_tag(self, id, tag, tag_value):
        idx = self._id_to_idx(id)
        rows = self.tables[idx].findall('ROW')
        index_list = []
        for row in rows:
            if row.find(tag).text.lstrip().rstrip() == str(tag_value):
                #found_row = row
                index_list.append(row.find('INDEX').text.lstrip().rstrip())
        return index_list

    def find_index_by_tags(self, id, tags_tag_values):
        idx = self._id_to_idx(id)
        rows = self.tables[idx].findall('ROW')
        index_list = []
        tag_list = list(tags_tag_values.keys())
        for row in rows:
            found = True
            for tag in tag_list:
                found = found and (row.find(tag.upper()).text.lstrip().rstrip() == str(tags_tag_values[tag]))
                if not found:
                    break
            if found:
                index_list.append(row.find('INDEX').text.lstrip().rstrip())
        return index_list

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

    def find_tables_by_type(self, table_type):
        """Returns list of table IDs of the specified type.

        Args:
            table_type (str): Table type as a string. e.g. 'RAM', 'TX_RAM_H', 'TX_RAM_V', 'RX_RAM_H', 'RX_RAM_V'

        Returns:
            list: List of table IDs
        """
        tables = []
        table_id_list = self.table_id_list()
        for id in table_id_list:
            if self.table_tag_info(id, 'TYPE') == table_type:
                tables.append(id)
        return tables

    def file_header(self):
        evk_logger.evk_logger.log_bold('')
        evk_logger.evk_logger.log_bold('RAM file general information')
        evk_logger.evk_logger.log_bold('============================')
        evk_logger.evk_logger.log_bold('')
        evk_logger.evk_logger.log_bold('{:15}  {} {}'.format('LOCATION', ':',self.filename))
        elements = self.ram_root.findall('*')
        table_indentation = 5
        for element in elements:
            if element.tag != 'TABLE':
                evk_logger.evk_logger.log_bold('{:15}  {} {}'.format(element.tag, ':',element.text.lstrip().rstrip()))
            else:
                table_elements = element.findall('*')
                evk_logger.evk_logger.log_bold('')
                evk_logger.evk_logger.log_bold('RAM TABLE', indentation=table_indentation)
                evk_logger.evk_logger.log_bold('---------', indentation=table_indentation)
                for table_element in table_elements:
                    if table_element.tag != 'ROW' and table_element.tag != 'FIELD_SPECS':
                        evk_logger.evk_logger.log_bold('{:15}  {} {}'.format(table_element.tag, ':',table_element.text.lstrip().rstrip()), indentation=table_indentation)
                evk_logger.evk_logger.log_bold('')
