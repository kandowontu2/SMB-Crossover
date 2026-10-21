"""Root execution of frozen E and original O2 head/foot native components."""
from pathlib import Path
import hashlib,json,sys
ROOT=Path(__file__).resolve().parents[2]
PACKET=ROOT/'build/verification/ryu49o2-head-components-f'
OUT=ROOT/'build/verification/root49o2-head-f-native-c'
CP=ROOT/'build/checkpoints/roster-audit-v49-provisional-o2'
PRIVATE=ROOT/'build/verification/root49o2-head-private-build-e/source/build'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    sys.dont_write_bytecode=True
    assert not OUT.exists()
    assert sha(PACKET/'freeze.json')=='032f12cf577910042852b570dbbd7d5ea613c14c449409694c58f42315ce1b7f'
    old_core=(ROOT/'build/verification/ryu49o2-head-components-e/component.lua').read_text()
    a='tostring(a.launchSeen),tostring(a.interrupted)'
    b='tostring(a.launchSeen or false),tostring(a.interrupted or false)'
    assert old_core.count(a)==1 and old_core.replace(a,b)==(PACKET/'component.lua').read_text()
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
            if subject=='o2' and mapper=='mmc3':continue # Actual E receipt retained and strictly normalized separately.
            folder=PACKET/f'binding-{subject}-{mapper}-root-f-a'
            binding=folder/'binding.json';b=json.loads(binding.read_text())
            script=folder/f'{subject}-{mapper}-root-f-a.lua';ok,error=parse(script.read_text(),str(script));assert ok,error
            rom=build/f'smb-crossover-{mapper}.nes'
            assert sha(rom)==b['rom_sha256']and sha(rom.with_suffix('.dbg'))==b['dbg_sha256']and sha(rom.with_suffix('.lbl'))==b['lbl_sha256']
            # bind.py prepares these empty output directories. Existing data
            # would be a hard failure; no prior evidence is overwritten.
            output=folder/'native-output'
            assert output.is_dir() and not any(output.iterdir())
            cases.append({'mapper':mapper,'subject':subject,'rom':str(rom),'rom_sha256':sha(rom),
                          'binding':str(binding),'binding_sha256':sha(binding),'script':str(script),'script_sha256':sha(script)})
    OUT.mkdir();report={'status':'running-frozen-E-native-components','accepted_release':False,'goal_complete':False,
                       'script_sha256':sha(Path(__file__)),
                       'retained_preflight_A_negative_sha256':sha(ROOT/'build/verification/root49o2-head-e-native-a-driver.log'),
                       'retained_native_B_JSON_negative_sha256':sha(ROOT/'build/verification/root49o2-head-e-native-b-driver.log'),
                       'normalized_actual_O2_M3_receipt_sha256':sha(PACKET/'normalizations/o2-mmc3-e-actual-a/normalization.json'),
                       'cases':cases}
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
