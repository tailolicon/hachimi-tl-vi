from __future__ import annotations

from collections.abc import Sequence

from .model import SourceEntry, Translation
from .qa import qa_pair
from .store import Store
from .translators.base import Translator


def batched(values: Sequence[SourceEntry], size: int):
    for i in range(0, len(values), size):
        yield values[i:i + size]


def translate_pending(
    store: Store,
    translator: Translator,
    *,
    kind: str | None = None,
    limit: int | None = None,
    batch_size: int = 20,
    reject_qa_errors: bool = True,
) -> dict[str, int]:
    pending = store.pending_entries(kind=kind, limit=limit)
    translated = 0
    rejected = 0
    for batch in batched(pending, max(1, batch_size)):
        output = translator.translate_batch(batch)
        for entry in batch:
            target = output[entry.uid]
            qa = qa_pair(entry.source_text, target)
            if reject_qa_errors and not qa["ok"]:
                rejected += 1
                continue
            store.save_translation(Translation(
                fingerprint=entry.fingerprint,
                target_text=target,
                status="translated",
                provider=translator.__class__.__name__,
                model=getattr(translator, "model", "unknown"),
                qa=qa,
            ))
            translated += 1
    return {"pending_seen": len(pending), "translated": translated, "rejected": rejected}
