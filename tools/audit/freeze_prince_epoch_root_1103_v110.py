"""Retain the zero-growth entrance repair prototype and real interrupt proof."""
import json,zipfile
from pathlib import Path
from prepare_selected_native_packet_v1 import R,sha
O=R/'build/prince-epoch-root-freeze-1103-v110'
D=R/'docs/qa/checkpoints/2026-11-03/prince-epoch-prototype-v110'
def main():
    O.mkdir(exist_ok=True);p=R/'build/prince-actor-1101-v1';sources=[Path(__file__),*(R/'tools/audit'/n for n in['measure_prince_spawn_epoch_1103_v145.py','check_prince_spawn_epoch_1103_v146.py','check_prince_spawn_epoch_isr_1103_v147.py','check_prince_spawn_epoch_nested_1103_v148.py'])]
    proofs=[p/n for n in['deferred-strike-measurement-v145.json','spawn-epoch-CPU-v146.json','spawn-epoch-ISR-CPU-v147.json','post-return-nested-IRQ-CPU-v148.json']]
    for f in proofs:
        q=json.loads(f.read_text())
        if f==proofs[0]:assert q['spawn_resync_proposal']and q['entry_addresses_unchanged']and q['source_backing_growth']==0
        else:assert q['passed']
        for name,h in q.get('bindings',{}).items():assert sha(R/name)==h,name
    irq=json.loads(proofs[2].read_text());nested=json.loads(proofs[3].read_text())
    assert irq['real_IRQ_actual_FF_lagNMI']=={'IRQ':628,'lagNMI':628}and irq['minimum_SP']==130
    assert nested['counts']=={'lag_NMI_gather':628,'nested_IRQ':777}and nested['minimum_nested_IRQ_SP']==125
    files=sources+proofs+[p/n for n in['native-services-v145.s','native-public-v145.s','native-metadata-v145.bin','native-labels-v145.json','spawn-epoch-negative-v146.json']]
    D.mkdir(parents=True);target=D/'inputs.zip'
    with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED,compresslevel=9)as z:
        for f in files:z.writestr(f.relative_to(R).as_posix(),f.read_bytes())
    assert target.stat().st_size<256000
    with zipfile.ZipFile(target)as z:
        for f in files:assert z.read(f.relative_to(R).as_posix())==f.read_bytes()
    out=dict(passed=True,source_prototype_only=True,source_code_injected=True,changed_full_cold_qualified=False,ROM_written=False,installed=False,archive_SHA256=sha(target),archive_bytes=target.stat().st_size,source_files=[f.relative_to(R).as_posix()for f in sources],scope='Zero-growth145 private metadata prototype reimports the original constructor from actual native coordinates once at the first engine8 epoch. Native engine7 entrance unchanged; genuine entrance176/1 stays176/1 and sourcefoot208 instead of staleY0. All existing entries and code/state payloads unchanged; no fixedY/new state/shared span. Old constructor Ready0 caller closure includes realcold and16Fresh cases. New ReadyA7 resync passes628IRQ+628genuineFF/777nestedIRQ, minimum130/125; subsequent epochs retain HP3/sword2. Actual new compressed backing/cookie/fullcold/native-emulator replays and separate area-backdrop/status fixes remain pending. This prototype has not changed the nightly.',bindings={f.relative_to(R).as_posix():sha(f)for f in files})
    (D/'receipt.json').write_text(json.dumps(out,indent=2)+'\n');(O/'receipt.json').write_text(json.dumps(out,indent=2)+'\n')
    a=R/'docs/qa/continuation-current.json';h=json.loads(a.read_text());h['Prince_native_current_1103'].update(epoch_prototype_checkpoint=D.relative_to(R).as_posix(),epoch_prototype_status='ZERO_GROWTH_CPU_IRQ_FF_NESTED_PASS_NOT_REBOUND_TO_COLD',epoch_prototype_scope=out['scope']);a.write_text(json.dumps(h,indent=2)+'\n')
    print(json.dumps({k:v for k,v in out.items()if k!='bindings'}))
if __name__=='__main__':main()
