import sublime
from ..protocol import ConfigurationItem, DocumentUri, ExecuteCommandParams, LSPAny
from .core.collections import DottedDict as DottedDict
from .core.constants import MarkdownLangMap as MarkdownLangMap, ST_STORAGE_PATH as ST_STORAGE_PATH
from .core.logging import exception_log as exception_log
from .core.promise import Promise as Promise
from .core.protocol import ClientNotification as ClientNotification, ClientRequest as ClientRequest, ClientResponse as ClientResponse, Notification as Notification, Request as Request, Response as Response, ServerNotification as ServerNotification, ServerResponse as ServerResponse
from .core.sessions import Session as Session, SessionBufferProtocol as SessionBufferProtocol, SessionViewProtocol as SessionViewProtocol
from .core.settings import client_configs as client_configs
from .core.types import ClientConfig as ClientConfig, method2attr as method2attr
from .core.url import parse_uri as parse_uri
from .core.views import uri_from_view as uri_from_view
from .core.workspace import WorkspaceFolder as WorkspaceFolder
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Final, TypeVar
from weakref import ref

HANDLER_MARKER: str
COMMAND_HANDLER_MARKER: str
URI_HANDLER_MARKER: str
P = TypeVar('P', bound=LSPAny)
R = TypeVar('R', bound=LSPAny)
CommandHandler = Callable[[list[P] | None], Promise[R]]
CommandHandlerForDecorator = Callable[[Any, list[P] | None], Promise[R]]
UriHandler = Callable[[DocumentUri, sublime.NewFileFlags], Promise[sublime.Sheet | None]]
UriHandlerForDecorator = Callable[[Any, DocumentUri, sublime.NewFileFlags], Promise[sublime.Sheet | None]]
PostResponseCallback = Callable[[], None]
RequestHandlerResponse = Promise[R] | tuple[Promise[R], PostResponseCallback]
g_plugins: dict[str, type[AbstractPlugin | LspPlugin]]

class PluginStartError(Exception):
    """
    Abort startup with a user-visible message.

    Raise it from `on_pre_start_async` to prevent plugin from starting.
    First argument is the text that will be shown in the status field.
    """
    def __init__(self, message: str) -> None: ...

def register_plugin(plugin: type[AbstractPlugin], notify_listener: bool = True) -> None:
    """
    Register an LSP plugin in LSP.

    You should put a call to this function in your `plugin_loaded` callback. This way, when your package is disabled
    by a user and then re-enabled again by a user, the changes in state are picked up by LSP, and your language server
    will start for the relevant views.

    While your helper package may still work without calling `register_plugin` in `plugin_loaded`, the user will have a
    better experience when you do call this function.

    Your implementation should look something like this:

    ```python
    from LSP.plugin import register_plugin
    from LSP.plugin import unregister_plugin
    from LSP.plugin import AbstractPlugin


    class MyPlugin(AbstractPlugin):
        ...


    def plugin_loaded():
        register_plugin(MyPlugin)

    def plugin_unloaded():
        unregister_plugin(MyPlugin)
    ```

    If you need to install supplementary files (e.g. javascript source code that implements the actual server), do so
    in `AbstractPlugin.install_or_update` in a blocking manner, without the use of Python's `threading` module.
    """
def register_plugin_impl(plugin: type[AbstractPlugin | LspPlugin], notify_listener: bool = True) -> None: ...
def unregister_plugin(plugin: type[AbstractPlugin]) -> None:
    """
    Unregister an LSP plugin in LSP.

    You should put a call to this function in your `plugin_unloaded` callback. this way, when your package is disabled
    by a user, your language server is shut down for the views that it is attached to. This results in a good user
    experience.
    """
def unregister_plugin_impl(plugin: type[AbstractPlugin | LspPlugin]) -> None: ...
def get_plugin(name: str) -> type[AbstractPlugin | LspPlugin] | None: ...

