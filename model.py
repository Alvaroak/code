from dataclasses import dataclass
from datetime import datetime

@dataclass(frozen=True)
class OrderLine() :
    order_id: str
    sku: str
    qty: int


class Batch():
    def __init__(self, ref: str, sku: str, qty: int, eta: datetime.date):
        self.reference = ref
        self.sku = sku
        self.eta = eta
        self._purchased_qty = qty
        # self.available_qty = qty
        self._allocated_lines = set() # type Set[OrderLine]

    def allocate(self, line: OrderLine) -> None:
        # self.available_qty -= line.qty
        self._allocated_lines.add(line)


    def de_allocate(self, line: OrderLine) -> None:
        if line in self._allocated_lines:
            self._allocated_lines.remove(line)


    @property
    def allocated_quantity(self) -> int:
        return sum(l.qty for l in self._allocated_lines)


    @property
    def available_qty(self) -> int:
        return self._purchased_qty - self.allocated_quantity


    def can_allocate(self, line: OrderLine) -> bool:
        return self.sku == line.sku and self.available_qty >= line.qty

    
    def __gt__(self, other):
        if self.eta is None:
            return False
        if other.eta is None:
            return True
        return self.eta > other.eta
            
        


def allocate_with_priority(line: OrderLine, batches: list[Batch]) -> Batch:
    batch = next(b for b in sorted(batches) if b.can_allocate(line))
    batch.allocate(line)
    return batch.reference
