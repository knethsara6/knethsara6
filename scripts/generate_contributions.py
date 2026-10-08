import os
import json
import urllib.request
from datetime import datetime
from PIL import Image, ImageDraw

USERNAME = "knethsara6"
OUTPUT = "contributions.gif"

query = """
query($login: String!) {
  user(login: $login) {
    contributionsCollection {
      contributionCalendar {
        weeks {
          contributionDays {
            date
            contributionCount
          }
        }
      }
    }
  }
}
"""

data = json.dumps({
    "query": query,
    "variables": {"login": USERNAME}
}).encode("utf-8")

request = urllib.request.Request(
    "https://api.github.com/graphql",
    data=data,
    headers={
        "Authorization": f"Bearer {os.environ['GITHUB_TOKEN']}",
        "Content-Type": "application/json"
    }
)

with urllib.request.urlopen(request) as response:
    result = json.loads(response.read().decode("utf-8"))

weeks = result["data"]["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]

levels = []

for week in weeks:
    levels.append([
        day["contributionCount"]
        for day in week["contributionDays"]
    ])

max_count = max(
    count
    for week in levels
    for count in week
)

def get_level(count):
    if count == 0:
        return 0
    if max_count == 0:
        return 0

    ratio = count / max_count

    if ratio <= 0.25:
        return 1
    elif ratio <= 0.5:
        return 2
    elif ratio <= 0.75:
        return 3
    else:
        return 4


CELL = 12
GAP = 3
STEP = CELL + GAP

WIDTH = len(levels) * STEP + 20
HEIGHT = 7 * STEP + 20

background = (13, 17, 23)

colors = [
    (22, 27, 34),
    (14, 68, 41),
    (0, 109, 65),
    (38, 166, 65),
    (57, 211, 83)
]

frames = []

for frame in range(8):
    image = Image.new("RGB", (WIDTH, HEIGHT), background)
    draw = ImageDraw.Draw(image)

    for x, week in enumerate(levels):
        for y, count in enumerate(week):
            level = get_level(count)

            # Animate squares from left to right
            visible = (x * 7 + y) <= frame * 45

            if not visible:
                level = 0

            px = 10 + x * STEP
            py = 10 + y * STEP

            draw.rounded_rectangle(
                [px, py, px + CELL, py + CELL],
                radius=2,
                fill=colors[level]
            )

    frames.append(image)

frames[0].save(
    OUTPUT,
    save_all=True,
    append_images=frames[1:],
    duration=180,
    loop=0
)

print(f"Created {OUTPUT}")
