import sys
from types import SimpleNamespace

from agent.tools.search import SearchTool


class FakeDdgs:
    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def text(self, query, region, max_results):
        assert query == "Raspberry Pi"
        assert region == "us-en"
        assert max_results == 1
        return [
            {
                "title": "Raspberry Pi",
                "body": "A small single-board computer.",
                "href": "https://www.raspberrypi.com/",
            }
        ]


def test_search_returns_shaped_text_without_using_the_network(monkeypatch):
    monkeypatch.setitem(sys.modules, "ddgs", SimpleNamespace(DDGS=FakeDdgs))

    result = SearchTool().search("Raspberry Pi")

    assert "Raspberry Pi" in result
    assert "small single-board computer" in result
