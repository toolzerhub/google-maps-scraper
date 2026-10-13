"""Scrape public Google Maps places, place details and reviews with Python. No login, one file."""
import argparse
import csv
import json
import os
import re
import sys
import time
from datetime import datetime, timezone
from urllib.parse import quote, unquote, urlencode

from curl_cffi import requests

BASE = "https://www.google.com"
REVIEWS_URL = BASE + "/httpservice/web/PrivateLocalSearchUiDataService/GetLocalBoqProxy"
CID = re.compile(r"0x[0-9a-f]+:0x[0-9a-f]+", re.IGNORECASE)
PAGE = 20  # Google sends 20 places or 20 reviews per request, never more
MAX_OFFSET = 180  # place search is empty from offset 200 (about 182 distinct places)
SORT_NEWEST = 2  # the only review order that walks the whole list
# With no --lat/--lng the map view is the whole world, so the place named in the query
# decides the results. A local view would pull "Apple Fifth Avenue" towards Apple Stores nearby.
WORLD_SPAN = 20_000_000
AREA_SPAN = 20_000  # default view width (metres) when --lat and --lng are given

# Google Maps asks for places with a "pb" parameter: a protobuf packed into a URL.
# A wrong pb does not fail, it quietly returns thin results. So these two are copied
# whole from the Maps web app and the script only changes a few fields in them.
SEARCH_PB = (
    "!4m12!1m3!1d50461.32351171156!2d-122.43759495!3d37.7705182!2m3!1f0!2f0!3f0!3m2!1i1920!2i1080!4f13.1"
    "!7i20!8i20!10b1!12m56!1m5!18b1!30b1!31m1!1b1!34e1!2m4!5m1!6e2!20e3!39b1!6m29!32i1!49b1!63m0!66b1"
    "!85b1!114b1!149b1!206b1!209b1!212b1!215b1!216b1!222b1!223b1!232b1!234b1!235b1!246b1!253b1!260b1"
    "!266b1!270b1!273b1!280b1!281b1!286b1!291m0!302i300!303i100!10b1!12b1!13b1!14b1!16b1!17m1!3e1!20m3"
    "!5e2!6b1!14b1!46m1!1b0!96b1!99b1!19m4!2m3!1i360!2i120!4i8!20m65!2m2!1i203!2i100!3m2!2i4!5b1!6m6!1m2"
    "!1i86!2i86!1m2!1i408!2i240!7m33!1m3!1e1!2b0!3e3!1m3!1e2!2b1!3e2!1m3!1e2!2b0!3e3!1m3!1e8!2b0!3e3!1m3"
    "!1e10!2b0!3e3!1m3!1e10!2b1!3e2!1m3!1e10!2b0!3e4!1m3!1e9!2b1!3e2!2b1!9b0!15m16!1m7!1m2!1m1!1e2!2m2"
    "!1i195!2i195!3i20!1m7!1m2!1m1!1e2!2m2!1i195!2i195!3i20!22m5!1sIESBatiPLrSYptQP84nGsA8:58"
    "!2s1i:0,t:246204,p:IESBatiPLrSYptQP84nGsA8:58!7e81!12e22!17sIESBatiPLrSYptQP84nGsA8:59!24m107!1m25"
    "!13m9!2b1!3b1!4b1!6i1!8b1!9b1!14b1!20b1!25b1!18m14!3b1!4b1!5b1!6b1!13b1!14b1!17b1!21b1!22b1!32b1"
    "!33m1!1b1!34b1!36e2!10m1!8e3!11m1!3e1!17b1!20m2!1e3!1e6!24b1!25b1!26b1!27b1!29b1!30m1!2b1!36b1!37b1"
    "!39m3!2m2!2i1!3i1!43b1!52b1!54m1!1b1!55b1!56m1!1b1!61m2!1m1!1e1!65m5!3m4!1m3!1m2!1i224!2i298!72m22"
    "!1m8!2b1!5b1!7b1!12m4!1b1!2b1!4m1!1e1!4b1!8m10!1m6!4m1!1e1!4m1!1e3!4m1!1e4"
    "!3sother_user_google_review_posts__and__hotel_and_vr_partner_review_posts!6m1!1e1!9b1!89b1!90m2!1m1"
    "!1e2!98m3!1b1!2b1!3b1!103b1!113b1!114m3!1b1!2m1!1b1!117b1!122m1!1b1!126b1!127b1!128m1!1b1!26m4!2m3"
    "!1i80!2i92!4i8!30m28!1m6!1m2!1i0!2i0!2m2!1i530!2i1080!1m6!1m2!1i1870!2i0!2m2!1i1920!2i1080!1m6!1m2"
    "!1i0!2i0!2m2!1i1920!2i20!1m6!1m2!1i0!2i1060!2m2!1i1920!2i1080!34m19!2b1!3b1!4b1!6b1!8m6!1b1!3b1!4b1"
    "!5b1!6b1!7b1!9b1!12b1!14b1!20b1!23b1!25b1!26b1!31b1!37m1!1e81!42b1!46m1!1e9!47m0!49m10!3b1!6m2!1b1"
    "!2b1!7m2!1e3!2b1!8b1!9b1!10e2!50m261!1m257!2m7!1u3!4sOpen now!5e1"
    "!9s0ahUKEwjev9eOr6SWAxWvl4kEHXgAN3sQ_KkBCAgoAg!10m2!3m1!1e1!2m7!1u2!4sTop rated!5e1"
    "!9s0ahUKEwjev9eOr6SWAxWvl4kEHXgAN3sQ_KkBCAkoAw!10m2!2m1!1e1!2m7!1u1!4sCheap!5e1"
    "!9s0ahUKEwjev9eOr6SWAxWvl4kEHXgAN3sQ_KkBCAooBA!10m2!1m1!1e1!2m7!1u1!4sUpscale!5e1"
    "!9s0ahUKEwjev9eOr6SWAxWvl4kEHXgAN3sQ_KkBCAsoBQ!10m2!1m1!1e2!2m11!1u62!2e1!4s!5e3"
    "!9s0ahUKEwjev9eOr6SWAxWvl4kEHXgAN3sQ_KkBCAwoBg!10m5!64m4!2m3!1i1!2i10!3sUSD!2m11!1u62!2e1!4s!5e3"
    "!9s0ahUKEwjev9eOr6SWAxWvl4kEHXgAN3sQ_KkBCA0oBw!10m5!64m4!2m3!1i10!2i20!3sUSD!2m11!1u62!2e1!4s!5e3"
    "!9s0ahUKEwjev9eOr6SWAxWvl4kEHXgAN3sQ_KkBCA4oCA!10m5!64m4!2m3!1i20!2i30!3sUSD!2m11!1u62!2e1!4s!5e3"
    "!9s0ahUKEwjev9eOr6SWAxWvl4kEHXgAN3sQ_KkBCA8oCQ!10m5!64m4!2m3!1i30!2i40!3sUSD!2m11!1u62!2e1!4s!5e3"
    "!9s0ahUKEwjev9eOr6SWAxWvl4kEHXgAN3sQ_KkBCBAoCg!10m5!64m4!2m3!1i40!2i50!3sUSD!2m11!1u62!2e1!4s!5e3"
    "!9s0ahUKEwjev9eOr6SWAxWvl4kEHXgAN3sQ_KkBCBEoCw!10m5!64m4!2m3!1i50!2i60!3sUSD!2m11!1u62!2e1!4s!5e3"
    "!9s0ahUKEwjev9eOr6SWAxWvl4kEHXgAN3sQ_KkBCBIoDA!10m5!64m4!2m3!1i60!2i70!3sUSD!2m11!1u62!2e1!4s!5e3"
    "!9s0ahUKEwjev9eOr6SWAxWvl4kEHXgAN3sQ_KkBCBMoDQ!10m5!64m4!2m3!1i70!2i80!3sUSD!2m11!1u62!2e1!4s!5e3"
    "!9s0ahUKEwjev9eOr6SWAxWvl4kEHXgAN3sQ_KkBCBQoDg!10m5!64m4!2m3!1i80!2i90!3sUSD!2m11!1u62!2e1!4s!5e3"
    "!9s0ahUKEwjev9eOr6SWAxWvl4kEHXgAN3sQ_KkBCBUoDw!10m5!64m4!2m3!1i90!2i100!3sUSD!2m10!1u62!2e1!4s!5e3"
    "!9s0ahUKEwjev9eOr6SWAxWvl4kEHXgAN3sQ_KkBCBYoEA!10m4!64m3!2m2!1i100!3sUSD!3m88!1u62!2m7!1m5!64m4!2m3"
    "!1i1!2i10!3sUSD!2s!2m7!1m5!64m4!2m3!1i10!2i20!3sUSD!2s!2m7!1m5!64m4!2m3!1i20!2i30!3sUSD!2s!2m7!1m5"
    "!64m4!2m3!1i30!2i40!3sUSD!2s!2m7!1m5!64m4!2m3!1i40!2i50!3sUSD!2s!2m7!1m5!64m4!2m3!1i50!2i60!3sUSD!2s"
    "!2m7!1m5!64m4!2m3!1i60!2i70!3sUSD!2s!2m7!1m5!64m4!2m3!1i70!2i80!3sUSD!2s!2m7!1m5!64m4!2m3!1i80!2i90"
    "!3sUSD!2s!2m7!1m5!64m4!2m3!1i90!2i100!3sUSD!2s!2m6!1m4!64m3!2m2!1i100!3sUSD!2s!3m1!1u2!3m1!1u3!4BIAE"
    "!2e2!3m1!3b1!59BQ2dBd0Fn!61b1!67m5!7b1!10b1!14b1!15m1!1b0!69i790!77b1"
)

