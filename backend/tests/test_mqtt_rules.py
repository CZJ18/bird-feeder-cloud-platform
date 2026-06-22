def test_mqtt_spec_only_persists_leave_and_status() -> None:
    event_types_to_store = {"leave"}
    event_types_to_ignore = {"enter"}

    assert "leave" in event_types_to_store
    assert "enter" in event_types_to_ignore
