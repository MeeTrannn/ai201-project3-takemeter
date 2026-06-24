"""Apply v2 labels: report, appeal, inquiry, commentary."""
import csv
from collections import Counter
from pathlib import Path

# index -> (label, review_flag)
LABELS = {
    0: ("inquiry", ""),
    1: ("commentary", ""),
    2: ("commentary", ""),
    3: ("commentary", ""),
    4: ("commentary", ""),
    5: ("commentary", ""),
    6: ("commentary", ""),
    7: ("appeal", ""),
    8: ("appeal", ""),
    9: ("appeal", ""),
    10: ("inquiry", ""),
    11: ("inquiry", ""),
    12: ("commentary", ""),
    13: ("appeal", ""),
    14: ("commentary", ""),
    15: ("commentary", ""),
    16: ("report", ""),
    17: ("commentary", ""),
    18: ("commentary", ""),
    19: ("commentary", ""),
    20: ("inquiry", "review"),
    21: ("commentary", "review"),
    22: ("inquiry", ""),
    23: ("appeal", ""),
    24: ("appeal", ""),
    25: ("appeal", ""),
    26: ("commentary", ""),
    27: ("appeal", ""),
    28: ("commentary", ""),
    29: ("commentary", ""),
    30: ("appeal", ""),
    31: ("commentary", ""),
    32: ("inquiry", ""),
    33: ("report", ""),
    34: ("report", ""),
    35: ("commentary", ""),
    36: ("commentary", ""),
    37: ("report", ""),
    38: ("commentary", ""),
    39: ("appeal", ""),
    40: ("appeal", ""),
    41: ("inquiry", ""),
    42: ("inquiry", ""),
    43: ("report", ""),
    44: ("commentary", ""),
    45: ("commentary", ""),
    46: ("appeal", ""),
    47: ("report", ""),
    48: ("inquiry", "review"),
    49: ("inquiry", ""),
    50: ("commentary", ""),
    51: ("commentary", ""),
    52: ("appeal", ""),
    53: ("inquiry", ""),
    54: ("inquiry", ""),
    55: ("commentary", ""),
    56: ("commentary", ""),
    57: ("commentary", ""),
    58: ("commentary", ""),
    59: ("commentary", ""),
    60: ("commentary", ""),
    61: ("commentary", ""),
    62: ("inquiry", "review"),
    63: ("report", ""),
    64: ("appeal", ""),
    65: ("inquiry", ""),
    66: ("appeal", ""),
    67: ("commentary", ""),
    68: ("inquiry", ""),
    69: ("inquiry", ""),
    70: ("inquiry", ""),
    71: ("inquiry", ""),
    72: ("commentary", ""),
    73: ("report", ""),
    74: ("commentary", ""),
    75: ("commentary", ""),
    76: ("commentary", ""),
    77: ("inquiry", "review"),
    78: ("report", ""),
    79: ("inquiry", "review"),
    80: ("appeal", ""),
    81: ("commentary", ""),
    82: ("commentary", ""),
    83: ("inquiry", ""),
    84: ("appeal", ""),
    85: ("appeal", ""),
    86: ("inquiry", ""),
    87: ("commentary", ""),
    88: ("report", ""),
    89: ("report", ""),
    90: ("commentary", ""),
    91: ("commentary", ""),
    92: ("report", ""),
    93: ("appeal", ""),
    94: ("report", ""),
    95: ("report", ""),
    96: ("appeal", ""),
    97: ("commentary", ""),
    98: ("commentary", ""),
    99: ("commentary", ""),
    100: ("commentary", ""),
    101: ("commentary", ""),
    102: ("commentary", ""),
    103: ("report", ""),
    104: ("report", ""),
    105: ("report", ""),
    106: ("report", ""),
    107: ("commentary", ""),
    108: ("commentary", ""),
    109: ("inquiry", ""),
    110: ("report", "review"),
    111: ("commentary", ""),
    112: ("commentary", ""),
    113: ("report", ""),
    114: ("report", ""),
    115: ("appeal", ""),
    116: ("report", ""),
    117: ("report", ""),
    118: ("inquiry", ""),
    119: ("report", ""),
    120: ("commentary", ""),
    121: ("commentary", ""),
    122: ("commentary", ""),
    123: ("commentary", ""),
    124: ("commentary", ""),
    125: ("commentary", ""),
    126: ("commentary", ""),
    127: ("commentary", ""),
    128: ("commentary", ""),
    129: ("inquiry", ""),
    130: ("inquiry", ""),
    131: ("commentary", ""),
    132: ("inquiry", ""),
    133: ("appeal", ""),
    134: ("appeal", ""),
    135: ("commentary", ""),
    136: ("appeal", ""),
    137: ("commentary", ""),
    138: ("commentary", ""),
    139: ("commentary", ""),
    140: ("inquiry", ""),
    141: ("commentary", ""),
    142: ("appeal", ""),
    143: ("commentary", ""),
    144: ("appeal", ""),
    145: ("commentary", ""),
    146: ("commentary", ""),
    147: ("appeal", ""),
    148: ("appeal", ""),
    149: ("inquiry", ""),
    150: ("inquiry", ""),
    151: ("inquiry", ""),
    152: ("inquiry", ""),
    153: ("inquiry", ""),
    154: ("inquiry", ""),
    155: ("inquiry", ""),
    156: ("inquiry", ""),
    157: ("inquiry", ""),
    158: ("commentary", ""),
    159: ("inquiry", ""),
    160: ("inquiry", ""),
    161: ("inquiry", ""),
    162: ("inquiry", ""),
    163: ("commentary", ""),
    164: ("commentary", ""),
    165: ("report", ""),
    166: ("inquiry", ""),
    167: ("inquiry", ""),
    168: ("inquiry", ""),
    169: ("inquiry", ""),
    170: ("commentary", ""),
    171: ("commentary", ""),
    172: ("commentary", ""),
    173: ("commentary", ""),
    174: ("appeal", ""),
    175: ("inquiry", ""),
    176: ("commentary", ""),
    177: ("commentary", ""),
    178: ("commentary", ""),
    179: ("commentary", ""),
    180: ("report", ""),
    181: ("commentary", ""),
    182: ("report", "review"),
    183: ("inquiry", ""),
    184: ("inquiry", ""),
    185: ("commentary", ""),
    186: ("appeal", ""),
    187: ("commentary", ""),
    188: ("report", ""),
    189: ("inquiry", ""),
    190: ("report", ""),
    191: ("commentary", ""),
    192: ("inquiry", ""),
    193: ("report", ""),
    194: ("report", ""),
    195: ("appeal", ""),
    196: ("commentary", ""),
    197: ("commentary", ""),
    198: ("inquiry", ""),
    199: ("commentary", "review"),
}

