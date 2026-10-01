from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from html import escape, unescape
from html.parser import HTMLParser
import json
from typing import Iterable


@dataclass(frozen=True, order=True)
class Fact:
    key: str
    value: str
    source: str

    def validate(self) -> None:
        for label, value in (("key", self.key), ("value", self.value), ("source", self.source)):
            if not isinstance(value, str) or not value or "\n" in value:
                raise ValueError(label + "_invalid")


def canonical_facts(facts: Iterable[Fact]) -> list[Fact]:
    rows=list(facts)
    for row in rows:
        row.validate()
    if len({row.key for row in rows}) != len(rows):
        raise ValueError("duplicate_fact_key")
    return sorted(rows)


def semantic_sha256(facts: Iterable[Fact]) -> str:
    rows=canonical_facts(facts)
    payload=json.dumps(
        [{"key":r.key,"value":r.value,"source":r.source} for r in rows],
        sort_keys=True,separators=(",",":"),ensure_ascii=False,
    ).encode()
    return "sha256:" + sha256(payload).hexdigest()


def render_json(facts: Iterable[Fact]) -> str:
    rows=canonical_facts(facts)
    return json.dumps(
        [{"key":r.key,"value":r.value,"source":r.source} for r in rows],
        sort_keys=True,separators=(",",":"),ensure_ascii=False,
    )


def parse_json(text: str) -> list[Fact]:
    doc=json.loads(text)
    if not isinstance(doc,list):
        raise ValueError("json_not_list")
    return canonical_facts(Fact(**row) for row in doc)


def _md_escape(value: str) -> str:
    return value.replace("\\","\\\\").replace("|","\\|")


def _md_unescape(value: str) -> str:
    out=[]
    escaped=False
    for ch in value:
        if escaped:
            out.append(ch); escaped=False
        elif ch=="\\":
            escaped=True
        else:
            out.append(ch)
    if escaped:
        out.append("\\")
    return "".join(out)


def _split_md_row(line: str) -> list[str]:
    if not line.startswith("|") or not line.endswith("|"):
        raise ValueError("markdown_row_invalid")
    body=line[1:-1]
    cells=[]; current=[]; escaped=False
    for ch in body:
        if escaped:
            current.append("\\"); current.append(ch); escaped=False
        elif ch=="\\":
            escaped=True
        elif ch=="|":
            cells.append("".join(current).strip()); current=[]
        else:
            current.append(ch)
    cells.append("".join(current).strip())
    return [_md_unescape(cell) for cell in cells]


def render_markdown(facts: Iterable[Fact]) -> str:
    rows=canonical_facts(facts)
    lines=["| key | value | source |","| --- | --- | --- |"]
    for row in rows:
        lines.append("| " + " | ".join(_md_escape(v) for v in (row.key,row.value,row.source)) + " |")
    return "\n".join(lines)


def parse_markdown(text: str) -> list[Fact]:
    lines=text.splitlines()
    if len(lines)<2 or lines[0]!="| key | value | source |":
        raise ValueError("markdown_header_invalid")
    return canonical_facts(Fact(*_split_md_row(line)) for line in lines[2:])


def render_html(facts: Iterable[Fact]) -> str:
    rows=canonical_facts(facts)
    body="".join(
        '<tr><td data-field="key">'+escape(r.key)+'</td>'
        '<td data-field="value">'+escape(r.value)+'</td>'
        '<td data-field="source">'+escape(r.source)+'</td></tr>'
        for r in rows
    )
    return '<table><thead><tr><th>key</th><th>value</th><th>source</th></tr></thead><tbody>'+body+'</tbody></table>'


class _FactHTMLParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.field: str | None=None
        self.current: dict[str,str]={}
        self.rows: list[Fact]=[]

    def handle_starttag(self, tag, attrs):
        if tag=="tr":
            self.current={}
        if tag=="td":
            data=dict(attrs)
            self.field=data.get("data-field")

    def handle_data(self, data):
        if self.field is not None:
            self.current[self.field]=self.current.get(self.field,"")+data

    def handle_endtag(self, tag):
        if tag=="td":
            self.field=None
        if tag=="tr" and set(self.current)=={"key","value","source"}:
            self.rows.append(Fact(
                unescape(self.current["key"]),
                unescape(self.current["value"]),
                unescape(self.current["source"]),
            ))


def parse_html(text: str) -> list[Fact]:
    parser=_FactHTMLParser()
    parser.feed(text)
    return canonical_facts(parser.rows)


def representation_record(facts: Iterable[Fact]) -> dict[str,dict[str,object]]:
    rows=canonical_facts(facts)
    expected=semantic_sha256(rows)
    formats={
        "JSON":(render_json,parse_json),
        "MARKDOWN":(render_markdown,parse_markdown),
        "HTML":(render_html,parse_html),
    }
    out={}
    for name,(renderer,parser) in formats.items():
        payload=renderer(rows)
        parsed=parser(payload)
        out[name]={
            "bytes":len(payload.encode()),
            "fact_count":len(parsed),
            "semantic_sha256":semantic_sha256(parsed),
            "semantic_preserved":semantic_sha256(parsed)==expected,
            "authority_effect":"NONE",
        }
    return out
