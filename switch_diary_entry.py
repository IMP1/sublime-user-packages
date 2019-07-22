import sublime
import sublime_plugin
import os

DIARY_PATH = "C:/Users/huwtaylor/Documents/dd"


class UpdateDiaryEntrySettings(sublime_plugin.EventListener):

    ignore_events = True

    def is_diary_entry(self, filename):
        if ".note" not in filename:
            return False
        # TODO: maybe make sure it's a diary entry?
        return True

    def on_load(self, view):
        if UpdateDiaryEntrySettings.ignore_events:
            return
            
        UpdateDiaryEntrySettings.ignore_events = True

        if not self.is_diary_entry(view.file_name()):
            return

        view.settings().set("rulers", [80])
        view.settings().set("word_wrap", False)
        view.settings().set("tab_size", 4)


class SwitchDiaryEntryCommand(sublime_plugin.TextCommand):

    def get_adjacent_entry_filename(self, current, direction):
        entries = os.listdir(DIARY_PATH)
        if not entries:
            return None
        if not current in entries:
            return None
        entries.sort()
        today_index = entries.index(current)
        next_index = today_index+direction
        if next_index < 0 or next_index >= len(entries):
            return None
        next_filename = entries[next_index]
        return next_filename

    def run(self, edit, forward, same_view):
        direction = -1
        if forward:
            direction = 1
        this_entry_filepath = self.view.file_name()
        this_entry_filename = this_entry_filepath.split("\\")[-1]
        next_entry = self.get_adjacent_entry_filename(this_entry_filename, direction)
        if next_entry:
            next_entry_filename = DIARY_PATH + "/" + next_entry
            window = self.view.window()
            if same_view:
                self.view.close()
            UpdateDiaryEntrySettings.ignore_events = False
            window.open_file(next_entry_filename)