class APIHandler:
    """Trigger initialization of decorated API methods."""
    handler_attr_map: dict[str, str]
    def __init__(self) -> None: ...
    def get_command_handler(self, command_name: str) -> CommandHandler[P, R] | None: ...
    def get_uri_handler(self, scheme: str) -> UriHandler | None: ...

def notification_handler(method: str) -> Callable[[Callable[[Any, P], None]], Callable[[Any, P], None]]:
    """
    Decorator to mark a method as a handler for a specific LSP notification.

    Usage:
        ```py
        @notification_handler('eslint/status')
        def on_eslint_status(self, params: str) -> None:
            ...
        ```

    The decorated method will be called with the notification parameters whenever the specified
    notification is received from the language server. Notification handlers do not return a value.

    :param      method:             The LSP notification method name (e.g., 'eslint/status').
    :returns:   A decorator that registers the function as a notification handler.
    """
def request_handler(method: str) -> Callable[[Callable[[Any, P], RequestHandlerResponse]], Callable[[Any, P, int], Promise[Response[R]]]]:
    """
    Decorator to mark a method as a handler for a specific LSP request.

    Usage:
        ```py
        @request_handler('eslint/openDoc')
        def on_open_doc(self, params: TextDocumentIdentifier) -> Promise[bool]:
            ...
        ```

    The decorated method will be called with the request parameters whenever the specified
    request is received from the language server. The method must return a Promise that resolves
    to the response value. The framework will automatically send it back to the server.

    :param      method:             The LSP request method name (e.g., 'eslint/openDoc').
    :returns:   A decorator that registers the function as a request handler.
    """
def command_handler(command_name: str) -> Callable[[CommandHandlerForDecorator], CommandHandlerForDecorator]:
    """
    Decorator to mark a method as a handler for a specific server command.

    Intercepts a `workspace/executeCommand` request with the given command name when triggered by the client.
    The decorated method is called with the command's `arguments` list (or `None` if absent).

    Usage:
        ```py
        @command_handler('typescript.rename')
        def on_custom_rename(self, arguments: list[LSPAny] | None) -> Promise[LspAny]:
            ...
        ```

    Note:
        Instead of `LSPAny`'s you can use more appropriate type for the specific command that is being handled.

    :param      command_name:   The command name as advertised by the server (e.g., 'rust-analyzer.showReferences').
    :returns:   A decorator that registers the function as a command handler.
    """
def uri_handler(scheme: str) -> Callable[[UriHandlerForDecorator], UriHandlerForDecorator]:
    """
    Decorator to mark a method as a handler for URIs with a specific scheme.

    The decorated method receives the full URI and a `sublime.NewFileFlags` bitflag and must return a `Promise`
    resolved with the opened `sublime.Sheet`, or `None` if the URI could not be opened.
    Decorated method is called on the async thread.

    Usage:
        ```py
        @uri_handler('foo')
        def on_open_foo_uri(self, uri: DocumentUri, flags: sublime.NewFileFlags) -> Promise[sublime.Sheet | None]:
            ...
        ```

    :param      scheme:     The URI scheme to handle (e.g. `'foo'` for URIs like `foo://...`).
    :returns:   A decorator that registers the function as a URI handler for the given scheme.
    """

@dataclass
class IsApplicableContext:
    """Context passed to `LspPlugin.is_applicable_async`."""
    configuration: ClientConfig
    view: sublime.View
    workspace_folders: list[WorkspaceFolder]

@dataclass
class OnPreStartContext:
    """Context passed to `LspPlugin.on_pre_start_async`."""
    configuration: ClientConfig
    variables: dict[str, str]
    view: sublime.View
    working_directory: str | None
    workspace_folders: list[WorkspaceFolder]

