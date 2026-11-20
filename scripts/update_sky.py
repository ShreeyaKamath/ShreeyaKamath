#!/usr/bin/env python3
"""Refresh the SVG star field from GitHub's contribution calendar."""
import json, os, pathlib, random, re, urllib.request
p=pathlib.Path("assets/living-sky.svg")
token=os.environ.get("GITHUB_TOKEN")
if not token:
    raise SystemExit("GITHUB_TOKEN missing; keeping existing banner unchanged")
query='query { user(login:"ShreeyaKamath") { contributionsCollection { contributionCalendar { totalContributions weeks { contributionDays { contributionCount date } } } } } }'
req=urllib.request.Request("https://api.github.com/graphql",data=json.dumps({"query":query}).encode(),headers={"Authorization":"Bearer "+token,"Content-Type":"application/json","User-Agent":"living-sky-github-profile"},method="POST")
with urllib.request.urlopen(req,timeout=25) as res:
    result=json.load(res)
if result.get("errors"):
    raise SystemExit("GitHub GraphQL returned errors: "+str(result["errors"]))
calendar=result["data"]["user"]["contributionsCollection"]["contributionCalendar"]
total=int(calendar["totalContributions"])
days=[d for w in calendar["weeks"] for d in w["contributionDays"]][-28:]
random.seed("shreeya-living-sky")
stars=[]
for i,d in enumerate(days):
    n=min(6,int(d["contributionCount"]))
    for j in range(n):
        x=575+(i%14)*29+random.randint(-8,8)
        y=37+(i//14)*82+j*11+random.randint(-5,5)
        radius=1.2+min(n,5)*.28
        dur=2.5+random.random()*4
        stars.append(f'<circle cx="{x}" cy="{y}" r="{radius:.1f}" fill="#fff7ee" opacity=".85"><animate attributeName="opacity" values=".25;1;.25" dur="{dur:.1f}s" repeatCount="indefinite"/></circle>')
if not stars:
    stars=['<circle cx="695" cy="100" r="2" fill="#fff7ee" opacity=".5"/>']
s=p.read_text()
s=re.sub(r'<!-- ACTIVITY_STARS_START -->.*?<!-- ACTIVITY_STARS_END -->','<!-- ACTIVITY_STARS_START -->'+''.join(stars)+'<!-- ACTIVITY_STARS_END -->',s,flags=re.S)
s=re.sub(r'(<text id="contrib-count"[^>]*>).*?(</text>)',lambda m:m.group(1)+f'{total:,} contributions · refreshed automatically'+m.group(2),s)
p.write_text(s)
print("Updated sky using public contribution-calendar data:",total)
