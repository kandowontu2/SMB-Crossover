"""Run passive phase/status diagnostics; require original native evidence exact."""
from pathlib import Path
import hashlib,json,sys
ROOT=Path(__file__).resolve().parents[2]
PACKET=ROOT/'build/verification/ryu49-head-phase-observer-g'
OUT=ROOT/'build/verification/root49o2-head-phase-status-g-d'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
BINDINGS={'mmc3':'556297ae4f7ccabb56f62060c7aef708d4bbe1e2c3faebfb61d9746da8185a18',
          'mmc5':'68fad312a9bb1384ed494b7606fa188b1ad50daca12097f12b26d2486a93c3bd'}

def main():
    sys.dont_write_bytecode=True;assert not OUT.exists()
    assert sha(PACKET/'freeze.json')=='f2b15f9bb83b3d3a8e2de6ce6fd13d6e174b128450f7da0dfabc4f1958d5762d'
    frozen=json.loads((PACKET/'freeze.json').read_text())
    for n,r in frozen['files'].items():assert sha(PACKET/n)==r['sha256']
    sys.path.insert(0,str(ROOT/'tools/playthroughs'));from roster_run import workspace_bytes
    assert workspace_bytes(ROOT)+40_000_000+225_000_000<50_000_000_000
    sys.path.insert(0,str(ROOT/'tools'));import run_mesen
    parser=ROOT/'build/verification/agent47-samus-controller-batch-h-preparation/parser'
    provenance=json.loads((parser/'provenance.json').read_text())
    for p in [provenance['wheel']]+provenance['extracted']:assert sha(Path(p['path']))==p['sha256']
    sys.path.insert(0,str(parser/'runtime'));from lupa.lua54 import LuaRuntime
    parse=LuaRuntime().eval("function(s,n)local f,e=load(s,n,'t');return f~=nil,e end")
    for filename in ('component.lua','observer-append.lua'):
        good,error=parse((PACKET/filename).read_text(),filename);assert good,error
    OUT.mkdir();report={'status':'running-passive-phase-status','accepted_release':False,'goal_complete':False,
                       'script_sha256':sha(Path(__file__)),'cases':[]}
    def save():(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    save()
    for mapper,h in BINDINGS.items():
        folder=PACKET/f'binding-e-{mapper}-phase-g-a';binding=folder/'binding.json';assert sha(binding)==h
        b=json.loads(binding.read_text());rom=Path(b['rom'])
        assert sha(rom)==b['rom_sha256']and sha(rom.with_suffix('.dbg'))==b['dbg_sha256']and sha(rom.with_suffix('.lbl'))==b['lbl_sha256']
        script=folder/f'e-{mapper}-phase-g-a.lua';assert sha(script)==b['wrapper_sha256']
        good,error=parse(script.read_text(),str(script));assert good,error
        out=folder/'native-output';assert out.is_dir()and not any(out.iterdir())
        c={'mapper':mapper,'binding_sha256':h,'rom_sha256':sha(rom)};report['cases'].append(c);save()
        code=run_mesen.run(script,rom,timeout=300,
                          emulator_options=['--nes.ramPowerOnState=AllZeros',
                                            '--nes.randomizeCpuPpuAlignment=false',
                                            '--nes.randomizeMapperPowerOnState=false'])
        c['native_exit']=code;save()
        before=ROOT/f'build/verification/ryu49o2-head-components-f/binding-e-{mapper}-root-f-a/native-output'
        literal={}
        for n in ('receipts.csv','snapshots.ram','writes.bin','events.csv'):
            assert(out/n).read_bytes()==(before/n).read_bytes(),('Passive observer full stream neutrality',mapper,n)
            literal[n]=sha(out/n)
        old=json.loads((before/'result.json').read_text());new=json.loads((out/'result.json').read_text())
        extra={n:{'bytes':(out/n).stat().st_size,'sha256':sha(out/n)}for n in ('phase-diag.csv','status-contracts.csv')}
        delta=new['payload_bytes_before_result']-old['payload_bytes_before_result']
        assert delta==sum(r['bytes']for r in extra.values()),('Exact supplemental byte accounting',delta,extra)
        wanted=dict(old);wanted['payload_bytes_before_result']=new['payload_bytes_before_result'];assert wanted==new
        c.update(all_four_native_streams_literal=literal,original_result_assertions_and_frames_exact=True,
                 only_result_payload_bytes_delta=delta,supplements=extra,result=new)
        assert code==1 and new['failures']==4 and new['completed']==126
        save()
    for n,r in frozen['files'].items():assert sha(PACKET/n)==r['sha256']
    report.update(status='PASS_TWO_PASSIVE_NATIVE_STREAM_NEUTRALITY_CHECKS_ORIGINAL_CASE61_NEGATIVE_RETAINED',
                  workspace_bytes=workspace_bytes(ROOT),qualification='Actual stack/status contracts and case61 telemetry require host review. Original126 arena/controller assertions and watchdog remain unchanged; no source or release acceptance.')
    save();print(json.dumps({'status':report['status'],'report_sha256':sha(OUT/'report.json')}))

if __name__=='__main__':main()