class LspPlugin(APIHandler):
    """
    Base class for LSP helper packages.

    Subclass this to integrate a language server with LSP. The session name is automatically
    derived from the top-level package name (i.e. `__module__.split('.')[0]`), so no manual
    configuration is needed.

    A minimal integration looks like this:

    ```py
    from LSP.plugin import LspPlugin


    class LspFooPlugin(LspPlugin):
        pass


    def plugin_loaded() -> None:
        LspFooPlugin.register()


    def plugin_unloaded() -> None:
        LspFooPlugin.unregister()
    ```

    LSP will look for a settings file at `Packages/<package_name>/<package_name>.sublime-settings`
    to read the `command`, `selector`, `schemes`, and other server configuration. Override
    the classmethods below to customise behaviour beyond what the settings file provides.

    Raise `PluginStartError` exception from `on_pre_start_async` to prevent plugin from starting while
    showing relevant message in the status field.

    Use `@notification_handler` and `@request_handler` decorators to handle non-standard
    server-to-client notifications and requests respectively.

    Use `@command_handler` to handle server-specific commands.
    """
    name: Final[str]
    plugin_storage_path: Final[Path]
    @classmethod
    def register(cls) -> None:
        """
        Register this plugin with LSP.

        Call this from your `plugin_loaded` callback so that LSP picks up configuration changes when your package
        is disabled and re-enabled:

        ```py
        def plugin_loaded() -> None:
            LspFooPlugin.register()
        ```
        """
    @classmethod
    def unregister(cls) -> None:
        """
        Unregister this plugin from LSP.

        Call this from your `plugin_unloaded` callback so that the language server is shut down when your package
        is disabled:

        ```py
        def plugin_unloaded() -> None:
            LspFooPlugin.unregister()
        ```
        """
    @classmethod
    def is_applicable_async(cls, context: IsApplicableContext) -> bool:
        """
        Determine whether the server should run on the view given by `context.view`.

        The default implementation checks whether the URI scheme and the syntax scope match against the schemes and
        selector from the settings file. You can override this method for example to dynamically evaluate the applicable
        selector, or to ignore certain views even when those would match the static config. Please note that no document
        syncronization messages (textDocument/didOpen, textDocument/didChange, textDocument/didClose, etc.) are sent to
        the server for ignored views.

        This method is called when the view gets opened. To manually trigger this method again, run the
        `lsp_check_applicable` TextCommand for the given view and with a `session_name` keyword argument.

        :param      context:           The plugin context.
        """
    @classmethod
    def on_pre_start_async(cls, context: OnPreStartContext) -> None:
        """
        Called just before the language server process is started.

        Override to perform any preparation needed before startup - for example installing or updating server binaries,
        resolving the working directory, or injecting extra template variables into `context.variables`.

        This method runs on a worker thread so perform any blocking I/O (e.g. downloading a binary, running
        `npm install`) directly here without spawning additional threads.

        Mutations to `context.working_directory` and `context.variables` are picked up and used when launching the
        server process.

        Raise `PluginStartError` with a message to abort startup and display a user-visible status message.

        :param      context:    The startup context. `context.configuration`, `context.variables` and
                                `context.working_directory` can be mutated to influence how the server is launched.
        """
    weaksession: ref[Session]
    def __init__(self, weaksession: ref[Session]) -> None:
        """
        Constructs a new instance.

        Called inside `initialize_async` - after the transport is established but before the LSP `initialize`
        request is sent to the server.

        :param weaksession: A weak reference to the `Session`. Resolve it with `self.weaksession()` when needed,
                            but do not store the resulting strong reference as an attribute - doing so creates a
                            reference cycle that prevents garbage collection.
        """
    def __init_subclass__(cls, **kwargs: Any) -> None: ...
    def on_initialized_async(self) -> None:
        """
        Called after the `initialized` notification has been sent to the language server.

        Override to perform any post-initialization work, such as sending custom notifications or requests
        that depend on the server's capabilities reported in the `initialize` response.
        """
    def on_pre_send_request_async(self, request: ClientRequest, view: sublime.View | None) -> None:
        """
        Notifies about a request that is about to be sent to the language server.

        :param    request:     The request object. The request['params'] can be modified by the plugin.
        :param    view:        The corresponding View if applicable.
        """
    def on_pre_send_response_async(self, response: ClientResponse) -> None:
        """
        Notifies about a response that is about to be sent to the language server.

        Called after the LSP client has resolved the response but before it is transmitted
        to the language server. The response['result'] can be modified by the plugin.

        :param    response:    The response object containing 'method', 'params', and 'result'.
        """
    def on_pre_send_notification_async(self, notification: ClientNotification) -> None:
        """
        Notifies about a notification that is about to be sent to the language server.

        :param    notification:  The notification object. The notification['params'] can be modified by the plugin.
        """
    def on_server_response_async(self, response: ServerResponse) -> None:
        """
        Notifies about a response message that has been received from the language server.

        Only successful responses are passed to this method.

        :param    response:  The response object to the request. The response['result'] field can be modified by the
                             plugin, before it gets further handled by the LSP package.
        """
    def on_server_notification_async(self, notification: ServerNotification) -> None:
        """
        Notifies about a notification message that has been received from the language server.

        :param    notification:  The notification object.
        """
    def on_text_changed_async(self, session_buffer: SessionBufferProtocol) -> None:
        """Called when the content of the session buffer has changed or a new buffer was opened (debounced)."""
    def on_selection_modified_async(self, session_view: SessionViewProtocol) -> None:
        """Called after the selection has been modified in a view (debounced)."""
    def on_session_end_async(self, exit_code: int | None, exception: Exception | None) -> None:
        """
        Notifies about the session ending (also if the session has crashed). Provides an opportunity to clean up
        any stored state or delete references to the session or plugin instance that would otherwise prevent the
        instance from being garbage-collected.

        If the session hasn't crashed, a shutdown message will be send immediately
        after this method returns. In this case exit_code and exception are None.
        If the session has crashed, the exit_code and an optional exception are provided.

        This API is triggered on async thread.
        """

