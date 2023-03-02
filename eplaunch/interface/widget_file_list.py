from random import randint
from tkinter import NSEW, VERTICAL, Frame, END, NS, TOP, BOTH, EXTENDED
from tkinter.ttk import Treeview, Scrollbar
from tkinter.messagebox import showinfo
from typing import Tuple, Optional, Callable, List


class FileListWidget(Treeview):

    def __init__(self, parent_frame: Frame, on_selection_changed: Optional[Callable[[List[str]], None]] = None):
        super().__init__(parent_frame, columns=['File Name'], show='headings', selectmode=EXTENDED)
        # disable callbacks while widget is initializing
        self.callback_on_selection_changed = None
        self.columns = ['File Name']
        # define headings
        for c in self.columns:
            self.heading(c, text=c)
        self.file_ids: List[str] = []
        self.bind('<<TreeviewSelect>>', self._selection_changed)
        self.bind('<Double-1>', self._item_double_clicked)
        self.callback_on_selection_changed = on_selection_changed

    def set_files(self, file_list: List[Tuple]):
        for file_id in self.file_ids:
            self.delete(file_id)
        self.file_ids.clear()
        for file_data in file_list:
            self.file_ids.append(self.insert('', END, values=file_data))

    def _selection_changed(self, *_):
        if not self.callback_on_selection_changed:
            return
        response = []
        for selected_id in self.selection():
            item_contents = self.item(selected_id)
            file_name = item_contents['values'][0]
            response.append(file_name)
        self.callback_on_selection_changed(response)

    def _item_double_clicked(self, _):
        for selected_item in self.selection():
            item = self.item(selected_item)
            record = [str(x) for x in item['values']]
            showinfo(title='Information', message=','.join(record))

    def try_to_reselect(self, files_to_reselect: List[str]):
        # don't call back during programmatic selection
        hold_callback = self.callback_on_selection_changed
        self.callback_on_selection_changed = None
        for f in self.file_ids:
            item = self.item(f)
            if item['values'][0] in files_to_reselect:
                self.selection_add(f)
        self.callback_on_selection_changed = hold_callback

    def set_new_columns(self, extended_column_names=None) -> None:
        # we always leave Filename, the list should include Stale, Weather, etc.
        if extended_column_names is None:
            extended_column_names = list()
        column_list = ['File Name']
        column_list.extend(extended_column_names)
        self["columns"] = column_list
        for i, c in enumerate(column_list):
            # self.column(i, anchor='c')
            self.heading(i, text=c)


class FileListScrollableFrame(Frame):
    def __init__(self, parent, on_selection_changed: Optional[Callable[[List[str]], None]] = None):
        super().__init__(parent)
        self.tree = FileListWidget(self, on_selection_changed)
        self.tree.grid(row=0, column=0, sticky=NSEW)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure('all', weight=1)
        scrollbar = Scrollbar(self, orient=VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.grid(row=0, column=1, sticky=NS)


def printer(selection: List[str]) -> None:
    print(selection)


counter = 0


def set_columns():
    global counter
    counter += 1
    if counter == 1:
        file_listing.tree.set_new_columns(['hi', 'world'])
    elif counter == 2:
        file_listing.tree.set_new_columns(['foo'])
    elif counter == 3:
        file_listing.tree.set_new_columns(['hello', 'world', 'bar'])
    elif counter == 4:
        file_listing.tree.set_new_columns()
    elif counter == 5:
        file_listing.tree.set_new_columns(['edwin', 'lee'])


if __name__ == "__main__":
    from tkinter import Button, Tk
    root = Tk()
    root.title('File Listing Widget Demo')

    file_listing = FileListScrollableFrame(root, printer)
    files = []
    for n in range(1, 100):
        rand = randint(1, 10)
        files.append((
            f"FileName{n}.png",
            "true" if rand > 5 else "",
            "PNG Image File",
            rand ** 2
        ))
    file_listing.tree.set_files(files)
    file_listing.pack(side=TOP, expand=True, fill=BOTH)
    file_listing.tree.try_to_reselect(['FileName1.png'])
    Button(text="add columns", command=set_columns).pack(side=TOP, fill='x')
    root.mainloop()