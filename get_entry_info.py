import sublime
import sublime_plugin
import datetime
import os

DIARY_PATH = "C:/Users/huwtaylor/Documents/dd"
PANEL_NAME = "diary_entry_info"

class UpdateEntryInfo(sublime_plugin.EventListener):

    ignore_events = False

    def on_load(self, view):
        if UpdateEntryInfo.ignore_events:
            return

        UpdateEntryInfo.ignore_events = True
        window = view.window()
        if window.active_panel() == "output." + PANEL_NAME:
            window.focus_view(view)
            window.run_command("get_entry_info")
        UpdateEntryInfo.ignore_events = False


class GetEntryInfoCommand(sublime_plugin.TextCommand):

    def is_diary_entry(self):
        return ".note" in self.view.file_name()
        # TODO: maybe make sure it's a diary entry?

    def get_date_string(self):
        region = self.view.find(r"\b\d{4}\-\d{2}\-\d{2}\b", 0)
        return self.view.substr(region)

    def get_times(self):
        regions = self.view.find_all(r"\b\d{4}\-\d{4}\b", 0)
        times = [self.view.substr(r) for r in regions]
        times = [t.split("-") for t in  times]
        times = [{"from": [int(t[0][0:2]), int(t[0][2:4])], "to": [int(t[1][0:2]), int(t[1][2:4])]} for t in times]

        # Add a last time for an ongoing time period.
        region = self.view.find(r"\b\d{4}\-[\D\W]", 0)
        if region:
            ongoing = self.view.substr(region)[0:4]
            now = datetime.datetime.now()
            times.append({"from": [int(ongoing[0:2]), int(ongoing[2:4])], "to": [now.hour, now.minute]})

        return times

    def get_hours(self, times):
        hours = 0 
        for t in times:
            h = t["to"][0] - t["from"][0]
            m = t["to"][1] - t["from"][1]
            while m < 0:
                h -= 1
                m += 60
            hours += h
            hours += (m / 60)
        mins = round(60 * (hours - int(hours)))
        hours = int(hours)
        return [hours, mins]

    def get_total_day(self, times):
        hours = 0

        h = times[-1]["to"][0] - times[0]["from"][0]
        m = times[-1]["to"][1] - times[0]["from"][1]
        while m < 0:
            h -= 1
            m += 60
        hours += h
        hours += (m / 60)

        mins = round(60 * (hours - int(hours)))
        hours = int(hours)
        return [hours, mins]

    def get_day_number(self):
        entries = os.listdir(DIARY_PATH)
        this_entry = self.view.file_name().split("/")[-1].split("\\")[-1]
        return entries.index(this_entry) + 1

    def get_todo_tree(self):
        regions = self.view.find_all("\\s*\\-\\s+\\[[X\\-\\s]\\].+?\n", 0)
        todos = [self.view.substr(r).strip("\n") for r in regions]
        tree = {'note': "", 'children':[]}
        for todo in todos:
            list_index = todo.index("-")
            status = todo[list_index+3:list_index+4]
            indent_level = (list_index - 2) // 4
            t = {'note': todo[(list_index+6):], 'children':[], 'status':status, 'parent':None}
            parent = tree
            if indent_level == 0:
                parent = tree
            else:
                for i in range(0, indent_level):
                    if not parent['children']:
                        continue
                    parent = parent['children'][-1]
            t['parent'] = parent
            parent['children'].append(t)
        return tree

    def get_todo_list(self, root, parent_list=None):
        if root['children']:
            local_tree = [root]
            for child in root['children']:
                local_tree.extend(self.get_todo_list(child))
            return local_tree
        else:
            return [root]

    def create_output(self, edit):
        panel = self.view.window().create_output_panel(PANEL_NAME)

        # Date and Times
        date  = self.get_date_string()
        day   = self.get_day_number()
        times = self.get_times()
        hours = self.get_hours(times)
        total = self.get_total_day(times)
        weekday = datetime.datetime.strptime(date, "%Y-%m-%d").strftime("%A")

        first_line = "Diary Entry for " + weekday + " (" + date + ")" + " - Day #" + str(day) 
        info = first_line + "\n"
        info += "=" * len(first_line) + "\n"
        info += "Hours worked: %02d:%02d\n" % tuple(hours)
        info += "Total day:    %02d:%02d\n" % tuple(total)

        # TODOs
        todo_tree = self.get_todo_tree()
        all_todos = self.get_todo_list(todo_tree)[1:] # Remove the abstract root
        completed_todos = [t for t in all_todos if t['status'] == "X"]
        cancelled_todos = [t for t in all_todos if t['status'] == "-"]

        if completed_todos:
            comp_len = max([len(t['note']) for t in completed_todos])
            info += "Completed Tasks:\n"
            for task in completed_todos:
                info += "  * " + task['note']
                parent = task['parent']
                while parent and parent['note']:
                    padding = 1 + comp_len - len(task['note'])
                    info += (" " * padding) + "(" + parent['note'] + ")"
                    parent = parent['parent']
        
                info += "\n"

        if cancelled_todos:
            canc_len = max([len(t['note']) for t in cancelled_todos])
            info += "Cancelled Tasks:\n"
            for task in cancelled_todos:
                info += "  * " + task['note']
                parent = task['parent']
                while parent and parent['note']:
                    padding = 1 + canc_len - len(task['note'])
                    info += (" " * padding) + "(" + parent['note'] + ")"
                    parent = parent['parent']
                info += "\n"

        panel.insert(edit, 0, info)

    def run(self, edit):
        if not self.is_diary_entry():
            return
        self.create_output(edit)
        self.view.window().run_command("show_panel", {"panel": "output." + PANEL_NAME})
