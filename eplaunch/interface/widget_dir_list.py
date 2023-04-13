from pathlib import Path
from tkinter import Tk, NSEW, VERTICAL, HORIZONTAL, Frame, END, NS, TOP, BOTH, EW, PhotoImage, BROWSE, filedialog
from tkinter.ttk import Treeview, Scrollbar
from typing import Callable, Optional


class DirListWidget(Treeview):
    def __init__(
            self, parent_frame: Frame,
            on_select: Optional[Callable[[bool, Path], None]] = None,
            on_root_changed: Optional[Callable[[Path], None]] = None
    ):
        super().__init__(parent_frame, selectmode=BROWSE)
        # member variables
        self.directory_node_ids = []
        self.root_path = None  # Path
        # disable callbacks while widget is initializing
        self.callback_on_new_selection = None
        self.callback_on_root_changed = None
        # set up the initial directory listing
        this_file_dir = Path(__file__).parent.resolve()
        initial_root_path = Path(this_file_dir)
        folder_icon_path = this_file_dir / 'resources' / 'folder_opened.png'
        self.root_folder_image = PhotoImage(file=folder_icon_path)
        folder_closed_icon_path = this_file_dir / 'resources' / 'folder_closed.png'
        self.non_root_folder_image = PhotoImage(file=folder_closed_icon_path)
        self.root_node = self.insert('', END, text=this_file_dir.anchor, open=True, image=self.root_folder_image)
        self.refresh_listing(initial_root_path)
        # bind some events, we may just forward them to callbacks
        self.bind('<<TreeviewSelect>>', self._item_selected)
        self.bind('<Double-1>', self._item_double_clicked)
        # connect bindings
        self.callback_on_new_selection = on_select
        self.callback_on_root_changed = on_root_changed

    def _item_selected(self, *_):
        if len(self.selection()) != 1:
            return  # must not have selected anything
        single_selected_item_id = self.selection()[0]
        item_contents = self.item(single_selected_item_id)
        if self.callback_on_new_selection:
            is_root = single_selected_item_id == self.root_node
            if is_root:
                selected_path = self.root_path
            else:
                selected_path = Path(item_contents['values'][0])
            self.callback_on_new_selection(is_root, selected_path)

    def _item_double_clicked(self, *_):
        if len(self.selection()) != 1:
            return  # must not have selected anything
        # with select-mode set to browse there should only be one selected item at a time
        single_selected_item_id = self.selection()[0]
        item_contents = self.item(single_selected_item_id)
        # default double click behavior is to reset the root to the double-clicked folder
        if single_selected_item_id == self.root_node:
            return
        # values will only hold one extra item, the absolute path for that node
        clicked_node_path = item_contents['values'][0]
        self.refresh_listing(Path(clicked_node_path))

    def reset_tree(self):
        self.heading('#0', text="(Dir Path)", anchor='w', command=self.select_new_root)
        for item in self.directory_node_ids:
            self.delete(item)
        self.directory_node_ids.clear()

    def select_new_root(self):
        response = filedialog.askdirectory()
        if not response:
            return
        p = Path(response)
        if p.exists():
            self.refresh_listing(p)

    def refresh_listing(self, new_path: Optional[Path] = None):
        self.reset_tree()
        if new_path is not None:
            string_root = str(new_path)
            self.heading('#0', text="Click here to select root...")
            self.root_path = new_path
            self.item(self.root_node, text=string_root, image=self.root_folder_image)
        new_id = self.insert(
            self.root_node, 'end', text=".. (parent dir)", values=(str(self.root_path.parent),),
            image=self.non_root_folder_image
        )
        self.directory_node_ids.append(new_id)
        for p in sorted(self.root_path.glob('*')):
            if p.is_dir() and not p.name.startswith('.') and not p.name.startswith('__py'):
                new_id = self.insert(
                    self.root_node, 'end', text=str(p.name), open=False, values=(str(p),),
                    image=self.non_root_folder_image
                )
                self.directory_node_ids.append(new_id)
            # elif p.is_file() and not p.name.startswith('.') and not p.name.startswith('__'):
            #     print(f"Filename \"{p.name}\"; File path \"{str(p)}\"")
        # self.update()
        if new_path and self.callback_on_root_changed:
            self.callback_on_root_changed(new_path)
        self.selection_set(self.root_node)


class DirListScrollableFrame(Frame):
    def __init__(
            self, parent,
            on_select: Optional[Callable[[bool, Path], None]] = None,
            on_root_changed: Optional[Callable[[Path], None]] = None
    ):
        super().__init__(parent)
        self.dir_list = DirListWidget(self, on_select, on_root_changed)
        self.dir_list.grid(row=0, column=0, sticky=NSEW)
        ysb = Scrollbar(self, orient=VERTICAL, command=self.dir_list.yview)
        xsb = Scrollbar(self, orient=HORIZONTAL, command=self.dir_list.xview)
        self.dir_list.configure(yscrollcommand=ysb.set, xscrollcommand=xsb.set)
        ysb.grid(row=0, column=1, sticky=NS)
        xsb.grid(row=1, column=0, sticky=EW)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)


if __name__ == "__main__":
    root = Tk()
    root.title('Directory Listing Widget Demo')
    file_listing = DirListScrollableFrame(root)
    file_listing.pack(side=TOP, expand=True, fill=BOTH)
    root.mainloop()
