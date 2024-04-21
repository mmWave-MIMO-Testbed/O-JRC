import evk.gui.Page as p
import tkinter as tk
import tkinter.ttk as ttk


import ram_file

class RamFileSelector():
    def __init__(self, parent, filename, filter=None, select_callback=None, *args, **kwargs):
        self.parent = parent
        self.lastPressed = None
        self.filename = filename
        self.select_callback = select_callback

        self.ram_file_selector_win = tk.Toplevel(parent)
        self.ram_file_selector_win.title(filename)
        if filter != None:
            if type(filter) != list:
                filter = [filter]

        file_name_length = 43
        description_length = 100
        supported_mod_length = 45
        version_length = 7
        selected_length = 8

        rf = ram_file.RamFile(filename)
        self.table_id_list = rf.table_id_list()
        ignore_tags = ['DATA_FORMAT', 'FIELD_SPECS', 'ROW']
        col_size = {'DESC': 40, 'TYPE':12, 'VERSION':16, 'ID':12, 'FREQ':10, 'TEMP':10, 'SUPPLY':10}
        table_info = {}
        col_def = []
        for id in range(len(self.table_id_list)):
            if  (filter == None) or (rf.table_tag_info(self.table_id_list[id], 'TYPE') in filter):
                tags = rf.tables[id].findall('*')
                table_info[id] = {}
                for tag in tags:
                    if tag.tag not in ignore_tags:
                        try:
                            cs = col_size[tag.tag]
                        except:
                            cs = 10
                        if not (tag.tag, cs) in col_def:
                            col_def.append((tag.tag, cs))
                        table_info[id].update({tag.tag: rf.table_tag_info(self.table_id_list[id], tag.tag)})

        tk.Label(self.ram_file_selector_win,  text='<<< Double-Click table ID to load table and write to RAM >>>', font=(12), fg='blue').pack(side=tk.TOP)
        self.mlb_tx = MultiListbox(self.ram_file_selector_win, col_def, self.ram_table_selected)
        for id in range(len(self.table_id_list)):
            if  (filter == None) or (rf.table_tag_info(self.table_id_list[id], 'TYPE') in filter):
                row_data = []
                for tag in tags:
                    if tag.tag not in ignore_tags:
                        row_data.append(table_info[id][tag.tag])
                self.mlb_tx.insert(tk.END, row_data)
        self.mlb_tx.pack(side=tk.TOP, expand=tk.NO,fill=tk.BOTH)

    def ram_table_selected(self):
        i = self.mlb_tx.curselection()[0]
        self.select_callback(self.filename, self.mlb_tx.lists[0].get(i))
        self.ram_file_selector_win.destroy()

class MultiListbox(tk.Frame):
    def __init__(self, master, lists, cbselected):
        tk.Frame.__init__(self, master)
        self.cbselected = cbselected
        self.lists = []
        for l,w in lists:
            frame = tk.Frame(self); frame.pack(side=tk.LEFT, expand=tk.YES, fill=tk.BOTH)
            tk.Label(frame, text=l, borderwidth=1, relief=tk.RAISED).pack(fill=tk.X)
            lb = tk.Listbox(frame, width=w, borderwidth=0, height=20, selectborderwidth=0, relief=tk.FLAT, exportselection=tk.FALSE)
            lb.pack(expand=tk.YES, fill=tk.BOTH)
            self.lists.append(lb)
            lb.bind('<B1-Motion>', lambda e, s=self: s._select(e.y))
            lb.bind('<Button-1>', lambda e, s=self: s._select(e.y))
            lb.bind('<Leave>', lambda e: 'break')
            lb.bind('<B2-Motion>', lambda e, s=self: s._b2motion(e.x, e.y))
            lb.bind('<Button-2>', lambda e, s=self: s._button2(e.x, e.y))
            lb.bind('<Double 1>', lambda e, s=self: s.__select(e.y))
        frame = tk.Frame(self); frame.pack(side=tk.LEFT, fill=tk.Y)
        tk.Label(frame, borderwidth=1, relief=tk.RAISED).pack(fill=tk.X)
        sb = tk.Scrollbar(frame, orient=tk.VERTICAL, command=self._scroll)
        sb.pack(expand=tk.YES, fill=tk.Y)
        self.lists[0]['yscrollcommand']=sb.set

    def __select(self, y):
        self.cbselected()

    def _select(self, y):
        row = self.lists[0].nearest(y)
        self.selection_clear(0, tk.END)
        self.selection_set(row)
        return 'break'

    def _button2(self, x, y):
        for l in self.lists: l.scan_mark(x, y)
        return 'break'

    def _b2motion(self, x, y):
        for l in self.lists: l.scan_dragto(x, y)
        return 'break'

    def _scroll(self, *args):
        for l in self.lists:
            l.yview(*args)

    def curselection(self):
        return self.lists[0].curselection()

    def delete(self, first, last=None):
        for l in self.lists:
            l.delete(first, last)

    def get(self, first, last=None):
        result = []
        for l in self.lists:
            result.append(l.get(first,last))
        if last:
            return map(None, *result)
        return result
        
    def index(self, index):
        self.lists[0].index(index)

    def insert(self, index, *elements):
        for e in elements:
            i = 0
            for l in self.lists:
                l.insert(index, e[i])
                i = i + 1

    def size(self):
        return self.lists[0].size()

    def see(self, index):
        for l in self.lists:
            l.see(index)

    def selection_anchor(self, index):
        for l in self.lists:
            l.selection_anchor(index)

    def selection_clear(self, first, last=None):
        for l in self.lists:
            l.selection_clear(first, last)

    def selection_includes(self, index):
        return self.lists[0].selection_includes(index)

    def selection_set(self, first, last=None):
        for l in self.lists:
            l.selection_set(first, last)