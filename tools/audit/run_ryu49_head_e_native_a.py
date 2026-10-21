"""Root execution of frozen E and original O2 head/foot native components."""
from pathlib import Path
import hashlib,json,sys
ROOT=Path(__file__).resolve().parents[2]
PACKET=ROOT/'build/verification/ryu49o2-head-components-e'
OUT=ROOT/'build/verification/root49o2-head-e-native-a'
CP=ROOT/'build/checkpoints/roster-audit-v49-provisional-o2'
PRIVATE=ROOT/'build/verification/root49o2-head-private-build-e/source/build'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    sys.dont_write_bytecode=True
    assert not OUT.exists()
    assert sha(PACKET/'freeze.json')=='af8cd27a8ca330d34e5d0d0ad01ca86b5849208077f3b7f2aef7ef0707760b86'
    assert sha(PACKET/'compiled-binding-e-a/report.json')=='e1b883b25ea2b5facaf001df76813d8491ffca4873315c8b91223d1e730de61b'
    freeze=json.loads((PACKET/'freeze.json').read_text())
    for n,r in freeze['files'].items():assert sha(PACKET/n)==r['sha256']
    sys.path.insert(0,str(ROOT/'tools/playthroughs'));from roster_run import workspace_bytes
    assert workspace_bytes(ROOT)+40_000_000+245_000_000<50_000_000_000
    sys.path.insert(0,str(ROOT/'tools'));import run_mesen
    parser=ROOT/'build/verification/agent47-samus-controller-batch-h-preparation/parser'
    provenance=json.loads((parser/'provenance.json').read_text())
    for p in [provenance['wheel']]+provenance['extracted']:assert sha(Path(p['path']))==p['sha256']
    sys.path.insert(0,str(parser/'runtime'));from lupa.lua54 import LuaRuntime
    parse=LuaRuntime().eval("function(s,n)local f,e=load(s,n,'t');return f~=nil,e end")
    ok,error=parse((PACKET/'component.lua').read_text(),'component');assert ok,error
    cases=[]
    for mapper in ('mmc3','mmc5'):
        for subject,build in (('o2',CP),('e',PRIVATE)):
            folder=PACKET/f'binding-{subject}-{mapper}-root-a'
            binding=folder/'binding.json';b=json.loads(binding.read_text())
            script=folder/f'{subject}-{mapper}-root-a.lua';ok,error=parse(script.read_text(),str(script));assert ok,error
            rom=build/f'smb-crossover-{mapper}.nes'
            assert sha(rom)==b['rom_sha256']and sha(rom.with_suffix('.dbg'))==b['dbg_sha256']and sha(rom.with_suffix('.lbl'))==b['lbl_sha256']
            assert not(folder/'native-output').exists()
            cases.append({'mapper':mapper,'subject':subject,'rom':str(rom),'rom_sha256':sha(rom),
                          'binding':str(binding),'binding_sha256':sha(binding),'script':str(script),'script_sha256':sha(script)})
    OUT.mkdir();report={'status':'running-frozen-E-native-components','accepted_release':False,'goal_complete':False,
                       'script_sha256':sha(Path(__file__)),'cases':cases}
    def save():(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    save()
    for c in cases:
        code=run_mesen.run(Path(c['script']),Path(c['rom']),timeout=300,
                           emulator_options=['--nes.ramPowerOnState=AllZeros',
                                             '--nes.randomizeCpuPpuAlignment=false',
                                             '--nes.randomizeMapperPowerOnState=false'])
        output=Path(c['binding']).parent/'native-output';log=ROOT/'build/verification'/(Path(c['rom']).stem+'-'+Path(c['script']).stem+'.log')
        c.update(native_exit=code,log_sha256=sha(log))
        if (output/'result.json').exists():
            c['result']=json.loads((output/'result.json').read_text());c['result_sha256']=sha(output/'result.json')
        save()
    for n,r in freeze['files'].items():assert sha(PACKET/n)==r['sha256']
    report.update(status='COMPLETE_NATIVE_RUNS_RETAIN_ALL_CONTROL_NEGATIVES_COMPONENT_REVIEW_PENDING',
                  workspace_bytes=workspace_bytes(ROOT),
                  qualification='Seeded components with actual guarded queries/writes. Original O2 source assertion failures are retained. Strict CPU receipt reexecution, proper-head end-of-head effects and full source/route gates remain separate.')
    save();print(json.dumps({'status':report['status'],'report_sha256':sha(OUT/'report.json'),
                            'native_exits':[(c['mapper'],c['subject'],c['native_exit'])for c in cases]}))

if __name__=='__main__':main()
