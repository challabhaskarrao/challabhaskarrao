import json
import os
import re
import urllib.request

TOKEN = os.environ["GH_TOKEN"]


def graphql(query):
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": query}).encode(),
        headers={"Authorization": "bearer " + TOKEN},
    )
    with urllib.request.urlopen(req) as res:
        return json.load(res)["data"]["viewer"]


user_id = graphql("{ viewer { id } }")["id"]

total = 0
cursor = "null"
while True:
    query = """
    { viewer {
        repositories(first: 50, after: %s, isFork: false,
                     ownerAffiliations: [OWNER, COLLABORATOR, ORGANIZATION_MEMBER]) {
          nodes {
            defaultBranchRef {
              target {
                ... on Commit { history(author: {id: "%s"}) { totalCount } }
              }
            }
          }
          pageInfo { hasNextPage endCursor }
        }
    } }
    """ % (cursor, user_id)
    repos = graphql(query)["repositories"]
    for repo in repos["nodes"]:
        branch = repo["defaultBranchRef"]
        if branch and branch["target"]:
            total += branch["target"]["history"]["totalCount"]
    if not repos["pageInfo"]["hasNextPage"]:
        break
    cursor = '"%s"' % repos["pageInfo"]["endCursor"]

with open("README.md", "r", encoding="utf-8") as f:
    readme = f.read()

new_block = "<!--COMMITS_START-->%s<!--COMMITS_END-->" % format(total, ",")
readme = re.sub(r"<!--COMMITS_START-->.*?<!--COMMITS_END-->", new_block, readme, flags=re.S)

with open("README.md", "w", encoding="utf-8") as f:
    f.write(readme)

print("Total commits:", total)
