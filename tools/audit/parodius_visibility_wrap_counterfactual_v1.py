"""Classify actual e11 regressions and model a disclosed wrap/clip fallback."""
from pathlib import Path
from collections import Counter
import argparse, copy, hashlib, json
from parodius_visibility_combined_pixels_v2 import model

sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text())
lines=lambda p:[json.loads(s)for s in p.read_text().splitlines()]


def maps(m):
    return ({pt:(v[1],v[2])for pt,v in m.items()if v[0]},
            {pt:(v[1],v[2])for pt,v in m.items()if not v[0]})


def comparison(base,new):
    b,o=maps(base);n,p=maps(new)
    return dict(body_pixels=[len(b),len(n)],primary_pixels=[sum(v[0]==0 for v in b.values()),sum(v[0]==0 for v in n.values())],other_lost=len(set(o)-set(p)),other_gained=len(set(p)-set(o)),other_pixel_values_changed=sum(o[k]!=p[k]for k in set(o)&set(p)))


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    for n in ['baseline','candidate','actual-pixels','output']:ap.add_argument('--'+n,type=Path,required=True)
    a=ap.parse_args();a.output.mkdir(parents=True,exist_ok=False)
    ds=[a.baseline,a.candidate];es=[{e['start']['frame']:e for e in lines(d/'epochs.jsonl')}for d in ds]
    actual={r['frame']:r for r in read(a.actual_pixels/'matched-epochs.json')}
    chrraw=(ds[0]/'candidate.nes').read_bytes()[1048592:]
    rows=[]
    for f in sorted(es[0]):
        old,new=[e[f]for e in es];pub=new['dma']['publication'];inds=pub['body']['indices'];assert inds==old['dma']['publication']['body']['indices']
        wrap=any(x>y for x,y in zip(inds,inds[1:]))
        parts=[new['start_hardware'][i*4:i*4+4]for i in inds]
        clipped=[dict(index=i,part=p)for i,p in zip(inds,parts)if not(32<=p[0]+1 and p[0]+16<=239 and 8<=p[3] and p[3]+7<=255)]
        fully_on=not clipped
        oldm,counts=model(old,chrraw);newm,newcounts=model(new,chrraw)
        oldall,_=model(old,chrraw,64);newall,_=model(new,chrraw,64)
        # This is an OFFLINE image-admission counterfactual only. No original
        # source, captured RAM, ROM or actual RGB file is changed.
        hypothetical=copy.deepcopy(new)
        fallback=wrap or not fully_on
        if fallback:
            for i in inds:hypothetical['start_hardware'][i*4:i*4+4]=old['start_hardware'][i*4:i*4+4]
        hm,_=model(hypothetical,chrraw)
        basebody,_=maps(oldm);newbody,_=maps(newm)
        lost=set(basebody)-set(newbody)
        reason=Counter()
        for pt in lost:
            limited=newm.get(pt);unlimited=newall.get(pt)
            if limited is not None and not limited[0]:reason['actual_limited_winner_other_sprite']+=1
            elif unlimited is not None and unlimited[0]:reason['hardware8_admission_missing_body_pixel']+=1
            elif unlimited is not None and not unlimited[0]:reason['unlimited_priority_other_sprite']+=1
            else:reason['other_unclassified_missing_body_pixel']+=1
        seq=[];rowcounts_equal=True
        lo=min(counts);hi=max(counts)
        for y in range(lo,hi+1):
            ys=[]
            for e in [old,new]:
                yy=[(i,e['start_hardware'][i*4])for i in sorted(inds)if e['start_hardware'][i*4]+1<=y<=e['start_hardware'][i*4]+16]
                ys.append(yy)
            if len(ys[0])!=len(ys[1]):rowcounts_equal=False
            if ys[0]!=ys[1]:seq.append(dict(scanline=y,baseline_index_Y=ys[0],candidate_index_Y=ys[1]))
        assert rowcounts_equal
        comp=comparison(oldm,newm)
        assert comp['body_pixels']==[actual[f]['baseline_body_pixels'],actual[f]['candidate_body_pixels']]
        rows.append(dict(frame=f,DMA=pub['id'],publication=pub['id'],indices=inds,wrap=wrap,fully_onscreen_strict=fully_on,clipped_parts=clipped,actual=comp,actual_body_regression=comp['body_pixels'][1]<comp['body_pixels'][0],actual_core_regression=comp['primary_pixels'][1]<comp['primary_pixels'][0],per_scanline_total_body_eligibility_counts_exact=rowcounts_equal,changed_body_Y_sequence_rows=seq,lost_body_pixel_causes=dict(reason),unlimited_comparison=comparison(oldall,newall),counterfactual_uses_original_order=fallback,counterfactual=comparison(oldm,hm)))
    def summary(rr):
        return dict(frames=len(rr),wrap=sum(r['wrap']for r in rr),nonwrap=sum(not r['wrap']for r in rr),strict_fully_onscreen=sum(r['fully_onscreen_strict']for r in rr),clipped=sum(not r['fully_onscreen_strict']for r in rr),changed_Y_sequence=sum(bool(r['changed_body_Y_sequence_rows'])for r in rr),actual_other_loss_frames=sum(r['actual']['other_lost']>0for r in rr))
    actual_summary=dict(body_regressions=summary([r for r in rows if r['actual_body_regression']]),core_regressions=summary([r for r in rows if r['actual_core_regression']]))
    for key in ['body_pixels','primary_pixels']:
        actual_summary[key+'_nonwrap_regression_examples']=[dict(frame=r['frame'],counts=r['actual'][key],fully_on=r['fully_onscreen_strict'])for r in rows if not r['wrap']and r['actual'][key][1]<r['actual'][key][0]][:12]
    cf=Counter()
    for r in rows:
        c=r['counterfactual'];cf['fallback_frames']+=r['counterfactual_uses_original_order'];cf['sorted_frames']+=not r['counterfactual_uses_original_order'];cf['body_regression_frames']+=c['body_pixels'][1]<c['body_pixels'][0];cf['core_regression_frames']+=c['primary_pixels'][1]<c['primary_pixels'][0];cf['body_improved_frames']+=c['body_pixels'][1]>c['body_pixels'][0];cf['core_improved_frames']+=c['primary_pixels'][1]>c['primary_pixels'][0];cf['other_loss_frames']+=c['other_lost']>0;cf['other_gain_frames']+=c['other_gained']>0;cf['other_value_change_frames']+=c['other_pixel_values_changed']>0
    (a.output/'classified-actual-and-counterfactual.json').write_text(json.dumps(rows,indent=2)+'\n')
    q=dict(analysis_complete=True,native_run=False,ROM_changed=False,actual_frames_retagged=False,counterfactual_is_model_only=True,matched_actual_epochs=len(rows),baseline_ROM_sha256=sha(ds[0]/'candidate.nes'),candidate_ROM_sha256=sha(ds[1]/'candidate.nes'),actual_negative_pixel_proof_sha256=sha(a.actual_pixels/'proof.json'),actual_regression_classification=actual_summary,counterfactual_summary=dict(cf),all_total_body_row_counts_preserved=True,model_counterfactual_no_regression=not any(cf[k]for k in ['body_regression_frames','core_regression_frames','other_loss_frames','other_value_change_frames']),tool_sha256=sha(Path(__file__)),limits='Counterfactual retains baseline order on actual physical OAM body-span wrap OR clipping; sorted only if every emitted part has x8..248 and visibleY32..239. Uses actual source-bound hardware/CHR/palette from ONE OctEasy640. Model is front-sprite admission, not new actual RGB/native evidence or exhaustive background composition. Changed per-row source Y sequence and body/other pixel winner causes are classified, not relabeled as CHR corruption. No implementation/adoption or other modes/lifecycle verdict.')
    bindings={str(p.resolve()):sha(p)for d in ds for p in d.iterdir()if p.is_file()}
    bindings.update({str((a.actual_pixels/'proof.json').resolve()):sha(a.actual_pixels/'proof.json'),str(Path(__file__).resolve()):sha(Path(__file__)),str((a.output/'classified-actual-and-counterfactual.json').resolve()):sha(a.output/'classified-actual-and-counterfactual.json')})
    (a.output/'manifest.json').write_text(json.dumps(bindings,indent=2)+'\n');q['manifest_sha256']=sha(a.output/'manifest.json');q['binding_count']=len(bindings)
    (a.output/'proof.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(q,indent=2))


if __name__=='__main__':main()