class AbstractPlugin(APIHandler, ABC):
    @classmethod
    @abstractmethod
    def name(cls) -> str:
        '''
        A human-friendly name. If your plugin is called "LSP-foobar", then this should return "foobar". If you also
        have your settings file called "LSP-foobar.sublime-settings", then you don\'t even need to re-implement the
        configuration method (see below).
        '''
    @classmethod
    def configuration(cls) -> tuple[sublime.Settings, str]:
        '''
        Return the Settings object that defines the "command", "selector", and optionally the "initialization_options",
        "env" and "tcp_port" as the first element in the tuple, and the path to the base settings
        filename as the second element in the tuple.

        The second element in the tuple is used to handle "settings" overrides from users properly. For example, if your
        plugin is called LSP-foobar, you would return "Packages/LSP-foobar/LSP-foobar.sublime-settings".

        The "command", "initialization_options" and "env" are subject to template string substitution. The following
        template strings are recognized:

        $file
        $file_base_name
        $file_extension
        $file_name
        $file_path
        $platform
        $project
        $project_base_name
        $project_extension
        $project_name
        $project_path

        These are just the values from window.extract_variables(). Additionally,

        $storage_path The path to the package storage (see AbstractPlugin.storage_path)
        $cache_path   sublime.cache_path()
        $temp_dir     tempfile.gettempdir()
        $home         os.path.expanduser(\'~\')
        $port         A random free TCP-port on localhost in case "tcp_port" is set to 0. This string template can only
                      be used in the "command"

        The "command" and "env" are expanded upon starting the subprocess of the Session. The "initialization_options"
        are expanded upon doing the initialize request. "initialization_options" does not expand $port.

        When you\'re managing your own server binary, you would typically place it in sublime.cache_path(). So your
        "command" should look like this: "command": ["$cache_path/LSP-foobar/server_binary", "--stdio"]
        '''
    @classmethod
    def is_applicable(cls, view: sublime.View, config: ClientConfig) -> bool:
        """
        Determine whether the server should run on the given view.

        The default implementation checks whether the URI scheme and the syntax scope match against the schemes and
        selector from the settings file. You can override this method for example to dynamically evaluate the applicable
        selector, or to ignore certain views even when those would match the static config. Please note that no document
        syncronization messages (textDocument/didOpen, textDocument/didChange, textDocument/didClose, etc.) are sent to
        the server for ignored views.

        This method is called when the view gets opened. To manually trigger this method again, run the
        `lsp_check_applicable` TextCommand for the given view and with a `session_name` keyword argument.

        :param      view:             The view
        :param      config:           The config
        """
    @classmethod
    def additional_variables(cls) -> dict[str, str] | None:
        """In addition to the above variables, add more variables here to be expanded."""
    @classmethod
    def storage_path(cls) -> str:
        '''
        The storage path. Use this as your base directory to install server files. Its path is \'$DATA/Package Storage\'.

        You should have an additional subdirectory preferably the same name as your plugin. For instance:

        ```python
        from LSP.plugin import AbstractPlugin
        import os


        class MyPlugin(AbstractPlugin):

            @classmethod
            def name(cls) -> str:
                return "my-plugin"

            @classmethod
            def basedir(cls) -> str:
                # Do everything relative to this directory
                return os.path.join(cls.storage_path(), cls.name())
        ```
        '''
    @classmethod
    def needs_update_or_installation(cls) -> bool:
        """
        If this plugin manages its own server binary, then this is the place to check whether the binary needs
        an update, or whether it needs to be installed before starting the language server.
        """
    @classmethod
    def install_or_update(cls) -> None:
        """
        Do the actual update/installation of the server binary. This runs in a separate thread, so don't spawn threads
        yourself here.
        """
    @classmethod
    def can_start(cls, window: sublime.Window, initiating_view: sublime.View, workspace_folders: list[WorkspaceFolder], configuration: ClientConfig) -> str | None:
        """
        Determines ability to start. This is called after needs_update_or_installation and after install_or_update.
        So you may assume that if you're managing your server binary, then it is already installed when this
        classmethod is called.

        :param      window:             The window
        :param      initiating_view:    The initiating view
        :param      workspace_folders:  The workspace folders
        :param      configuration:      The configuration

        :returns:   A string describing the reason why we should not start a language server session, or None if we
                    should go ahead and start a session.
        """
    @classmethod
    def on_pre_start(cls, window: sublime.Window, initiating_view: sublime.View, workspace_folders: list[WorkspaceFolder], configuration: ClientConfig) -> str | None:
        '''
        Callback invoked just before the language server subprocess is started. This is the place to do last-minute
        adjustments to your "command" or "initialization_options" in the passed-in "configuration" argument, or change
        the order of the workspace folders. You can also choose to return a custom working directory, but consider that
        a language server should not care about the working directory.

        :param      window:             The window
        :param      initiating_view:    The initiating view
        :param      workspace_folders:  The workspace folders, you can modify these
        :param      configuration:      The configuration, you can modify this one

        :returns:   A desired working directory, or None if you don\'t care
        '''
    @classmethod
    def on_post_start(cls, window: sublime.Window, initiating_view: sublime.View, workspace_folders: list[WorkspaceFolder], configuration: ClientConfig) -> None:
        """
        Callback invoked when the subprocess was just started.

        :param      window:             The window
        :param      initiating_view:    The initiating view
        :param      workspace_folders:  The workspace folders
        :param      configuration:      The configuration
        """
    @classmethod
    def markdown_language_id_to_st_syntax_map(cls) -> MarkdownLangMap | None:
        """
        Override this method to tweak the syntax highlighting of code blocks in popups from your language server.
        The returned object should be a dictionary exactly in the form of mdpopup's language_map setting.

        See: https://facelessuser.github.io/sublime-markdown-popups/settings/#mdpopupssublime_user_lang_map

        :returns:   The markdown language map, or None
        """
    weaksession: ref[Session]
    def __init__(self, weaksession: ref[Session]) -> None:
        """
        Constructs a new instance. Your instance is constructed after a response to the initialize request.

        :param      weaksession:  A weak reference to the Session. You can grab a strong reference through
                                  self.weaksession(), but don't hold on to that reference.
        """
    def on_settings_changed(self, settings: DottedDict) -> None:
        """
        Override this method to alter the settings that are returned to the server for the
        workspace/didChangeConfiguration notification and the workspace/configuration requests.

        :param      settings:      The settings that the server should receive.
        """
    def on_workspace_configuration(self, params: ConfigurationItem, configuration: Any) -> Any:
        """
        Override to augment configuration returned for the workspace/configuration request.

        :param      params:         A ConfigurationItem for which configuration is requested.
        :param      configuration:  The pre-resolved configuration for given params using the settings object or None.

        :returns: The resolved configuration for given params.
        """
    def on_pre_server_command(self, command: ExecuteCommandParams, done_callback: Callable[[], None]) -> bool:
        '''
        Intercept a command that is about to be sent to the language server.

        :param    command:        The payload containing a "command" and optionally "arguments".
        :param    done_callback:  The callback that you promise to invoke when you return true.

        :returns: True if *YOU* will handle this command plugin-side, false otherwise. You must invoke the
                  passed `done_callback` when you\'re done.
        '''
    def on_pre_send_request_async(self, request_id: int, request: Request[Any, Any]) -> None:
        """
        Notifies about a request that is about to be sent to the language server.
        This API is triggered on async thread.

        :param    request_id:  The request ID.
        :param    request:     The request object. The request params can be modified by the plugin.
        """
    def on_pre_send_notification_async(self, notification: Notification[Any]) -> None:
        """
        Notifies about a notification that is about to be sent to the language server.
        This API is triggered on async thread.

        :param    notification:  The notification object. The notification params can be modified by the plugin.
        """
    def on_server_response_async(self, method: str, response: Response[Any]) -> None:
        """
        Notifies about a response message that has been received from the language server.
        Only successful responses are passed to this method.

        :param    method:    The method of the request.
        :param    response:  The response object to the request. The response.result field can be modified by the
                             plugin, before it gets further handled by the LSP package.
        """
    def on_server_notification_async(self, notification: Notification[Any]) -> None:
        """
        Notifies about a notification message that has been received from the language server.

        :param    notification:  The notification object.
        """
    def on_open_uri_async(self, uri: DocumentUri, callback: Callable[[str | None, str, str], None]) -> bool:
        """
        Called when a language server reports to open an URI. If you know how to handle this URI, then return True and
        invoke the passed-in callback some time.

        The arguments of the provided callback work as follows:

        - The first argument is the title of the view that will be populated with the content of a new scratch view.
          If `None` is passed, no new view will be opened and the other arguments are ignored.
        - The second argument is the content of the view.
        - The third argument is the syntax to apply for the new view.
        """
    def on_session_buffer_changed_async(self, session_buffer: SessionBufferProtocol) -> None:
        """Called when the content of the session buffer has changed or a new buffer was opened."""
    def on_selection_modified_async(self, session_view: SessionViewProtocol) -> None:
        """Called after the selection has been modified in a view (debounced)."""
    def on_session_end_async(self, exit_code: int | None, exception: Exception | None) -> None:
        """
        Notifies about the session ending (also if the session has crashed). Provides an opportunity to clean up
        any stored state or delete references to the session or plugin instance that would otherwise prevent the
        instance from being garbage-collected.

        If the session hasn't crashed, a shutdown message will be send immediately
        after this method returns. In this case exit_code and exception are None.
        If the session has crashed, the exit_code and an optional exception are provided.

        This API is triggered on async thread.
        """
