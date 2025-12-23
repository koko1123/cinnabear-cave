"""Aggressive tests for crossword format converters."""
import pytest
from src.converters import (
    crosshare_to_capi,
    _build_2d_grid,
    _is_block,
    _is_letter,
    _starts_across_word,
    _starts_down_word,
    _get_word_length,
    _get_solution,
    _find_entries,
)


class TestHelperFunctions:
    """Tests for internal helper functions."""

    def test_build_2d_grid_3x3(self):
        """Test 2D grid construction from flat array."""
        flat = ["A", "B", "C", "D", "E", "F", "G", "H", "I"]
        result = _build_2d_grid(flat, 3, 3)
        assert result == [
            ["A", "B", "C"],
            ["D", "E", "F"],
            ["G", "H", "I"],
        ]

    def test_build_2d_grid_2x4(self):
        """Test non-square grid."""
        flat = ["A", "B", "C", "D", "E", "F", "G", "H"]
        result = _build_2d_grid(flat, 2, 4)
        assert result == [
            ["A", "B", "C", "D"],
            ["E", "F", "G", "H"],
        ]

    def test_is_block(self):
        """Test block detection."""
        assert _is_block(".") is True
        assert _is_block("A") is False
        assert _is_block(" ") is False
        assert _is_block("") is False

    def test_is_letter(self):
        """Test letter detection."""
        assert _is_letter("A") is True
        assert _is_letter("z") is True
        assert _is_letter(".") is False
        assert _is_letter(" ") is False
        assert _is_letter("") is False


class TestWordDetection:
    """Tests for word start detection."""

    def test_starts_across_at_left_edge(self):
        """Word starting at left edge of grid."""
        grid = [
            ["C", "A", "T"],
            [".", ".", "."],
            [".", ".", "."],
        ]
        assert _starts_across_word(grid, 0, 0, 3, 3) is True

    def test_starts_across_after_block(self):
        """Word starting after a block."""
        grid = [
            [".", "C", "A"],
            [".", ".", "."],
            [".", ".", "."],
        ]
        assert _starts_across_word(grid, 0, 1, 3, 3) is True

    def test_not_starts_across_middle_of_word(self):
        """Middle of word should not start a word."""
        grid = [
            ["C", "A", "T"],
            [".", ".", "."],
            [".", ".", "."],
        ]
        assert _starts_across_word(grid, 0, 1, 3, 3) is False
        assert _starts_across_word(grid, 0, 2, 3, 3) is False

    def test_not_starts_across_single_cell(self):
        """Single cell (no continuation) should not start word."""
        grid = [
            ["A", ".", "."],
            [".", ".", "."],
            [".", ".", "."],
        ]
        assert _starts_across_word(grid, 0, 0, 3, 3) is False

    def test_not_starts_across_on_block(self):
        """Block cells should not start words."""
        grid = [
            [".", "A", "B"],
            [".", ".", "."],
            [".", ".", "."],
        ]
        assert _starts_across_word(grid, 0, 0, 3, 3) is False

    def test_starts_down_at_top_edge(self):
        """Word starting at top edge of grid."""
        grid = [
            ["C", ".", "."],
            ["A", ".", "."],
            ["T", ".", "."],
        ]
        assert _starts_down_word(grid, 0, 0, 3, 3) is True

    def test_starts_down_after_block(self):
        """Word starting after a block above."""
        grid = [
            [".", ".", "."],
            ["C", ".", "."],
            ["A", ".", "."],
        ]
        assert _starts_down_word(grid, 1, 0, 3, 3) is True

    def test_not_starts_down_middle_of_word(self):
        """Middle of vertical word should not start a word."""
        grid = [
            ["C", ".", "."],
            ["A", ".", "."],
            ["T", ".", "."],
        ]
        assert _starts_down_word(grid, 1, 0, 3, 3) is False
        assert _starts_down_word(grid, 2, 0, 3, 3) is False

    def test_not_starts_down_single_cell(self):
        """Single cell (no continuation) should not start down word."""
        grid = [
            ["A", ".", "."],
            [".", ".", "."],
            [".", ".", "."],
        ]
        assert _starts_down_word(grid, 0, 0, 3, 3) is False


