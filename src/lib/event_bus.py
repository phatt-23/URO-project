import re
from enum import StrEnum
from dataclasses import dataclass
from typing import Callable, Any, Dict, List, Optional, Union, overload
from lib.types import Singleton

EventName = str
EventData = Dict[str, Any]


class EventPattern(StrEnum):
    _IDENTIFIER = r"[a-zA-Z][a-zA-Z0-9_]*(?:-\d+)?"
    _DOTTED_PATH = rf"(?:\.{_IDENTIFIER})*"
    EXACT = rf"(^{_IDENTIFIER}{_DOTTED_PATH}#{_IDENTIFIER}{_DOTTED_PATH}$)"
    SUB_STRING = rf"({_IDENTIFIER}{_DOTTED_PATH}#{_IDENTIFIER}{_DOTTED_PATH})"


class Event:
    name: EventName
    data: EventData
    is_handled: bool

    def __init__(self, name: EventName, data: EventData | None = None):
        self.name = name
        self.data = data or {}
        self.is_handled = False

    def __getitem__(self, key: str):
        return self.data.get(key)

    def __repr__(self):
        return f"Event(name='{self.name}', data={self.data})"


EventCallback = Callable[[Event], bool]


@dataclass
class EventPublishment:
    name: EventName
    data: EventData

@dataclass
class EventPatternSubscriber:
    pattern: str 
    callback: EventCallback


@dataclass
class EventSubscription:
    event_name: EventName 
    event_callback: EventCallback


class EventBus(Singleton):
    _subscribers: Dict[EventName, List[EventCallback]]
    _pattern_subscribers: List[EventPatternSubscriber]

    def __init__(self):
        self._subscribers = {}
        self._pattern_subscribers = []

    def subscribe(self, event_name: EventName, event_callback: EventCallback):
        if re.match(EventPattern.EXACT, event_name) is None:
            raise ValueError(f"Cannot subscribe to an event: '{event_name}'! (Incorrent naming convention)")

        if event_name not in self._subscribers:
            self._subscribers[event_name] = []
        self._subscribers[event_name].append(event_callback)

    def subscribe_pattern(self, event_name_pattern: str, event_callback: EventCallback):
        subscriber = EventPatternSubscriber(event_name_pattern, event_callback)
        self._pattern_subscribers.append(subscriber)


    def publish(self, event: Union[Event, EventName, EventPublishment], data: Optional[EventData] = None):
        if isinstance(event, EventName):
            event = Event(name=event, data=data)

        if isinstance(event, EventPublishment):
            assert data is None
            event = Event(name=event.name, data=event.data)

        if re.match(EventPattern.EXACT, event.name) is None:
            raise ValueError(f"Cannot publish an event: '{event.name}'! (Incorrent naming convention)")
        
        # call the pattern subscriber's callback if their pattern 
        # captures the published event name 
        for s in self._pattern_subscribers:
            match = re.match(s.pattern, event.name) 
            if match is None:
                continue

            is_handled = s.callback(event)
            if is_handled:
                return

        # call the subscriber's callback if they 
        # are subscribed to the published event
        for callback in self._subscribers.get(event.name, []):
            is_handled = callback(event)
            if is_handled:
                return
    
    def unsubscribe_for(self, obj: object):
        """Unsubscribes all subscriptions of the object (its bound methods) and returns them."""

        unsubed_subscriptions: list[EventSubscription] = []

        for event_name, callbacks in self._subscribers.items():
            for callback in callbacks:
                # check if the callback is a bound method
                if hasattr(callback, "__self__") and callback.__self__ is obj:
                    sub = EventSubscription(event_name, callback)
                    unsubed_subscriptions.append(sub)
                    self._subscribers[event_name].remove(callback)

        return unsubed_subscriptions


bus = EventBus()


def test():
    events_string = """
    LayoutView.ComposeView2.MessageEditor.SendButton#click
    LayoutView.ComposeView.MessageEditor.SendButton#some_category.click
    LayoutView.ComposeView.MessageEditor.SendButton#category.subcategory.click
    layout_view.compose_view.message_editor.send_button#click
    layout_view.mail_view.category_list.folder_item-0#click
    layout_view.mail_view.category_list.folder_item-0#hover
    layout_menu.compose_button#click
    layout_menu-23.some_button-123#click
    layout_menu.some_button-34#click
    layout_view.compose_view.message_editor.send_button#click
    layout_view.mail_view.category_list.folder_item-0#click
    layout_view.mail_view.category_list.folder_item-0#hover
    layout_menu.compose_button#click

    layout_menu.some_button-#click
    _layout_view.compose_view.message_editor.send_button#click
    sfsdfdsd-345
    sdfsdf
        layout_view.mail_view.category_list.folder_item-0#click
        layout_view.mail_view.category_list.folder_item-0#hover
        layout_menu.compose_button#click
    """

    print("Search string:\n", events_string)

    for m in re.findall(EventPattern.SUB_STRING, events_string):
        print("matched:", m)
    
    lines = events_string.splitlines()
    for line in lines:
        if re.match(EventPattern.EXACT, line) is None:
            print(f"This line is not a correct event name: '{line}'")

