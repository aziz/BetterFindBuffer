import sublime
import sublime_plugin
import re, os, shutil

# TODO:
# - Add line highlighting
# - Clean up the logic in open_file

class FileOpeningSupport(object):
    def open_file(self, transient = False):
        view   = self.view
        window = self.view.window()

        # If we have multiple groups, then select the next one in layout
        # to open the new file.  We only do transient if we have a
        # split layout.
        start_group = window.active_group()
        dest_group  = (start_group + 1) % window.num_groups()
        should_open = (not transient) or (start_group != dest_group)
        open_flags = sublime.TRANSIENT if transient else 0

        if (view.name() == "Find Results") and should_open:
            line_no = self.get_line_no()
            file_name = self.get_file()
            print ("BetterFind: Opening file: %s - %s" % (file_name, transient))

            new_view = None
            window.focus_group(dest_group)
            if line_no is not None and file_name is not None:
                open_flags = open_flags | sublime.ENCODED_POSITION
                file_loc = "%s:%s" % (file_name, line_no)
                new_view = view.window().open_file(file_loc, open_flags)
            elif file_name is not None:
                print("Opening transient window")
                new_view = view.window().open_file(file_name, open_flags)

            # Transient windows may not respect the focus group, so we move
            # them manually
            if new_view and transient:
                window.set_view_index(new_view, dest_group, 0)

            # If transient, then jump back over to find view
            if transient:
                window.focus_group(start_group)

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

class FindInFilesOpenFileCommand(sublime_plugin.TextCommand, FileOpeningSupport):
    def run(self, edit):
        self.open_file(transient = False)


class FindInFilesJumpFileCommand(sublime_plugin.TextCommand):
    def run(self, edit, forward=True):
        print("BetterFind: jumping")
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

class FindInFilesFindNextCommand(sublime_plugin.TextCommand, FileOpeningSupport):
    def run(self, edit, forward=True):
        print("BetterFind: find next: %s " % forward)
        v = self.view
        window = v.window()

        if forward:
            window.run_command("find_next",)
        else:
            window.run_command("find_prev", {"forward": False})

        # If we want to support transient preview
        self.open_file(transient = True)

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