PLACE_PB = (
    "!1m24!1s0x808587fb77f5f64d:0x25d564f177f99946!3m12!1m3!1d70955.52414391714!2d-122.47782249999999"
    "!3d37.77647210000001!2m3!1f0!2f0!3f0!3m2!1i1032!2i1080!4f13.1!4m2!3d37.7764721!4d-122.47782249999999"
    "!15m6!1m5!1s0x808587fb77f5f64d:0x25d564f177f99946!4s/g/11sbx1rx9m!5sChIJTfb1d_uHhYARRpn5d_Fk1SU"
    "!6s13062388621852480980!7s111760009274306176011!6scoffee in San Francisco!12m4!2m3!1i360!2i120!4i8"
    "!13m57!2m2!1i203!2i100!3m2!2i4!5b1!6m6!1m2!1i86!2i86!1m2!1i408!2i240!7m33!1m3!1e1!2b0!3e3!1m3!1e2"
    "!2b1!3e2!1m3!1e2!2b0!3e3!1m3!1e8!2b0!3e3!1m3!1e10!2b0!3e3!1m3!1e10!2b1!3e2!1m3!1e10!2b0!3e4!1m3!1e9"
    "!2b1!3e2!2b1!9b0!15m8!1m7!1m2!1m1!1e2!2m2!1i195!2i195!3i20!14m2!1sPkSBata5KJ79ptQPv7bd0Q8!7e81"
    "!15m111!1m29!4e2!13m9!2b1!3b1!4b1!6i1!8b1!9b1!14b1!20b1!25b1!18m17!3b1!4b1!5b1!6b1!9b1!13b1!14b1"
    "!17b1!20b1!21b1!22b1!30b1!32b1!33m1!1b1!34b1!36e2!10m1!8e3!11m1!3e1!17b1!20m2!1e3!1e6!24b1!25b1!26b1"
    "!27b1!29b1!30m1!2b1!36b1!37b1!39m3!2m2!2i1!3i1!43b1!52b1!54m1!1b1!55b1!56m1!1b1!61m2!1m1!1e1!65m5"
    "!3m4!1m3!1m2!1i224!2i298!72m22!1m8!2b1!5b1!7b1!12m4!1b1!2b1!4m1!1e1!4b1!8m10!1m6!4m1!1e1!4m1!1e3!4m1"
    "!1e4!3sother_user_google_review_posts__and__hotel_and_vr_partner_review_posts!6m1!1e1!9b1!89b1!90m2"
    "!1m1!1e2!98m3!1b1!2b1!3b1!103b1!113b1!114m3!1b1!2m1!1b1!117b1!122m1!1b1!126b1!127b1!128m1!1b1!21m0"
    "!22m2!1e81!8e4!29m0!30m6!3b1!6m1!2b1!7m1!2b1!9b1!34m5!7b1!10b1!14b1!15m1!1b0!37i790"
    "!38sChdjb2ZmZWUgaW4gU2FuIEZyYW5jaXNjb1oZIhdjb2ZmZWUgaW4gc2FuIGZyYW5jaXNjb5IBC2NvZmZlZV9zaG9wmgEjQ2haRFNVaE5NRzluUzBWSlEwRm5TVU5xZFZwRWJreEJFQUXgAQD6AQQIKBA_"
    "!39sThe Coffee Movement!41b1"
)

