#!/usr/bin/env python3
"""One millimetre scene -> portable HTML, SVG and optional outlined CMYK PDF.

Preview uses only the Python standard library. PDF/outlined SVG additionally need
fonttools and reportlab (PDF only). This script never executes scene content.
"""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import math
from pathlib import Path
import re
import sys
import tempfile
from urllib.parse import urlsplit

MM_PT = 72 / 25.4
HEX = re.compile(r"^#[0-9a-fA-F]{6}$")
IDENTIFIER = re.compile(r"^[a-zA-Z][a-zA-Z0-9_-]{0,63}$")
MAX_ELEMENTS = 2000


class DesignError(ValueError):
    pass


def number(value, where, minimum=None, maximum=None):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise DesignError(f"{where}: expected a finite number")
    if minimum is not None and value < minimum or maximum is not None and value > maximum:
        raise DesignError(f"{where}: number out of range")
    return float(value)


def strict_keys(obj, allowed, where):
    if not isinstance(obj, dict):
        raise DesignError(f"{where}: expected an object")
    unexpected = set(obj) - set(allowed)
    if unexpected:
        raise DesignError(f"{where}: unsupported fields {sorted(unexpected)}")


def safe_url(value, where):
    if not isinstance(value, str) or any(ord(ch) < 32 for ch in value):
        raise DesignError(f"{where}: invalid URL")
    try:
        parsed = urlsplit(value)
        # Accessing port also validates malformed or out-of-range port numbers.
        parsed.port
    except ValueError as exc:
        raise DesignError(f"{where}: malformed HTTP(S) URL") from exc
    if parsed.scheme not in ("https", "http") or not parsed.hostname or parsed.username or parsed.password:
        raise DesignError(f"{where}: only absolute HTTP(S) URLs without credentials are allowed")
    return value