LABEL_VERSION = "v2"
VALID = {"report", "appeal", "inquiry", "commentary"}


def main():
    project = Path(__file__).parent
    main_path = project / "the-reddit-climate-change-dataset-posts-clean.csv"
    review_path = project / "annotation_batch1_review.csv"

    rows = list(csv.DictReader(main_path.open(encoding="utf-8")))
    assert len(rows) == 200
    assert len(LABELS) == 200

    out = []
    for i, row in enumerate(rows):
        label, review_flag = LABELS[i]
        assert label in VALID
        out.append({
            "text": row["text"],
            "prelabel": label,
            "label": label,
            "prelabeled_by_ai": "true",
            "review_flag": review_flag,
            "label_version": LABEL_VERSION,
        })

    fieldnames = ["text", "prelabel", "label", "prelabeled_by_ai", "review_flag", "label_version"]
    with main_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(out)

    with review_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["row_id", *fieldnames])
        writer.writeheader()
        for i, row in enumerate(out[:50]):
            writer.writerow({"row_id": i, **row})

    counts = Counter(v[0] for v in LABELS.values())
    flags = sum(1 for v in LABELS.values() if v[1])
    print(f"Label version: {LABEL_VERSION}")
    print(f"Distribution: {dict(counts)}")
    print(f"Review flags: {flags}")
    print(f"Wrote {main_path}")
    print(f"Wrote {review_path} (rows 0-49)")


if __name__ == "__main__":
    main()
