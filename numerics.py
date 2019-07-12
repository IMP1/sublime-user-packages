import sublime
import sublime_plugin

class IncrementCommand(sublime_plugin.TextCommand):

    def run(self, edit, delta):
        selection = self.view.sel()
        for region in selection:
            region_text = self.view.substr(region)
            try:
                result = str(int(region_text) + delta)
            except Exception as e:
                print(e)
                result = region_text
            self.view.replace(edit, region, result)


class InsertRegionNumberCommand(sublime_plugin.TextCommand):

    def run(self, edit):
        selection = self.view.sel()
        for i, region in enumerate(selection):
            region_number = str(i + 1)
            if region.empty():
                self.view.insert(edit, region.a, region_number)
            else:
                self.view.replace(edit, region, region_number)