class TestWordLength:
    """Tests for word length calculation."""

    def test_across_word_length_full_row(self):
        """Word spanning entire row."""
        grid = [
            ["C", "A", "T"],
            [".", ".", "."],
            [".", ".", "."],
        ]
        assert _get_word_length(grid, 0, 0, 3, 3, "across") == 3

    def test_across_word_length_partial(self):
        """Word ending at block."""
        grid = [
            ["C", "A", ".", "T"],
            [".", ".", ".", "."],
        ]
        assert _get_word_length(grid, 0, 0, 2, 4, "across") == 2

    def test_down_word_length_full_column(self):
        """Word spanning entire column."""
        grid = [
            ["C", ".", "."],
            ["A", ".", "."],
            ["T", ".", "."],
        ]
        assert _get_word_length(grid, 0, 0, 3, 3, "down") == 3

    def test_down_word_length_partial(self):
        """Vertical word ending at block."""
        grid = [
            ["C", ".", "."],
            ["A", ".", "."],
            [".", ".", "."],
            ["T", ".", "."],
        ]
        assert _get_word_length(grid, 0, 0, 4, 3, "down") == 2


class TestSolutionExtraction:
    """Tests for solution extraction."""

    def test_across_solution(self):
        """Extract across word solution."""
        grid = [
            ["C", "A", "T"],
            [".", ".", "."],
            [".", ".", "."],
        ]
        assert _get_solution(grid, 0, 0, 3, "across") == "CAT"

    def test_down_solution(self):
        """Extract down word solution."""
        grid = [
            ["C", ".", "."],
            ["A", ".", "."],
            ["T", ".", "."],
        ]
        assert _get_solution(grid, 0, 0, 3, "down") == "CAT"

    def test_solution_uppercase(self):
        """Solutions should be uppercase."""
        grid = [
            ["c", "a", "t"],
            [".", ".", "."],
            [".", ".", "."],
        ]
        assert _get_solution(grid, 0, 0, 3, "across") == "CAT"

    def test_solution_with_empty_cells(self):
        """Empty cells become spaces in solution."""
        grid = [
            ["C", " ", "T"],
            [".", ".", "."],
            [".", ".", "."],
        ]
        assert _get_solution(grid, 0, 0, 3, "across") == "C T"


