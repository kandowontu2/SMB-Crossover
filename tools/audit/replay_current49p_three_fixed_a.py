"""Independent power-on fixed replays on current Pit-wings P, no capture."""
from pathlib import Path
import concurrent.futures,hashlib,json,subprocess,sys
ROOT=Path(__file__).resolve().parents[2]
PACKET=ROOT/'build/verification/mm48-private-reference-runner-u'
CP=ROOT/'build/checkpoints/roster-audit-v49-provisional-pit-wings-p'
OUT=ROOT/'build/verification/root49p-three-fixed-a'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    sys.dont_write_bytecode=True
    assert not OUT.exists()
    assert sha(CP/'manifest.json')=='be6ef9fd6447de62e6cce5ea2574b369b63cf33106210047facf65596726d8b5'
    cat=json.loads((CP/'manifest.json').read_text())['source_hashes']
    assert all(sha(ROOT/n)==h for n,h in cat.items())
    sys.path.insert(0,str(ROOT/'tools/playthroughs'));from roster_run import workspace_bytes
    used=workspace_bytes(ROOT);assert used+245_000_000<50_000_000_000
    OUT.mkdir();descriptor=OUT/'current-p-mmc3-reference.json'
    command=[sys.executable,str(PACKET/'reference_io.py'),'--mapper','mmc3']
    for key,path in [('rom',CP/'smb-crossover-mmc3.nes'),('dbg',CP/'smb-crossover-mmc3.dbg'),
                     ('lbl',CP/'smb-crossover-mmc3.lbl'),('map',CP/'smb-crossover-mmc3.map'),
                     ('source-archive',CP/'source-v49-pit-wings-p.zip'),('build-report',CP/'manifest.json')]:
        command+=['--'+key,str(path)]
    command+=['--output',str(descriptor)]
    with (OUT/'descriptor.log').open('wb')as f:r=subprocess.run(command,cwd=ROOT,stdout=f,stderr=subprocess.STDOUT)
    assert r.returncode==0
    desc_sha=sha(descriptor)
    variants=((0,'Mario','root49n-mario-fixed-a-0-v0-mmc3'),
              (8,'Luigi','root49n-luigi-fixed-a-8-v0-mmc3'),
              (2,'Samus','root49o2-samus-fixed-o-2-v0-mmc3'))
    cases=[]
    for char,name,oldtag in variants:
        old=ROOT/'build/roster-through-2-2'/oldtag;m=json.loads((old/'manifest.json').read_text())
        assert m['verified_through_2_2']and m['result']['all_six_stages']and m['result']['deaths']==0
        assert m['controller_only']and not m['memory_or_register_writes']and m['full_frame_audit']
        inputs=old/'inputs.csv';assert sha(inputs)==m['inputs_sha256']
        tag='root49p-three-fixed-a'
        expected=ROOT/'build/roster-through-2-2'/f'{tag}-{char}-v0-mmc3';assert not expected.exists()
        cmd=[sys.executable,str(PACKET/'roster_run_reference.py'),'--reference-descriptor',str(descriptor),
             '--reference-sha256',desc_sha,'--reference-reserve-bytes','75000000',
             '--character',str(char),'--mapper','mmc3','--tag',tag,'--replay',str(inputs),
             '--frames','32000','--timeout','300']
        cases.append({'character':char,'name':name,'command':cmd,'expected':str(expected),
                      'old_manifest':str(old/'manifest.json'),'old_manifest_sha256':sha(old/'manifest.json'),
                      'inputs_sha256':sha(inputs),'old_result':m['result']})
    report={'status':'running-three-current-P-fixed-replays','accepted_release':False,'goal_complete':False,
            'script_sha256':sha(Path(__file__)),'descriptor_sha256':desc_sha,'workspace_before':used,
            'prospective_own_reserve':225_000_000,'other_future_reserve':20_000_000,'cases':cases}
    def save():(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    save()
    def run(c):
        with (OUT/(c['name']+'.log')).open('wb')as f:r=subprocess.run(c['command'],cwd=ROOT,stdout=f,stderr=subprocess.STDOUT)
        p=Path(c['expected'])/'manifest.json';m=json.loads(p.read_text())
        c.update(native_exit=r.returncode,manifest_sha256=sha(p),result=m.get('result'),verified_through_2_2=m['verified_through_2_2'])
        c['pass']=bool(r.returncode==0 and m['verified_through_2_2']and m['result']['all_six_stages']and m['result']['deaths']==0)
        assert m['controller_only']and not m['memory_or_register_writes']and m['full_frame_audit']
        assert m['rom_sha256']==sha(CP/'smb-crossover-mmc3.nes')and m['inputs_sha256']==c['inputs_sha256']
        return c
    with concurrent.futures.ThreadPoolExecutor(max_workers=2)as pool:
        for future in concurrent.futures.as_completed([pool.submit(run,c)for c in cases]):future.result();save()
    assert all(sha(ROOT/n)==h for n,h in cat.items())
    passed=all(c.get('pass')for c in cases)
    report.update(status='PASS_THREE_CURRENT_P_FIXED_ORDINARY_END2_2_REPLAYS'if passed else'NEGATIVE_CURRENT_P_FIXED_REPLAY',
                  workspace_after=workspace_bytes(ROOT),
                  qualification='Complete controller-only power-on replay, full frame audit, no grants/saved states/prefix/discovery tail. No every-weapon/final recording/hardware/source-parity claim.')
    save();print(json.dumps({'status':report['status'],'report_sha256':sha(OUT/'report.json')}));assert passed

if __name__=='__main__':main()
