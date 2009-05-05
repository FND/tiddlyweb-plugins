"""
Test Differ plugin.
"""

import sys
sys.path.append(".")

from differ import generate_inline_diff


def test_generate_inline_diff():

	a = "lorem ipsum"
	b = "lorem foo ipsum"
	actual = generate_inline_diff(a, b)
	expected = "lorem <ins>foo </ins>ipsum"
	assert actual == expected

	a = "dolor sit amet"
	b = "dolor amet"
	actual = generate_inline_diff(a, b)
	expected = "dolor <del>sit </del>amet"
	assert actual == expected

	a = "foo bar baz"
	b = "foo xxx baz"
	actual = generate_inline_diff(a, b)
	expected = "foo <del>bar</del><ins>xxx</ins> baz"
	assert actual == expected

	a = "foo bar baz\n\nlorem ipsum\ndolor sit amet"
	b = "foo baz\n\nlorem xxx ipsum\ndolor yyy amet"
	actual = generate_inline_diff(a, b)
	expected = "foo<del> bar</del> baz\n\nlorem<ins> xxx</ins> ipsum\ndolor <del>sit</del><ins>yyy</ins> amet"
	assert actual == expected

	a = "foo bar \nbaz"
	b = "foo \nbar baz"
	actual = generate_inline_diff(a, b)
	expected = "foo <ins>\n</ins>bar <del>\n</del>baz"
	assert actual == expected
