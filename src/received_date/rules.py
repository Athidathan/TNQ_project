"""Business rules and configuration for Received-Date extraction.

All changeable business rules and open product-owner decisions live here.
Each rule has a PROVISIONAL default pending final confirmation from the Product Owner.
"""

from typing import Final, Literal

# ---------------------------------------------------------------------------
# Q1: Slash / dot numeric date ambiguity (e.g. 03/04/2026)
# Options:
#   - "INVALID_IF_AMBIGUOUS": Never guess. If both DD/MM and MM/DD are valid calendar
#     dates, treat as ambiguous and return INVALID. If only one order is possible
#     (e.g., 13/01/2026 or 01/13/2026), use that valid order.
#   - "DMY": Always assume Day/Month/Year (UK/European/Indian academic standard).
#   - "MDY": Always assume Month/Day/Year (US standard).
#   - "INFER_DOCUMENT_CONTEXT": Check all dates across the current document to infer
#     whether the manuscript adheres to DMY or MDY. If any unambiguous date indicates MDY,
#     choose MDY. If any indicates DMY, choose DMY. If all are ambiguous, default to DMY.
# PROVISIONAL (waiting for product owner, Q1)
SlashPolicy = Literal["INVALID_IF_AMBIGUOUS", "DMY", "MDY", "INFER_DOCUMENT_CONTEXT"]
SLASH_POLICY: SlashPolicy = "INVALID_IF_AMBIGUOUS"

# ---------------------------------------------------------------------------
# Q2: Two-digit year expansion base (e.g. 12/05/26)
# Default is 2000, so '26' becomes 2026.
# PROVISIONAL (waiting for product owner, Q2)
TWO_DIGIT_YEAR_BASE: Final[int] = 2000

# ---------------------------------------------------------------------------
# Q3: Accepted labels for received date
# Only explicit received-date labels are accepted.
# Fallbacks like 'Submitted', 'Accepted', 'Published online' are excluded.
# PROVISIONAL (waiting for product owner, Q3)
LABELS: Final[tuple[str, ...]] = (
    "received",
    "date received",
    "received on",
    "manuscript received",
    "date of receipt",
)

# ---------------------------------------------------------------------------
# Q4: Multiple conflicting Received dates in a single file
# Options: "INVALID", "FIRST", "EARLIEST", "LATEST"
# Identical repeats (e.g., header & body identical) are consolidated to one date.
# If different dates appear under Received labels, return INVALID.
# PROVISIONAL (waiting for product owner, Q4)
MULTIPLE_RECEIVED_POLICY: Final[Literal["INVALID", "FIRST", "EARLIEST", "LATEST"]] = "INVALID"

# ---------------------------------------------------------------------------
# Q5: Partial dates (e.g. 'Mar 2026', '2026')
# When False, partial dates are rejected as INVALID.
# PROVISIONAL (waiting for product owner, Q5)
ALLOW_PARTIAL_DATES: Final[bool] = False

# ---------------------------------------------------------------------------
# Q6: Plausibility checks (e.g., future dates, dates after Accepted, ancient years)
# When False, any valid calendar date is accepted without business plausibility constraints.
# PROVISIONAL (waiting for product owner, Q6)
CHECK_PLAUSIBILITY: Final[bool] = False

# ---------------------------------------------------------------------------
# Q7: Misspelt month names (e.g. 'Janaury')
# When False, no fuzzy matching is performed; misspellings result in INVALID.
# PROVISIONAL (waiting for product owner, Q7)
ALLOW_FUZZY_MONTHS: Final[bool] = False

# ---------------------------------------------------------------------------
# Q8: Hidden text, tracked changes, and comments in Word documents
# PROVISIONAL (waiting for product owner, Q8)
INCLUDE_HIDDEN_TEXT: Final[bool] = True
INCLUDE_TRACKED_INSERTIONS: Final[bool] = True
EXCLUDE_DELETED_TEXT: Final[bool] = True
EXCLUDE_COMMENTS: Final[bool] = True

# ---------------------------------------------------------------------------
# Q9: Non-English month names (e.g. '2 janvier 2026')
# When False, only English month names and abbreviations are supported.
# PROVISIONAL (waiting for product owner, Q9)
SUPPORT_NON_ENGLISH_MONTHS: Final[bool] = False

# ---------------------------------------------------------------------------
# Q10: File selection criteria in the input folder
# Process only .docx files (case-insensitive) directly in the folder.
# Skip Word temporary lock files starting with '~$'. Do not recurse into subdirectories.
# PROVISIONAL (waiting for product owner, Q10)
RECURSIVE_DIRECTORY_SEARCH: Final[bool] = False
SKIP_LOCK_FILES: Final[bool] = True

# ---------------------------------------------------------------------------
# Q11: Output formatting and directory handling
# Sort rows by filename in ASCII/alphabetical order. Automatically create output folder if missing.
# PROVISIONAL (waiting for product owner, Q11)
SORT_OUTPUT_BY_FILENAME: Final[bool] = True
CREATE_OUTPUT_DIR: Final[bool] = True
