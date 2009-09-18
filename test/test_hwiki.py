from hwiki import _read_bracketed_list


def test_read_bracketed_list():
	txt = "foo"
	assert _read_bracketed_list(txt) == ["foo"]

	txt = "foo bar"
	assert _read_bracketed_list(txt) == ["foo", "bar"]

	txt = "foo bar\nlorem ipsum"
	expected = ["foo", "bar", "lorem", "ipsum"]
	assert _read_bracketed_list(txt) == expected

	txt = "foo [[lorem ipsum]] bar"
	expected = ["foo", "bar", "lorem ipsum"]
	assert _read_bracketed_list(txt) == expected

	txt = "foo [[lorem ipsum]] bar [[dolor sit amet]] baz"
	expected = ["foo", "bar", "baz", "lorem ipsum", "dolor sit amet"]
	assert _read_bracketed_list(txt) == expected

	txt = "foo [[lorem ipsum]] bar\n[[dolor sit amet]] baz"
	expected = ["foo", "bar", "baz", "lorem ipsum", "dolor sit amet"]
	assert _read_bracketed_list(txt) == expected
