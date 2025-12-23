"""Test script to fetch and convert a specific puzzle."""
import asyncio
import json
from src.crosshare import fetch_puzzle, fetch_puzzle_list, is_valid_puzzle_size, get_clue_count
from src.converters import crosshare_to_capi

async def main():
    # Find a puzzle with 60 < clues < 80
    print("Searching for a puzzle with 60-80 clues...")

    for page in range(1, 10):
        puzzles = await fetch_puzzle_list(page)
        print(f"Page {page}: {len(puzzles)} puzzles")

        for p in puzzles:
            puzzle_id = p.get("id")
            if not puzzle_id:
                continue

            ch_puzzle = await fetch_puzzle(puzzle_id)
            clue_count = get_clue_count(ch_puzzle)

            if is_valid_puzzle_size(ch_puzzle):
                print(f"\nFound valid puzzle: {ch_puzzle.get('title')} ({clue_count} clues)")
                break
        else:
            continue
        break
    else:
        print("No valid puzzle found in first 10 pages")
        return

    print(f"\n=== Crosshare Puzzle ===")
    print(f"Title: {ch_puzzle.get('title')}")
    print(f"Size: {ch_puzzle.get('size')}")
    print(f"Grid length: {len(ch_puzzle.get('grid', []))}")
    print(f"Clue count: {len(ch_puzzle.get('clues', []))}")

    # Show grid structure
    size = ch_puzzle.get('size', {})
    rows = size.get('rows', 0)
    cols = size.get('cols', 0)
    grid = ch_puzzle.get('grid', [])

    print(f"\n=== Grid ({rows}x{cols}) ===")
    for r in range(rows):
        row_cells = []
        for c in range(cols):
            idx = r * cols + c
            cell = grid[idx] if idx < len(grid) else '?'
            row_cells.append(cell if cell != '.' else '#')
        print(''.join(f"{c:>2}" for c in row_cells))

    print("\n=== Converting to CAPI format ===")
    capi = crosshare_to_capi(ch_puzzle)

    print(f"Dimensions: {capi['dimensions']}")
    print(f"Entry count: {len(capi['entries'])}")

    # Show first few entries
    print("\n=== First 5 Entries ===")
    for entry in capi['entries'][:5]:
        print(f"  {entry['id']}: {entry['clue'][:50]}... @ ({entry['position']['x']},{entry['position']['y']}) len={entry['length']}")

    # Write the CAPI JSON to a file for the test page
    with open('test_puzzle.json', 'w') as f:
        json.dump(capi, f, indent=2)

    print("\n=== Wrote test_puzzle.json ===")

if __name__ == "__main__":
    asyncio.run(main())
