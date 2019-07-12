import sublime
import sublime_plugin

class EvaluateExpressionCommand(sublime_plugin.TextCommand):

    def run(self, edit):
        selection = self.view.sel()
        for region in selection:
            region_text = self.view.substr(region)
            code = compile(region_text, "SublimeUserCode", "eval")
            try:
                result = str(eval(code))
            except Exception as e:
                print(e)
                result = region_text
            self.view.replace(edit, region, result)


class ExecuteStatement(sublime_plugin.TextCommand):

    def run(self, edit):
        selection = self.view.sel()
        for region in selection:
            region_text = self.view.substr(region)
            code = compile(region_text, "SublimeUserCode", "exec")
            try:
                exec(code)
            except Exception as e:
                print(e)
