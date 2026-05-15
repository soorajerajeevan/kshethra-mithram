import hashlib
import json
from datetime import datetime

LINE_WIDTH = 64
ITEM_WIDTH = 40
QTY_WIDTH = 5
AMT_WIDTH = 14
TOTAL_LABEL_WIDTH = 50
TOTAL_VALUE_WIDTH = 18
PAGE_WIDTH_PX = 576
SIDE_PADDING_PX = 5
CONTENT_WIDTH_PX = PAGE_WIDTH_PX - (SIDE_PADDING_PX * 2)
DEFAULT_X = SIDE_PADDING_PX
DEFAULT_Y = 24
ROW_HEIGHT = 18
CHAR_WIDTH = CONTENT_WIDTH_PX / LINE_WIDTH


def _amount_rs(value):
    return f"Rs. {float(value or 0):,.2f}"


def _amount_plain(value):
    return f"{float(value or 0):,.2f}"


def _center_text(text, width):
    text = (text or "")[:width]
    # For multi-byte characters, use simple left-right centering
    text_len = len(text)
    left_pad = max(0, (width - text_len) // 2)
    right_pad = width - text_len - left_pad
    return " " * left_pad + text + " " * right_pad


def _display_width(text):
    """Calculate approximate display width of text."""
    return sum(1 for _ in text)


def _truncate_to_width(text, max_width):
    """Truncate text to fit within max_width display characters."""
    width = 0
    for i, char in enumerate(text):
        if width >= max_width:
            return text[:i]
        width += 1
    return text


def _kv_line(label, value, width):
    return f"{label} {value or ''}"[:width]


def _total_line(label, value):
    label_text = (label or "")[:TOTAL_LABEL_WIDTH]
    value_text = (value or "")[:TOTAL_VALUE_WIDTH]
    return f"{label_text:<{TOTAL_LABEL_WIDTH}}{value_text:>{TOTAL_VALUE_WIDTH}}"


def _word_spans(text):
    spans = []
    idx = 0
    token_index = 0
    while idx < len(text):
        if text[idx].isspace():
            idx += 1
            continue
        start = idx
        while idx < len(text) and not text[idx].isspace():
            idx += 1
        token = text[start:idx]
        spans.append({"token_index": token_index, "text": token, "start": start})
        token_index += 1
    return spans


def _stable_hash(content):
    return hashlib.sha1(content.encode("utf-8")).hexdigest()[:12]


def _snap_line_pitch(value):
    return int(round(int(value or 0) / ROW_HEIGHT) * ROW_HEIGHT)


def build_receipt_lines(bill, temple_name, temple_address, temple_phone, receipt_footer):
    lines = []

    def add(text, kind="text"):
        lines.append({"text": text[:LINE_WIDTH], "kind": kind})

    sep = "-" * LINE_WIDTH
    eq = "=" * LINE_WIDTH

    add(_center_text(temple_name, LINE_WIDTH), "header")
    addr = temple_address or ""
    for i in range(0, len(addr), LINE_WIDTH):
        add(_center_text(addr[i:i + LINE_WIDTH], LINE_WIDTH), "header")
    add(_center_text(_kv_line("Phone:", temple_phone, LINE_WIDTH), LINE_WIDTH), "header")
    add(sep, "divider")
    add(_kv_line("Bill No:", bill.bill_number, LINE_WIDTH), "meta")
    add(_kv_line("Date:", bill.bill_date.strftime("%d/%m/%Y %H:%M"), LINE_WIDTH), "meta")

    devotee_name = bill.devotee.full_name or ""
    for i in range(0, len(devotee_name), LINE_WIDTH - 9):
        prefix = "Devotee: " if i == 0 else "         "
        add((prefix + devotee_name[i:i + (LINE_WIDTH - 9)])[:LINE_WIDTH], "meta")

    if bill.devotee.devotee_id:
        add(_kv_line("ID:", bill.devotee.devotee_id, LINE_WIDTH), "meta")
    if bill.devotee.phone:
        add(_kv_line("Phone:", bill.devotee.phone, LINE_WIDTH), "meta")

    add(sep, "divider")
    add(f"{'ITEM':<{ITEM_WIDTH}} {'QTY':>{QTY_WIDTH}} {'AMOUNT':>{AMT_WIDTH}}", "table-header")
    add(sep, "divider")

    for item in bill.items:
        name = item.item_name or ""
        qty = f"{float(item.quantity or 0):g}"
        amt = _amount_plain(item.total_price)
        
        # If name is short enough, display on single line with qty and amount
        # Otherwise, display name on first line and qty/amount on second line
        if len(name) <= (ITEM_WIDTH - 5):
            truncated_name = _truncate_to_width(name, ITEM_WIDTH)
            padded_name = f"{truncated_name:<{ITEM_WIDTH}}"[:ITEM_WIDTH]
            add(f"{padded_name} {qty[:QTY_WIDTH]:>{QTY_WIDTH}} {amt[-AMT_WIDTH:]:>{AMT_WIDTH}}", "item")
        else:
            # Long name: put on first line, qty/amount on second line
            full_name = _truncate_to_width(name, LINE_WIDTH)
            add(full_name, "item")
            # Second line: right-align qty and amount
            qty_amt_spacing = " " * (LINE_WIDTH - QTY_WIDTH - 1 - AMT_WIDTH)
            add(f"{qty_amt_spacing}{qty[:QTY_WIDTH]:>{QTY_WIDTH}} {amt[-AMT_WIDTH:]:>{AMT_WIDTH}}", "item")
        
        if item.notes:
            note_prefix = "  > "
            note_text = (note_prefix + item.notes)[:LINE_WIDTH]
            add(note_text, "item-note")

    add(sep, "divider")
    add(_total_line("Subtotal", _amount_rs(bill.subtotal)), "total")

    if bill.discount_amount > 0:
        if bill.discount_percent > 0:
            label = f"Discount ({float(bill.discount_percent or 0):.1f}%)"
        else:
            label = "Discount"
        add(_total_line(label, f"-{_amount_rs(bill.discount_amount)}"), "total")
    if bill.donation_amount > 0:
        add(_total_line("Donation", _amount_rs(bill.donation_amount)), "total")

    add(eq, "divider-strong")
    add(_total_line("TOTAL", _amount_rs(bill.grand_total)), "total-strong")
    add(eq, "divider-strong")
    if bill.payment_mode:
        add(_kv_line("Payment Mode:", bill.payment_mode, LINE_WIDTH), "meta")
    if bill.payment_reference:
        ref = bill.payment_reference or ""
        for i in range(0, len(ref), LINE_WIDTH - 11):
            prefix = "Reference: " if i == 0 else "           "
            add((prefix + ref[i:i + (LINE_WIDTH - 11)])[:LINE_WIDTH], "meta")

    add(sep, "divider")
    add(_center_text("THANK YOU", LINE_WIDTH), "footer")
    footer = receipt_footer or ""
    for i in range(0, len(footer), LINE_WIDTH):
        add(footer[i:i + LINE_WIDTH], "footer")
    add(_center_text("Powered by kshethra-mithram", LINE_WIDTH), "footer")
    add(sep, "divider")
    return lines


def normalize_layout_config(raw_value):
    default_config = {"version": 1, "lineAdjustments": {}, "wordAdjustments": {}, "dividers": []}
    if not raw_value:
        return default_config
    try:
        data = json.loads(raw_value) if isinstance(raw_value, str) else dict(raw_value)
    except (TypeError, ValueError):
        return default_config

    line_adj = data.get("lineAdjustments", {})
    word_adj = data.get("wordAdjustments", {})
    dividers = data.get("dividers", [])
    if not isinstance(line_adj, dict):
        line_adj = {}
    if not isinstance(word_adj, dict):
        word_adj = {}
    if not isinstance(dividers, list):
        dividers = []
    normalized_dividers = []
    for divider in dividers:
        if not isinstance(divider, dict):
            continue
        normalized_dividers.append({
            "id": str(divider.get("id") or f"div-{len(normalized_dividers)}"),
            "x": int(divider.get("x", DEFAULT_X)),
            "y": int(divider.get("y", DEFAULT_Y)),
            "width": int(divider.get("width", CONTENT_WIDTH_PX)),
            "char": "=" if str(divider.get("char", "-")) == "=" else "-",
            "enabled": bool(divider.get("enabled", True)),
        })

    return {
        "version": int(data.get("version", 1)),
        "lineAdjustments": {
            str(k): {
                "x": int((v or {}).get("x", 0)),
                "y": _snap_line_pitch((v or {}).get("y", 0)),
                "enabled": bool((v or {}).get("enabled", True)),
            }
            for k, v in line_adj.items()
            if isinstance(v, dict)
        },
        "wordAdjustments": {
            str(k): {
                "x": int((v or {}).get("x", 0)),
                "y": _snap_line_pitch((v or {}).get("y", 0)),
                "enabled": bool((v or {}).get("enabled", True)),
            }
            for k, v in word_adj.items()
            if isinstance(v, dict)
        },
        "dividers": normalized_dividers,
    }


def compute_layout_model(lines, layout_config):
    line_adjustments = layout_config.get("lineAdjustments", {})
    word_adjustments = layout_config.get("wordAdjustments", {})

    rendered_lines = []
    rendered_words = []
    rendered_line_dividers = []
    line_y = DEFAULT_Y
    for index, line in enumerate(lines):
        line_text = line["text"]
        line_id = f"line-{index}-{_stable_hash(line_text + str(index))}"
        adj = line_adjustments.get(line_id, {})
        enabled = bool(adj.get("enabled", True))
        x = DEFAULT_X + int(adj.get("x", 0))
        y = line_y + _snap_line_pitch(adj.get("y", 0))
        if y < 2:
            y = 2

        rendered_lines.append({
            "lineId": line_id,
            "index": index,
            "text": line_text,
            "kind": line.get("kind", "text"),
            "x": x,
            "y": y,
            "enabled": enabled,
        })
        if line.get("kind", "").startswith("divider"):
            rendered_line_dividers.append({
                "id": f"{line_id}-rule",
                "x": x,
                "y": y + 10,
                "width": CONTENT_WIDTH_PX,
                "char": "=" if line.get("kind") == "divider-strong" else "-",
                "enabled": True,
            })

        if not line.get("kind", "").startswith("divider"):
            spans = _word_spans(line_text)
            for span in spans:
                word_id = f"{line_id}-word-{span['token_index']}"
                wadj = word_adjustments.get(word_id, {})
                rendered_words.append({
                    "wordId": word_id,
                    "lineId": line_id,
                    "text": span["text"],
                    "start": span["start"],
                "x": x + int(span["start"] * CHAR_WIDTH) + int(wadj.get("x", 0)),
                "y": y + _snap_line_pitch(wadj.get("y", 0)),
                "enabled": enabled and bool(wadj.get("enabled", True)),
            })

        line_y += ROW_HEIGHT

    now = datetime.utcnow().isoformat()
    rendered_dividers = []
    for idx, divider in enumerate(layout_config.get("dividers", [])):
        rendered_dividers.append({
            "id": divider.get("id", f"div-{idx}-{now}"),
            "x": int(divider.get("x", DEFAULT_X)),
            "y": int(divider.get("y", DEFAULT_Y)),
            "width": int(divider.get("width", CONTENT_WIDTH_PX)),
            "char": "=" if str(divider.get("char", "-")) == "=" else "-",
            "enabled": bool(divider.get("enabled", True)),
        })

    return {
        "metrics": {
            "lineWidthChars": LINE_WIDTH,
            "rowHeight": ROW_HEIGHT,
            "charWidth": CHAR_WIDTH,
            "canvasWidth": PAGE_WIDTH_PX,
            "canvasHeight": max(900, line_y + 40),
            "contentWidth": CONTENT_WIDTH_PX,
            "defaultX": DEFAULT_X,
            "defaultY": DEFAULT_Y,
        },
        "lines": rendered_lines,
        "words": rendered_words,
        "dividers": rendered_line_dividers + rendered_dividers,
    }