class TestFindEntries:
    """Tests for complete entry finding."""

    def test_simple_3x3_one_across(self):
        """Simple 3x3 grid with one across word."""
        grid = [
            ["C", "A", "T"],
            [".", ".", "."],
            [".", ".", "."],
        ]
        clue_map = {(1, 0): "Feline animal"}  # 0 = across
        entries = _find_entries(grid, 3, 3, clue_map)

        assert len(entries) == 1
        assert entries[0]["id"] == "1-across"
        assert entries[0]["number"] == 1
        assert entries[0]["clue"] == "Feline animal"
        assert entries[0]["direction"] == "across"
        assert entries[0]["length"] == 3
        assert entries[0]["position"] == {"x": 0, "y": 0}
        assert entries[0]["solution"] == "CAT"

    def test_simple_3x3_one_down(self):
        """Simple 3x3 grid with one down word."""
        grid = [
            ["C", ".", "."],
            ["A", ".", "."],
            ["T", ".", "."],
        ]
        clue_map = {(1, 1): "Feline animal"}  # 1 = down
        entries = _find_entries(grid, 3, 3, clue_map)

        assert len(entries) == 1
        assert entries[0]["id"] == "1-down"
        assert entries[0]["direction"] == "down"
        assert entries[0]["solution"] == "CAT"

    def test_crossing_words(self):
        """Two words that cross each other."""
        # C A T
        # A . .
        # R . .
        grid = [
            ["C", "A", "T"],
            ["A", ".", "."],
            ["R", ".", "."],
        ]
        clue_map = {
            (1, 0): "Feline",  # 1-across
            (1, 1): "Vehicle",  # 1-down
        }
        entries = _find_entries(grid, 3, 3, clue_map)

        assert len(entries) == 2

        across = next(e for e in entries if e["direction"] == "across")
        down = next(e for e in entries if e["direction"] == "down")

        assert across["solution"] == "CAT"
        assert across["number"] == 1
        assert down["solution"] == "CAR"
        assert down["number"] == 1

    def test_multiple_words_numbered_correctly(self):
        """Multiple words get sequential numbers."""
        # C A T
        # . . .
        # D O G
        grid = [
            ["C", "A", "T"],
            [".", ".", "."],
            ["D", "O", "G"],
        ]
        clue_map = {
            (1, 0): "Feline",
            (2, 0): "Canine",
        }
        entries = _find_entries(grid, 3, 3, clue_map)

        assert len(entries) == 2
        nums = sorted([e["number"] for e in entries])
        assert nums == [1, 2]

    def test_complex_grid_with_intersections(self):
        """Complex grid with multiple intersecting words."""
        # C A T .
        # A . E .
        # R . A .
        # . . . .
        grid = [
            ["C", "A", "T", "."],
            ["A", ".", "E", "."],
            ["R", ".", "A", "."],
            [".", ".", ".", "."],
        ]
        clue_map = {
            (1, 0): "Feline",  # CAT across
            (1, 1): "Vehicle",  # CAR down
            (2, 1): "Beverage",  # TEA down
        }
        entries = _find_entries(grid, 4, 4, clue_map)

        assert len(entries) == 3

        cat = next(e for e in entries if e["solution"] == "CAT")
        car = next(e for e in entries if e["solution"] == "CAR")
        tea = next(e for e in entries if e["solution"] == "TEA")

        assert cat["direction"] == "across"
        assert cat["number"] == 1
        assert car["direction"] == "down"
        assert car["number"] == 1
        assert tea["direction"] == "down"
        assert tea["number"] == 2

    def test_missing_clue_defaults_to_empty(self):
        """Missing clues should default to empty string."""
        grid = [
            ["C", "A", "T"],
            [".", ".", "."],
            [".", ".", "."],
        ]
        clue_map = {}  # No clues provided
        entries = _find_entries(grid, 3, 3, clue_map)

        assert len(entries) == 1
        assert entries[0]["clue"] == ""


