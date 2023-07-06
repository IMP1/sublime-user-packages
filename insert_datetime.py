import sublime
import sublime_plugin
import datetime

class InsertTime(sublime_plugin.TextCommand):

    TIME_FORMAT = "%H:%M"

    def run(self, edit):
        current_time = datetime.datetime.now().strftime(TIME_FORMAT)
        for region in self.view.sel():
            if region.empty():
                self.view.insert(edit, region.a, current_time)
            else:
                self.view.replace(edit, region, current_time)


class InsertDate(sublime_plugin.TextCommand):
    
    DATE_FORMAT = "%Y-%m-%d"

    def run(self, edit):
        current_time = datetime.datetime.now().strftime(DATE_FORMAT)
        for region in self.view.sel():
            if region.empty():
                self.view.insert(edit, region.a, current_time)
            else:
                self.view.replace(edit, region, current_time)

