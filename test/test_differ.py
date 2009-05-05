"""
Test Differ plugin.
"""

import sys
sys.path.append(".")

import differ


def test_diff():

	diff = differ.diff

	a = "lorem ipsum"
	b = "lorem foo ipsum"
	actual = diff(a, b)
	expected = "- lorem ipsum\n+ lorem foo ipsum\n?       ++++\n"
	assert actual == expected

	a = "lorem ipsum"
	b = "lorem foo ipsum"
	actual = diff(a, b, "inline")
	expected = "lorem <ins>foo </ins>ipsum"
	assert actual == expected


def test_generate_inline_diff():

	generate_inline_diff = differ.generate_inline_diff

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