class ScrapeError(Exception):
    pass


def at(node, *path):
    """Walk Google's unnamed arrays. A missing slot is None, not an error."""
    for i in path:
        if not isinstance(node, list) or len(node) <= i:
            return None
        node = node[i]
    return node


def text(node):
    return node if isinstance(node, str) and node else None


def iso_ms(ms):
    try:
        return datetime.fromtimestamp(int(ms) / 1000, timezone.utc).replace(microsecond=0).isoformat()
    except (TypeError, ValueError):
        return None


class Maps:
    def __init__(self, proxy=None):
        self.proxies = {"http": proxy, "https": proxy} if proxy else None

    def get(self, url):
        try:
            resp = requests.get(
                url, impersonate="chrome", proxies=self.proxies, timeout=30, allow_redirects=False,
                headers={"accept": "*/*", "accept-language": "en-US,en;q=0.9", "referer": BASE + "/"},
            )
        except requests.RequestsError as exc:
            raise ScrapeError(f"Network error: {exc}") from exc
        # Google sends blocked clients to /sorry/ with a 302 or a 429.
        if resp.status_code in (302, 403, 429) or "/sorry/" in resp.url or "unusual traffic" in resp.text[:5000]:
            raise ScrapeError(
                f"Google answered HTTP {resp.status_code}: this IP is rate-limited or blocked. "
                "Wait a while and ask for less, or try a home connection or --proxy (datacenter IPs get blocked first)."
            )
        if resp.status_code == 400:
            raise ScrapeError("Google rejected the request (HTTP 400). Its page format may have changed; please open an issue.")
        if resp.status_code != 200:
            raise ScrapeError(f"Unexpected HTTP {resp.status_code} from Google.")
        return resp

    def json(self, url):
        body = self.get(url).text
        if not body.startswith(")]}'"):
            raise ScrapeError("Google did not answer with data (no JSON). Try again, or use --proxy.")
        try:
            return json.loads(body[body.index("\n") + 1:])
        except ValueError as exc:
            raise ScrapeError("Google sent data this script cannot read. Please open an issue.") from exc

    # --- places ----------------------------------------------------------

    def search_page(self, query, offset, lat=0, lng=0, span=WORLD_SPAN):
        pb = SEARCH_PB
        # The first !1s in this pb is the search text slot (it holds Google's session id).
        pb = re.sub(r"!1s[^!]*", lambda _: "!1s" + query.replace("!", " "), pb, count=1)
        pb = re.sub(r"!8i\d+", f"!8i{offset}", pb, count=1)
        # The map view: centre (!2d longitude, !3d latitude) and width in metres (!1d).
        pb = re.sub(r"!2d-?[\d.]+", f"!2d{lng}", pb, count=1)
        pb = re.sub(r"!3d-?[\d.]+", f"!3d{lat}", pb, count=1)
        pb = re.sub(r"!1d[\d.]+", f"!1d{span}", pb, count=1)
        params = {"tbm": "map", "authuser": "0", "hl": "en", "gl": "us", "q": query, "pb": pb}
        doc = self.json(BASE + "/search?" + urlencode(params, quote_via=quote))
        rows = [at(r, 1) for r in at(doc, 64) or []]
        if not rows and offset == 0:
            # A query that names one famous place ("Louvre Museum Paris") gets that place alone.
            rows = [at(doc, 0, 1, 0, 14)]
        return [r for r in rows if isinstance(r, list) and (text(at(r, 10)) or text(at(r, 11)))]

    def search(self, query, limit, lat=0, lng=0, span=WORLD_SPAN):
        found, seen = [], set()
        for offset in range(0, MAX_OFFSET + 1, PAGE):
            fresh = 0
            for rec in self.search_page(query, offset, lat, lng, span):
                place = clean_place(rec)
                # Pages overlap by about 10%, so drop repeats.
                if place["cid"] not in seen:
                    seen.add(place["cid"])
                    found.append(place)
                    fresh += 1
            if not fresh or len(found) >= limit:
                break
            time.sleep(0.5)
        if len(found) < limit and offset >= MAX_OFFSET:
            print(f"Note: Google stopped at {len(found)} places for this search. "
                  "Use --lat, --lng and --span to search other parts of the map.", file=sys.stderr)
        return found[:limit]

    def place(self, cid):
        pb = PLACE_PB.replace(CID.search(PLACE_PB).group(0), cid)
        params = {"authuser": "0", "hl": "en", "gl": "us", "pb": pb}
        doc = self.json(BASE + "/maps/preview/place?" + urlencode(params, quote_via=quote))
        rec = at(doc, 6)
        # An unknown cid does not error: Google answers with the pb's own sample place.
        if not text(at(rec, 11)) or (text(at(rec, 10)) or "").lower() != cid.lower():
            raise ScrapeError(f"No place found for {cid}.")
        return clean_place(rec)

    def resolve(self, value):
        """Turn a Maps URL, a cid or a name into a cid."""
        value = value.strip()
        if re.match(r"https?://", value):
            m = CID.search(unquote(value))
            if m:
                return m.group(0).lower()
            # Long URLs without a cid still carry the place name: /maps/place/<name>/@lat,lng
            m = re.search(r"/maps/place/([^/@?]+)", value)
            if not m:
                raise ScrapeError(f"No place found in this URL: {value}")
            value = unquote(m.group(1)).replace("+", " ")
        m = CID.fullmatch(value)
        if m:
            return m.group(0).lower()
        hits = self.search_page(value, 0)
        if not hits:
            raise ScrapeError(f"No place found for '{value}'.")
        return text(at(hits[0], 10))

    # --- reviews ---------------------------------------------------------

    def reviews(self, cid, limit, authors=False):
        out, cursor = [], None
        while len(out) < limit:
            if cursor:
                inner = [None, SORT_NEWEST] + [None] * 9 + [[cid]] + [None] * 7 + [cursor]
            else:
                inner = [None, SORT_NEWEST] + [None] * 7 + [PAGE, None, [cid]]
            reqpld = quote(json.dumps([None, [None] * 9 + [inner]], separators=(",", ":")))
            url = f"{REVIEWS_URL}?msc=gwsrpc&hl=en&gl=us&reqpld={reqpld}"
            try:
                doc = self.json(url)
            except ScrapeError:
                # Google sometimes answers one page with nothing. A second try fixes it.
                time.sleep(2)
                doc = self.json(url)
            rows = at(doc, 1, 10, 2) or []
            out.extend(r for r in (clean_review(row, authors) for row in rows) if r)
            cursor = text(at(doc, 1, 10, 6))
            if not rows or not cursor:
                break
            time.sleep(0.5)
        if not out:
            raise ScrapeError(f"No reviews found for {cid}. The place may not exist or has no public reviews.")
        return out[:limit]


