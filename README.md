# Google Maps Scraper (Python)

[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/)
[![Last verified](https://img.shields.io/badge/last%20verified-2026--10--13-brightgreen.svg)](#how-we-keep-it-working)

Scrape public Google Maps places, place details and reviews with Python. No login, no API key, one file.

> **Need this at scale?** The script is for learning and small jobs. The [ToolzerHub Google Maps API](https://toolzerhub.com/apis/google-maps?utm_source=github&utm_medium=readme&utm_campaign=google-maps-scraper) returns place search, place details and full review lists, plus a photo for each place, as JSON from any server, with no blocks to handle. 100 free credits a month, no card needed.

## What it scrapes

| Command | What you get |
|---|---|
| `search <query>` | Businesses for a search such as "coffee shops in Seattle": name, address, phone, website, rating, review count, weekly hours, coordinates and category. Up to about 180 per search. Save as JSON or as a CSV leads list |
| `place <name, URL or cid>...` | One place with the same fields, plus description and amenities. Takes a place name, a Google Maps URL or a cid |
| `reviews <name, URL or cid>` | Public reviews of a place, newest first: rating, text, date, language, review photos and the owner's reply |

## Quick start

```bash
git clone https://github.com/toolzerhub/google-maps-scraper.git
cd google-maps-scraper
pip install -r requirements.txt
python google_maps_scraper.py search "coffee shops in Seattle" --limit 20
```

More examples:

```bash
python google_maps_scraper.py search "dentists in Chicago" --limit 100 -o dentists.csv
python google_maps_scraper.py search "bookstores" --lat 47.6062 --lng -122.3321 --span 3000 -o books.json
python google_maps_scraper.py place "Louvre Museum Paris" -o louvre.json
python google_maps_scraper.py place "Times Square New York" "Space Needle Seattle"
python google_maps_scraper.py reviews "Apple Fifth Avenue New York" --limit 100 -o reviews.json
python google_maps_scraper.py reviews 0x47e671d877937b0f:0xb975fcfa192f84d4 --limit 40
```

Every command takes `-o file` to save the result and `--proxy URL` to route through a proxy. The script also reads `HTTPS_PROXY`. A file name ending in `.csv` saves a CSV instead of JSON. Put the place in the query ("coffee shops in Seattle"), or give a map centre with `--lat`, `--lng` and `--span` (view width in metres, default 20000). A `place` or `reviews` input can be a name, a Google Maps URL or a cid (`0x...:0x...`, the `cid` field in every result). A name uses the top search hit, so pass the cid when you need an exact place. Reviews hide reviewer names unless you add `--authors`.

## Example output

`python google_maps_scraper.py search "coffee shops in Seattle" --limit 5` (two places shown)

```json
[
  {
    "cid": "0x54906ab2f0c61d05:0x771b2a7dce963d58",
    "place_id": "ChIJBR3G8LJqkFQRWD2Wzn0qG3c",
    "name": "Storyville Coffee Pike Place",
    "categories": [
      "Coffee shop",
      "Bakery",
      "Cafe",
      "Coffee roastery",
      "Coffee store",
      "Espresso bar"
    ],
    "address": "94 Pike St Top floor Suite 34, Seattle, WA 98101",
    "latitude": 47.60895,
    "longitude": -122.3404309,
    "phone": "(206) 780-5777",
    "website": "https://storyville.com/pages/pike-place-market",
    "rating": 4.6,
    "review_count": 3229,
    "open_status": "Open · Closes 5 PM",
    "hours": {
      "Monday": "6:59 AM–5 PM",
      "Tuesday": "6:59 AM–5 PM",
      "Wednesday": "6:59 AM–5 PM",
      "Thursday": "6:59 AM–5 PM",
      "Friday": "6:59 AM–6 PM",
      "Saturday": "6:59 AM–6 PM",
      "Sunday": "6:59 AM–6 PM"
    },
    "timezone": "America/Los_Angeles",
    "description": "High-style, modern craft coffee cafe",
    "attributes": {
      "Accessibility": [
        "Wheelchair accessible entrance",
        "Wheelchair accessible restroom",
        "Wheelchair accessible parking lot"
      ]
    },
    "country_code": "US",
    "maps_url": "https://www.google.com/maps/place/?q=place_id:ChIJBR3G8LJqkFQRWD2Wzn0qG3c"
  },
  {
    "cid": "0x54906b88c68b6ae9:0x675e801f4206257f",
    "place_id": "ChIJ6WqLxohrkFQRfyUGQh-AXmc",
    "name": "Overcast Coffee",
    "categories": [
      "Coffee shop",
      "Bar",
      "Coffee stand",
      "Coffee store",
      "Pastry shop"
    ],
    "address": "1517 12th Ave Ste 100, Seattle, WA 98122",
    "latitude": 47.6146106,
    "longitude": -122.3171338,
    "phone": "(206) 588-2621",
    "website": "http://www.overcastcoffee.co/",
    "rating": 4.7,
    "review_count": 315,
    "open_status": "Open · Closes 6 PM",
    "hours": {
      "Monday": "7 AM–6 PM",
      "Tuesday": "7 AM–6 PM",
      "Wednesday": "7 AM–6 PM",
      "Thursday": "7 AM–6 PM",
      "Friday": "7 AM–6 PM",
      "Saturday": "8 AM–5 PM",
      "Sunday": "8 AM–5 PM"
    },
    "timezone": "America/Los_Angeles",
    "description": null,
    "attributes": {
      "Accessibility": [
        "Wheelchair accessible entrance",
        "Wheelchair accessible parking lot"
      ]
    },
    "country_code": "US",
    "maps_url": "https://www.google.com/maps/place/?q=place_id:ChIJ6WqLxohrkFQRfyUGQh-AXmc"
  }
]
```

`python google_maps_scraper.py place "Louvre Museum Paris"` (amenities shortened)

```json
{
  "cid": "0x47e671d877937b0f:0xb975fcfa192f84d4",
  "place_id": "ChIJD3uTd9hx5kcR1IQvGfr8dbk",
  "name": "Louvre Museum",
  "categories": [
    "Art museum",
    "Museum",
    "Tourist attraction"
  ],
  "address": "75001 Paris, France",
  "latitude": 48.8606111,
  "longitude": 2.337644,
  "phone": "+33 1 40 20 53 17",
  "website": "https://www.louvre.fr/",
  "rating": 4.7,
  "review_count": 379973,
  "open_status": "Closed · Opens 9 AM Wed",
  "hours": {
    "Monday": "9 AM–6 PM",
    "Tuesday": "Closed",
    "Wednesday": "9 AM–9 PM",
    "Thursday": "9 AM–6 PM",
    "Friday": "9 AM–9 PM",
    "Saturday": "9 AM–6 PM",
    "Sunday": "9 AM–6 PM"
  },
  "timezone": "Europe/Paris",
  "description": "Landmark art museum with vast collection",
  "attributes": {
    "Accessibility": [
      "Assisted listening devices",
      "Assistive hearing loop",
      "Wheelchair accessible entrance"
    ]
  },
  "country_code": "FR",
  "maps_url": "https://www.google.com/maps/place/?q=place_id:ChIJD3uTd9hx5kcR1IQvGfr8dbk"
}
```

`python google_maps_scraper.py reviews "Tartine Bakery San Francisco" --limit 2`

```json
[
  {
    "review_id": "Ci9DQUlRQUNvZENodHljRjlvT2s1SldXVTNibXMyYTNKamEwcDNkSGxzYkVOc1RGRRAB",
    "rating": 5,
    "text": "Best chocolate cake I have ever had! I got the morning bun latte it was delicious! Can not recommend more!",
    "language": "en",
    "posted_at": "2026-10-11T18:22:51+00:00",
    "edited": false,
    "relative_time": "2 days ago",
    "photos": [],
    "owner_response": "We're tickled pink to hear that you loved our chocolate cake and morning bun latte! It's heartening to know that our flavors made a mark. We can't wait to serve up more delicious treats for you at Tartine. Thank you!",
    "owner_response_time": "a day ago"
  },
  {
    "review_id": "Ci9DQUlRQUNvZENodHljRjlvT2tSUFNuTnRVMlJ5WkdoTlRISklWazU0YlZKRFpWRRAB",
    "rating": 5,
    "text": null,
    "language": null,
    "posted_at": "2026-10-10T22:43:46+00:00",
    "edited": false,
    "relative_time": "2 days ago",
    "photos": [],
    "owner_response": "Hi, we're stoked to see your 5-star rating! At Tartine, we aim to create memorable meals with our fresh ingredients. Can't wait to serve you those standout flavors again soon!",
    "owner_response_time": "2 days ago"
  }
]
```

Full outputs for every command are in [examples/](examples).

## Fields

### search and place

| Field | Description |
|---|---|
| cid | Google's id for the place (`0x...:0x...`). Use it to join results and to remove repeats. Takes `place` and `reviews` directly |
| place_id | The `ChIJ...` id used by Google's Places products |
| name, categories | Business name and its category list |
| address | Address as Maps shows it |
| latitude, longitude | Coordinates as numbers |
| phone, website | Phone as Maps shows it, and the website. Null when the place lists none |
| rating | Average stars, for example 4.7 |
| review_count | Number of reviews as an integer. It matches the number of reviews `reviews` returns for a place (317 of 317 on one café we walked) |
| open_status | Maps' own sentence for right now, such as "Open · Closes 5 PM" |
| hours | Opening hours for each weekday, or null when the place lists none (hotels, parks) |
| timezone | IANA timezone of the place |
| description | Short description, when Maps has one |
| attributes | Amenity groups such as Accessibility, as lists of names |
| country_code | Two-letter country code |
| maps_url | Link that opens the place on Google Maps |

### reviews

| Field | Description |
|---|---|
| review_id | Google's id for the review |
| rating | Stars, 1 to 5 |
| text | Review text, or null for a star-only rating (28% to 75% of reviews on the places we checked) |
| language | Language code of the text, or null |
| posted_at | ISO 8601 UTC. For an edited review this is the edit time |
| edited | True when the reviewer edited it |
| relative_time | Maps' own wording, such as "2 days ago" |
| photos | Links to photos added to the review |
| owner_response, owner_response_time | The business reply and its relative time, or null |
| author_name, author_url | Only with `--authors` |

## How it works

1. `search` and `place` ask for the same two addresses the Maps web page uses: `google.com/search?tbm=map` and `google.com/maps/preview/place`. The requests look like Chrome (`curl_cffi` copies its network fingerprint). Their `pb` parameter is a long packed string. The script holds a copy and changes only the query, the result offset and the map view.
2. Google answers with JSON made of unnamed arrays. Each business is one array of about 260 slots, and a search result and a place page use the same one, so a search already gives you phone, hours and rating. A query that names one famous place ("Louvre Museum Paris") comes back as that single place.
3. `reviews` asks the address Maps uses to load reviews, 20 per page, newest first, and follows the cursor Google returns until it has enough.
4. Each record is cleaned into the fields above. Counts become integers, times become ISO 8601 UTC and repeats across pages are dropped. Raw arrays are never returned.

A longer walkthrough with timed runs, a city-grid example and datacenter vs residential results: [How to scrape Google Maps with Python](https://toolzerhub.com/blog/how-to-scrape-google-maps?utm_source=github&utm_medium=readme&utm_campaign=google-maps-scraper).

## Limits

- Public data only.
- Search stops at about 180 places per query and map view, and Google decides how many it has for a query (a search for museums in London gave 20). To cover a big city, run the search again with `--lat`, `--lng` and a small `--span` for each neighbourhood.
- Reviews come newest first, 20 per request, with no sort or filter. Other orders return only part of the list. There are no like counts or reviewer details beyond the name and link.
- Not included: business photos, popular times, menus, prices, questions and answers, and a place's own posts. The language is fixed to English (US).
- Google rate-limits an IP that asks for a lot. It worked from a datacenter IP and from residential IPs at the volumes we tried (a few hundred requests in total), with no proxy needed. If you are blocked, the script exits with "this IP is rate-limited or blocked". Wait, ask for less, run it from a home connection, or pass `--proxy` (a sticky residential proxy works best).
- No concurrency. The script waits half a second between pages and retries a failed review page once. That is all, so it stays short enough to read in one sitting.
- It breaks when Google changes the Maps pages. A stale copy of the `pb` parameter shows up as empty or thin results, or as an HTTP 400 error. See "How we keep it working".

## Scaling up

The script is for learning and small jobs. At scale you run into blocks, changing page formats and proxy costs. The [ToolzerHub Google Maps API](https://toolzerhub.com/apis/google-maps?utm_source=github&utm_medium=readme&utm_campaign=google-maps-scraper) handles all of that:

| | This script | ToolzerHub API |
|---|---|---|
| Data | Place search, place details and reviews | 3 Google Maps endpoints (search, place details, reviews), with a photo for each place |
| Blocks and proxies | Your problem | Handled |
| When Google changes | Wait for a fix here | Fixed on our side |
| Cost | Free, plus your proxy | 100 free credits a month, then from $0.99 per 1,000 calls |

## How we keep it working

Every command is run against live Google Maps pages before each update, and the "last verified" badge shows the last day they all passed. If something breaks, [open an issue](https://github.com/toolzerhub/google-maps-scraper/issues).

## FAQ

**Is scraping Google Maps legal?**
Scraping publicly available data is generally allowed in many places, but it depends on your country, what you collect and how you use it. Read the Legal section below.

**Why am I getting blocked?**
Google blocks IP addresses that ask for a lot, datacenter IPs first. Use a home connection or a residential proxy, and slow down.

**Can it get a photo of each business?**
No. The [ToolzerHub API](https://toolzerhub.com/apis/google-maps?utm_source=github&utm_medium=readme&utm_campaign=google-maps-scraper) returns one per place.

**How do I get more than 180 places?**
Search each part of the city on its own with `--lat`, `--lng` and `--span`, then join the files and drop repeats by `cid`.

## Related scrapers

- [instagram-scraper](https://github.com/toolzerhub/instagram-scraper): public Instagram profiles, posts, comments and search
- [tiktok-scraper](https://github.com/toolzerhub/tiktok-scraper): public TikTok profiles, videos, comments and hashtags
- [threads-scraper](https://github.com/toolzerhub/threads-scraper): public Threads profiles, posts, replies and search
- [reddit-scraper](https://github.com/toolzerhub/reddit-scraper): public subreddits, posts, comments, search and user posts
- [linkedin-scraper](https://github.com/toolzerhub/linkedin-scraper): public LinkedIn jobs, companies, profiles and posts
- [facebook-ad-library-scraper](https://github.com/toolzerhub/facebook-ad-library-scraper): public Meta Ad Library ads by keyword or advertiser, with their videos and images
- [zillow-scraper](https://github.com/toolzerhub/zillow-scraper): public Zillow listings, property details, Zestimates and price history

## Legal and responsible use

This project is for education and for collecting **publicly available** data. You are responsible for how you use it.

- **Public data only.** The script reads pages anyone can see without an account. Do not use it to get around logins, paywalls, CAPTCHAs or other access controls.
- **Terms and robots rules.** Google's terms of service may restrict automated access. Read them and decide for yourself; following them is your responsibility.
- **Personal data.** Reviews and business listings can contain personal data. Laws such as the GDPR (EU and UK) and the CCPA (California) may apply. Collect only what you need, have a lawful basis, keep it secure, delete it when you no longer need it, and respect people's requests to access or erase their data.
- **Copyright.** Reviews, photos and descriptions belong to their creators. Do not republish them without permission.
- **Be gentle.** Keep request rates low and do not disrupt the service.
- **No warranty.** The software is provided "as is" under the MIT License, without warranty of any kind. The authors are not liable for any claim or damage arising from its use.
- **Not affiliated.** This project is not affiliated with, endorsed by or sponsored by Google LLC. Google and Google Maps are trademarks of Google LLC.
- **Takedown requests.** If you own rights in something here and want it changed or removed, email contact@toolzerhub.com.

This section is not legal advice. If you are unsure, talk to a lawyer.

## License

[MIT](LICENSE) © ToolzerHub
