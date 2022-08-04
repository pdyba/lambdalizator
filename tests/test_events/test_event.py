from lbz.events.event import Event


class MyTestEvent(Event):
    type = "MY_TEST_EVENT"


class TestEvent:
    def test_base_event_creation_and_structure(self) -> None:
        event = {"x": 1}
        new_event = MyTestEvent(event)

        assert new_event.type == "MY_TEST_EVENT"
        assert new_event.data == {"x": 1}
        assert new_event.serialized_data == '{"x": 1}'

    def test__eq__same(self) -> None:
        new_event_1 = MyTestEvent({"x": 1})
        new_event_2 = MyTestEvent({"x": 1})

        assert new_event_1 == new_event_2

    def test__eq__different_data(self) -> None:
        new_event_1 = MyTestEvent({"x": 1})
        new_event_2 = MyTestEvent({"x": 2})

        assert new_event_1 != new_event_2

    def test__eq__different_type_same_data(self) -> None:
        class MySecondTestEvent(Event):
            type = "MY_SECOND_TEST_EVENT"

        new_event_1 = MyTestEvent({"x": 1})
        new_event_2 = MySecondTestEvent({"x": 1})

        assert new_event_1 != new_event_2
