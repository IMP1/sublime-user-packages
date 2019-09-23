import sublime
import sublime_plugin
import os
import re

DIARY_PATH = "C:/Users/huwtaylor/Documents/dd" # TODO: make all of the constants in different files unified somwhere.
DATE_REGEX = re.compile(r'\d{4}\-\d{2}\-\d{2}')


class LinkingEntries(sublime_plugin.TextCommand):


    def is_visible(self, event=None):
        if event:
            click_point = self.view.window_to_text((event["x"], event["y"]))
        else:
            click_point = self.view.sel()[0].begin()
        scope_text = self.view.substr(self.view.extract_scope(click_point))
        return bool(DATE_REGEX.match(scope_text))

    def run(self, edit, event=None):
        if event:
            click_point = self.view.window_to_text((event["x"], event["y"]))
            self.open_entry(self.get_entry_name(click_point))
        else:
            for region in self.view.sel():
                self.open_entry(self.get_entry_name(region.begin()))

    def get_entry_name(self, point):
        scope_region = self.view.extract_scope(point)
        return self.view.substr(scope_region)

    def open_entry(self, date_string):
        filename = date_string + ".note"
        entries = os.listdir(DIARY_PATH)
        if not entries:
            return
        if not filename in entries:
            return
        if filename:
            filename = DIARY_PATH + "/" + filename
            self.view.window().open_file(filename)

    def want_event(self):
        return True
