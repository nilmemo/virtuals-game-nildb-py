import json
import subprocess

def get_nildb_keys():
    try:
        cmd = "node generate.js"
        results = subprocess.run(cmd, shell=True, text=True, capture_output=True, check=True)

        obj = {
          "contest": "nature-v1",
          "team": "red",
          "schema_id": "5b13523b-392d-4e8d-8325-3ef60e06f3d3",
          "hosts": [
            {
              "url": "nildb-zy8u.nillion.network",
              "name": "did:nil:testnet:nillion1fnhettvcrsfu8zkd5zms4d820l0ct226c3zy8u",
              "bearer": "eyJ0eXAiOiJKV1QiLCJhbGciOiJFUzI1NksifQ.eyJpYXQiOjE3MzgwOTM2OTgsImV4cCI6MTczODEyOTY5OCwiaXNzIjoiZGlkOm5pbDp0ZXN0bmV0Om5pbGxpb24xeTJuNWxkYXpzemx4enltMDU1cmYzOXFhYzZodjdna3AzZXc5ZW4iLCJhdWQiOiJkaWQ6bmlsOnRlc3RuZXQ6bmlsbGlvbjFmbmhldHR2Y3JzZnU4emtkNXptczRkODIwbDBjdDIyNmMzenk4dSJ9.z66AjvLaToerSLFbXfekMvldPO1mgAQnMW3ZDRh1wutDzxqcn97Og5RENLkk8dWQyuDVGfPAD15i3iKq2ea-AQ"
            },
            {
              "url": "nildb-rl5g.nillion.network",
              "name": "did:nil:testnet:nillion14x47xx85de0rg9dqunsdxg8jh82nvkax3jrl5g",
              "bearer": "eyJ0eXAiOiJKV1QiLCJhbGciOiJFUzI1NksifQ.eyJpYXQiOjE3MzgwOTM2OTgsImV4cCI6MTczODEyOTY5OCwiaXNzIjoiZGlkOm5pbDp0ZXN0bmV0Om5pbGxpb24xeTJuNWxkYXpzemx4enltMDU1cmYzOXFhYzZodjdna3AzZXc5ZW4iLCJhdWQiOiJkaWQ6bmlsOnRlc3RuZXQ6bmlsbGlvbjE0eDQ3eHg4NWRlMHJnOWRxdW5zZHhnOGpoODJudmtheDNqcmw1ZyJ9.iyZ9ND-AaZzY-iFbFDpAstZ9GC0rZ8Y0FQN3XqsbOSc33XZ6Ji0wm8jQ6R_VQmLfHNkvRigthzjuiDLJ0ZbptA"
            },
            {
              "url": "nildb-lpjp.nillion.network",
              "name": "did:nil:testnet:nillion167pglv9k7m4gj05rwj520a46tulkff332vlpjp",
              "bearer": "eyJ0eXAiOiJKV1QiLCJhbGciOiJFUzI1NksifQ.eyJpYXQiOjE3MzgwOTM2OTgsImV4cCI6MTczODEyOTY5OCwiaXNzIjoiZGlkOm5pbDp0ZXN0bmV0Om5pbGxpb24xeTJuNWxkYXpzemx4enltMDU1cmYzOXFhYzZodjdna3AzZXc5ZW4iLCJhdWQiOiJkaWQ6bmlsOnRlc3RuZXQ6bmlsbGlvbjE2N3BnbHY5azdtNGdqMDVyd2o1MjBhNDZ0dWxrZmYzMzJ2bHBqcCJ9.DPXzW7uxt0ghFHabOFOWOKHdyDVdB_WlI-_RcFuNt4gOsgkUmkRHmVwfAxnLSr-gRiJZnEyI7x7V399b5iI5hA"
            }
          ],
          "schema": {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "title": "Creative Contest Schema",
            "type": "object",
            "properties": {
              "_id": {
                "type": "string",
                "description": "The id of the record"
              },
              "contest": {
                "type": "string",
                "description": "The name of the poetry contest and version eg nature-v1"
              },
              "team": {
                "type": "string",
                "description": "The team the agent belongs to"
              },
              "text": {
                "type": "object",
                "properties": {
                  "$share": {
                    "type": "string",
                    "description": "Any text; secret shared"
                  }
                },
                "required": [
                  "$share"
                ]
              }
            },
            "required": [
              "_id",
              "text",
              "team",
              "contest"
            ]
          }
        }

        obj["hosts"] = eval(results.stdout)

        with open('.nildb.config.json', 'w') as file:
            json.dump(obj, file)
        return True
    except Exception as e:
        print(f"Exception occurred: {e}")
        return False