def validate_scene(scene):
    strict_keys(scene, {"schema_version", "title", "size_mm", "bleed_mm", "safe_mm", "colors", "fonts", "faces"}, "scene")
    if isinstance(scene.get("schema_version"),bool) or scene.get("schema_version") != 1:
        raise DesignError("schema_version must be 1")
    if not isinstance(scene.get("title"), str) or not scene["title"].strip():
        raise DesignError("title must be nonempty text")
    size = scene.get("size_mm")
    if not isinstance(size, list) or len(size) != 2:
        raise DesignError("size_mm must be [width, height]")
    width, height = [number(v, "size_mm", 1, 2000) for v in size]
    bleed = number(scene.get("bleed_mm", 0), "bleed_mm", 0, 30)
    number(scene.get("safe_mm", 4), "safe_mm", 0, min(width, height) / 2)
    colors = scene.get("colors")
    if not isinstance(colors, dict) or not colors:
        raise DesignError("colors must be a nonempty named color map")
    for name, color in colors.items():
        if not IDENTIFIER.fullmatch(name):
            raise DesignError(f"invalid color name {name!r}")
        strict_keys(color, {"hex", "cmyk", "note"}, f"colors.{name}")
        if not isinstance(color.get("hex"), str) or not HEX.fullmatch(color["hex"]):
            raise DesignError(f"colors.{name}.hex must be #RRGGBB")
        if "cmyk" in color:
            if not isinstance(color["cmyk"], list) or len(color["cmyk"]) != 4:
                raise DesignError(f"colors.{name}.cmyk must contain four percentages")
            for channel in color["cmyk"]:
                number(channel, f"colors.{name}.cmyk", 0, 100)
    fonts = scene.get("fonts", {})
    if not isinstance(fonts, dict):
        raise DesignError("fonts must be a named font map")
    for name, font in fonts.items():
        if not IDENTIFIER.fullmatch(name):
            raise DesignError(f"invalid font name {name!r}")
        strict_keys(font, {"family", "path", "font_index", "weight", "axes"}, f"fonts.{name}")
        if not isinstance(font.get("family"), str) or not font["family"].strip():
            raise DesignError(f"fonts.{name}.family must be nonempty")
        if "path" in font and (not isinstance(font["path"], str) or not font["path"].strip()):
            raise DesignError(f"fonts.{name}.path must be a nonempty local path")
        if "weight" in font:
            number(font["weight"], f"fonts.{name}.weight", 1, 1000)
        if "font_index" in font and (isinstance(font["font_index"],bool) or not isinstance(font["font_index"],int) or font["font_index"] < 0):
            raise DesignError(f"fonts.{name}.font_index must be a nonnegative collection index")
        if "axes" in font:
            if not isinstance(font["axes"], dict):
                raise DesignError(f"fonts.{name}.axes must be a map")
            for tag, value in font["axes"].items():
                if not isinstance(tag, str) or len(tag) != 4:
                    raise DesignError("font axis tags must be four characters")
                number(value, f"fonts.{name}.axes.{tag}")
    faces = scene.get("faces")
    if not isinstance(faces, list) or not 1 <= len(faces) <= 32:
        raise DesignError("faces must contain between 1 and 32 faces")
    identifiers = set()
    warnings = []
    safe = scene.get("safe_mm", 4)
    for index, face in enumerate(faces):
        where = f"faces[{index}]"
        strict_keys(face, {"id", "name", "background", "elements"}, where)
        if not isinstance(face.get("id"), str) or not IDENTIFIER.fullmatch(face["id"]) or face["id"] in identifiers:
            raise DesignError(f"{where}.id must be a unique safe identifier")
        identifiers.add(face["id"])
        if not isinstance(face.get("name", face["id"]), str):
            raise DesignError(f"{where}.name must be text")
        if face.get("background") not in colors:
            raise DesignError(f"{where}.background must name a color")
        elements = face.get("elements")
        if not isinstance(elements, list) or len(elements) > MAX_ELEMENTS:
            raise DesignError(f"{where}.elements must be a list of at most {MAX_ELEMENTS} elements")
        for ei, element in enumerate(elements):
            at = f"{where}.elements[{ei}]"
            if not isinstance(element, dict):
                raise DesignError(f"{at}: expected an object")
            kind = element.get("type")
            fields = {
                "rect": {"type", "x", "y", "width", "height", "fill", "stroke", "stroke_mm", "radius_mm"},
                "line": {"type", "x1", "y1", "x2", "y2", "stroke", "stroke_mm"},
                "text": {"type", "x", "y", "text", "font", "size_pt", "fill", "tracking_mm", "align", "line_height_mm"},
                "qr": {"type", "x", "y", "size_mm", "url", "dark", "light", "quiet_modules"},
            }
            if kind not in fields:
                raise DesignError(f"{at}: supported elements are rect, line, text and qr")
            strict_keys(element, fields[kind], at)
            for key in ("fill", "stroke", "dark", "light"):
                if key in element and element[key] not in colors:
                    raise DesignError(f"{at}.{key}: unknown named color")
            if kind == "line":
                for key in ("x1", "x2"):
                    number(element.get(key), f"{at}.{key}", -bleed, width + bleed)
                for key in ("y1", "y2"):
                    number(element.get(key), f"{at}.{key}", -bleed, height + bleed)
                if "stroke" not in element:
                    raise DesignError(f"{at}: line requires stroke")
            else:
                x = number(element.get("x"), f"{at}.x", -bleed, width + bleed)
                y = number(element.get("y"), f"{at}.y", -bleed, height + bleed)
                if kind == "rect":
                    w = number(element.get("width"), f"{at}.width", 0.001, width + 2 * bleed)
                    h = number(element.get("height"), f"{at}.height", 0.001, height + 2 * bleed)
                    if x + w > width + bleed + 1e-6 or y + h > height + bleed + 1e-6:
                        raise DesignError(f"{at}: rectangle extends outside bleed")
                    if "fill" not in element and "stroke" not in element:
                        raise DesignError(f"{at}: rectangle requires fill or stroke")
                    number(element.get("radius_mm", 0), f"{at}.radius_mm", 0, min(w, h) / 2)
                elif kind == "text":
                    if not isinstance(element.get("text"), str) or not element["text"] or len(element["text"]) > 10000:
                        raise DesignError(f"{at}.text must contain between 1 and 10000 characters")
                    if any(ord(ch) < 32 and ch != "\n" for ch in element["text"]):
                        raise DesignError(f"{at}.text contains control characters")
                    if element.get("font") not in fonts or "fill" not in element:
                        raise DesignError(f"{at}: text requires a named font and fill")
                    font_size = number(element.get("size_pt"), f"{at}.size_pt", 1, 500)
                    number(element.get("tracking_mm", 0), f"{at}.tracking_mm", -10, 30)
                    number(element.get("line_height_mm", font_size / MM_PT * 1.2), f"{at}.line_height_mm", 0.1, 500)
                    if element.get("align", "left") not in ("left", "center", "right"):
                        raise DesignError(f"{at}.align must be left, center or right")
                    if x < safe or x > width - safe or y < safe or y > height - safe:
                        warnings.append(f"{at}: text anchor is outside the safe inset; inspect actual glyph bounds")
                    if font_size < 6:
                        warnings.append(f"{at}: text is below 6 pt; inspect at finished physical size")
                elif kind == "qr":
                    qr_size = number(element.get("size_mm"), f"{at}.size_mm", 5, min(width, height))
                    safe_url(element.get("url"), f"{at}.url")
                    if "dark" not in element or "light" not in element:
                        raise DesignError(f"{at}: QR requires dark and light colors")
                    quiet = element.get("quiet_modules", 4)
                    if isinstance(quiet, bool) or not isinstance(quiet, int) or not 4 <= quiet <= 20:
                        raise DesignError(f"{at}: quiet_modules must be an integer >= 4")
                    if x + qr_size > width or y + qr_size > height:
                        raise DesignError(f"{at}: QR must fit inside trim")
                    matrix = make_qr(element["url"])
                    if qr_size / (len(matrix) + quiet * 2) < 0.35:
                        warnings.append(f"{at}: QR modules are below 0.35 mm; enlarge and verify the printed result")
                    if min(x, y, width - x - qr_size, height - y - qr_size) < safe:
                        warnings.append(f"{at}: QR is outside the safe inset")
            if "stroke_mm" in element:
                number(element["stroke_mm"], f"{at}.stroke_mm", 0.01, 100)
    return warnings


