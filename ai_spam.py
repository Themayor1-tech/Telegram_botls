import re

SPAM_KEYWORDS = ["free", "money", "click here", "promo", "win"]
SPAM_REGEX = [
    r"https?://\S+",          # links
    r"([A-Za-z])\1{4,}",      # repeated letters (heeeeeelp)
    r"[💰🎉🔥]{3,}",           # repeated emojis
]

def score_message(message: str) -> int:
    score = 0
    text = message.lower()

    # Keyword score
    for word in SPAM_KEYWORDS:
        if word in text:
            score += 20

    # Regex patterns
    for pattern in SPAM_REGEX:
        if re.search(pattern, text):
            score += 25

    return min(score, 100)

def is_spam(message: str, threshold: int = 50) -> bool:
    return score_message(message) >= threshold
