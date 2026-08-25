from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from .compiler import compile_localized_data
from .extractors import import_asset_directory, import_localize_dump, import_master_mdb
from .indexer import generate_index
from .pipeline import translate_pending
from .store import Store
from .translators import OpenAICompatibleTranslator
from .validator import validate_project


def _print(value) -> None:
    print(json.dumps(value, ensure_ascii=False, indent=2))


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="tlvi", description="JP -> VI translation pipeline for Hachimi Edge")
    p.add_argument("--db", default="work/tlvi.db", help="Translation-memory SQLite path")
    sub = p.add_subparsers(dest="command", required=True)

    sub.add_parser("init", help="Initialize translation-memory database")

    x = sub.add_parser("import-mdb", help="Import Japanese strings from master.mdb")
    x.add_argument("path")

    x = sub.add_parser("import-localize", help="Import Hachimi localize_dump.json")
    x.add_argument("path")

    x = sub.add_parser("import-assets", help="Import Japanese Hachimi-compatible asset JSON directory")
    x.add_argument("path")

    x = sub.add_parser("translate", help="Translate pending entries using OpenAI-compatible API")
    x.add_argument("--kind")
    x.add_argument("--limit", type=int)
    x.add_argument("--batch-size", type=int, default=20)
    x.add_argument("--allow-qa-errors", action="store_true")
    x.add_argument("--api-base")
    x.add_argument("--api-key")
    x.add_argument("--model")

    x = sub.add_parser("manual", help="Set a manual translation by stable entry UID")
    x.add_argument("uid")
    x.add_argument("text")

    x = sub.add_parser("compile", help="Compile translated entries to localized_data")
    x.add_argument("--out", default="localized_data")

    x = sub.add_parser("validate", help="Validate Hachimi files and translation invariants")
    x.add_argument("--localized-dir", default="localized_data")

    x = sub.add_parser("index", help="Generate Hachimi updater index.json with BLAKE3")
    x.add_argument("--localized-dir", default="localized_data")
    x.add_argument("--base", default="index_base.json")
    x.add_argument("--out", default="index.json")

    sub.add_parser("status", help="Show corpus / translation-memory statistics")
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    with Store(args.db) as store:
        if args.command == "init":
            _print({"ok": True, "db": str(Path(args.db))})
        elif args.command == "import-mdb":
            _print(import_master_mdb(args.path, store))
        elif args.command == "import-localize":
            _print({"localize": import_localize_dump(args.path, store)})
        elif args.command == "import-assets":
            _print(import_asset_directory(args.path, store))
        elif args.command == "translate":
            translator = OpenAICompatibleTranslator(api_base=args.api_base, api_key=args.api_key, model=args.model)
            _print(translate_pending(
                store,
                translator,
                kind=args.kind,
                limit=args.limit,
                batch_size=args.batch_size,
                reject_qa_errors=not args.allow_qa_errors,
            ))
        elif args.command == "manual":
            store.set_manual_translation(args.uid, args.text)
            _print({"ok": True, "uid": args.uid})
        elif args.command == "compile":
            _print(compile_localized_data(store, args.out))
        elif args.command == "validate":
            report = validate_project(store, args.localized_dir)
            _print(report)
            return 0 if report["ok"] else 2
        elif args.command == "index":
            index = generate_index(args.localized_dir, args.base, args.out)
            _print({"ok": True, "files": len(index["files"]), "output": args.out})
        elif args.command == "status":
            _print(store.stats())
    return 0


if __name__ == "__main__":
    sys.exit(main())
