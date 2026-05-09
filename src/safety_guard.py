
import re
from src.schemas import SafetyResult


RESPONSES = {
    "insider_trading": "I can’t help with trading based on confidential or material non-public information. I can explain legal research-based investing instead.",
    "market_manipulation": "I can’t help manipulate prices, coordinate artificial buying, spoof orders, or create fake trading volume. I can help with ethical market analysis.",
    "money_laundering": "I can’t help hide funds, avoid reporting rules, structure deposits, or obscure the source of money. I can explain compliant financial processes.",
    "guaranteed_returns": "I can’t promise guaranteed returns, certain profits, or foolproof investment outcomes. All investments carry risk.",
    "reckless_advice": "I can’t support reckless financial actions like risking retirement savings, emergency funds, margin loans, or a home for speculation.",
    "sanctions_evasion": "I can’t help bypass sanctions, OFAC controls, or tracing requirements. I can explain sanctions compliance at a high level.",
    "fraud": "I can’t help draft fake documents or support fraudulent claims. I can help with legitimate documentation instead.",
}


EDUCATIONAL_ALLOW = [
    r"\bwhat is\b",
    r"\bwhat are\b",
    r"\bwhat's\b",
    r"\bexplain\b",
    r"\bdefinition\b",
    r"\bdifference between\b",
    r"\bwhat's the difference\b",
    r"\bare\b.*\blegal\b",
    r"\bis it.*legitimate\b",
    r"\bwhy\b.*\billegal\b",
    r"\bhow does\b.*\bwork\b",
    r"\bhow do\b.*\bdetect\b",
    r"\bpenalt(y|ies)\b",
    r"\brules\b",
    r"\brequirements\b",
    r"\bregulations\b",
    r"\bdetect\b",
    r"\binvestigate\b",
    r"\bcompliance\b",
    r"\bobligations\b",
    r"\brisk(s)? of\b",
    r"\bfactors should\b",
    r"\bhistorical average\b",
    r"\bred flag\b",
]


HARMFUL_REQUEST_VERBS = [
    r"\bhelp me\b",
    r"\bhow can i\b",
    r"\bhow do i\b",
    r"\bshow me\b",
    r"\btell me to\b",
    r"\bdesign\b",
    r"\bdraft\b",
    r"\bdo it\b",
    r"\bwhen should i\b",
    r"\bshould i\b",
]


CATEGORY_PATTERNS = {
    "insider_trading": [
        r"(confidential|non[- ]public|material non[- ]public|unannounced|inside|insider|tip|leak).*"
        r"(buy|sell|trade|shares|stock|load up|profit|position)",
        r"(buy|sell|trade|shares|stock|load up).*"
        r"(confidential|non[- ]public|material non[- ]public|unannounced|inside|insider|tip|leak)",
        r"(earnings|announcement|acquisition|merger).*before.*(call|announcement|public|tomorrow)",
    ],
    "market_manipulation": [
        r"(pump|dump|pump[- ]and[- ]dump).*",
        r"(manipulate|move|push).*price",
        r"coordinated.*(buy|buying|scheme)",
        r"(wash trade|spoof|layering|fake volume|create volume)",
    ],
    "money_laundering": [
        r"(move|transfer|route).*(cash|money|funds).*without.*report",
        r"(structure|split).*deposit.*(avoid|under|threshold|report)",
        r"(avoid|bypass).*(aml|kyc|reporting)",
        r"(hide|obscure|layer).*(source|funds|money|trading profits|profits)",
        r"tax authorities.*(hide|avoid|not report)|hide.*tax authorities",
    ],
    "guaranteed_returns": [
        r"(guarantee|guaranteed|promise).*(return|returns|profit|double|money)",
        r"(100% certain|100 percent certain|sure profit|certain to go up)",
        r"(foolproof|risk[- ]free|no risk).*(make|profit|return|returns|way)",
    ],
    "reckless_advice": [
        r"(put|invest).*(all|entire).*(retirement savings|savings|emergency fund|money).*"
        r"(crypto|options|stock|stocks|nvidia|bitcoin)",
        r"(take|use).*(margin loan|loan|leverage).*buy",
        r"(borrow|mortgage).*(house|home|money).*"
        r"(stock|stocks|crypto|options|invest|buy)",
        r"which stock.*mortgage.*house",
    ],
    "sanctions_evasion": [
        r"(bypass|avoid|evade).*(ofac|sanction|sanctions)",
        r"sanctioned.*(company|entity|russian).*without.*(trace|traced|report)",
        r"shell company.*(bypass|avoid|sanction|ofac)",
    ],
    "fraud": [
        r"(draft|create|make|forge|fake|falsify).*(fake|contract note|document|statement|kyc)",
        r"fake.*(contract note|document|statement|claim|losses)",
    ],
}


def _matches_any(patterns: list[str], text: str) -> bool:
    return any(re.search(pattern, text) for pattern in patterns)


def safety_check(query: str) -> SafetyResult:
    text = query.lower().strip()

    is_educational = _matches_any(EDUCATIONAL_ALLOW, text)
    is_harmful_request = _matches_any(HARMFUL_REQUEST_VERBS, text)

    for category, patterns in CATEGORY_PATTERNS.items():
        if _matches_any(patterns, text):
            if is_educational and not is_harmful_request:
                return SafetyResult(allowed=True)

            return SafetyResult(
                allowed=False,
                category=category,
                response=RESPONSES[category],
            )

    return SafetyResult(allowed=True)