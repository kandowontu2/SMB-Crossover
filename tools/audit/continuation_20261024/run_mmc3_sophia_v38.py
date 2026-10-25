from pathlib import Path
import json
D=Path(__file__).resolve().parent
V=D/'mmc3-static-call-v37'
aborted=V/'native-sophia-v1/aborted-host-observer.json'
assert not aborted.exists()
aborted.write_text(json.dumps(dict(passed=False,complete=False,host_observer_aborted=True,reason='Full emu.getState on every stack write made the observer too slow for its fixed host timeout. Stopped only the owned test processes; retained all original logs. No gameplay or guard assertion was waived. V2 records the address of each native stack write directly, protects the same six bytes/five NMI payloads and enforces the same stack floor.'),indent=2))
s=(D/'run_mmc3_sophia_v37.py').read_text(encoding='utf-8')
anchor="exec(compile(s,str(D/'run_mmc3_sophia_v27.py'),'exec'),globals())"
replacement="""s=s.replace("O=V/'native-sophia-v1'","O=V/'native-sophia-v2'").replace('mmc3_tiny_call_guard_v1.lua','mmc3_tiny_call_guard_v2.lua')
s=s.replace("for kind in['fresh','prefix']:","for kind in['fresh']:")
s=s.replace('exact failed physical-input prefix beyond original freeze plus fresh adaptive full1-1 clear','fresh adaptive full1-1 attempt with native original audio and exact stack/code/NMI/bank guards; fixed prior physical inputs remain a separate diagnostic')
exec(compile(s,str(D/'run_mmc3_sophia_v27.py'),'exec'),globals())"""
assert s.count(anchor)==1
s=s.replace(anchor,replacement)
exec(compile(s,str(D/'run_mmc3_sophia_v37.py'),'exec'),globals())
