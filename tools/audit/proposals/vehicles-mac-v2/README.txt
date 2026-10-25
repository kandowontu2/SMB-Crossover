Use proposal-v2 only. See review-tools/vehicles-mike-mac-source-audit-2026-10-25.txt for findings and explicit limits.
Two repairs: scrolled TMNT Kiai pickup coordinates and Mac extra-life boxing-state preservation. No installed source mutation.
proposal-v2/source contains private patched source; source-original is the restored exact f00 source snapshot. To reproduce, create a new external output, copy source-original into source, baseline.nes/.dbg/.lbl/.map plus frozen-source.json, then run review-tools/vehicles_mike_mac_audit_prepare_v1.py with --packet pointing at that output (use repository copy so ROOT resolves correctly). Do not rerun prepare against the already-edited proposal-v2.
Repair checks: vehicles_mike_mac_audit_cpu_v1.py --baseline baseline.nes --candidate candidate.nes --output a new directory.
Baseline family checks: vehicles_mike_mac_audit_source_v1.py --rom baseline.nes --source-root source-original --output a new directory.
Native integration, physical rendered/contact proof and adoption belong to ROOT.
