

import os
print(os.getcwd())
os.chdir(r"C:\Users\name\xxxxxxxxxx")

import pandas as pd # type: ignore
act = pd.read_csv("activities_example.txt", sep=",")
resp = pd.read_csv("responses_example.txt", sep=",")
main = resp.merge(act, on="name")



def to_list(value):
    if pd.isna(value) or value is None or value == "":
        return []
    return value.split("|")

documents = []

for activity_id, group in main.groupby("activity_id"):
    row = group.iloc[0]
    doc = {
        "activity_id": row['activity_id'],
        "name": row['name'],
        "category": to_list(row.get('category', None)),
        "intensities": to_list(row.get('intensities', None)),
        "environment": [
            {"type": row.get('environment_type', ""),
             "sub_environments": to_list(row.get('environment_subs', None))
            }
        ],
        "survey_responses": [
            {"user_id": r['user_id'], "frequency": r['frequency']} 
            for _, r in group.iterrows()
        ]
    }
    documents.append(doc)


import json
with open("activities_mongo.json", "w") as f:
    json.dump(documents, f, indent=2)
    


## Javascript query examples
#db.activities_mongo.find(
#  { 
#    "environment.type": "Indoor",
#    "survey_responses.user_id": "user123"
#  }
#)

#db.activities.aggregate([
#  { $match: { intensities: { $in: ["High", "Medium"] } } },
#  { $unwind: "$survey_responses" },
#  {
#    $group: {
#      _id: null,
#      total_frequency: { $sum: "$survey_responses.frequency" }
#    }
#  }
#])


## PYTHON EXAMPLE QUERIES
# sum dqf for high or medium in a single category
sum(row["frequency"]
    for activity in documents
    if any(i in ["High","Medium"] for i in activity["intensities"])
    for row in activity["survey_responses"])
len(documents) # Number of activities

# Number of responses per activity
for activity in documents:
    print(f'{activity["name"]}: {len(activity["survey_responses"])}')

# Total dqf by activity
for doc in documents:
    print(f'{doc["name"]}: {sum(row["frequency"] for row in doc["survey_responses"])}')

## User-focused query examples
# user_id, activity, dqf
result={}
for activity in documents:
    name=activity["name"]
    for row in activity["survey_responses"]:
        key=(row["user_id"], name)
        result[key]=result.get(key,0)+row["frequency"]
print(result)
df=pd.Series(result).reset_index(name="frequency") # Make tabular dataframe
df.columns=["user_id","name","frequency"] # Set dataframe colums   
df=df.sort_values(["user_id","name"]) # Sort as needed

# only user_id, dqf
result={}
for activity in documents:
    for row in activity["survey_responses"]:
        user=row["user_id"]
        result[user]=result.get(user,0)+row["frequency"]

# user, count activities
result={}
for activity in documents:
    for row in activity["survey_responses"]:
        user=row["user_id"]
        result[user]=result.get(user,0)+1

# user, sum dqf
result={}
for activity in documents:
    for row in activity["survey_responses"]:
        user=row["user_id"]
        result[user]=result.get(user,0)+row["frequency"]
df=pd.Series(result).reset_index(name="frequency")
df.columns=["user_id","dqf"]
df=df.sort_values("dqf", 
                  ascending=False)
