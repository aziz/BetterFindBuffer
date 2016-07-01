import sublime
import sublime_plugin
import re, os, shutil

class FindInFilesOpenFileCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        view = self.view
        line_no = self.get_line_no()
        file_name = self.get_file()
        if line_no is not None and file_name is not None:
            file_loc = "%s:%s" % (file_name, line_no)
            view.window().open_file(file_loc, sublime.ENCODED_POSITION)
        elif file_name is not None:
            view.window().open_file(file_name)

    def get_line_no(self):
        view = self.view
        if len(view.sel()) == 1:
            line_text = view.substr(view.line(view.sel()[0]))
            match = re.match(r"\s*(\d+).+", line_text)
            if match:
                return match.group(1)
        return None

    def get_file(self):
        view = self.view
        if len(view.sel()) == 1:
            line = view.line(view.sel()[0])
            while line.begin() > 0:
                line_text = view.substr(line)
                match = re.match(r"(.+):$", line_text)
                if match:
                    if os.path.exists(match.group(1)):
                        return match.group(1)
                line = view.line(line.begin() - 1)
        return None


class FindInFilesJumpFileCommand(sublime_plugin.TextCommand):
    def run(self, edit, forward=True):
        v = self.view
        files = v.find_by_selector("entity.name.filename.find-in-files")
        caret = v.sel()[0]
        if forward:
            file_match = next((f for f in files if caret.begin() < f.begin()), None)
        else:
            files.reverse()
            file_match = next((f for f in files if caret.begin() > f.begin()), None)
        if file_match:
            region = sublime.Region(file_match.begin(), file_match.begin())
            v.sel().clear()
            v.sel().add(region)
            top_offset = v.text_to_layout(region.begin())[1] - v.line_height()
            v.set_viewport_position((0, top_offset), True)


class FindInFilesSetReadOnly(sublime_plugin.EventListener):
    def is_find_results(self, view):
        syntax = view.settings().get('syntax', '')
        if syntax:
            return syntax.endswith("Find Results.hidden-tmLanguage")

    def on_activated_async(self, view):
        if self.is_find_results(view):
            view.run_command('bfb_clear_file_path')
            view.set_read_only(True)

    def on_deactivated_async(self, view):
        if self.is_find_results(view):
            view.set_read_only(False)


# Some plugins like **Color Highlighter** are forcing their color-scheme to the activated view
# Although, it's something that should be fixed on their side, in the meantime, it's safe to force
# the color shceme on `on_activated_async` event.
class BFBForceColorSchemeCommand(sublime_plugin.EventListener):
    def on_activated_async(self, view):
        syntax = view.settings().get('syntax')
        if syntax and (syntax.endswith("Find Results.hidden-tmLanguage")):
            settings = sublime.load_settings('Find Results.sublime-settings')
            color_scheme = settings.get('color_scheme')
            if color_scheme:
                view.settings().set('color_scheme', color_scheme)


class BfbClearFilePathCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        folders = sublime.active_window().folders()
        for folder in folders:
            path, folder_name = os.path.split(folder)
            regions = self.view.find_all(path)
            for r in reversed(regions):
                self.view.fold(sublime.Region(r.a, r.b+1))


class BfbTogglePopupHelpCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        popup_max_width = 600
        popup_max_height = 600
        html = sublime.load_resource("Packages/BetterFindBuffer/shortcuts.html")
        self.view.show_popup(html, 0, -1, popup_max_width, popup_max_height)


class BfbFoldAndMoveToNextFileCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        begin = self.get_begin()
        end = self.get_end()
        self.view.fold(sublime.Region(begin.b + 1, end.a - 1))
        # sublime.set_timeout_async(self.move_to_next, 100)

    def move_to_next(self):
        self.view.run_command('find_next')

    def get_begin(self):
        view = self.view
        if len(view.sel()) == 1:
            line = view.line(view.sel()[0])
            while line.begin() > 0:
                line_text = view.substr(line)
                match = re.match(r"\S(.+):$", line_text)
                if match:
                    return(line)
                line = view.line(line.begin() - 1)
        return None

    def get_end(self):
        view = self.view
        if len(view.sel()) == 1:
            line = view.line(view.sel()[0])
            while line.end() <= view.size():
                line_text = view.substr(line)
                if len(line_text) == 0:
                    return(line)
                line = view.line(line.end() + 1)
        return None



def plugin_loaded():
    default_package_path = os.path.join(sublime.packages_path(), "Default")

    if not os.path.exists(default_package_path):
        os.makedirs(default_package_path)

    source_path = os.path.join(sublime.packages_path(), "BetterFindBuffer", "Find Results.hidden-tmLanguage")
    destination_path = os.path.join(default_package_path, "Find Results.hidden-tmLanguage")

    if os.path.isfile(destination_path):
        os.unlink(destination_path)

    shutil.copy(source_path, default_package_path)


def plugin_unloaded():
    default_package_path = os.path.join(sublime.packages_path(), "Default")
    destination_path = os.path.join(default_package_path, "Find Results.hidden-tmLanguage")
    if os.path.exists(default_package_path) and os.path.isfile(destination_path):
        os.remove(destination_path)
