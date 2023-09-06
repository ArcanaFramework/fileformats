def test_circular_import_between_text_and_application():
    from fileformats.text import Plain  # noqa
