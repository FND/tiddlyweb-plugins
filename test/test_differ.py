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

	actual = diff(a, b, "inline")
	expected = "lorem <ins>foo </ins>ipsum"
	assert actual == expected

	actual = diff(a, b, "horizontal")
	expected = """<tr><td class="diff_next" id="difflib_chg_to0__0"><a href="#difflib_chg_to0__top">t</a></td><td class="diff_header" id="from0_1">1</td><td nowrap="nowrap">lorem&nbsp;ipsum</td><td class="diff_next"><a href="#difflib_chg_to0__top">t</a></td><td class="diff_header" id="to0_1">1</td><td nowrap="nowrap">lorem&nbsp;<span class="diff_add">foo&nbsp;</span>ipsum</td></tr>"""
	assert expected in actual


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
