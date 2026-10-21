"""Read retained I2 data; preserve and qualify its unsigned velocity columns."""
from pathlib import Path
from collections import Counter
from decimal import Decimal
import csv,hashlib,json,re,sys

ROOT=Path(__file__).resolve().parents[2]
RUN=ROOT/'build/roster-through-2-2/root49p-pit-final-lift-i2-6-v0-mmc3'
PREP=ROOT/'build/verification/root49p-pit-final-lift-i2'
OUT=ROOT/'build/verification/root49p-pit-i2-lift-host-review-a.json'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def integer(s):
    v=Decimal(s);assert v==v.to_integral_value();return int(v)

def main():
    assert not OUT.exists()
    inputs=[PREP/'report.json',PREP/'policy.lua',PREP/'observer.lua',RUN/'pit49p-final-lifts-h.csv',
            RUN/'pit-final-lift-i-controller.csv',RUN/'inputs.csv',RUN/'trace.csv',RUN/'manifest.json']
    before={str(p.relative_to(ROOT)):sha(p)for p in inputs}
    observer=(PREP/'observer.lua').read_text()
    assert observer.count('v>=0x1600000 and v-0x1000000 or v')==1
    assert not re.search(r'emu\.(?:write|setState|setInput|saveState|loadState)\s*\(',observer)
    policy=(PREP/'policy.lua').read_text().splitlines()[0]
    parser=ROOT/'build/verification/agent47-samus-controller-batch-h-preparation/parser'
    provenance=json.loads((parser/'provenance.json').read_text())
    for p in [provenance['wheel']]+provenance['extracted']:assert sha(Path(p['path']))==p['sha256']
    sys.path.insert(0,str(parser/'runtime'));from lupa.lua54 import LuaRuntime
    h=LuaRuntime().execute(policy+';return PIT_LIFT_HOOKS')
    hooks={q['name']:q for _,q in h['foreground'].items()}
    rom=(ROOT/'build/checkpoints/roster-audit-v49-provisional-pit-wings-p/smb-crossover-mmc3.nes').read_bytes()
    counts=Counter();negative=Counter();raw=[]
    with (RUN/'pit49p-final-lifts-h.csv').open(newline='')as f:
        for row in csv.DictReader(f):
            r={k:(v if k in ('event','grid8x8hex')else integer(v))for k,v in row.items()}
            for name in ('qVX','qVY'):
                u=r[name];assert 0<=u<=0xffffff
                signed=u-0x1000000 if u>=0x800000 else u
                assert signed%0x1000000==u
                negative[name]+=signed<0
            if r['event']!='endFrame-context-only':
                q=hooks[r['event']];assert (r['pc'],r['bank'])==(q['address'],q['bank'])
                at=16+q['bank']*8192+q['address']%8192
                assert rom[at:at+8]==bytes(q['bytes'].values())
                assert r['nmi']==r['irq']==0
            counts[r['event']]+=1;raw.append(r)
    # A CPU EXEC after the native STA is context, not a memory callback.
    # Establish the observed post-instruction state without inventing a typed
    # bus-write receipt that this observer never captured.
    after=[r for r in raw if r['event']=='NativePlatformPlayerY_after_STA']
    assert len(after)==48
    for r in after:
        s=r['objectOffset'];assert s==1
        assert r[f'e{s}_id']==0x26 and r[f'e{s}_platformFlag']==s
        assert r['qY']//65536==(r[f'e{s}_y']-32)&255
    with (RUN/'pit-final-lift-i-controller.csv').open(newline='')as f:decisions=list(csv.DictReader(f))
    phases=[];previous=None
    for r in decisions:
        if r['phase']!=previous:phases.append(r);previous=r['phase']
    assert [(r['phase'],integer(r['frame']))for r in phases]==[
        ('approach',7881),('lift-air',7901),('ride',7973),('bank-air',8020),('done',8110)]
    end=phases[-1];assert (integer(end['x']),integer(end['y']),integer(end['feetLeft']),integer(end['feetRight']))==(2584,128,0x52,0x52)
    result=json.loads((PREP/'report.json').read_text())['result']
    assert result['frames']==10312 and result['failure']=='death'and result['stage_entries']['0-2']==9254
    assert before=={str(p.relative_to(ROOT)):sha(p)for p in inputs}
    report=dict(status='PASS_RETAINED_I2_ACTUAL_LIFT_SUPPORT_WITH_UNSIGNED_Q_QUALIFICATION',
        script_sha256=sha(Path(__file__)),inputs=before,rows=len(raw),events=dict(counts),
        negative_Q24_values_interpreted_on_host=dict(negative),
        Q24_qualification='Raw I/I2 qVX/qVY are unsigned24 due observer threshold0x1600000. Retained unchanged. Host uses exact integral Decimal then subtracts0x1000000 at>=0x800000. Controller uses native c.vy and live fractions, never these logged q columns. J repairs future observer only.',
        observed_native_post_STA_rows=len(after),first_post_STA_frame=after[0]['frame'],last_post_STA_frame=after[-1]['frame'],
        controller_phase_transitions=phases,result=result,
        qualification='Native physical-bank/compiled8 EXEC contexts and observed post-STA Y relation; no typed store callback was captured by I2. Ordinary adaptive pass of1-2 then death1-3. No full fixed clear, all-frame visual/SFX or final-video claim.')
    OUT.write_text(json.dumps(report,indent=2)+'\n');print(report['status'],sha(OUT))

if __name__=='__main__':main()
