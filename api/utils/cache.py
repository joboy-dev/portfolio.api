from typing import Any, Dict, List, Optional


class FeatureCache:
    """In-memory cache for one feature/resource.

    Shape mirrors what's asked for: {"total": int, "data": {<identifier>: <dict>, ...}}
    `data` keys are whichever identifier(s) a model's `fetch_by_id` accepts
    (id, unique_id, and slug where the model has one), all pointing at the
    same cached dict so a lookup by any of them is a cache hit.

    A single item is stored under several keys in `data`, so `data`'s length
    isn't the item count and can't drive pagination math. A separate
    insertion-ordered list tracks distinct items added via `store_page` and
    is what `has_page`/`get_page` slice from. Items cached individually via
    `store_item` only land in `data` (for id lookups) — they're not spliced
    into that ordered list, since their true page position is unknown.

    Pagination assumes pages are walked sequentially (1, 2, 3, ...) under a
    stable sort/filter. Callers must bypass the cache whenever search/filter/
    sort params deviate from the route's default "browse all" case.
    """

    def __init__(self):
        self._total: Optional[int] = None
        self._data: Dict[str, Dict[str, Any]] = {}
        self._order: List[Dict[str, Any]] = []

    def is_loaded(self) -> bool:
        return self._total is not None

    @property
    def total(self) -> int:
        return self._total or 0

    def cached_count(self) -> int:
        return len(self._order)

    def has_page(self, page: int, per_page: int) -> bool:
        """True if enough sequentially-cached items exist to serve this page."""

        if not self.is_loaded():
            return False

        required = page * per_page
        return self.cached_count() >= required or required >= self.total

    def get_page(self, page: int, per_page: int) -> List[Dict[str, Any]]:
        offset = (page - 1) * per_page
        return self._order[offset:offset + per_page]

    def store_page(self, items: List[Dict[str, Any]], total: int, *id_fields: str):
        self._total = total
        for item in items:
            self._order.append(item)
            self._index_item(item, *id_fields)

    def get_item(self, identifier: str) -> Optional[Dict[str, Any]]:
        return self._data.get(identifier)

    def store_item(self, item: Dict[str, Any], *id_fields: str):
        self._index_item(item, *id_fields)

    def put(self, identifier: str, item: Dict[str, Any]):
        """Stores `item` under an explicit, arbitrary key (eg. for singleton resources)."""

        self._total = 1
        self._data[identifier] = item

    def _index_item(self, item: Dict[str, Any], *id_fields: str):
        for field in id_fields:
            key = item.get(field)
            if key:
                self._data[str(key)] = item

    def clear(self):
        self._total = None
        self._data = {}
        self._order = []


_caches: Dict[str, FeatureCache] = {}


def get_cache(name: str) -> FeatureCache:
    """Returns the shared FeatureCache for `name`, creating it on first use."""

    if name not in _caches:
        _caches[name] = FeatureCache()
    return _caches[name]
