import json
import re

_FENCE = re.compile(r"^```(?:json)?\s*\n?(.*?)\n?```", re.S)
_DOUBLE = re.compile(r"([,{])\s*([A-Za-z_$][A-Za-z0-9_$]*)\s*:", re.M)
_SINGLE_KEY = re.compile(r"([,{]\s*)'([A-Za-z_$][A-Za-z0-9_$]*)'\s*:", re.M)
_SINGLE_VALUE = re.compile(r":\s*'([^'\\]*(?:\\.[^'\\]*)*)'\s*([,}\]])", re.M)
_TRAILING = re.compile(r",(\s*[}\]])", re.M)
_BARE_TRUE = re.compile(r"\bTrue\b")
_BARE_FALSE = re.compile(r"\bFalse\b")
_BARE_NONE = re.compile(r"\bNone\b")


def _first_json_root(text):
    text = text.strip()
    if text.startswith("`"):
        m = _FENCE.search(text)
        if m:
            text = m.group(1)
    start = None
    for i, ch in enumerate(text):
        if ch in "[{":
            start = i
            break
    if start is None:
        return text.strip()
    depth = 0
    in_string = False
    escaped = False
    for i in range(start, len(text)):
        ch = text[i]
        if in_string:
            if escaped:
                escaped = False
            elif ch == "\\":
                escaped = True
            elif ch == '"':
                in_string = False
        else:
            if ch == '"':
                in_string = True
            elif ch == "[" or ch == "{":
                depth += 1
            elif ch == "]" or ch == "}":
                depth -= 1
                if depth == 0:
                    return text[start:i + 1]
    return text[start:].strip()


def _escape_controls_in_strings(text):
    out = []
    in_string = False
    escaped = False
    for ch in text:
        if in_string:
            if escaped:
                out.append(ch)
                escaped = False
            elif ch == "\\":
                out.append(ch)
                escaped = True
            elif ch == '"':
                out.append(ch)
                in_string = False
            elif ch < " " and ch != "\t":
                out.append("\\u%04x" % ord(ch))
            else:
                out.append(ch)
        else:
            if ch == '"':
                in_string = True
                out.append(ch)
            else:
                out.append(ch)
    return "".join(out)


def _fix_unquoted_keys(text):
    return _DOUBLE.sub(r'\1"\2":', text)


def _fix_single_quotes(text):
    text = _SINGLE_KEY.sub(r'\1"\2":', text)
    text = _SINGLE_VALUE.sub(r':"\1"\2', text)
    return text


def _fix_trailing_comma(text):
    return _TRAILING.sub(r"\1", text)


def _fix_bare_literals(text):
    text = _BARE_TRUE.sub("true", text)
    text = _BARE_FALSE.sub("false", text)
    text = _BARE_NONE.sub("null", text)
    return text


def sanitize(text):
    text = _first_json_root(text)
    text = _escape_controls_in_strings(text)
    text = _fix_unquoted_keys(text)
    text = _fix_trailing_comma(text)
    text = _fix_single_quotes(text)
    text = _fix_bare_literals(text)
    return text


def parse(text):
    sanitized = sanitize(text)
    return json.loads(sanitized)
