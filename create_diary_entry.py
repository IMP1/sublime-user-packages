import sublime
import sublime_plugin
import datetime
import os
import re

DIARY_PATH = "C:/Users/huwtaylor/Documents/dd"

class CreateDiaryEntryCommand(sublime_plugin.TextCommand):

    def get_previous_entry(self, today_filename):
        entries = os.listdir(DIARY_PATH)
        if not entries:
            return None
        # Add today's date and then get its index to find yesterday
        entries.append(today_filename)
        entries.sort()
        today_index = entries.index(today_filename)
        last_filename = entries[today_index-1]
        last_file = open(DIARY_PATH + "/" + last_filename, mode="r", encoding="utf-8")
        last_entry = last_file.read()
        return last_entry

    def get_previous_todos(self, today_filename):
        last_entry = self.get_previous_entry(today_filename)
        if last_entry == None:
            return []
        todo_section = re.search("# To Do[\n]*(.*?)# Notes", last_entry, re.DOTALL)
        todo_lines = todo_section.group(1).split("\n")
        for i, line in enumerate(todo_lines):
            if not re.search("\[[\s\-X]\]", line):
                parent_index = i-1
                while todo_lines[parent_index] is None or not re.search("\[[\s\-X]\]", todo_lines[parent_index]):
                    parent_index -= 1
                parent_line = todo_lines[parent_index]
                if ("[X]" in parent_line) or ("[-]" in parent_line):
                    todo_lines[i] = None
        unremoved_todos = [todo for todo in todo_lines if todo is not None]
        unfinished_todos = [todo for todo in unremoved_todos if not "[X]" in todo]
        uncancelled_todos = [todo for todo in unfinished_todos if not "[-]" in todo]
        return uncancelled_todos

    def run(self, edit):
        current_datetime = datetime.datetime.now()
        today_filename = current_datetime.strftime("%Y-%m-%d.note")

        # DEBUG: This makes the next entry even if it's not the day for it yet.
        while today_filename in os.listdir(DIARY_PATH):
            current_datetime += datetime.timedelta(days=1)
            today_filename = current_datetime.strftime("%Y-%m-%d.note")
        # /DEBUG

        if today_filename in os.listdir(DIARY_PATH):
            self.view.window().open_file(DIARY_PATH + "/" + today_filename)
            return

        date_string = current_datetime.strftime("%Y-%m-%d")
        time_string = (current_datetime - datetime.timedelta(minutes=2)).strftime("%H%M")
        entry_template = date_string + "\n"
        entry_template += time_string + "-\n\n"
        entry_template += "# To Do\n\n"

        previous_todos = self.get_previous_todos(today_filename)
        for todo in previous_todos:
            entry_template += todo+"\n"
        entry_template += "# Notes\n\n\n(-∅-)"
        view = self.view.window().new_file()
        view.insert(edit, 0, entry_template)
        view.assign_syntax("Note.sublime-syntax")
        view.settings().set("rulers", [80])
        view.settings().set("word_wrap", False)
        view.settings().set("tab_size", 4)
        view.settings().set("default_dir", DIARY_PATH)
        view.set_name(today_filename)
        # view.window().run_command("prompt_save_as")

