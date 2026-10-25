"""Repeat optimized Alucard native cases against the frozen root8ff baselines.

Same-total phase changes remain explicit. Acceptance here additionally requires
no more physical/idle frames, no lost draws and no worse longest physical stall.
The rejected e6b result and its stricter exact-row qualifier remain unchanged.
"""
from pathlib import Path
import argparse, csv, hashlib, json, shutil, subprocess, sys

ROOT = Path(__file__).resolve().parents[2]
BASE = '8ff245ae662059abbc77c5de517260032775b7ba881a5201b8b54686ccf08277'
CAND = '4c70fe485f73fb8d437fae2e79ae8ddad83908dc26d4008f21e0a2abeccee2da'
BASE_PROBE = 'a8c4417993d1108dbc7ca00d14d7ed84f11a6a8d03cf9c7798fd5e67c7d2344d'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def measure(rows, key):
    values = [int(r[key]) for r in rows]
    longest = streak = 0
    for value in values:
        streak = 0 if value else streak+1
        longest = max(longest, streak)
    return dict(total=sum(values), zero_frames=values.count(0), longest_zero_streak=longest)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for n in ['prepared','baseline-probe','output']:p.add_argument('--'+n,type=Path,required=True)
    a=p.parse_args();out=a.output.resolve();assert not out.is_relative_to(ROOT)
    assert sha(a.prepared/'candidate.nes')==CAND and sha(a.prepared/'baseline.nes')==BASE
    assert sha(a.baseline_probe/'proof.json')==BASE_PROBE
    baseline_packet=json.loads((a.baseline_probe/'proof.json').read_text())
    assert baseline_packet['native_guards_passed'] and not baseline_packet['passed']
    out.mkdir(parents=True,exist_ok=False)
    names=['cv3_dmc_complete_native_v1.py','cv3_dmc_complete_native_v1.lua',
           'z2_platform_native_qa.lua','observe_chip_committed_write.py',
           'run_mesen_isolated.py','check_tmnt_render_oa.py']
    bindings={str(ROOT/'tools/audit'/n):sha(ROOT/'tools/audit'/n)for n in names}
    assert all(bindings[k]==v for k,v in baseline_packet['tools'].items()if k in bindings)
    frozen=out/'frozen';frozen.mkdir()
    for n in names:shutil.copy2(ROOT/'tools/audit'/n,frozen/n)
    shutil.copy2(Path(__file__),frozen/Path(__file__).name)
    (out/'prelaunch.json').write_text(json.dumps(dict(ROM_sha256=CAND,baseline_ROM_sha256=BASE,
        reused_root_baseline_packet_sha256=BASE_PROBE,tools=bindings,
        qualifier_sha256=sha(Path(__file__))),indent=2)+'\n',encoding='utf-8')
    comparisons=[];receipts={}
    for profile in ['basic','pressure']:
        before=a.baseline_probe/(profile+'-baseline');after=out/(profile+'-candidate')
        before_proof=before/'native-proof.json'
        assert baseline_packet['receipts'][str(before_proof)]==sha(before_proof)
        cmd=[sys.executable,str(ROOT/'tools/audit/cv3_dmc_complete_native_v1.py'),
             '--rom',str(a.prepared/'candidate.nes'),'--output',str(after),
             '--character','5','--variant','3','--profile',profile,'--run']
        with(out/(profile+'-host.log')).open('w',encoding='utf-8')as log:
            subprocess.run(cmd,cwd=ROOT,check=True,stdout=log,stderr=subprocess.STDOUT)
        old,new=[json.loads((d/'native-proof.json').read_text())for d in[before,after]]
        assert old['passed']and new['passed']and old['ROM_sha256']==BASE and new['ROM_sha256']==CAND
        all_rows=[list(csv.DictReader((d/'cadence.csv').open()))for d in[before,after]]
        for i,(b,c)in enumerate(zip(old['cases'],new['cases']),1):
            assert b['name']==c['name']and b['modeReadback']==c['modeReadback']==c['q']['mode']
            rs=[[r for r in rows if int(r['case'])==i]for rows in all_rows]
            assert [len(r)for r in rs]==[b['frames'],c['frames']]
            totals=[dict(draws=0,updates=0),dict(draws=0,updates=0)];deficits=[]
            for frame in range(max(map(len,rs))):
                for j,rows in enumerate(rs):
                    if frame<len(rows):
                        for k in totals[j]:totals[j][k]+=int(rows[frame][k])
                if any(totals[1][k]<totals[0][k]for k in totals[0]):
                    deficits.append(dict(physical_frame_offset=frame,baseline=dict(totals[0]),candidate=dict(totals[1])))
            metrics=[{k:measure(rows,k)for k in['draws','updates']}for rows in rs]
            passed=(c['durationUpdates']==b['durationUpdates']and c['frames']<=b['frames']and c['draws']>=b['draws']
                    and all(metrics[1][k]['zero_frames']<=metrics[0][k]['zero_frames']and
                            metrics[1][k]['longest_zero_streak']<=metrics[0][k]['longest_zero_streak']and
                            totals[1][k]>=totals[0][k]for k in['draws','updates']))
            comparisons.append(dict(profile=profile,name=b['name'],mode=b['modeReadback'],
                passed=passed,baseline_frames=b['frames'],candidate_frames=c['frames'],
                baseline_draws=b['draws'],candidate_draws=c['draws'],
                baseline_updates=b['durationUpdates'],candidate_updates=c['durationUpdates'],
                baseline_metrics=metrics[0],candidate_metrics=metrics[1],
                temporary_prefix_deficits=deficits))
        for d in[before,after]:receipts[str(d/'native-proof.json')]=sha(d/'native-proof.json')
        print(json.dumps(dict(profile=profile,native_guards_pass=True,comparisons=comparisons[-len(new['cases']):])),flush=True)
    assert all(sha(Path(k))==v for k,v in bindings.items())
    result=dict(passed=all(r['passed']for r in comparisons),adopted=False,goal_complete=False,
        ROM_sha256=CAND,baseline_ROM_sha256=BASE,native_guards_passed=True,
        original_root_baseline_reused=True,baseline_packet_sha256=BASE_PROBE,
        all_physical_prefixes_nonnegative=all(not r['temporary_prefix_deficits']for r in comparisons),
        comparisons=comparisons,receipts=receipts,tools=bindings,qualifier_sha256=sha(Path(__file__)),
        scope='Two fresh optimized candidate native runs, six paired Alucard Easy/Hard cases, '
              'against unchanged individually passing root8ff baselines. The old aggregate failed '
              'for e6b and remains failed. New same-update/no-draw-loss/no-extra-physical-or-idle-frame/'
              'no-longer-stall gate explicitly allows changed phase with every temporary prefix '
              'deficit disclosed. This does not certify whole-roster gameplay, waveform or universal lag removal.')
    (out/'proof.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(passed=result['passed'],all_prefixes_nonnegative=result['all_physical_prefixes_nonnegative'],proof_sha256=sha(out/'proof.json'))))
    raise SystemExit(0 if result['passed']else 1)


if __name__=='__main__':main()
