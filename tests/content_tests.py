import pytest
import datetime
from ezcv.content import sort_content
# Testing content types

## Test Content class methods

## Test Markdown class

def test_sort_content_alphabetical():
    content = [
        [{"title": "Zebra", "institution": "Zoo"}, "<html>...</html>", "zebra.html"],
        [{"title": "apple", "institution": "Farm"}, "<html>...</html>", "apple.html"],
        [{"institution": "Library", "created":None, "updated":None}, "<html>...</html>", "banana.html"],  # No title, fallback to file name
        [{"title": "Apple", "institution": "Tech"}, "<html>...</html>", "apple-tech.html"]
    ]

    expected_titles = ["Apple","apple", "banana.html", "Zebra"]

    sorted_content = sort_content(content, "alphabetical")
    sorted_titles = [item[0].get("title", item[2]) for item in sorted_content]

    assert sorted_titles == expected_titles

def test_sort_content_newest():
    current_year = datetime.datetime.now().year
    current_month = datetime.datetime.now().month

    content = [
        # Item with explicit recent date
        [{"title": "Item C", "year_started": 2024, "month_started": 5}, "<html></html>", "fileC.md"],
        # Item with older date
        [{"title": "Item A", "year_started": 2020, "month_started": 6}, "<html></html>", "fileA.md"],
        # Item with current date (missing year/month — will default)
        [{"title": "Item B"}, "<html></html>", "fileB.md"],
    ]

    sorted_content = sort_content(content, "newest")

    # Extract just the titles for easy assertion
    sorted_titles = [item[0]["title"] for item in sorted_content]

    # Expected: newest -> current (default) -> oldest
    expected_order = ["Item C", "Item A", "Item B"]

    assert sorted_titles == expected_order, f"Expected {expected_order}, got {sorted_titles}"

def make_entry(title, year_started, month_started, current=False, created=None, updated=None, file_name="file.md"):
    now = datetime.datetime.now()
    created = created or now
    updated = updated or now
    return [{
        "title": title,
        "year_started": year_started,
        "month_started": month_started,
        "current": current,
        "created": created,
        "updated": updated,
    }, "<html>", file_name]

def test_sort_created():
    old = make_entry("Old File", 2022, 1, created=datetime.datetime(2022, 1, 1))
    mid = make_entry("Mid File", 2023, 1, created=datetime.datetime(2023, 1, 1))
    new = make_entry("New File", 2024, 1, created=datetime.datetime(2024, 1, 1))

    sorted_result = sort_content([old, new, mid], "created")
    titles = [item[0]["title"] for item in sorted_result]
    assert titles == ["New File", "Mid File", "Old File"]

def test_sort_updated():
    old = make_entry("Old File", 2022, 1, updated=datetime.datetime(2022, 1, 1))
    mid = make_entry("Mid File", 2023, 1, updated=datetime.datetime(2023, 1, 1))
    new = make_entry("New File", 2024, 1, updated=datetime.datetime(2024, 1, 1))

    sorted_result = sort_content([old, new, mid], "updated")
    titles = [item[0]["title"] for item in sorted_result]
    assert titles == ["New File", "Mid File", "Old File"]

def test_sort_present():
    current_entry = make_entry("Current Project", 2023, 5, current=True)
    past_entry = make_entry("Old Project", 2020, 4, current=False)
    past_entry_2 = make_entry("Old Project 2", 2021, 4, current=False)
    middle_entry = make_entry("Mid Project", 2019, 6, current=True)
    middleish_entry = make_entry("Middleish Project", 2018, 6, current=True)

    sorted_result = sort_content([past_entry, middleish_entry,middle_entry, current_entry, past_entry_2], "present")
    titles = [item[0]["title"] for item in sorted_result]
    assert titles == ["Current Project", "Mid Project", "Middleish Project","Old Project 2", "Old Project"]


## Test image class