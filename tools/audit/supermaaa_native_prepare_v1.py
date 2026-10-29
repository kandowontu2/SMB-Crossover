"""Prepare one fully handoff-bound SuperMaaa native route; never launch here."""
from pathlib import Path
import argparse
import json
import current_roster_compact_11_v1 as base
from checkpoint_roster_packets_v1 import verify
from roster_expansion_native_prepare_v2 import navigation


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--rom',type=Path,required=True)
    p.add_argument('--expected-sha256',required=True)
    p.add_argument('--handoff',type=Path,required=True)
    p.add_argument('--handoff-sha256',required=True)
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--mode',choices=['easy','hard'],default='easy')
    p.add_argument('--frames',type=int,default=7000)
    p.add_argument('--private-emulator',type=Path,required=True)
    a=p.parse_args();a.identity='supermaaa';a.replay=None
    a.policy=base.ROOT/'tools/playthroughs/supermaaa_11_v1.lua'
    hp=a.handoff.resolve();assert base.sha(hp)==a.handoff_sha256
    h=json.loads(hp.read_text());bound={};verify(h,bound)
    assert isinstance(h['bindings'],dict)
    for path,digest in h['bindings'].items():
        assert base.sha(path)==digest,path
        bound[str(Path(path).resolve())]=digest
    assert h['candidate_ROM']==a.expected_sha256==base.sha(a.rom)
    for suffix,key in [('.dbg','candidate_DBG'),('.lbl','candidate_LBL')]:
        path=a.rom.resolve().with_suffix(suffix)
        assert base.sha(path)==h[key]
        bound[str(path)]=h[key]
    bound[str(a.rom.resolve())]=a.expected_sha256
    base.BASE.update(supermaaa=(0,0,'MarioVariant',2))
    base.navigation=navigation
    base.SCRIPT=Path(__file__).with_name('roster_expansion_cold_capture_v3.lua')
    base.prepare(a)
    ready=a.output.resolve()/'ready.json';d=json.loads(ready.read_text())
    d['bindings'].update(bound)
    for dep in [hp,Path(__file__),Path(__file__).with_name('checkpoint_roster_packets_v1.py'),
                Path(__file__).with_name('roster_expansion_native_prepare_v2.py')]:
        d['bindings'][str(dep.resolve())]=base.sha(dep)
    emulator=a.private_emulator.resolve();proof=emulator.parent/'proof.json'
    e=json.loads(proof.read_text())
    assert e['passed']and e['host_callback_1_3_seconds_completed']
    assert e['only_setting_changed']=='Debug.ScriptWindow.ScriptTimeout'
    for path,digest in e['bindings'].items():
        assert base.sha(path)==digest;d['bindings'][path]=digest
    d['bindings'][str(proof)]=base.sha(proof)
    i=d['command'].index('--emulator')+1
    assert d['command'][i]=='C:/Mesen2/Mesen.exe'
    d['command'][i]=str(emulator)
    d['host_callback_budget_seconds']=5
    d['controller_scope']='Cold genuine Select32 cycle to raw0/MarioVariant2, actual Start16/lives and ordinary pad1-1 discovery. Original timer/stomp neck mechanics; no emulated writes/cheats. Normal8-sprite hardware, bounded lossless container and strict DMA/CHR/camera/interrupt guards. No all-item/ability or FPS claim.'
    ready.write_text(json.dumps(d,indent=2)+'\n')
    print(json.dumps(dict(ready=str(ready),sha256=base.sha(ready),bound_handoff_inputs=len(bound))))


if __name__=='__main__':
    main()
