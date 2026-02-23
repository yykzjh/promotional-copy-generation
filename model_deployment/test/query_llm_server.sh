curl http://localhost:8000/v1/chat/completions \
    -H "Content-Type: application/json" \
    -d '{
        "model": "models/Qwen3-30B-A3B-Instruct-2507-FP8",
        "messages": [
            {"role": "system", "content": "你是一个经验丰富的文案写手，擅长根据用户的需求生成推广文案。"},
            {"role": "user", "content": "请根据以下描述生成推广文案：今天去吃了牛牛New寿喜烧火锅，很好吃，推荐给大家。"}
        ]
    }'
