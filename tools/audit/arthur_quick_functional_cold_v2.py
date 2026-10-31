"""Retain v1's real Select-C-publication harness negative; use native ABI.

The genuine Select input queues the Roll/Quick portrait and intentionally
publishes the resolved graphics C bank. A, low/fixed banks and matching C
hardware/shadow remain strictly checked by the original execution helper.
"""
from pathlib import Path
p=Path(__file__).with_name('arthur_quick_functional_cold_v1.py')
s=p.read_text()
assert s.count("A.O/'cold'")==1
s=s.replace("A.O/'cold'","A.O/'cold-v2'")
old="'QueueSelection','InitializeArea'"
assert s.count(old)==1
s=s.replace(old,"'QueueSelection','CrossoverMenuInput','InitializeArea'")
exec(compile(s,__file__,'exec'),globals())
