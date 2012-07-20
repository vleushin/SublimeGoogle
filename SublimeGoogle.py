import sublime
import sublime_plugin
import webbrowser

def settings_filename():
    return '%s.sublime-settings' % __name__

def settings():
    return sublime.load_settings(settings_filename())

def make_query(view):
    terms = [view.word(selection) if selection.empty() else selection for selection in view.sel()]
    return ' '.join(map(view.substr, terms))

def add_query_to_history(query):
    history = settings().get('history') or []
    if query in history:
        history.pop(history.index(query))
    history.insert(0, query)
    settings().set('history', history)
    sublime.save_settings(settings_filename())

def launch_browser(query):
    query_for_search = query.replace(' ', '%20').replace('"', '%22')
    webbrowser.open_new_tab(settings().get('google_url') % query_for_search)
    add_query_to_history(query);


class GoogleSearchSelectionCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        launch_browser(make_query(self.view))


class GoogleSearchSelectionWithHintsCommand(sublime_plugin.WindowCommand):
    def run(self):
        query = make_query(self.window.active_view())
        self.hints = [query, '"%s"' % query] + ['%s %s' % (hint, query) for hint in settings().get('hints')]
        self.window.show_quick_panel(self.hints, self.on_done)

    def on_done(self, picked):
        if picked >= 0:
            launch_browser(self.hints[picked])


class GoogleSearchFromInputCommand(sublime_plugin.WindowCommand):
    def run(self):
        self.window.show_input_panel('Search Google for:', '', self.on_done, None, None)

    def on_done(self, query):
        launch_browser(query)


class GoogleSearchHistoryCommand(sublime_plugin.WindowCommand):
    def run(self):
        self.window.show_quick_panel(settings().get('history'), self.on_done)

    def on_done(self, picked):
        if picked >= 0:
            launch_browser(settings().get('history')[picked])