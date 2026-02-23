curl http://localhost:8002/v1/images/generations \
    -H "Content-Type: application/json" \
    -d '{
        "prompt": "A beautiful sunset over a calm ocean",
        "n": 1,
        "size": "224x224"
    }'
