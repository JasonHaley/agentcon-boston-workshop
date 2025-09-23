import re
from typing import Optional

# Canonical clause types
CLAUSE_TYPES = [
    "parties", "consideration", "services", "fees", "expenses", "term",
    "termination", "relationship", "exclusivity", "ip", "confidentiality",
    "dispute_resolution", "governing_law", "severability", "entire_agreement",
    "amendments", "definitions", "notices", "execution", "misc"
]

# Ordered rules (first match wins)
RULES: list[tuple[str, list[re.Pattern]]] = [
    ("parties", [
        re.compile(r"\bpart(y|ies)\b", re.I),
        re.compile(r"\bintro(duction)?\b", re.I),
    ]),
    ("consideration", [
        re.compile(r"\bconsideration\b", re.I),
        re.compile(r"\brecitals?\b", re.I),
    ]),
    ("services", [
        re.compile(r"\bservices?\b", re.I),
        re.compile(r"\bscope\b", re.I),
        re.compile(r"\bstatement of work\b|\bSOW\b", re.I),
        re.compile(r"\bdeliverables?\b", re.I),
    ]),
    ("fees", [
        re.compile(r"\bfees?\b", re.I),
        re.compile(r"\bcompensation\b", re.I),
        re.compile(r"\bretainer\b", re.I),
        re.compile(r"\bpayment (terms|schedule)\b", re.I),
        re.compile(r"\bbilling\b", re.I),
        re.compile(r"\brate(s)?\b", re.I),
    ]),
    ("expenses", [
        re.compile(r"\bexpense(s)?\b", re.I),
        re.compile(r"\breimbursement\b", re.I),
    ]),
    ("termination", [
        re.compile(r"\btermination\b", re.I),
        re.compile(r"\bterminate\b", re.I),
    ]),
    ("term", [
        re.compile(r"\bterm\b", re.I),
        re.compile(r"\beffective date\b", re.I),
        re.compile(r"\bcommencement\b|\beffective\b", re.I),
        re.compile(r"\brenew(al|s)?\b|\bauto-?renew\b", re.I),
        re.compile(r"\bduration\b", re.I),
    ]),
    ("indemnification", [
        re.compile(r"\bindemnification\b", re.I),
    ]),
    ("liability", [
        re.compile(r"\bliability\b", re.I),
        re.compile(r"\blimitation of liability\b", re.I),
    ]),
    ("warranty", [
        re.compile(r"\bwarranty\b", re.I),
        re.compile(r"\bdisclaimer\b", re.I),
        re.compile(r"\bwarranty/disclaimer\b", re.I),
    ]),
    ("relationship", [
        re.compile(r"\brelationship\b", re.I),
        re.compile(r"\bindependent contractor\b", re.I),
        re.compile(r"\bno agency\b|\bno partnership\b|\bno employment\b", re.I),
    ]),
    ("exclusivity", [
        re.compile(r"\bexclusivit(y|ies)\b", re.I),
        re.compile(r"\bnon-?exclusiv", re.I),
    ]),
    ("ip", [
        re.compile(r"\bintellectual property\b|\bIP\b", re.I),
        re.compile(r"\bownership\b", re.I),
        re.compile(r"\bwork (made )?for hire\b", re.I),
        re.compile(r"\bwork product\b", re.I),
        re.compile(r"\blicense\b", re.I),
        re.compile(r"\bpre[- ]?existing materials\b", re.I),
    ]),
    ("confidentiality", [
        re.compile(r"\bconfidential(it(y|ies))?\b", re.I),
        re.compile(r"\bnon[- ]?disclosure\b|\bNDA\b", re.I),
        re.compile(r"\bconfidential information\b", re.I),
    ]),
    ("dispute_resolution", [
        re.compile(r"\bdispute(s)?\b", re.I),
        re.compile(r"\barbitration\b|\bmediate|mediation\b", re.I),
        re.compile(r"\bforum selection\b|\bvenue\b", re.I),
        re.compile(r"\battorneys'? fees\b", re.I),
    ]),
    ("governing_law", [
        re.compile(r"\bgoverning law\b", re.I),
        re.compile(r"\blaw\b", re.I),
        re.compile(r"\bjurisdiction\b", re.I),
        re.compile(r"\bchoice of law\b", re.I),
    ]),
    ("severability", [
        re.compile(r"\bseverabilit(y|ies)\b", re.I),
        re.compile(r"\binvalidity\b", re.I),
    ]),
    ("entire_agreement", [
        re.compile(r"\bentire agreement\b", re.I),
        re.compile(r"\bintegration\b|\bmerger\b", re.I),
        re.compile(r"\bwhole agreement\b", re.I),
        re.compile(r"\bconsulting agreement\b", re.I),
    ]),
    ("amendments", [
        re.compile(r"\bamend(ment|ments)\b", re.I),
        re.compile(r"\bmodification(s)?\b|\bchanges?\b", re.I),
        re.compile(r"\bwaiver(s)?\b", re.I),
    ]),
    ("definitions", [
        re.compile(r"\bdefinitions?\b", re.I),
        re.compile(r"\binterpretation\b", re.I),
    ]),
    ("notices", [
        re.compile(r"\bnotice(s)?\b", re.I),
        re.compile(r"\bnotices and communications\b", re.I),
    ]),
    ("execution", [
        re.compile(r"\bsignature(s)?\b|\bsignatures\b", re.I),
        re.compile(r"\bexecution\b|\bcounterparts\b", re.I),
        re.compile(r"\be-?signatures?\b|\belectronic signatures?\b", re.I),
    ]),
    ("misc", [
        re.compile(r"\bmisc(ellaneous)?\b", re.I),
        re.compile(r"\bgeneral provisions?\b", re.I),
        re.compile(r"\bgeneral?\b", re.I),
    ]),
]

