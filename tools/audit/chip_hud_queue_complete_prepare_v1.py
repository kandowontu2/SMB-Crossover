"""Freeze successor diagnostic/full-route commands; ROOT alone launches."""
from pathlib import Path
from types import SimpleNamespace
import hashlib
import json

from current_roster_compact_11_v1 import prepare, lua, linked

R=Path(__file__).resolve().parents[2]
B=R/'build'
SHA='129dabe88489c78e1ead49b17e898979bd01ee0806d44eba2efc1871d4dd227f'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    rom=B/'chip_hud_queue_complete.nes'
    assert sha(rom)==SHA
    raw,syms,address,location,_=linked(rom)
    original=B/'verification/chip-d49f-easy-v1'
    probe=B/'verification/chip-d49f-late-vram-probe-v1'
    cfg=json.loads((probe/'startup-config.json').read_text())
    assert cfg['start_frame']==1470 and cfg['cutoff_frame']==1477
    for n,value in cfg['ram'].items():assert address(n)==value
    for h in cfg['hooks'].values():
        at=location(h['source_symbol'])+h['source_delta']
        assert address(h['source_symbol'])+h['source_delta']==h['pc']
        assert raw[at:at+len(h['bytes'])]==bytes(h['bytes'])
        for k in h['banks']:
            physical=16+k*8192+(h['pc']&8191)
            assert raw[physical:physical+len(h['bytes'])]==bytes(h['bytes'])
    cfg['ROM_sha256']=SHA
    module=R/'tools/audit/chip_render_vram_probe_v1.lua'
    harness=R/'tools/audit/current_roster_compact_11_v1.lua'
    policy=R/'tools/playthroughs/current_roster_chip_pickup_v2.lua'
    packets=[]
    for phase in ['diagnostic','full-route']:
        out=B/'verification'/('chip-129d-late-replay-v1'if phase=='diagnostic'else'chip-129d-easy-v1')
        prepare(SimpleNamespace(rom=rom,expected_sha256=SHA,output=out,identity='chip',mode='easy',
            frames=1500 if phase=='diagnostic'else 8000,policy=policy,
            replay=original/'inputs.csv'if phase=='diagnostic'else None))
        config=out/'startup-config.json';config.write_text(json.dumps(cfg,indent=2)+'\n',newline='\n')
        run=out/'run.lua';text=run.read_text();needle='dofile('+lua(harness.as_posix())+')'
        assert text.count(needle)==1
        append=('PROTO_STARTUP_VRAM_TIMING='+lua(cfg)+'\n'
            'local previousClose=ROSTER_CONFIG.bass_close\n'
            'local chipClose=dofile('+lua(module.as_posix())+')\n'
            'ROSTER_CONFIG.bass_close=function()local q=previousClose and previousClose()or{};'
            'q.chip_vram_probe=chipClose();return q end\n')
        run.write_text(text.replace(needle,append+needle),newline='\n')
        ready=out/'ready.json';z=json.loads(ready.read_text());z['bindings'][str(run)]=sha(run)
        for p in [Path(__file__),module,config,B/'chip_hud_queue_complete_build.json',
                B/'chip_hud_queue_complete_controls.json',original/'ready.json',original/'result.json',
                original/'inputs.csv',original/'events.jsonl',probe/'startup-config.json',
                probe/'chip-render-vram.csv',probe/'result.json',probe/'launch.json']:
            z['bindings'][str(p)]=sha(p)
        z['scope']=dict(prepared_only=True,native_run=False,phase=phase,
            actual_parent='adopted5a with Kirby/Mike retained, only current Chip bank79 changes',
            exact_original_inputs=1475 if phase=='diagnostic'else None,
            unchanged_controller_and_strict_guards=True,old_d49f_FALSE_retained=True,
            terminal='Original input exhaustion remains a diagnostic-only FALSE, never a route PASS.'if phase=='diagnostic'else'Original adaptive8000 route; independent saved-input replay still required after clear.',
            actual_timing_window=[1470,1477],new_CSV_files=1,new_PNG_files=0,
            cost='Observed second producer sequence costs946 additional foreground CPU while saving336 consumer/NMI CPU. Not a lag-win claim; native cadence/full route remain required.')
        ready.write_text(json.dumps(z,indent=2)+'\n',newline='\n')
        assert all(sha(p)==h for p,h in z['bindings'].items())
        (out/'command.json').write_text(json.dumps(z['command'],indent=2)+'\n',newline='\n')
        packets.append(dict(phase=phase,ready=str(ready),sha256=sha(ready),bindings=len(z['bindings']),command=str(out/'command.json')))
    out=B/'chip_hud_queue_complete_prepared.json'
    out.write_text(json.dumps(dict(prepared_only=True,native_run=False,candidate_sha256=SHA,packets=packets),indent=2)+'\n',newline='\n')
    print(json.dumps(dict(prepared_only=True,path=str(out),sha256=sha(out),packets=packets),indent=2))


if __name__=='__main__':main()
