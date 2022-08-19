# Some setup for a python virtual environment
# python3 -m venv env
# source env/bin/activate
# pip install requests

import requests
import json
import time
import os

api = os.environ["api"]
accesskey = os.environ["accesskey"]
secretkey = os.environ["secretkey"]

milliseconds = int(round(time.time() * 1000))

# Generate a Token for access to Prisma Cloud Compute.
response = requests.post(
    api+"login", json={"username": accesskey, "password": secretkey})
TOKEN = response.json()['token']

# Set Prisma Cloud Headers for Login with token
headers = {
    'x-redlock-auth': TOKEN,
    'content-type': 'application/json'
}

rql = {}
rql['aws-ec2'] = "config from cloud.resource where cloud.type = 'aws' AND resource.status = Active AND api.name = 'aws-ec2-describe-instances' AND json.rule = state.code equals 16"
rql['aws-rds'] = "config from cloud.resource where cloud.type = 'aws' AND resource.status = Active AND api.name = 'aws-rds-describe-db-instances'"
rql['aws-nat'] = "config from cloud.resource where cloud.type = 'aws' AND resource.status = Active AND api.name = 'aws-vpc-nat-gateway'"
rql['aws-lb'] = "config from cloud.resource where cloud.type = 'aws' AND resource.status = Active AND api.name = 'aws-elbv2-describe-load-balancers'"
rql['aws-red'] = "config from cloud.resource where cloud.type = 'aws' AND resource.status = Active AND api.name = 'aws-redshift-describe-clusters'"

rql["gcp-instances"] = "config from cloud.resource where cloud.type = 'gcp' AND resource.status = Active AND api.name = 'gcloud-compute-instances-list' AND json.rule = status equals RUNNING"
rql["gcp-router"] = "config from cloud.resource where cloud.type = 'gcp' AND resource.status = Active AND api.name = 'gcloud-compute-router'"
rql["gcp-nat"] = "config from cloud.resource where cloud.type = 'gcp' AND resource.status = Active AND api.name = 'gcloud-compute-nat'"
rql["gcp-sql"] = "config from cloud.resource where cloud.type = 'gcp' AND resource.status = Active AND api.name = 'gcloud-sql-instances-list'"

rql["azure-server"] = "config from cloud.resource where cloud.type = 'azure' AND resource.status = Active AND api.name = 'azure-sql-server-list' "
rql["azure-database"] = "config from cloud.resource where cloud.type = 'azure' AND resource.status = Active AND api.name = 'azure-sql-db-list' "
rql["azure-instance"] = "config from cloud.resource where cloud.type = 'azure' AND resource.status = Active AND api.name = 'azure-sql-managed-instance' "
rql["azure-lb"] = "config from cloud.resource where cloud.type = 'azure' AND resource.status = Active AND api.name = 'azure-network-lb-list'"
rql["azure-post"] = "config from cloud.resource where cloud.type = 'azure' AND resource.status = Active AND api.name = 'azure-postgresql-server' "


def call_api(type, t):

    data_rql = {
        "query": rql[type],
        "limit": "0",
        "timeRange": {
            "type": "absolute",
            "value": {
                "startTime": str(t),
                "endTime": str(t)
            }
        }
    }

    return requests.post(api+"search/config", headers=headers, data=json.dumps(data_rql)).json()["data"]["totalRows"]


# print(json.dumps(data))
totals = {"total": 0, "aws": 0, "gcp": 0, "azure": 0}
for x in rql:
    count = call_api(x, milliseconds)
    totals["total"] += count
    if(x[0:2] == "aw"):totals["aws"] += count
    if(x[0:2] == "gc"):totals["gcp"] += count
    if(x[0:2] == "az"):totals["azure"] += count
    print("%s: %s" % (x, count))
print("AWS: "+str(totals["aws"]))
print("GCP: "+str(totals["gcp"]))
print("Azure: "+str(totals["azure"]))
print("Total: "+str(totals["total"]))
