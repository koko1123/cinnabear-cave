"""Seed the database with initial puzzles from the frontend."""
import asyncio
from datetime import datetime

from sqlalchemy import select

from src.db import async_session, init_db
from src.models import Puzzle

# Puzzle data from hibernating-cinnabear/src/data/puzzles.ts
PUZZLES = [
    {
        "id": "puzzle-1",
        "number": 1,
        "name": "Quick Crossword 1",
        "creator": {"name": "Cinnabear", "webUrl": ""},
        "date": int(datetime.now().timestamp() * 1000),
        "webPublicationDate": int(datetime.now().timestamp() * 1000),
        "dimensions": {"cols": 13, "rows": 13},
        "crosswordType": "quick",
        "solutionAvailable": True,
        "dateSolutionAvailable": int(datetime.now().timestamp() * 1000),
        "entries": [
            {"id": "1-across", "number": 1, "humanNumber": "1", "clue": "Large body of salt water (5)", "direction": "across", "length": 5, "position": {"x": 0, "y": 0}, "separatorLocations": {}, "solution": "OCEAN", "group": ["1-across"]},
            {"id": "6-across", "number": 6, "humanNumber": "6", "clue": "Opposite of night (3)", "direction": "across", "length": 3, "position": {"x": 7, "y": 0}, "separatorLocations": {}, "solution": "DAY", "group": ["6-across"]},
            {"id": "7-across", "number": 7, "humanNumber": "7", "clue": "A dwelling place (4)", "direction": "across", "length": 4, "position": {"x": 0, "y": 2}, "separatorLocations": {}, "solution": "HOME", "group": ["7-across"]},
            {"id": "8-across", "number": 8, "humanNumber": "8", "clue": "Male offspring (3)", "direction": "across", "length": 3, "position": {"x": 6, "y": 2}, "separatorLocations": {}, "solution": "SON", "group": ["8-across"]},
            {"id": "9-across", "number": 9, "humanNumber": "9", "clue": "Not old (3)", "direction": "across", "length": 3, "position": {"x": 10, "y": 2}, "separatorLocations": {}, "solution": "NEW", "group": ["9-across"]},
            {"id": "10-across", "number": 10, "humanNumber": "10", "clue": "Precious metal (4)", "direction": "across", "length": 4, "position": {"x": 0, "y": 4}, "separatorLocations": {}, "solution": "GOLD", "group": ["10-across"]},
            {"id": "11-across", "number": 11, "humanNumber": "11", "clue": "Opposite of hot (4)", "direction": "across", "length": 4, "position": {"x": 5, "y": 4}, "separatorLocations": {}, "solution": "COLD", "group": ["11-across"]},
            {"id": "12-across", "number": 12, "humanNumber": "12", "clue": "Writing fluid (3)", "direction": "across", "length": 3, "position": {"x": 10, "y": 4}, "separatorLocations": {}, "solution": "INK", "group": ["12-across"]},
            {"id": "13-across", "number": 13, "humanNumber": "13", "clue": "Heavenly body (4)", "direction": "across", "length": 4, "position": {"x": 0, "y": 6}, "separatorLocations": {}, "solution": "STAR", "group": ["13-across"]},
            {"id": "14-across", "number": 14, "humanNumber": "14", "clue": "Frozen water (3)", "direction": "across", "length": 3, "position": {"x": 5, "y": 6}, "separatorLocations": {}, "solution": "ICE", "group": ["14-across"]},
            {"id": "15-across", "number": 15, "humanNumber": "15", "clue": "Tree limb (4)", "direction": "across", "length": 4, "position": {"x": 9, "y": 6}, "separatorLocations": {}, "solution": "LIMB", "group": ["15-across"]},
            {"id": "16-across", "number": 16, "humanNumber": "16", "clue": "Nocturnal bird (3)", "direction": "across", "length": 3, "position": {"x": 0, "y": 8}, "separatorLocations": {}, "solution": "OWL", "group": ["16-across"]},
            {"id": "17-across", "number": 17, "humanNumber": "17", "clue": "Earth (4)", "direction": "across", "length": 4, "position": {"x": 4, "y": 8}, "separatorLocations": {}, "solution": "SOIL", "group": ["17-across"]},
            {"id": "18-across", "number": 18, "humanNumber": "18", "clue": "Wager (3)", "direction": "across", "length": 3, "position": {"x": 9, "y": 8}, "separatorLocations": {}, "solution": "BET", "group": ["18-across"]},
            {"id": "19-across", "number": 19, "humanNumber": "19", "clue": "Canine (3)", "direction": "across", "length": 3, "position": {"x": 0, "y": 10}, "separatorLocations": {}, "solution": "DOG", "group": ["19-across"]},
            {"id": "20-across", "number": 20, "humanNumber": "20", "clue": "Feline (3)", "direction": "across", "length": 3, "position": {"x": 4, "y": 10}, "separatorLocations": {}, "solution": "CAT", "group": ["20-across"]},
            {"id": "21-across", "number": 21, "humanNumber": "21", "clue": "Consume food (3)", "direction": "across", "length": 3, "position": {"x": 8, "y": 10}, "separatorLocations": {}, "solution": "EAT", "group": ["21-across"]},
            {"id": "22-across", "number": 22, "humanNumber": "22", "clue": "Scarlet color (3)", "direction": "across", "length": 3, "position": {"x": 0, "y": 12}, "separatorLocations": {}, "solution": "RED", "group": ["22-across"]},
            {"id": "23-across", "number": 23, "humanNumber": "23", "clue": "Illumination (5)", "direction": "across", "length": 5, "position": {"x": 4, "y": 12}, "separatorLocations": {}, "solution": "LIGHT", "group": ["23-across"]},
            {"id": "24-across", "number": 24, "humanNumber": "24", "clue": "Crimson (3)", "direction": "across", "length": 3, "position": {"x": 10, "y": 12}, "separatorLocations": {}, "solution": "RED", "group": ["24-across"]},
            {"id": "1-down", "number": 1, "humanNumber": "1", "clue": "Citrus fruit (6)", "direction": "down", "length": 6, "position": {"x": 0, "y": 0}, "separatorLocations": {}, "solution": "ORANGE", "group": ["1-down"]},
            {"id": "2-down", "number": 2, "humanNumber": "2", "clue": "Automobile (3)", "direction": "down", "length": 3, "position": {"x": 2, "y": 0}, "separatorLocations": {}, "solution": "CAR", "group": ["2-down"]},
            {"id": "3-down", "number": 3, "humanNumber": "3", "clue": "Consumed food (3)", "direction": "down", "length": 3, "position": {"x": 4, "y": 0}, "separatorLocations": {}, "solution": "ATE", "group": ["3-down"]},
            {"id": "4-down", "number": 4, "humanNumber": "4", "clue": "Affirmative (3)", "direction": "down", "length": 3, "position": {"x": 7, "y": 0}, "separatorLocations": {}, "solution": "YES", "group": ["4-down"]},
            {"id": "5-down", "number": 5, "humanNumber": "5", "clue": "Also (3)", "direction": "down", "length": 3, "position": {"x": 9, "y": 0}, "separatorLocations": {}, "solution": "AND", "group": ["5-down"]},
        ],
    },
    {
        "id": "puzzle-2",
        "number": 2,
        "name": "Quick Crossword 2",
        "creator": {"name": "Cinnabear", "webUrl": ""},
        "date": int(datetime.now().timestamp() * 1000),
        "webPublicationDate": int(datetime.now().timestamp() * 1000),
        "dimensions": {"cols": 11, "rows": 11},
        "crosswordType": "quick",
        "solutionAvailable": True,
        "dateSolutionAvailable": int(datetime.now().timestamp() * 1000),
        "entries": [
            {"id": "1-across", "number": 1, "humanNumber": "1", "clue": "Fruit with a peel (6)", "direction": "across", "length": 6, "position": {"x": 0, "y": 0}, "separatorLocations": {}, "solution": "BANANA", "group": ["1-across"]},
            {"id": "5-across", "number": 5, "humanNumber": "5", "clue": "Opposite of west (4)", "direction": "across", "length": 4, "position": {"x": 7, "y": 0}, "separatorLocations": {}, "solution": "EAST", "group": ["5-across"]},
            {"id": "6-across", "number": 6, "humanNumber": "6", "clue": "Flying mammal (3)", "direction": "across", "length": 3, "position": {"x": 0, "y": 2}, "separatorLocations": {}, "solution": "BAT", "group": ["6-across"]},
            {"id": "7-across", "number": 7, "humanNumber": "7", "clue": "Upper limb (3)", "direction": "across", "length": 3, "position": {"x": 4, "y": 2}, "separatorLocations": {}, "solution": "ARM", "group": ["7-across"]},
            {"id": "8-across", "number": 8, "humanNumber": "8", "clue": "Writing tool (3)", "direction": "across", "length": 3, "position": {"x": 8, "y": 2}, "separatorLocations": {}, "solution": "PEN", "group": ["8-across"]},
            {"id": "9-across", "number": 9, "humanNumber": "9", "clue": "Large body of water (3)", "direction": "across", "length": 3, "position": {"x": 0, "y": 4}, "separatorLocations": {}, "solution": "SEA", "group": ["9-across"]},
            {"id": "10-across", "number": 10, "humanNumber": "10", "clue": "Insect that makes honey (3)", "direction": "across", "length": 3, "position": {"x": 4, "y": 4}, "separatorLocations": {}, "solution": "BEE", "group": ["10-across"]},
            {"id": "11-across", "number": 11, "humanNumber": "11", "clue": "Obtain (3)", "direction": "across", "length": 3, "position": {"x": 8, "y": 4}, "separatorLocations": {}, "solution": "GET", "group": ["11-across"]},
            {"id": "12-across", "number": 12, "humanNumber": "12", "clue": "Permit (3)", "direction": "across", "length": 3, "position": {"x": 0, "y": 6}, "separatorLocations": {}, "solution": "LET", "group": ["12-across"]},
            {"id": "13-across", "number": 13, "humanNumber": "13", "clue": "Perform on stage (3)", "direction": "across", "length": 3, "position": {"x": 4, "y": 6}, "separatorLocations": {}, "solution": "ACT", "group": ["13-across"]},
            {"id": "14-across", "number": 14, "humanNumber": "14", "clue": "A tangle (4)", "direction": "across", "length": 4, "position": {"x": 0, "y": 8}, "separatorLocations": {}, "solution": "KNOT", "group": ["14-across"]},
            {"id": "15-across", "number": 15, "humanNumber": "15", "clue": "Circular shape (4)", "direction": "across", "length": 4, "position": {"x": 5, "y": 8}, "separatorLocations": {}, "solution": "RING", "group": ["15-across"]},
            {"id": "16-across", "number": 16, "humanNumber": "16", "clue": "Celestial body (4)", "direction": "across", "length": 4, "position": {"x": 0, "y": 10}, "separatorLocations": {}, "solution": "MOON", "group": ["16-across"]},
            {"id": "17-across", "number": 17, "humanNumber": "17", "clue": "Meal at midday (5)", "direction": "across", "length": 5, "position": {"x": 5, "y": 10}, "separatorLocations": {}, "solution": "LUNCH", "group": ["17-across"]},
            {"id": "1-down", "number": 1, "humanNumber": "1", "clue": "Sphere (4)", "direction": "down", "length": 4, "position": {"x": 0, "y": 0}, "separatorLocations": {}, "solution": "BALL", "group": ["1-down"]},
            {"id": "2-down", "number": 2, "humanNumber": "2", "clue": "A performance (3)", "direction": "down", "length": 3, "position": {"x": 2, "y": 0}, "separatorLocations": {}, "solution": "ACT", "group": ["2-down"]},
            {"id": "3-down", "number": 3, "humanNumber": "3", "clue": "Not out (2)", "direction": "down", "length": 2, "position": {"x": 4, "y": 0}, "separatorLocations": {}, "solution": "IN", "group": ["3-down"]},
            {"id": "4-down", "number": 4, "humanNumber": "4", "clue": "Simple (4)", "direction": "down", "length": 4, "position": {"x": 8, "y": 0}, "separatorLocations": {}, "solution": "EASY", "group": ["4-down"]},
        ],
    },
    {
        "id": "puzzle-3",
        "number": 3,
        "name": "Quick Crossword 3",
        "creator": {"name": "Cinnabear", "webUrl": ""},
        "date": int(datetime.now().timestamp() * 1000),
        "webPublicationDate": int(datetime.now().timestamp() * 1000),
        "dimensions": {"cols": 9, "rows": 9},
        "crosswordType": "quick",
        "solutionAvailable": True,
        "dateSolutionAvailable": int(datetime.now().timestamp() * 1000),
        "entries": [
            {"id": "1-across", "number": 1, "humanNumber": "1", "clue": "Tall plant with trunk (4)", "direction": "across", "length": 4, "position": {"x": 0, "y": 0}, "separatorLocations": {}, "solution": "TREE", "group": ["1-across"]},
            {"id": "4-across", "number": 4, "humanNumber": "4", "clue": "Body of water (4)", "direction": "across", "length": 4, "position": {"x": 5, "y": 0}, "separatorLocations": {}, "solution": "LAKE", "group": ["4-across"]},
            {"id": "5-across", "number": 5, "humanNumber": "5", "clue": "Piece of furniture for sitting (5)", "direction": "across", "length": 5, "position": {"x": 0, "y": 2}, "separatorLocations": {}, "solution": "CHAIR", "group": ["5-across"]},
            {"id": "6-across", "number": 6, "humanNumber": "6", "clue": "Writing surface (4)", "direction": "across", "length": 4, "position": {"x": 0, "y": 4}, "separatorLocations": {}, "solution": "DESK", "group": ["6-across"]},
            {"id": "7-across", "number": 7, "humanNumber": "7", "clue": "Not closed (4)", "direction": "across", "length": 4, "position": {"x": 5, "y": 4}, "separatorLocations": {}, "solution": "OPEN", "group": ["7-across"]},
            {"id": "8-across", "number": 8, "humanNumber": "8", "clue": "Timepiece (5)", "direction": "across", "length": 5, "position": {"x": 0, "y": 6}, "separatorLocations": {}, "solution": "CLOCK", "group": ["8-across"]},
            {"id": "9-across", "number": 9, "humanNumber": "9", "clue": "Opposite of night (3)", "direction": "across", "length": 3, "position": {"x": 6, "y": 6}, "separatorLocations": {}, "solution": "DAY", "group": ["9-across"]},
            {"id": "10-across", "number": 10, "humanNumber": "10", "clue": "Illumination source (4)", "direction": "across", "length": 4, "position": {"x": 0, "y": 8}, "separatorLocations": {}, "solution": "LAMP", "group": ["10-across"]},
            {"id": "11-across", "number": 11, "humanNumber": "11", "clue": "Literary work (4)", "direction": "across", "length": 4, "position": {"x": 5, "y": 8}, "separatorLocations": {}, "solution": "BOOK", "group": ["11-across"]},
            {"id": "1-down", "number": 1, "humanNumber": "1", "clue": "Foot covering (4)", "direction": "down", "length": 4, "position": {"x": 0, "y": 0}, "separatorLocations": {}, "solution": "TACK", "group": ["1-down"]},
            {"id": "2-down", "number": 2, "humanNumber": "2", "clue": "Opposite of exit (5)", "direction": "down", "length": 5, "position": {"x": 2, "y": 0}, "separatorLocations": {}, "solution": "ENTRY", "group": ["2-down"]},
            {"id": "3-down", "number": 3, "humanNumber": "3", "clue": "Epoch (3)", "direction": "down", "length": 3, "position": {"x": 4, "y": 2}, "separatorLocations": {}, "solution": "ERA", "group": ["3-down"]},
        ],
    },
]


async def seed():
    """Seed the database with puzzles."""
    await init_db()

    async with async_session() as session:
        for puzzle_data in PUZZLES:
            # Check if puzzle already exists
            result = await session.execute(
                select(Puzzle).where(Puzzle.puzzle_number == puzzle_data["number"])
            )
            existing = result.scalar_one_or_none()

            if existing:
                print(f"Puzzle {puzzle_data['number']} already exists, skipping")
                continue

            puzzle = Puzzle(
                puzzle_number=puzzle_data["number"],
                name=puzzle_data["name"],
                data=puzzle_data,  # Store entire object as JSONB
            )
            session.add(puzzle)
            print(f"Added puzzle: {puzzle_data['name']}")

        await session.commit()
        print("Seeding complete!")


if __name__ == "__main__":
    asyncio.run(seed())
