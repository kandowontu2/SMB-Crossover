"""Sequential actual-pixel reproduction and exact-candidate SMB3 font repair check."""
from pathlib import Path
import hashlib,json,subprocess,sys

ROOT=Path(__file__).resolve().parents[2]
D=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    out=D/'m3-hud-timing-v1/final-native-v1';out.mkdir(exist_ok=False)
    baseline=D/'final-roll-items-v1/adoption-single-owner-v1/candidate.nes'
    candidate=D/'m3-hud-timing-v1/private-owner-v2/candidate.nes'
    assert sha(baseline)=='9bac46e934d3301e378139783febf2d54c4fd5753a62e082f2d7e6580946d58c'
    assert sha(candidate)=='5ec81c9250c20aee31af0d3b98c241932c72b3147e05702de70e266f3c854893'
    rows=[]
    for name,rom,identity in [('baseline-luigi3',baseline,'luigi3'),('candidate-luigi3',candidate,'luigi3'),('candidate-mario3',candidate,'mario3')]:
        folder=out/name;route=D/'current8ff-roster-v1'/(identity+'-easy')
        command=[sys.executable,str(ROOT/'tools/audit/probe_m3_hud_timing_v1.py'),'--rom',str(rom),'--route',str(route),'--output',str(folder),'--frames','3000']
        with(out/(name+'.host.log')).open('w')as log:r=subprocess.run(command,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
        proof=json.loads((folder/'proof.json').read_text())
        assert proof['exit']==0 and proof['native']['pixel_frames']>1500
        if name.startswith('baseline'):
            assert r.returncode==1 and not proof['passed']and len(proof['native']['bad'])>100
        else:assert r.returncode==0 and proof['passed']and not proof['native']['bad']and not proof['late_font_publications']
        rows.append(dict(name=name,ROM_sha256=sha(rom),pixel_frames=proof['native']['pixel_frames'],mismatched_frames=len(proof['native']['bad']),font_publications=proof['font_publications'],late_font_publications=len(proof['late_font_publications']),proof_sha256=sha(folder/'proof.json')))
        print(json.dumps(rows[-1]),flush=True)
    cpu=D/'m3-hud-timing-v1/owner-cpu-v2/proof.json';routes=D/'m3-hud-timing-v1/affected-routes-v1/proof.json'
    c=json.loads(cpu.read_text());n=json.loads(routes.read_text())
    assert c['passed']and c['cases']==1600 and c['candidate_sha256']==sha(candidate)
    assert n['complete']and n['passed']and n['ROM_sha256']==sha(candidate)and len(n['runs'])==11
    proof=dict(passed=True,goal_complete=False,ROM_sha256=sha(candidate),baseline_ROM_sha256=sha(baseline),native=rows,cpu_cases=1600,affected_identity_routes=11,
               refs={str(p):sha(p)for p in [cpu,routes,D/'m3-hud-timing-v1/private-owner-v2/proof.json']},
               tools={str(ROOT/'tools/audit'/n):sha(ROOT/'tools/audit'/n)for n in ['probe_m3_hud_timing_v1.py','check_m3_hud_owner_cpu_v1.py','prepare_m3_hud_owner_v1.py','qualify_m3_hud_owner_v1.py']},
               scope='Baseline incorrect-font pixels reproduced with actual read-only PPU screen data; both SMB3 identities have zero wrong bar-mask pixels in the fixed3000-frame replay prefixes and no late font545 publication. All11 identities sharing the changed generic leaf independently clear1-1 without death, with completed-loop camera/body-CHR guards. Registers/flags/writes pass1600CPU cases; nonM3 leaf overhead<=19CPU cycles is explicit, not a universal cadence guarantee. All actual remaining source/CHR/addresses unchanged; no full-roster current every-item, all-Hard, campaign, hardware or MMC3 expansion claim.')
    (out/'proof.json').write_text(json.dumps(proof,indent=2)+'\n',encoding='utf-8');print(json.dumps(dict(passed=True,ROM_sha256=sha(candidate),native=rows)))


if __name__=='__main__':main()