# Byte-mode QR, ECC Q, versions 1--10. Reed-Solomon arithmetic is over GF(256).
# Tables are standard QR block layouts and alignment positions, not assets.
Q_BLOCKS = [None, [(1,26,13)], [(1,44,22)], [(2,35,17)], [(2,50,24)],
            [(2,33,15),(2,34,16)], [(4,43,19)], [(2,32,14),(4,33,15)],
            [(4,40,18),(2,41,19)], [(4,36,16),(4,37,17)], [(6,43,19),(2,44,20)]]
ALIGNMENTS = [None, [], [6,18], [6,22], [6,26], [6,30], [6,34],
              [6,22,38], [6,24,42], [6,26,46], [6,28,50]]


def gf_mul(a, b):
    product = 0
    while b:
        if b & 1:
            product ^= a
        a <<= 1
        if a & 0x100:
            a ^= 0x11D
        b >>= 1
    return product


def parity(data, count):
    generator = [1]
    root = 1
    for _ in range(count):
        updated = [0] * (len(generator) + 1)
        for j, value in enumerate(generator):
            updated[j] ^= value
            updated[j + 1] ^= gf_mul(value, root)
        generator = updated
        root = gf_mul(root, 2)
    remainder = list(data) + [0] * count
    for i in range(len(data)):
        coefficient = remainder[i]
        if coefficient:
            for j, value in enumerate(generator):
                remainder[i + j] ^= gf_mul(value, coefficient)
    return remainder[-count:]


def bits(value, length):
    return [(value >> i) & 1 for i in range(length - 1, -1, -1)]


def bch(value, shift, polynomial):
    remainder = value << shift
    while remainder.bit_length() >= polynomial.bit_length():
        remainder ^= polynomial << (remainder.bit_length() - polynomial.bit_length())
    return (value << shift) | remainder


