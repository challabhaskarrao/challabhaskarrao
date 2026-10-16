import json
import os
import re
import urllib.request
from datetime import datetime, timezone

USER = "challabhaskarrao"
TOKEN = os.environ["GH_TOKEN"]


def graphql(query):
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": query}).encode(),
        headers={"Authorization": "bearer " + TOKEN},
    )
    with urllib.request.urlopen(req) as res:
        return json.load(res)["data"]["user"]


created = graphql('{ user(login: "%s") { createdAt } }' % USER)["createdAt"]
start_year = int(created[:4])
end_year = datetime.now(timezone.utc).year

total = 0
for year in range(start_year, end_year + 1):
    query = """
    { user(login: "%s") {
        contributionsCollection(from: "%d-01-01T00:00:00Z", to: "%d-12-31T23:59:59Z") {
          totalCommitContributions
        }
    } }
    """ % (USER, year, year)
    total += graphql(query)["contributionsCollection"]["totalCommitContributions"]

with open("README.md", "r", encoding="utf-8") as f:
    readme = f.read()

new_block = "<!--COMMITS_START-->%s<!--COMMITS_END-->" % format(total, ",")
readme = re.sub(r"<!--COMMITS_START-->.*?<!--COMMITS_END-->", new_block, readme, flags=re.S)

with open("README.md", "w", encoding="utf-8") as f:
    f.write(readme)

print("Total commits:", total)
