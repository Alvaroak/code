from datetime import date, timedelta
import pytest

# from model import ...
from model import OrderLine, Batch, allocate_with_priority
from datetime import datetime

today = date.today()
tomorrow = today + timedelta(days=1)
later = tomorrow + timedelta(days=10)

def make_test_batch_and_line(batch_sku: str, batch_qty: int, line_qty: int, line_sku: str=None, batch_eta: datetime.date=today):
    if not line_sku:
        line_sku = batch_sku
    return (
        Batch("batch_1", batch_sku, qty=batch_qty, eta=batch_eta),
        OrderLine("ref 123", line_sku, qty=line_qty)
    )


def test_allocating_to_a_batch_reduces_the_available_quantity():
    # pytest.fail("todo")
    # batch = Batch("batch_1", "SHORT-LAMP", qty=10, eta=date.today())
    # line = OrderLine("ref 123", "SHORT-LAMP", qty=2)

    batch, line = make_test_batch_and_line("SHORT-LAMP", 10, 2)
    batch.allocate(line)
    assert batch.available_qty == 8

def test_can_allocate_if_available_greater_than_required():
    batch, line = make_test_batch_and_line("SHORT-LAMP", 10, 2)
    assert batch.available_qty > line.qty
    assert batch.can_allocate(line)


def test_cannot_allocate_if_available_smaller_than_required():
    batch, line = make_test_batch_and_line("SHORT-LAMP", 10, 12)
    assert batch.available_qty < line.qty
    assert batch.can_allocate(line) is False


def test_can_allocate_if_available_equal_to_required():
    batch, line = make_test_batch_and_line("SHORT-LAMP", 10, 10)
    assert batch.available_qty == line.qty
    assert batch.can_allocate(line)


def test_cannot_allocate_if_skus_do_not_match():
    batch, line = make_test_batch_and_line("SHORT-LAMP", 10, 2, "LARGE-LAMP")
    assert batch.can_allocate(line) is False


def test_can_onlt_Deallocate_allocated_lines():
    batch, line = make_test_batch_and_line("SHORT-LAMP", 10, 2, "LARGE-LAMP")
    batch.de_allocate(line)
    assert batch.available_qty == 10


def test_duplicate_allocations_not_allowed():
    batch, line = make_test_batch_and_line("SHORT-LAMP", 10, 2)
    batch.allocate(line)
    batch.allocate(line)
    assert batch.available_qty == 8


def test_prefers_warehouse_batches_to_shipments():
    stock_batch = Batch("batch_1", "SHORT-LAMP", qty=10, eta=None)
    shipment_batch = Batch("batch_1", "SHORT-LAMP", qty=10, eta=today)
    line = OrderLine("ref 123", "SHORT-LAMP", qty=2)
    allocated_batch_ref = allocate_with_priority(line, [stock_batch, shipment_batch])
    assert allocated_batch_ref == stock_batch.reference


def test_prefers_earlier_batches():
    today_batch = Batch("batch_1", "SHORT-LAMP", qty=10, eta=today)
    tomorrow_batch = Batch("batch_1", "SHORT-LAMP", qty=10, eta=tomorrow)
    later_batch = Batch("batch_1", "SHORT-LAMP", qty=10, eta=later)
    line = OrderLine("ref 123", "SHORT-LAMP", qty=2)
    allocated_batch_ref = allocate_with_priority(line, [later_batch, tomorrow_batch, today_batch])
    assert allocated_batch_ref == today_batch.reference


def test_prefers_earlier_qty_available_batches():
    today_batch = Batch("batch_1", "SHORT-LAMP", qty=1, eta=today)
    tomorrow_batch = Batch("batch_1", "SHORT-LAMP", qty=10, eta=tomorrow)
    later_batch = Batch("batch_1", "SHORT-LAMP", qty=10, eta=later)
    line = OrderLine("ref 123", "SHORT-LAMP", qty=2)
    allocated_batch_ref = allocate_with_priority(line, [later_batch, tomorrow_batch, today_batch])
    assert allocated_batch_ref == tomorrow_batch.reference
