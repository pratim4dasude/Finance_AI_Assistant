import re
from src.schemas import SafetyResult


BLOCK_RULES = {
    "insider_trading": [
        r"inside information",
        r"insider tip",
        r"material non[- ]public",
        r"trade before.*announcement",
    ],
    "market_manipulation": [
        r"pump and dump",
        r"manipulate.*stock",
        r"spoof.*order",
        r"create fake volume",
    ],
    "money_laundering": [
        r"launder money",
        r"hide source of funds",
        r"avoid aml",
        r"bypass kyc",
    ],
    "guaranteed_returns": [
        r"guaranteed profit",
        r"risk[- ]free.*high return",
        r"100% sure.*profit",
        r"guarantee.*returns",
    ],
    "reckless_advice": [
        r"put all my money",
        r"go all in",
        r"borrow.*to invest",
        r"max out.*loan.*stock",
    ],
}

EDUCATIONAL_ALLOW = [
    "what is",
    "explain",
    "definition",
    "educational",
    "why is it illegal",
    "how does it work",
]


RESPONSES = {
    "insider_trading": "I can’t help with trading based on material non-public information. I can explain legal research-based investing instead.",
    "market_manipulation": "I can’t help with market manipulation or coordinated trading schemes. I can help with ethical market analysis.",
    "money_laundering": "I can’t help with bypassing AML/KYC controls or hiding fund sources. I can explain compliant onboarding requirements.",
    "guaranteed_returns": "I can’t claim or engineer guaranteed investment returns. All investments carry risk.",
    "reckless_advice": "I can’t support reckless financial actions like going all-in or borrowing heavily to speculate. I can help compare safer allocation options.",
}


def safety_check(query: str) -> SafetyResult:
    text = query.lower()

    if any(phrase in text for phrase in EDUCATIONAL_ALLOW):
        return SafetyResult(allowed=True)

    for category, patterns in BLOCK_RULES.items():
        for pattern in patterns:
            if re.search(pattern, text):
                return SafetyResult(
                    allowed=False,
                    category=category,
                    response=RESPONSES[category],
                )

    return SafetyResult(allowed=True)