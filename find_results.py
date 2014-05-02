import sublime
import sublime_plugin
import re
import os
import shutil


class FindInFilesOpenFileCommand(sublime_plugin.TextCommand):

    def run(self, edit):
        view = self.view
        if view.name() == "Find Results":
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
            file_match = next(
                (f for f in files if caret.begin() < f.begin()), None)
        else:
            files.reverse()
            file_match = next(
                (f for f in files if caret.begin() > f.begin()), None)
        if file_match:
            region = sublime.Region(file_match.begin(), file_match.begin())
            v.sel().clear()
            v.sel().add(region)
            line_index = len(
                v.split_by_newlines(sublime.Region(0, v.sel()[0].begin()))) - 1
            top_offset = line_index * v.line_height()
            v.set_viewport_position((0, top_offset), True)


class FindInFilesSetReadOnly(sublime_plugin.EventListener):

    def is_find_results(self, view):
        syntax = view.settings().get('syntax', '')
        if syntax:
            return syntax.endswith("Find Results.hidden-tmLanguage")

    def on_activated_async(self, view):
        if self.is_find_results(view):
            view.set_read_only(True)

    def on_deactivated_async(self, view):
        if self.is_find_results(view):
            view.set_read_only(False)


def plugin_loaded():
    default_package_path = os.path.join(sublime.packages_path(), "Default")

    if not os.path.exists(default_package_path):
        os.makedirs(default_package_path)

    source_path = os.path.join(
        sublime.packages_path(), "BetterFindBuffer", "Find Results.hidden-tmLanguage")
    destination_path = os.path.join(
        default_package_path, "Find Results.hidden-tmLanguage")

    if os.path.isfile(destination_path):
        os.unlink(destination_path)

    shutil.copy(source_path, default_package_path)


def plugin_unloaded():
    default_package_path = os.path.join(sublime.packages_path(), "Default")
    destination_path = os.path.join(
        default_package_path, "Find Results.hidden-tmLanguage")
    if os.path.exists(default_package_path) and os.path.isfile(destination_path):
        os.remove(destination_path)
