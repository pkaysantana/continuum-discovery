import urllib.request
import json
import traceback

def search_egfr_apo():
    query = {
      "query": {
        "type": "group",
        "logical_operator": "and",
        "nodes": [
          {
            "type": "terminal",
            "service": "text",
            "parameters": {
              "attribute": "rcsb_entity_source_organism.scientific_name",
              "operator": "exact_match",
              "value": "Homo sapiens"
            }
          },
          {
            "type": "terminal",
            "service": "text",
            "parameters": {
              "attribute": "struct.title",
              "operator": "contains_words",
              "value": "EGFR"
            }
          },
          {
            "type": "terminal",
            "service": "text",
            "parameters": {
              "attribute": "rcsb_entry_info.nonpolymer_entity_count",
              "operator": "equals",
              "value": 0
            }
          }
        ]
      },
      "request_options": {
        "return_all_hits": True
      },
      "return_type": "entry"
    }

    url = 'https://search.rcsb.org/rcsbsearch/v2/query'
    req = urllib.request.Request(url, data=json.dumps(query).encode('utf-8'), headers={'Content-Type': 'application/json'})
    
    try:
        with urllib.request.urlopen(req) as response:
            res = json.loads(response.read().decode())
            print(f"Found {res.get('total_count', 0)} structures.")
            for r in res.get('result_set', []):
                print(r['identifier'])
    except Exception as e:
        print("Error", e)

search_egfr_apo()
