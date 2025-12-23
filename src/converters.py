"""Format converters for crossword puzzle data."""
from datetime import datetime


def crosshare_to_capi(crosshare: dict) -> dict:
    """Convert Crosshare puzzle format to CAPICrossword format.

    Crosshare format:
    - grid: flat array of strings ("." = block, letter = cell)
    - clues: [{num, dir (0=across, 1=down), clue}]
    - size: {rows, cols}

    CAPICrossword format:
    - dimensions: {cols, rows}
    - entries: [{id, number, humanNumber, clue, direction, length, position, solution, group}]
    """
    rows = crosshare["size"]["rows"]
    cols = crosshare["size"]["cols"]
    grid = crosshare["grid"]

    # Build 2D grid for easier processing
    grid_2d = _build_2d_grid(grid, rows, cols)

    # Build clue lookup map: (num, dir) -> clue text
    # dir: 0 = across, 1 = down
    clue_map = {(c["num"], c["dir"]): c["clue"] for c in crosshare.get("clues", [])}

    # Find all word positions and build entries
    entries = _find_entries(grid_2d, rows, cols, clue_map)

    return {
        "id": crosshare.get("id", ""),
        "number": 0,  # Will be assigned by caller
        "name": crosshare.get("title", "Untitled"),
        "creator": {"name": crosshare.get("authorName", "Unknown"), "webUrl": ""},
        "date": int(datetime.now().timestamp() * 1000),
        "webPublicationDate": int(datetime.now().timestamp() * 1000),
        "dimensions": {"cols": cols, "rows": rows},
        "crosswordType": "quick",
        "solutionAvailable": True,
        "dateSolutionAvailable": int(datetime.now().timestamp() * 1000),
        "entries": entries,
    }


def _build_2d_grid(flat_grid: list[str], rows: int, cols: int) -> list[list[str]]:
    """Convert flat grid array to 2D grid."""
    return [[flat_grid[r * cols + c] for c in range(cols)] for r in range(rows)]


def _is_block(cell: str) -> bool:
    """Check if a cell is a block (black square)."""
    return cell == "."


def _is_letter(cell: str) -> bool:
    """Check if a cell contains a letter."""
    return cell not in (".", " ", "")


def _find_entries(
    grid_2d: list[list[str]], rows: int, cols: int, clue_map: dict
) -> list[dict]:
    """Find all crossword entries (words) from the grid.

    A cell starts a word if:
    - It's not a block
    - For ACROSS: it's at left edge OR cell to left is a block, AND cell to right exists and is not a block
    - For DOWN: it's at top edge OR cell above is a block, AND cell below exists and is not a block
    """
    entries = []

    # First pass: assign clue numbers to cells
    # A cell gets a number if it starts ANY word (across or down)
    cell_numbers: dict[tuple[int, int], int] = {}
    current_number = 1

    for r in range(rows):
        for c in range(cols):
            cell = grid_2d[r][c]
            if _is_block(cell):
                continue

            starts_across = _starts_across_word(grid_2d, r, c, rows, cols)
            starts_down = _starts_down_word(grid_2d, r, c, rows, cols)

            if starts_across or starts_down:
                cell_numbers[(r, c)] = current_number
                current_number += 1

    # Second pass: build entries
    for (r, c), num in cell_numbers.items():
        # Check for across word
        if _starts_across_word(grid_2d, r, c, rows, cols):
            length = _get_word_length(grid_2d, r, c, rows, cols, "across")
            solution = _get_solution(grid_2d, r, c, length, "across")
            clue = clue_map.get((num, 0), "")  # 0 = across

            entry_id = f"{num}-across"
            entries.append({
                "id": entry_id,
                "number": num,
                "humanNumber": str(num),
                "clue": clue,
                "direction": "across",
                "length": length,
                "position": {"x": c, "y": r},
                "separatorLocations": {},
                "solution": solution,
                "group": [entry_id],
            })

        # Check for down word
        if _starts_down_word(grid_2d, r, c, rows, cols):
            length = _get_word_length(grid_2d, r, c, rows, cols, "down")
            solution = _get_solution(grid_2d, r, c, length, "down")
            clue = clue_map.get((num, 1), "")  # 1 = down

            entry_id = f"{num}-down"
            entries.append({
                "id": entry_id,
                "number": num,
                "humanNumber": str(num),
                "clue": clue,
                "direction": "down",
                "length": length,
                "position": {"x": c, "y": r},
                "separatorLocations": {},
                "solution": solution,
                "group": [entry_id],
            })

    return entries


def _starts_across_word(
    grid_2d: list[list[str]], r: int, c: int, rows: int, cols: int
) -> bool:
    """Check if cell (r, c) starts an across word."""
    cell = grid_2d[r][c]
    if _is_block(cell):
        return False

    # Must be at left edge OR have a block to the left
    left_is_boundary = c == 0 or _is_block(grid_2d[r][c - 1])

    # Must have at least one more cell to the right that's not a block
    has_continuation = c + 1 < cols and not _is_block(grid_2d[r][c + 1])

    return left_is_boundary and has_continuation


def _starts_down_word(
    grid_2d: list[list[str]], r: int, c: int, rows: int, cols: int
) -> bool:
    """Check if cell (r, c) starts a down word."""
    cell = grid_2d[r][c]
    if _is_block(cell):
        return False

    # Must be at top edge OR have a block above
    top_is_boundary = r == 0 or _is_block(grid_2d[r - 1][c])

    # Must have at least one more cell below that's not a block
    has_continuation = r + 1 < rows and not _is_block(grid_2d[r + 1][c])

    return top_is_boundary and has_continuation


def _get_word_length(
    grid_2d: list[list[str]], r: int, c: int, rows: int, cols: int, direction: str
) -> int:
    """Get the length of a word starting at (r, c) in the given direction."""
    length = 0

    if direction == "across":
        while c + length < cols and not _is_block(grid_2d[r][c + length]):
            length += 1
    else:  # down
        while r + length < rows and not _is_block(grid_2d[r + length][c]):
            length += 1

    return length


def _get_solution(
    grid_2d: list[list[str]], r: int, c: int, length: int, direction: str
) -> str:
    """Extract the solution (letters) for a word starting at (r, c)."""
    letters = []

    for i in range(length):
        if direction == "across":
            cell = grid_2d[r][c + i]
        else:  # down
            cell = grid_2d[r + i][c]

        # Handle empty cells (user hasn't filled in yet)
        if _is_letter(cell):
            letters.append(cell.upper())
        else:
            letters.append(" ")

    return "".join(letters)
