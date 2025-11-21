from backend.tools import search_inventory


def test_search_inventory_basic_sedan_range() -> None:
    """Basic integration-style test for the mocked inventory search."""
    results = search_inventory(body_type="sedan", min_price=18000, max_price=30000)

    # We expect at least one sedan in this band (Aurora / Horizon).
    assert results, "Expected at least one sedan in the 18k–30k price band"

    for vehicle in results:
        assert vehicle["body_type"].lower() == "sedan"
        assert 18_000 <= vehicle["price"] <= 30_000
        assert vehicle["in_stock"] is True


