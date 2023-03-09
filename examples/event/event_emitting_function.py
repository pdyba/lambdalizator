from lbz.events import Event, EventAPI, event_emitter


class SomeEvent(Event):
    type = "SOME_TYPE"


@event_emitter
def send_event() -> None:
    EventAPI().register(SomeEvent({"message": 24}))