class TestFullConversion:
    """End-to-end conversion tests."""

    def test_minimal_crosshare_puzzle(self):
        """Convert minimal Crosshare puzzle."""
        crosshare = {
            "id": "test123",
            "title": "Test Puzzle",
            "authorName": "Test Author",
            "size": {"rows": 3, "cols": 3},
            "grid": ["C", "A", "T", ".", ".", ".", ".", ".", "."],
            "clues": [{"num": 1, "dir": 0, "clue": "Feline animal"}],
        }

        result = crosshare_to_capi(crosshare)

        assert result["id"] == "test123"
        assert result["name"] == "Test Puzzle"
        assert result["creator"]["name"] == "Test Author"
        assert result["dimensions"] == {"cols": 3, "rows": 3}
        assert len(result["entries"]) == 1
        assert result["entries"][0]["solution"] == "CAT"

    def test_crosshare_puzzle_with_crossing(self):
        """Convert Crosshare puzzle with crossing words."""
        crosshare = {
            "id": "cross123",
            "title": "Crossing Puzzle",
            "authorName": "Author",
            "size": {"rows": 3, "cols": 3},
            "grid": ["C", "A", "T", "A", ".", ".", "R", ".", "."],
            "clues": [
                {"num": 1, "dir": 0, "clue": "Feline"},
                {"num": 1, "dir": 1, "clue": "Vehicle"},
            ],
        }

        result = crosshare_to_capi(crosshare)

        assert len(result["entries"]) == 2

        across = next(e for e in result["entries"] if e["direction"] == "across")
        down = next(e for e in result["entries"] if e["direction"] == "down")

        assert across["clue"] == "Feline"
        assert across["solution"] == "CAT"
        assert down["clue"] == "Vehicle"
        assert down["solution"] == "CAR"

    def test_larger_puzzle_5x5(self):
        """Convert a 5x5 puzzle."""
        # . R O S E
        # M A X E D
        # . . . . .
        # . . . . .
        # . . . . .
        crosshare = {
            "id": "five123",
            "title": "5x5 Puzzle",
            "authorName": "Author",
            "size": {"rows": 5, "cols": 5},
            "grid": [
                ".", "R", "O", "S", "E",
                "M", "A", "X", "E", "D",
                ".", ".", ".", ".", ".",
                ".", ".", ".", ".", ".",
                ".", ".", ".", ".", ".",
            ],
            "clues": [
                {"num": 1, "dir": 0, "clue": "Flower"},
                {"num": 2, "dir": 0, "clue": "Pushed to limit"},
                {"num": 1, "dir": 1, "clue": "Beam of light"},
            ],
        }

        result = crosshare_to_capi(crosshare)

        # Should have: ROSE (across), MAXED (across), RA (down)
        assert result["dimensions"] == {"cols": 5, "rows": 5}
        entries = result["entries"]

        rose = next((e for e in entries if e["solution"] == "ROSE"), None)
        maxed = next((e for e in entries if e["solution"] == "MAXED"), None)

        assert rose is not None
        assert rose["direction"] == "across"
        assert rose["length"] == 4

        assert maxed is not None
        assert maxed["direction"] == "across"
        assert maxed["length"] == 5

    def test_defaults_for_missing_fields(self):
        """Test default values for missing optional fields."""
        crosshare = {
            "size": {"rows": 2, "cols": 2},
            "grid": ["A", "B", "C", "D"],
            "clues": [],
        }

        result = crosshare_to_capi(crosshare)

        assert result["id"] == ""
        assert result["name"] == "Untitled"
        assert result["creator"]["name"] == "Unknown"
        assert result["crosswordType"] == "quick"
        assert result["solutionAvailable"] is True

    def test_entry_structure_complete(self):
        """Verify all required CAPICrossword entry fields are present."""
        crosshare = {
            "id": "struct123",
            "title": "Structure Test",
            "authorName": "Author",
            "size": {"rows": 3, "cols": 3},
            "grid": ["C", "A", "T", ".", ".", ".", ".", ".", "."],
            "clues": [{"num": 1, "dir": 0, "clue": "Animal"}],
        }

        result = crosshare_to_capi(crosshare)
        entry = result["entries"][0]

        # All required fields must be present
        assert "id" in entry
        assert "number" in entry
        assert "humanNumber" in entry
        assert "clue" in entry
        assert "direction" in entry
        assert "length" in entry
        assert "position" in entry
        assert "separatorLocations" in entry
        assert "solution" in entry
        assert "group" in entry

        # Verify types
        assert isinstance(entry["id"], str)
        assert isinstance(entry["number"], int)
        assert isinstance(entry["humanNumber"], str)
        assert isinstance(entry["length"], int)
        assert isinstance(entry["position"], dict)
        assert "x" in entry["position"]
        assert "y" in entry["position"]
        assert isinstance(entry["group"], list)


