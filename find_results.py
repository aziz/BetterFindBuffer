import sublime
import sublime_plugin
import re, os, shutil

class FindInFilesOpenFileCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        view = self.view
        for sel in view.sel():
            line_no = self.get_line_no(sel)
            file_name = self.get_file(sel)
            if line_no and file_name:
                file_loc = "%s:%s" % (file_name, line_no)
                view.window().open_file(file_loc, sublime.ENCODED_POSITION)
            elif file_name:
                view.window().open_file(file_name)

    def get_line_no(self, sel):
        view = self.view
        line_text = view.substr(view.line(sel))
        match = re.match(r"\s*(\d+).+", line_text)
        if match:
            return match.group(1)
        return None

    def get_file(self, sel):
        view = self.view
        line = view.line(sel)
        while line.begin() > 0:
            line_text = view.substr(line)
            match = re.match(r"(.+):$", line_text)
            if match:
                if os.path.exists(match.group(1)):
                    return match.group(1)
            line = view.line(line.begin() - 1)
        return None


class FindInFilesOpenAllFilesCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        view = self.view
        if view.name() == "Find Results":
            for file_name in self.get_files():
                view.window().open_file(file_name, sublime.ENCODED_POSITION)

    def get_files(self):
        view = self.view
        content = view.substr(sublime.Region(0, view.size()))
        return [match.group(1) for match in re.finditer(r"^([^\s].+):$", content, re.MULTILINE)]


class FindInFilesJumpFileCommand(sublime_plugin.TextCommand):
    def run(self, edit, forward=True):
        v = self.view
        files = v.find_by_selector("entity.name.filename.find-in-files")
        caret = v.sel()[0]


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
        if self.view.is_folded(self.view.sel()[0]):
            self.view.unfold(self.view.sel()[0])


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
        popup_max_width = 800
        popup_max_height = 800
        html = sublime.load_resource("Packages/BetterFindBuffer/shortcuts.html")
        self.view.show_popup(html, 0, -1, popup_max_width, popup_max_height)


class BfbFoldAndMoveToNextFileCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        begin = self.get_begin()
        end = self.get_end()
        self.view.fold(sublime.Region(begin.b + 1, end.a - 1))
        sublime.set_timeout_async(self.move_to_next, 0)

    def move_to_next(self):
        self.view.run_command('find_in_files_jump_file')
        self.view.run_command('find_in_files_jump_match')

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


class FindInFilesSetReadOnly(sublime_plugin.EventListener):
    def is_find_results(self, view):
        syntax = view.settings().get('syntax', '')
        if syntax:
            return syntax.endswith("Find Results.hidden-tmLanguage")

    def on_activated_async(self, view):
        if self.is_find_results(view):
            settings = sublime.load_settings('BetterFindBuffer.sublime-settings')
            if settings.get('fold_path_prefix', True):
                view.run_command('bfb_clear_file_path')
            view.set_read_only(settings.get('readonly', True))

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
