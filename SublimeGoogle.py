import sublime
import sublime_plugin
import webbrowser

def settings_get(name):
    return sublime.load_settings('%s.sublime-settings' % __name__).get(name)

def settings_set(name, value):
    return sublime.load_settings('%s.sublime-settings' % __name__).set(name, value)

def get_history():
    return settings_get('history')[:settings_get('history_size')] or []

def add_query_to_history(query):
    history = get_history()
    if query in history:
        history.pop(history.index(query))
    history.insert(0, query)
    settings_set('history', history)
    sublime.save_settings('%s.sublime-settings' % __name__)

def make_query(view):
    terms = [view.word(selection) if selection.empty() else selection for selection in view.sel()]
    return ' '.join(map(view.substr, terms))

def launch_browser(query):
    query_for_browser = query.replace(' ', '%20').replace('"', '%22')
    webbrowser.open_new_tab(settings_get('google_url') % query_for_browser)
    add_query_to_history(query);

class GoogleSearchSelectionCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        launch_browser(make_query(self.view))

class GoogleSearchSelectionWithHintsCommand(sublime_plugin.WindowCommand):
    def run(self):
        query = make_query(self.window.active_view())
        self.hints = [hint % query for hint in settings_get('hints')]
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
        self.window.show_quick_panel(get_history(), self.on_done)

    def on_done(self, picked):
        if picked >= 0:
            launch_browser(get_history()[picked])