def clean_hours(days):
    """{'Monday': '9 AM-6 PM', ...} in week order. Google lists seven days, starting today."""
    hours = {}
    for day in days or []:
        name = text(at(day, 0))
        spans = [text(at(s, 0)) for s in at(day, 3) or []]
        if name:
            hours[name] = ", ".join(s for s in spans if s) or None
    order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    return {d: hours[d] for d in order if d in hours} or None


def clean_attributes(groups):
    """{'Accessibility': ['Wheelchair accessible entrance', ...], ...}"""
    out = {}
    for group in at(groups, 1) or []:
        names = [text(at(f, 1)) for f in at(group, 2) or []]
        if text(at(group, 1)) and any(names):
            out[group[1]] = [n for n in names if n]
    return out or None


def clean_place(rec):
    """One business from Google's 260-slot array. Search results and place pages share this shape."""
    place_id = text(at(rec, 78))
    count = at(rec, 4, 8)
    return {
        "cid": text(at(rec, 10)),
        "place_id": place_id,
        "name": text(at(rec, 11)),
        "categories": [c for c in at(rec, 13) or [] if isinstance(c, str)],
        "address": text(at(rec, 39)) or text(at(rec, 18)),
        "latitude": at(rec, 9, 2),
        "longitude": at(rec, 9, 3),
        "phone": text(at(rec, 178, 0, 0)),
        "website": text(at(rec, 7, 0)),
        "rating": at(rec, 4, 7),
        "review_count": count if isinstance(count, int) else None,
        "open_status": text(at(rec, 203, 1, 4, 0)),
        "hours": clean_hours(at(rec, 203, 0)),
        "timezone": text(at(rec, 30)),
        "description": text(at(rec, 32, 0, 1)),
        "attributes": clean_attributes(at(rec, 100)),
        "country_code": text(at(rec, 243)),
        "maps_url": f"https://www.google.com/maps/place/?q=place_id:{place_id}" if place_id else None,
    }


