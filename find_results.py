import sublime
import sublime_plugin
import re, os, shutil


class FileOpeningSupport(object):
    """ Base class for plugins that need file opening support. """
    def open_file(self, transient = False):
        view   = self.view
        window = self.view.window()

        # If we have multiple groups, then select the next one in layout
        # to open the new file.  We only do transient if we have a
        # split layout.
        # todo: move this to a config option
        use_transient_preview = True
        if transient and not use_transient_preview:
            return

        start_group = window.active_group()
        dest_group  = (start_group + 1) % window.num_groups()
        should_open = (not transient) or (start_group != dest_group)

        if (view.name() == "Find Results") and should_open:
            line_no   = self.get_line_no()
            file_name = self.get_file()
            find_term = self.get_find_term()
            open_flags  = sublime.TRANSIENT if transient else 0

            print ("BetterFind: file: [%s] trans: [%s] term: [%s]" % (file_name,
                                                                      transient,
                                                                      find_term))
            new_view = None
            window.focus_group(dest_group)
            if line_no is not None and file_name is not None:
                open_flags = open_flags | sublime.ENCODED_POSITION
                file_loc = "%s:%s" % (file_name, line_no)
                new_view = view.window().open_file(file_loc, open_flags)
            elif file_name is not None:
                new_view = view.window().open_file(file_name, open_flags)
            window.focus_group(start_group)

            # Transient views don't respect the focus group, move explicitly
            # XXX: Not sure if we can do this before view is loaded.
            if new_view and transient:
                window.set_view_index(new_view, dest_group, 0)

            def finish_open():
                # delay until view is done loading
                if new_view.is_loading():
                    sublime.set_timeout(finish_open, 50)

                # Find and highlight the current result in transient window
                new_view.erase_regions("bfb_key")
                if transient:
                    row_num = 0 if (line_no is None) else int(line_no) - 1
                    line_start_pos = new_view.text_point(row_num, 0)

                    ##print("line: %s pos: %s" % (line_no, line_start_pos))
                    ##print("  : %s" % new_view.substr(line_start_pos))
                    ##print("  : %s" % new_view.substr(new_view.line(line_start_pos)))

                    # XXX: Don't have active find settings, so use most generic options
                    region = new_view.find(find_term, line_start_pos, flags = sublime.IGNORECASE)
                    if region is not None:
                        new_view.add_regions("bfb_key", [region],
                           scope="string", flags = sublime.DRAW_NO_OUTLINE)

                    # Transient views don't respect the focus group, move explicitly
                    window.set_view_index(new_view, dest_group, 0)

                    # Adding regions can change group focus, so set back
                    window.focus_group(start_group)

            if new_view:
                finish_open()

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

    def get_find_term(self):
        # Scan back in view for current search term for selected result
        view = self.view
        if len(view.sel()) == 1:
            line = view.line(view.sel()[0])
            while line.begin() > 0:
                line_text = view.substr(line)
                match = re.match(r"^Searching.*?\"(.*)\".*?$", line_text)
                if match:
                    term = match.group(1)
                    return term
                line = view.line(line.begin() - 1)
        return None

class FindInFilesOpenFileCommand(sublime_plugin.TextCommand, FileOpeningSupport):
    def run(self, edit):
        self.open_file(transient = False)


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

class FindInFilesFindNextCommand(sublime_plugin.TextCommand, FileOpeningSupport):
    def run(self, edit, forward=True):
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