class TestEdgeCases:
    """Edge case and regression tests."""

    def test_all_blocks_except_one_word(self):
        """Grid that's mostly blocks with one word."""
        grid = [
            [".", ".", ".", ".", "."],
            [".", ".", ".", ".", "."],
            ["H", "E", "L", "L", "O"],
            [".", ".", ".", ".", "."],
            [".", ".", ".", ".", "."],
        ]
        clue_map = {(1, 0): "Greeting"}
        entries = _find_entries(grid, 5, 5, clue_map)

        assert len(entries) == 1
        assert entries[0]["solution"] == "HELLO"
        assert entries[0]["position"] == {"x": 0, "y": 2}

    def test_two_letter_words(self):
        """Minimum length words (2 letters)."""
        grid = [
            ["A", "T", "."],
            [".", ".", "."],
            [".", ".", "."],
        ]
        clue_map = {(1, 0): "Preposition"}
        entries = _find_entries(grid, 3, 3, clue_map)

        assert len(entries) == 1
        assert entries[0]["length"] == 2

    def test_word_at_bottom_right_corner(self):
        """Word ending at bottom-right corner."""
        grid = [
            [".", ".", "."],
            [".", ".", "."],
            [".", "A", "B"],
        ]
        clue_map = {(1, 0): "Two letters"}
        entries = _find_entries(grid, 3, 3, clue_map)

        assert len(entries) == 1
        assert entries[0]["position"] == {"x": 1, "y": 2}

    def test_vertical_word_at_right_edge(self):
        """Vertical word at right edge of grid."""
        grid = [
            [".", ".", "A"],
            [".", ".", "B"],
            [".", ".", "C"],
        ]
        clue_map = {(1, 1): "ABC"}
        entries = _find_entries(grid, 3, 3, clue_map)

        assert len(entries) == 1
        assert entries[0]["direction"] == "down"
        assert entries[0]["position"] == {"x": 2, "y": 0}

    def test_checkerboard_pattern(self):
        """Alternating blocks and letters."""
        grid = [
            ["A", ".", "B"],
            [".", "C", "."],
            ["D", ".", "E"],
        ]
        # No 2+ letter words in this pattern
        clue_map = {}
        entries = _find_entries(grid, 3, 3, clue_map)

        # No words should be found (all single cells)
        assert len(entries) == 0

    def test_full_grid_no_blocks(self):
        """Grid with no blocks at all."""
        grid = [
            ["A", "B", "C"],
            ["D", "E", "F"],
            ["G", "H", "I"],
        ]
        clue_map = {
            (1, 0): "ABC",
            (2, 0): "DEF",
            (3, 0): "GHI",
            (1, 1): "ADG",
            (2, 1): "BEH",
            (3, 1): "CFI",
        }
        entries = _find_entries(grid, 3, 3, clue_map)

        # 3 across + 3 down = 6 words
        assert len(entries) == 6

        across_entries = [e for e in entries if e["direction"] == "across"]
        down_entries = [e for e in entries if e["direction"] == "down"]

        assert len(across_entries) == 3
        assert len(down_entries) == 3

    def test_single_row_puzzle(self):
        """1xN puzzle (single row)."""
        crosshare = {
            "id": "row123",
            "title": "Row Puzzle",
            "authorName": "Author",
            "size": {"rows": 1, "cols": 5},
            "grid": ["H", "E", "L", "L", "O"],
            "clues": [{"num": 1, "dir": 0, "clue": "Greeting"}],
        }

        result = crosshare_to_capi(crosshare)
        assert len(result["entries"]) == 1
        assert result["entries"][0]["solution"] == "HELLO"

    def test_single_column_puzzle(self):
        """Nx1 puzzle (single column)."""
        crosshare = {
            "id": "col123",
            "title": "Column Puzzle",
            "authorName": "Author",
            "size": {"rows": 5, "cols": 1},
            "grid": ["H", "E", "L", "L", "O"],
            "clues": [{"num": 1, "dir": 1, "clue": "Greeting"}],
        }

        result = crosshare_to_capi(crosshare)
        assert len(result["entries"]) == 1
        assert result["entries"][0]["direction"] == "down"
        assert result["entries"][0]["solution"] == "HELLO"