def clean_review(row, authors):
    review_id = text(at(row, 5))
    if not review_id:
        return None
    relative = text(at(row, 2, 0))
    review = {
        "review_id": review_id,
        "rating": at(row, 1),
        "text": (text(at(row, 27)) or "").replace("<br>", "\n") or None,  # Google sends line breaks as <br>
        "language": text(at(row, 26)),
        # One timestamp per review. If the reviewer edited it, this is the edit time.
        "posted_at": iso_ms(at(row, 2, 2)),
        "edited": bool(relative) and relative.lower().startswith("edited"),
        "relative_time": relative,
        "photos": [u for u in (text(at(p, 0)) for p in at(row, 14) or []) if u],
        "owner_response": text(at(row, 4, 2)),
        "owner_response_time": text(at(row, 4, 1)),
    }
    if authors:
        review["author_name"] = text(at(row, 3, 0))
        review["author_url"] = text(at(row, 3, 2))
    return review


def write_csv(path, data):
    rows = data if isinstance(data, list) else [data]
    # Lists and objects go into one cell as text, so every row has the same columns.
    flat = [{k: ("; ".join(map(str, v)) if isinstance(v, list) else json.dumps(v, ensure_ascii=False) if isinstance(v, dict) else v)
             for k, v in row.items()} for row in rows]
    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(flat[0]) if flat else [])
        writer.writeheader()
        writer.writerows(flat)


