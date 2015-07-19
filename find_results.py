import sublime
import sublime_plugin
import re, os, shutil

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


class FindInFilesJumpCommand(sublime_plugin.TextCommand):
    def run(self, edit, forward=True, cycle=True):
        caret = self.view.sel()[0]
        matches = self.filter_matches(caret, self.find_matches())
        if forward:
            match = self.find_next_match(caret, matches, cycle)
        else:
            match = self.find_prev_match(caret, matches, cycle)
        if match:
            self.goto_match(match)

    def find_next_match(self, caret, matches, cycle):
        default = matches[0] if cycle and len(matches) else None
        return next((m for m in matches if caret.begin() < m.begin()), default)

    def filter_matches(self, caret, matches):
        footers = self.view.find_by_selector('footer.find-in-files')
        lower_bound = next((f.end() for f in reversed(footers) if f.end() < caret.begin()), 0)
        upper_bound = next((f.end() for f in footers if f.end() > caret.begin()), self.view.size())
        return [m for m in matches if m.begin() > lower_bound and m.begin() < upper_bound]

    def find_prev_match(self, caret, matches, cycle):
        default = matches[-1] if cycle and len(matches) else None
        return next((m for m in reversed(matches) if caret.begin() > m.begin()), default)

    def goto_match(self, match):
        self.view.sel().clear()
        self.view.sel().add(match)


class FindInFilesJumpFileCommand(FindInFilesJumpCommand):
    def find_matches(self):
        return self.view.find_by_selector('entity.name.filename.find-in-files')

    def goto_match(self, match):
        v = self.view
        region = sublime.Region(match.begin(), match.begin())
        super(FindInFilesJumpFileCommand, self).goto_match(region)
        top_offset = v.text_to_layout(region.begin())[1] - v.line_height()
        v.set_viewport_position((0, top_offset), True)


class FindInFilesJumpMatchCommand(FindInFilesJumpCommand):
    def find_matches(self):
        return self.view.get_regions('match')

    def goto_match(self, match):
        v = self.view
        super(FindInFilesJumpMatchCommand, self).goto_match(match)
        vx, vy = v.viewport_position()
        vw, vh = v.viewport_extent()
        x, y = v.text_to_layout(match.begin())
        h = v.line_height()
        if y < vy or y + h > vy + vh:
            v.show_at_center(match)


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