# Pre-clean: strip numbering like "1.", "I.", "Section 1.2", etc.
_PRENUMBER = re.compile(
    r"""
    ^\s*
    (?: (?:section|sec\.|article|art\.)\s+ )?   # optional label
    (?: §\s* )?                                  # optional section symbol
    (?:
        \d+(?:\.\d+)*            |               # 1, 1.2, 1.2.3
        [IVXLCDM]{1,6}           |               # Roman numerals I, II, IV, etc.
        [A-Z]                    |               # A, B, C (single letter)
        \(\s*(?:\d+|[a-zA-Z])\s*\)               # (1), (a)
    )
    (?:                                       
        [\)\].:]\s*        |                    # ), ., ], :
        [–—-]\s*                               # dash/en-dash/em-dash
    )
    """,
    re.VERBOSE | re.IGNORECASE,
)

def _normalize_heading(h: str) -> str:
    h = h.strip()
    h = _PRENUMBER.sub("", h)           # remove leading numbering/labels
    h = re.sub(r"[_#*:•\-–—]+", " ", h) # collapse bullets/punct
    h = re.sub(r"\s+", " ", h)          # squeeze spaces
    return h.strip()

def classify_clause_heading(heading: str, default: Optional[str] = None) -> Optional[str]:
    """
    Return a normalized clause_type for a section heading.
    - Case-insensitive, tolerant of numbering/bullets.
    - First matching rule wins (ordered by specificity/priority).
    - If none match, returns `default` (None by default).
    """
    if not heading or not heading.strip():
        return default
    h = _normalize_heading(heading)
    
    # Special case: a heading like "Term and Termination" → prefer termination
    if re.search(r"\btermination\b", h, re.I):
        return "termination"
    if re.search(r"\bterm\b", h, re.I):
        # Only return 'term' if 'termination' wasn't present
        return "term"

    for ctype, patterns in RULES:
        for pat in patterns:
            if pat.search(h):
                return ctype

    return default