def main():
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--proxy", default=os.environ.get("HTTPS_PROXY"), help="proxy URL, e.g. http://user:pass@host:port")
    common.add_argument("-o", "--output", help="write the result to this file (JSON, or CSV if it ends in .csv)")
    parser = argparse.ArgumentParser(description="Scrape public Google Maps data. No login.")
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("search", parents=[common], help="places for a search such as 'coffee shops in Seattle'")
    p.add_argument("query")
    p.add_argument("--limit", type=int, default=20, help="how many places, up to about 180 (default 20)")
    p.add_argument("--lat", type=float, help="latitude of the map centre")
    p.add_argument("--lng", type=float, help="longitude of the map centre")
    p.add_argument("--span", type=float, help=f"width of the map view in metres (default {AREA_SPAN}), e.g. 2000 for a neighbourhood")
    p = sub.add_parser("place", parents=[common], help="details for one place")
    p.add_argument("place", nargs="+", help="place name, Google Maps URL or cid")
    p = sub.add_parser("reviews", parents=[common], help="public reviews of a place, newest first")
    p.add_argument("place", help="place name, Google Maps URL or cid")
    p.add_argument("--limit", type=int, default=20, help="how many reviews (default 20)")
    p.add_argument("--authors", action="store_true", help="include reviewer names and profile links")
    args = parser.parse_args()

    maps = Maps(args.proxy)
    try:
        if args.command == "search":
            if (args.lat is None) != (args.lng is None) or (args.span and args.lat is None):
                parser.error("--lat and --lng go together, and --span needs both")
            if args.lat is None:
                data = maps.search(args.query, args.limit)
            else:
                data = maps.search(args.query, args.limit, args.lat, args.lng, args.span or AREA_SPAN)
        elif args.command == "place":
            data = [maps.place(maps.resolve(p)) for p in args.place]
        else:
            data = maps.reviews(maps.resolve(args.place), args.limit, args.authors)
    except ScrapeError as exc:
        sys.exit(f"Error: {exc}")

    if args.command == "place" and len(data) == 1:
        data = data[0]
    if args.output and args.output.lower().endswith(".csv"):
        write_csv(args.output, data)
        print(f"Saved to {args.output}")
    elif args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
        print(f"Saved to {args.output}")
    else:
        print(json.dumps(data, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
