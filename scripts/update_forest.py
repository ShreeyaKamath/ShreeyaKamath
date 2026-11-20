#!/usr/bin/env python3
"""Generate reproducible living-forest SVG foliage from GitHub contributions."""
import json, os, pathlib, random, re, urllib.request, math
p=pathlib.Path("assets/living-forest.svg")
token=os.environ.get("GITHUB_TOKEN")
if not token: raise SystemExit("GITHUB_TOKEN not set")
query='query { user(login:"ShreeyaKamath") { contributionsCollection { contributionCalendar { totalContributions weeks { contributionDays { contributionCount date } } } } } }'
request=urllib.request.Request("https://api.github.com/graphql",data=json.dumps({"query":query}).encode(),headers={"Authorization":"Bearer "+token,"Content-Type":"application/json","User-Agent":"living-forest-profile"},method="POST")
with urllib.request.urlopen(request,timeout=30) as r: result=json.load(r)
if result.get("errors"): raise SystemExit(str(result["errors"]))
calendar=result["data"]["user"]["contributionsCollection"]["contributionCalendar"]
total=calendar["totalContributions"]
days=[d for w in calendar["weeks"] for d in w["contributionDays"]][-30:]
random.seed(2026)
leaves=[];flies=[]
palette=["#b4dbb1","#e9b8cc","#d0b5ef","#f5d99b","#b9e8db"]
for day_index,day in enumerate(days):
    count=int(day["contributionCount"])
    for j in range(min(7,count)):
        angle=random.random()*math.tau
        radius=math.sqrt(random.random())
        x=12+radius*155*math.cos(angle)
        y=-235+radius*100*math.sin(angle)
        color=palette[min(4,count//3)]
        delay=(day_index+j)%9
        leaves.append(f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="{5+min(count,9)}" ry="{3+min(count,6)}" fill="{color}" opacity=".9" transform="rotate({random.randrange(0,180)} {x:.1f} {y:.1f})"><animate attributeName="opacity" values=".55;1;.55" dur="{3+delay}s" repeatCount="indefinite"/></ellipse>')
recent=sum(int(d["contributionCount"]) for d in days[-7:])
for i in range(min(40,recent)):
    x=random.randint(570,1130);y=random.randint(160,380);duration=3+random.random()*5
    flies.append(f'<circle cx="{x}" cy="{y}" r="{2+random.random()*2:.1f}" fill="#ffe9a0"><animate attributeName="opacity" values=".15;1;.15" dur="{duration:.1f}s" repeatCount="indefinite"/><animateTransform attributeName="transform" type="translate" values="0 0;{random.randrange(-20,21)} -14;0 0" dur="{duration*2:.1f}s" repeatCount="indefinite"/></circle>')
if not leaves: leaves=['<ellipse cx="12" cy="-235" rx="7" ry="4" fill="#c9b6ed"/>']
if not flies: flies=['<circle cx="730" cy="250" r="2" fill="#ffe9a0" opacity=".5"/>']
s=p.read_text()
s=re.sub(r'<!-- GROWTH_START -->.*?<!-- GROWTH_END -->','<!-- GROWTH_START -->'+''.join(leaves)+'<!-- GROWTH_END -->',s,flags=re.S)
s=re.sub(r'<!-- FIREFLIES_START -->.*?<!-- FIREFLIES_END -->','<!-- FIREFLIES_START -->'+''.join(flies)+'<!-- FIREFLIES_END -->',s,flags=re.S)
s=re.sub(r'(<text id="forest-count"[^>]*>).*?(</text>)',lambda m:m.group(1)+f'{total:,} yearly contributions · {recent} in the last 7 days'+m.group(2),s)
p.write_text(s)
print("Updated living forest:",total,"contributions;",len(leaves),"flowers;",len(flies),"fireflies")
