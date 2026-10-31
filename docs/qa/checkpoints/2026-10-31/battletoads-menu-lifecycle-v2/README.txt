BT menu/lifecycle metadata-only correction; source candidate35842285 exact

Frozen v1 API derived a ROM bank from DBG ooffs for RAM3 image segments. Those
offsets are into cache.bin, not the NES PRG payload. The corrected API explicitly
labels raw3 execution and image offsets for all cached workers. ROM loader and
cold callbacks keep true ROM-bank fields. No source, build output, tests or old
receipt changed. V1 and its reporting negative remain in the source archive.

The full inherited menu/lifecycle/source controls and limitations are unchanged:
BT remains pending actual shared mixed-cold/parser/Main and native qualification.
Installed f56 three Peach constants must still be genuinely composed. Use this
row-and-cold-API.json rather than the original v1 symbol report.
