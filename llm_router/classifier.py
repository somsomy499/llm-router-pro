"""Task complexity classifier for routing decisions."""
import re

COMPLEXITY_PATTERNS = {
    "simple": [r"^(hi|hello|hey|thanks|ok)", r"^(yes|no|true|false)$"],
    "moderate": [r"explain", r"compare", r"summarize", r"list", r"what is"],
    "complex": [r"write.*code", r"implement", r"debug", r"refactor", r"design.*system"],
    "advanced": [r"analyze", r"prove", r"optimize", r"architecture", r"trade.?offs"],
}

class TaskClassifier:
    def classify(self, messages):
        text = messages[-1].get("content", "").lower()
        scores = {}
        for complexity, patterns in COMPLEXITY_PATTERNS.items():
            score = sum(1 for p in patterns if re.search(p, text))
            scores[complexity] = score
        if not any(scores.values()):
            return "moderate"
        return max(scores, key=scores.get)
