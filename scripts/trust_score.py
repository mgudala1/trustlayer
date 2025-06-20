# scripts/trust_score.py

def calculate_trust_score(comments):
    pos = sum(1 for c in comments if c.get("sentiment") == "positive")
    neg = sum(1 for c in comments if c.get("sentiment") == "negative")
    total = pos + neg

    if total == 0:
        return {"score": None, "confidence": 0}

    ratio = pos / total
    confidence = total
    score = round(ratio * 100, 1)

    return {"score": score, "confidence": confidence}
