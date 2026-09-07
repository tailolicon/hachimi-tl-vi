from __future__ import annotations

"""Production-sync entry point for the Tanino Gimlet V-row source-bridge hardener."""

try:
    from scripts.harden_tanino_gimlet_v_row_source_bridge import ROOT, harden
except ModuleNotFoundError:  # direct `python scripts/...py` execution
    from harden_tanino_gimlet_v_row_source_bridge import ROOT, harden


def main() -> int:
    changed = harden(ROOT)
    print(f"tanino_gimlet_v_row_source_bridge_finding_changed={str(changed).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
