import re
from rapidfuzz import process, fuzz
from typing import Dict, List, Any, Optional

class HeaderStandardizationService:
    def __init__(self, canonical_fields: Dict[str, List[str]], threshold: int = 80):
        self.canonical_fields = canonical_fields
        self.threshold = threshold
        self.canonical_to_synonyms_map = self._build_canonical_to_synonyms_map()

    def _build_canonical_to_synonyms_map(self) -> Dict[str, str]:
        """Creates a mapping from all synonyms back to their canonical field."""
        mapping = {}
        for canonical_field, synonyms in self.canonical_fields.items():
            for synonym in synonyms:
                mapping[self._normalize_header(synonym)] = canonical_field
        return mapping

    @staticmethod
    def _normalize_header(header: str) -> str:
        """Normalizes a header string by stripping whitespace, lowercasing, and removing OCR noise."""
        header = header.strip().lower()
        # Remove common OCR noise characters and symbols
        header = re.sub(r'[^\w\s]', '', header)  # Remove non-alphanumeric except spaces
        header = re.sub(r'\s+', ' ', header).strip() # Replace multiple spaces with single space
        return header

    def fuzzy_match_header(self, raw_header: str) -> Optional[str]:
        """
        Fuzzy matches a raw header to a canonical field using RapidFuzz.
        Returns the canonical field if a match is found above the threshold, otherwise None.
        """
        normalized_raw_header = self._normalize_header(raw_header)
        
        best_match = None
        highest_score = -1

        all_synonyms = []
        for synonyms_list in self.canonical_fields.values():
            all_synonyms.extend([self._normalize_header(s) for s in synonyms_list])

        if not all_synonyms:
            return None

        # Use process.extractOne to find the best match from all synonyms
        match_result = process.extractOne(
            normalized_raw_header, 
            all_synonyms, 
            scorer=fuzz.token_set_ratio, 
            score_cutoff=self.threshold
        )

        if match_result:
            matched_synonym, score, _ = match_result
            if score >= highest_score:
                highest_score = score
                # Map the matched synonym back to its canonical field
                best_match = self.canonical_to_synonyms_map.get(matched_synonym)
        
        return best_match

    def map_headers_to_canonical(self, raw_headers: List[str]) -> Dict[str, str]:
        """
        Maps a list of raw headers to their canonical fields.
        Output: { "raw_header": "canonical_field" }
        """
        mapped_headers = {}
        for header in raw_headers:
            canonical_field = self.fuzzy_match_header(header)
            if canonical_field:
                mapped_headers[header] = canonical_field
        return mapped_headers