def mask_bit(mask, row, col):
    return [lambda: (row + col) % 2 == 0,
            lambda: row % 2 == 0, lambda: col % 3 == 0,
            lambda: (row + col) % 3 == 0,
            lambda: (row // 2 + col // 3) % 2 == 0,
            lambda: (row * col) % 2 + (row * col) % 3 == 0,
            lambda: ((row * col) % 2 + (row * col) % 3) % 2 == 0,
            lambda: ((row * col) % 3 + (row + col) % 2) % 2 == 0][mask]()


def make_qr(url):
    raw = url.encode("utf-8")
    # Explicit UTF-8 ECI prevents decoder-dependent guessing for non-ASCII URLs.
    prefix = bits(7,4) + bits(26,8) if any(byte >= 128 for byte in raw) else []
    version = None
    for candidate in range(1, 11):
        capacity = sum(count * data for count, _, data in Q_BLOCKS[candidate])
        if len(prefix) + 4 + (8 if candidate < 10 else 16) + len(raw) * 8 <= capacity * 8:
            version = candidate
            break
    if version is None:
        raise DesignError("QR URL exceeds this renderer's version-10 ECC-Q capacity; use a shorter stable URL")
    data_bits = prefix + bits(4, 4) + bits(len(raw), 8 if version < 10 else 16)
    for byte in raw:
        data_bits.extend(bits(byte, 8))
    data_bits.extend([0] * min(4, capacity * 8 - len(data_bits)))
    data_bits.extend([0] * ((-len(data_bits)) % 8))
    codewords = [sum(bit << (7-j) for j, bit in enumerate(data_bits[i:i+8])) for i in range(0, len(data_bits), 8)]
    while len(codewords) < capacity:
        codewords.append(0xEC if (len(codewords) - len(data_bits) // 8) % 2 == 0 else 0x11)
    blocks, ecc = [], []
    offset = 0
    for count, total, data in Q_BLOCKS[version]:
        for _ in range(count):
            block = codewords[offset:offset+data]
            blocks.append(block)
            ecc.append(parity(block, total - data))
            offset += data
    stream = [block[i] for i in range(max(map(len, blocks))) for block in blocks if i < len(block)]
    stream += [block[i] for i in range(max(map(len, ecc))) for block in ecc if i < len(block)]
    payload = [bit for byte in stream for bit in bits(byte, 8)]
    size = version * 4 + 17

    def build(mask):
        matrix = [[None] * size for _ in range(size)]
        for row, col in ((0,0),(0,size-7),(size-7,0)):
            for dy in range(-1,8):
                for dx in range(-1,8):
                    yy, xx = row + dy, col + dx
                    if 0 <= yy < size and 0 <= xx < size:
                        matrix[yy][xx] = (0 <= dx <= 6 and dy in (0,6)) or (0 <= dy <= 6 and dx in (0,6)) or (2 <= dx <= 4 and 2 <= dy <= 4)
        for row in ALIGNMENTS[version]:
            for col in ALIGNMENTS[version]:
                if matrix[row][col] is not None:
                    continue
                for dy in range(-2,3):
                    for dx in range(-2,3):
                        matrix[row+dy][col+dx] = max(abs(dx),abs(dy)) != 1
        for i in range(8,size-8):
            if matrix[i][6] is None:
                matrix[i][6] = i % 2 == 0
            if matrix[6][i] is None:
                matrix[6][i] = i % 2 == 0
        format_value = bch((3 << 3) | mask, 10, 0x537) ^ 0x5412
        for i in range(15):
            value = bool((format_value >> i) & 1)
            row = i if i < 6 else i + 1 if i < 8 else size - 15 + i
            matrix[row][8] = value
            col = size - i - 1 if i < 8 else 7 if i == 8 else 15 - i - 1
            matrix[8][col] = value
        matrix[size-8][8] = True
        if version >= 7:
            version_value = bch(version, 12, 0x1F25)
            for i in range(18):
                row, col = i // 3, i % 3 + size - 11
                matrix[row][col] = matrix[col][row] = bool((version_value >> i) & 1)
        offset = 0
        upward = True
        col = size - 1
        while col > 0:
            if col == 6:
                col -= 1
            rows = range(size-1,-1,-1) if upward else range(size)
            for row in rows:
                for x in (col,col-1):
                    if matrix[row][x] is None:
                        value = bool(payload[offset]) if offset < len(payload) else False
                        matrix[row][x] = value ^ mask_bit(mask,row,x)
                        offset += 1
            upward = not upward
            col -= 2
        return matrix

    def penalty(matrix):
        score = 0
        for rows in (matrix, list(zip(*matrix))):
            for row in rows:
                run, last = 0, None
                for cell in row:
                    if cell == last:
                        run += 1
                        if run == 5:
                            score += 3
                        elif run > 5:
                            score += 1
                    else:
                        last, run = cell, 1
                for i in range(size-10):
                    if list(row[i:i+11]) in ([True,False,True,True,True,False,True,False,False,False,False],
                                             [False,False,False,False,True,False,True,True,True,False,True]):
                        score += 40
        for row in range(size-1):
            for col in range(size-1):
                if matrix[row][col] == matrix[row+1][col] == matrix[row][col+1] == matrix[row+1][col+1]:
                    score += 3
        score += int(abs(sum(map(sum,matrix)) * 100 / (size*size) - 50) // 5) * 10
        return score

    candidates = [build(mask) for mask in range(8)]
    return min(candidates, key=penalty)


def fmt(value):
    return f"{value:.6f}".rstrip("0").rstrip(".") or "0"


def attr(value):
    return html.escape(str(value), quote=True)


class Outlines:
    """Explicit font outlines. No hidden fallback; unsupported shaping fails closed."""
    def __init__(self, scene, source):
        try:
            from fontTools.ttLib import TTFont, TTLibError
            from fontTools.varLib.instancer import instantiateVariableFont
        except ImportError as exc:
            raise DesignError("Outlined export requires fonttools. Install it in your chosen Python environment.") from exc
        self.loaded = {}
        for name, spec in scene["fonts"].items():
            if not spec.get("path"):
                raise DesignError(f"fonts.{name}.path is required for outlined export; choose a licensed local font")
            path = Path(spec["path"]).expanduser()
            if not path.is_absolute():
                path = source.parent / path
            if not path.is_file():
                raise DesignError(f"fonts.{name}.path does not exist: {path}")
            try:
                font = TTFont(str(path),fontNumber=spec.get("font_index",0))
                if "fvar" in font:
                    axes = {axis.axisTag: axis.defaultValue for axis in font["fvar"].axes}
                    axes.update(spec.get("axes", {}))
                    if "wght" in axes:
                        axes["wght"] = spec.get("weight", axes["wght"])
                    font = instantiateVariableFont(font, axes, inplace=False)
                cmap = font.getBestCmap()
                if not cmap or "hmtx" not in font:
                    raise DesignError(f"fonts.{name}: font lacks Unicode cmap or horizontal metrics")
                self.loaded[name] = (font, font.getGlyphSet(), cmap, font["head"].unitsPerEm)
            except (TTLibError,ValueError,KeyError) as exc:
                raise DesignError(f"fonts.{name}: could not load the chosen font/collection/axes: {exc}") from exc

    def line(self, element, text):
        font, glyphs, cmap, upem = self.loaded[element["font"]]
        # Simple per-codepoint placement supports Latin and unshaped CJK. Shaped
        # scripts, combining marks and bidi require another shaping-aware renderer.
        import unicodedata
        if any(unicodedata.category(ch).startswith("M") or unicodedata.bidirectional(ch) in ("R","AL","AN")
               or 0x0900 <= ord(ch) <= 0x0DFF or 0x1000 <= ord(ch) <= 0x109F
               or 0x1780 <= ord(ch) <= 0x17FF for ch in text):
            raise DesignError("Outlined text needs complex shaping; use a shaping-aware vector exporter instead")
        scale = element["size_pt"] / MM_PT / upem
        tracking = element.get("tracking_mm", 0)
        names = []
        for ch in text:
            if ord(ch) not in cmap:
                raise DesignError(f"Selected font lacks glyph {ch!r} (U+{ord(ch):04X})")
            names.append(cmap[ord(ch)])
        advances = [font["hmtx"].metrics[name][0] * scale for name in names]
        total = sum(advances) + tracking * max(0,len(names)-1)
        align = element.get("align", "left")
        x = element["x"] - (total / 2 if align == "center" else total if align == "right" else 0)
        result = []
        for name, advance in zip(names, advances):
            result.append((glyphs, name, x, scale))
            x += advance + tracking
        return result


def qr_rects(element):
    matrix = make_qr(element["url"])
    quiet = element.get("quiet_modules", 4)
    module = element["size_mm"] / (len(matrix) + 2 * quiet)
    for row, values in enumerate(matrix):
        col = 0
        while col < len(values):
            if not values[col]:
                col += 1
                continue
            start = col
            while col < len(values) and values[col]:
                col += 1
            yield (element["x"] + (quiet + start) * module,
                   element["y"] + (quiet + row) * module, (col-start) * module, module)


def svg_face(scene, face, outlines=None, bleed=False):
    width, height = scene["size_mm"]
    extra = scene.get("bleed_mm", 0) if bleed else 0
    color = lambda name: scene["colors"][name]["hex"]
    result = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{fmt(width+extra*2)}mm" height="{fmt(height+extra*2)}mm" viewBox="{fmt(-extra)} {fmt(-extra)} {fmt(width+extra*2)} {fmt(height+extra*2)}" role="img" aria-label="{attr(face.get("name",face["id"]))}">',
              f'<title>{attr(scene["title"])} — {attr(face.get("name",face["id"]))}</title>',
              f'<rect x="{fmt(-extra)}" y="{fmt(-extra)}" width="{fmt(width+2*extra)}" height="{fmt(height+2*extra)}" fill="{color(face["background"])}"/>']
    for element in face["elements"]:
        kind = element["type"]
        if kind == "rect":
            attributes = {key: fmt(element[key]) for key in ("x","y","width","height")}
            attributes["fill"] = color(element["fill"]) if "fill" in element else "none"
            if "stroke" in element:
                attributes.update({"stroke":color(element["stroke"]), "stroke-width":fmt(element.get("stroke_mm",0.15))})
            if element.get("radius_mm"):
                attributes["rx"] = fmt(element["radius_mm"])
            result.append('<rect ' + ' '.join(f'{key}="{attr(value)}"' for key,value in attributes.items()) + '/>')
        elif kind == "line":
            attributes = ' '.join(f'{key}="{fmt(element[key])}"' for key in ("x1","y1","x2","y2"))
            result.append(f'<line {attributes} stroke="{color(element["stroke"])}" stroke-width="{fmt(element.get("stroke_mm",0.15))}"/>')
        elif kind == "text":
            leading = element.get("line_height_mm",element["size_pt"] / MM_PT * 1.2)
            for line_number, line in enumerate(element["text"].split("\n")):
                y = element["y"] + line_number * leading
                if outlines is None:
                    font = scene["fonts"][element["font"]]
                    anchor = {"left":"start", "center":"middle", "right":"end"}[element.get("align","left")]
                    result.append(f'<text x="{fmt(element["x"])}" y="{fmt(y)}" font-family="{attr(font["family"])}" font-weight="{font.get("weight",400)}" font-size="{fmt(element["size_pt"]/MM_PT)}" letter-spacing="{fmt(element.get("tracking_mm",0))}" font-kerning="none" font-variant-ligatures="none" text-anchor="{anchor}" fill="{color(element["fill"])}" xml:space="preserve">{attr(line)}</text>')
                else:
                    from fontTools.pens.svgPathPen import SVGPathPen
                    for glyphs, name, x, scale in outlines.line(element,line):
                        pen = SVGPathPen(glyphs)
                        glyphs[name].draw(pen)
                        result.append(f'<path d="{attr(pen.getCommands())}" fill="{color(element["fill"])}" fill-rule="nonzero" transform="translate({fmt(x)} {fmt(y)}) scale({fmt(scale)} {fmt(-scale)})"/>')
        elif kind == "qr":
            result.append(f'<g aria-label="QR: {attr(element["url"])}" shape-rendering="crispEdges">')
            result.append(f'<rect x="{fmt(element["x"])}" y="{fmt(element["y"])}" width="{fmt(element["size_mm"])}" height="{fmt(element["size_mm"])}" fill="{color(element["light"])}"/>')
            path = " ".join(f'M{fmt(x)} {fmt(y)}h{fmt(w)}v{fmt(h)}h{fmt(-w)}z' for x,y,w,h in qr_rects(element))
            result.append(f'<path d="{path}" fill="{color(element["dark"])}"/></g>')
    result.append('</svg>')
    return '\n'.join(result)


def html_preview(scene, svgs):
    sections = []
    for face, svg in zip(scene["faces"],svgs):
        sections.append(f'<section><h2>{attr(face.get("name",face["id"]))}</h2>{svg}</section>')
    return '''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; img-src data:; font-src 'none'; base-uri 'none'; form-action 'none'">
<title>''' + attr(scene["title"]) + '''</title><style>
*{box-sizing:border-box}body{margin:0;padding:32px;background:#ededed;color:#1e1e1e;font:16px system-ui,sans-serif}
main{max-width:1120px;margin:auto}h1{font-weight:500;font-size:24px}p{line-height:1.5;color:#555}
.faces{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,360px),1fr));gap:24px}
section{min-width:0}h2{font-size:14px;font-weight:500}svg{display:block;width:100%;height:auto;box-shadow:0 8px 25px #0002}
@media print{body{padding:0;background:white}.faces{display:block}section{break-after:page}svg{width:auto;box-shadow:none}h1,h2,p{display:none}}
</style></head><body><main><h1>''' + attr(scene["title"]) + '</h1><p>' + attr(f'{scene["size_mm"][0]} × {scene["size_mm"][1]} mm · RGB screen preview. Inspect the physical print export separately.') + '</p><div class="faces">' + '\n'.join(sections) + '</div></main></body></html>\n'


def export_pdf(scene, target, outlines):
    try:
        from reportlab.pdfgen.canvas import Canvas
        from fontTools.pens.reportLabPen import ReportLabPen
    except ImportError as exc:
        raise DesignError("CMYK PDF requires reportlab and fonttools in your chosen Python environment") from exc
    class PdfGlyphPen(ReportLabPen):
        # FontTools' default ReportLabPen targets graphics.shapes.Path. Canvas
        # paths use close() rather than closePath(); the other methods agree.
        def _closePath(self):
            self.path.close()
    for name, spec in scene["colors"].items():
        if "cmyk" not in spec:
            raise DesignError(f"colors.{name}.cmyk is required for CMYK PDF; no silent RGB conversion is performed")
    width, height = scene["size_mm"]
    bleed = scene.get("bleed_mm",0)
    marks = 5.0
    offset = bleed + marks
    page_width, page_height = (width + offset*2)*MM_PT, (height+offset*2)*MM_PT
    canvas = Canvas(str(target), pagesize=(page_width,page_height), pageCompression=1, invariant=1)
    canvas.setTitle(scene["title"])
    canvas.setSubject("Outlined vector artwork; working DeviceCMYK; physical proof required; not PDF/X certified")
    canvas.setAuthor("Code Driven Design")
    canvas.setCreator("render_design.py")
    for face in scene["faces"]:
        canvas.setTrimBox((offset*MM_PT,offset*MM_PT,(offset+width)*MM_PT,(offset+height)*MM_PT))
        canvas.setBleedBox((marks*MM_PT,marks*MM_PT,(marks+width+2*bleed)*MM_PT,(marks+height+2*bleed)*MM_PT))
        canvas.saveState()
        canvas.translate(offset*MM_PT,(offset+height)*MM_PT)
        canvas.scale(MM_PT,-MM_PT)

        def fill(name):
            canvas.setFillColorCMYK(*(value/100 for value in scene["colors"][name]["cmyk"]))

        def stroke(name):
            canvas.setStrokeColorCMYK(*(value/100 for value in scene["colors"][name]["cmyk"]))

        fill(face["background"])
        canvas.rect(-bleed,-bleed,width+bleed*2,height+bleed*2,stroke=0,fill=1)
        for element in face["elements"]:
            kind = element["type"]
            if kind == "rect":
                if "fill" in element:
                    fill(element["fill"])
                if "stroke" in element:
                    stroke(element["stroke"])
                    canvas.setLineWidth(element.get("stroke_mm",0.15))
                args = (element["x"],element["y"],element["width"],element["height"])
                if element.get("radius_mm"):
                    canvas.roundRect(*args,element["radius_mm"],stroke=int("stroke" in element),fill=int("fill" in element))
                else:
                    canvas.rect(*args,stroke=int("stroke" in element),fill=int("fill" in element))
            elif kind == "line":
                stroke(element["stroke"])
                canvas.setLineWidth(element.get("stroke_mm",0.15))
                canvas.line(element["x1"],element["y1"],element["x2"],element["y2"])
            elif kind == "text":
                fill(element["fill"])
                leading = element.get("line_height_mm",element["size_pt"]/MM_PT*1.2)
                for line_number,line in enumerate(element["text"].split("\n")):
                    y = element["y"]+line_number*leading
                    for glyphs,name,x,scale in outlines.line(element,line):
                        canvas.saveState()
                        canvas.translate(x,y)
                        canvas.scale(scale,-scale)
                        pen = PdfGlyphPen(glyphs,canvas.beginPath())
                        glyphs[name].draw(pen)
                        canvas.drawPath(pen.path,stroke=0,fill=1,fillMode=1)
                        canvas.restoreState()
            elif kind == "qr":
                fill(element["light"])
                canvas.rect(element["x"],element["y"],element["size_mm"],element["size_mm"],stroke=0,fill=1)
                fill(element["dark"])
                path = canvas.beginPath()
                for x,y,w,h in qr_rects(element):
                    path.rect(x,y,w,h)
                canvas.drawPath(path,stroke=0,fill=1,fillMode=1)
        canvas.restoreState()
        canvas.setStrokeColorCMYK(0,0,0,1)
        canvas.setLineWidth(0.25)
        for x in (offset,offset+width):
            for low,high in ((0.75,marks-0.75),(marks+2*bleed+height+0.75,page_height/MM_PT-0.75)):
                canvas.line(x*MM_PT,low*MM_PT,x*MM_PT,high*MM_PT)
        for y in (offset,offset+height):
            for low,high in ((0.75,marks-0.75),(marks+2*bleed+width+0.75,page_width/MM_PT-0.75)):
                canvas.line(low*MM_PT,y*MM_PT,high*MM_PT,y*MM_PT)
        canvas.showPage()
    canvas.save()


def factory_spec(scene):
    width,height = scene["size_mm"]
    bleed = scene.get("bleed_mm",0)
    return {
        "title":scene["title"], "trim_mm":[width,height],
        "bleed_mm":bleed, "bleed_box_mm":[width+bleed*2,height+bleed*2],
        "page_order":[face.get("name",face["id"]) for face in scene["faces"]],
        "safe_inset_mm":scene.get("safe_mm",4), "colors":scene["colors"],
        "font_mode":"outlined for PDF; SVG mode stated in manifest",
        "qr":[{"face":face["id"],"url":e["url"],"total_size_mm":e["size_mm"],"quiet_modules":e.get("quiet_modules",4),"ecc":"Q"}
              for face in scene["faces"] for e in face["elements"] if e["type"]=="qr"],
        "production_notes":["HEX is a digital reference; CMYK percentages are separate working recipes.",
                            "Printer must select the output ICC profile and verify a physical proof.",
                            "No Pantone match, PDF/X compliance, stock, finish or quantity is implied.",
                            "Scan the QR from the finished printed and coated sample before a full run."]
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("scene", type=Path)
    parser.add_argument("--out", type=Path, help="Output directory (required except --validate)")
    parser.add_argument("--validate", action="store_true", help="Validate data without writing output")
    parser.add_argument("--pdf", action="store_true", help="Write outlined DeviceCMYK artwork.pdf")
    parser.add_argument("--outline-svg", action="store_true", help="Outline glyphs in SVG and HTML preview")
    parser.add_argument("--bleed-svg", action="store_true", help="Include bleed in SVG/preview canvas")
    parser.add_argument("--overwrite", action="store_true", help="Explicitly replace generated files")
    args = parser.parse_args(argv)
    try:
        source = args.scene.expanduser().resolve(strict=True)
        if source.stat().st_size > 4_000_000:
            raise DesignError("Scene JSON exceeds the 4 MB limit")
        scene = json.loads(source.read_text(encoding="utf-8-sig"))
        warnings = validate_scene(scene)
        for warning in warnings:
            print(f"WARNING: {warning}",file=sys.stderr)
        if args.validate:
            print("Scene valid. Geometry anchors checked; visually inspect text bounds and scan exported QR.")
            return 0
        if args.out is None:
            parser.error("--out is required unless --validate is used")
        out = args.out.expanduser().resolve()
        names = ["preview.html","factory-spec.json","manifest.json"] + [face["id"]+".svg" for face in scene["faces"]]
        if args.pdf:
            names.append("artwork.pdf")
        if out == source.parent and source.name in names:
            raise DesignError("Output would overwrite the input scene")
        existing = [name for name in names if (out/name).exists()]
        if existing and not args.overwrite:
            raise DesignError("Output files already exist: " + ", ".join(existing) + "; choose another directory or --overwrite")
        if any((out/name).is_symlink() for name in names):
            raise DesignError("Refusing to replace a symlink output")
        outlines = Outlines(scene,source) if args.pdf or args.outline_svg else None
        svgs = [svg_face(scene,face,outlines if args.outline_svg else None,args.bleed_svg) for face in scene["faces"]]
        preview = html_preview(scene,svgs)
        # Generate everything in a sibling staging directory first. A font/PDF
        # failure must not leave half of a new design in the chosen output folder.
        out.parent.mkdir(parents=True,exist_ok=True)
        with tempfile.TemporaryDirectory(prefix=".design-stage-",dir=out.parent) as folder:
            staging = Path(folder)
            for face,svg in zip(scene["faces"],svgs):
                (staging/(face["id"]+".svg")).write_text(svg+"\n",encoding="utf-8")
            (staging/"preview.html").write_text(preview,encoding="utf-8")
            (staging/"factory-spec.json").write_text(json.dumps(factory_spec(scene),ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
            if args.pdf:
                export_pdf(scene,staging/"artwork.pdf",outlines)
            generated = {name:hashlib.sha256((staging/name).read_bytes()).hexdigest() for name in names if name!="manifest.json"}
            manifest = {"schema_version":1,"source_sha256":hashlib.sha256(source.read_bytes()).hexdigest(),
                        "generated_sha256":generated,"svg_text":"outlined" if args.outline_svg else "live-system-font",
                        "pdf_color":"DeviceCMYK; unprofiled working values" if args.pdf else None,
                        "warnings":warnings}
            (staging/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
            out.mkdir(parents=True,exist_ok=True)
            for name in names:
                if (out/name).is_symlink() or ((out/name).exists() and not args.overwrite):
                    raise DesignError(f"Output changed during generation; refusing to replace {name}")
                (staging/name).replace(out/name)
        print(json.dumps({"output":str(out),"files":names,"warnings":len(warnings)},ensure_ascii=False))
        return 0
    except (DesignError,OSError,json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}",file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
