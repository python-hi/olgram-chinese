from dataclasses import dataclass
from typing import Any, Dict, List, Tuple

from aiogram.dispatcher import Dispatcher


@dataclass()
class Handler:
    callback: Any
    custom_filters: Tuple[Any]
    kwargs: Dict[Any, Any]
    commands: Any = None
    regexp: Any = None
    content_types: Any = None
    state: Any = None
    run_task: Any = None


class Router:
    def __init__(self):
        self._message_handlers: List[Handler] = []
        self._inline_handlers: List[Handler] = []
        self._callback_handlers: List[Handler] = []

    def message_handler(
        self, *custom_filters, commands=None, regexp=None, content_types=None, state=None, run_task=None, **kwargs
    ):
        def decorator(callback):
            self._message_handlers.append(
                Handler(callback, custom_filters, kwargs, commands, regexp, content_types, state, run_task)
            )
            return callback

        return decorator

    def inline_handler(self, *custom_filters, state=None, run_task=None, **kwargs):
        def decorator(callback):
            self._inline_handlers.append(Handler(callback, custom_filters, kwargs, state=state, run_task=run_task))
            return callback

        return decorator

    def callback_query_handler(self, *custom_filters, state=None, run_task=None, **kwargs):
        def decorator(callback):
            self._callback_handlers.append(Handler(callback, custom_filters, kwargs, state=state, run_task=run_task))
            return callback

        return decorator

    def setup(self, dp: Dispatcher):
        for handler in self._message_handlers:
            dp.register_message_handler(
                handler.callback,
                *handler.custom_filters,
                commands=handler.commands,
                regexp=handler.regexp,
                content_types=handler.content_types,
                state=handler.state,
                run_task=handler.run_task,
                **handler.kwargs
            )

        for handler in self._inline_handlers:
            dp.register_inline_handler(
                handler.callback,
                *handler.custom_filters,
                state=handler.state,
                run_task=handler.run_task,
                **handler.kwargs
            )

        for handler in self._callback_handlers:
            dp.register_callback_query_handler(
                handler.callback,
                *handler.custom_filters,
                state=handler.state,
                run_task=handler.run_task,
                **handler.kwargs
            )
