import wx


class FileNameMenus(object):

    def __init__(self, menu, start_separator_id, end_separator_id, config, path_to_config):
        self.menu = menu
        self.start_separator_id = start_separator_id
        self.end_separator_id = end_separator_id
        self.config = config
        self.path_to_config = path_to_config
        self.menu_items_for_files = []
        self.file_name_to_id = {}

    def delete_file_list(self):
        menu_list = self.menu.GetMenuItems()
        mode = False
        for menu_item in menu_list:
            if menu_item.GetId() == self.end_separator_id:
                mode = False
            if mode:
                self.menu.Remove(menu_item)
            if menu_item.GetId() == self.start_separator_id:
                mode = True

    def get_file_list(self):
        list_of_menu_item_labels = []
        menu_list = self.menu.GetMenuItems()
        mode = False
        self.file_name_to_id = {}
        for menu_item in menu_list:
            if menu_item.GetId() == self.end_separator_id:
                mode = False
            if mode:
                list_of_menu_item_labels.append(menu_item.GetLabel())
                self.file_name_to_id[menu_item.GetLabel()] = menu_item.GetId()
            if menu_item.GetId() == self.start_separator_id:
                mode = True
        return list_of_menu_item_labels

    def add_file_name_list(self, list_of_file_names):
        self.delete_file_list()
        menu_list = self.menu.GetMenuItems()
        mode = False
        for position, menu_item in enumerate(menu_list):
            if mode:
                for file_count, file_name in enumerate(list_of_file_names):
                    # add the file name and derive a ID number based on the count and the first separator ID
                    new_menu_item = self.menu.Insert(position + file_count, self.compute_file_menu_id( file_count ),
                                                     file_name, kind=wx.ITEM_CHECK)
                    #new_menu_item.Check(True)
                    self.menu_items_for_files.append(new_menu_item)
                    self.menu.Bind(wx.EVT_MENU, self.handle_menu_selection, new_menu_item)
                break
            if menu_item.GetId() == self.start_separator_id:
                mode = True

    def compute_file_menu_id(self,index):
        return self.start_separator_id * 20 + index

    def handle_menu_selection(self, event):
        current_menu_item = self.menu.FindItemById(event.GetId())
        print('clicked menu item:', current_menu_item.GetLabel(), current_menu_item.GetId())
        self.uncheck_other_items(current_menu_item)

    def save_config(self):
        # in Windows using RegEdit these appear in:
        #    HKEY_CURRENT_USER\Software\EP-Launch3
        self.config.WriteInt(self.path_to_config + "/Count",len(self.menu_items_for_files))
        # save menu items to configuration file
        menu_labels =  [menu_item.GetLabel() for menu_item in self.menu_items_for_files]
        for count, menu_label in enumerate(menu_labels):
            self.config.Write(self.path_to_config + "/Path-{:02d}".format(count), menu_label)

    def retrieve_config(self):
        count_menu_lables = self.config.ReadInt(self.path_to_config + "/Count",0)
        list_of_labels =[]
        for count in range(0,count_menu_lables):
            label = self.config.Read(self.path_to_config + "/Path-{:02d}".format(count))
            if label:
                list_of_labels.append(label)
        self.add_file_name_list(list_of_labels)

    def uncheck_other_items(self, current_menu_item):
        current_menu_item_id = current_menu_item.GetId()
        for menu_item in self.menu_items_for_files:
            menu_item_id = menu_item.GetId()
            if menu_item_id != current_menu_item_id:
                self.menu.Check(menu_item_id,False)



