"""Freeze the ONE a801 held native pilot and separate Vine counterexample."""
from pathlib import Path
import argparse,collections,hashlib,json,shutil
R=Path(__file__).resolve().parents[2]
D=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
N=D/'mm-proto-publication-native-ready-v1';V=D/'mm-proto-publication-candidate-v3/vine-chain-v3'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(p,z):p.write_text(json.dumps(z,indent=2)+'\n')

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args();assert not a.output.exists()and not a.output.resolve().is_relative_to(R);a.output.mkdir(parents=True)
    run=json.loads((N/'native-receipt.json').read_text());review=json.loads((N/'review-v2/proof.json').read_text());vine=json.loads((V/'proof.json').read_text())
    assert run['passed']and run['launches']==1 and run['retries']==0 and run['worker_released']
    assert not review['release_suitable']and review['physical_DMA_net_delta']==-3 and review['actual_owned_consumed_constructions']==46
    assert vine['acknowledges_partial_image_even_when_body_bytes_changed']and not vine['whole_page_or_intact_body_tag_guarantee']
    rows=[json.loads(s)for s in(N/'ownership.jsonl').read_text().splitlines()];timing=[json.loads(s)for s in(N/'timing.jsonl').read_text().splitlines()]
    first=[q for q in rows if q['kind']=='NMI-acceptance'and q['ppu']['frame']==385];assert len(first)==1
    mainid=first[0]['main'];assert mainid==369 and first[0]['state']['NmiDisable']==255 and first[0]['last_roster']==14
    release=next(q for q in rows if q['kind']=='Main-release'and q['main']['id']==mainid)
    roster=next(q for q in rows if q['kind']=='DrawAll-roster-ready'and q['construction']['id']==14)
    ret=next(q for q in rows if q['kind']=='NMI-return'and q['ppu']['frame']==385)
    baseline=D/'mm-proto-publication-ownership-v1/prepare-v2';oldrows=[json.loads(s)for s in(baseline/'ownership.jsonl').read_text().splitlines()]
    oldfirst=next(q for q in oldrows if q['kind']=='NMI-acceptance'and q['ppu']['frame']==385)
    oldrelease=next(q for q in oldrows if q['kind']=='Main-release'and q['main']['id']==369)
    oldroster=next(q for q in oldrows if q['kind']=='DrawAll-roster-ready'and q['construction']['id']==14)
    causal=dict(first_visible_count_deficit=review['first_deficit'],candidate_acceptance=first[0],candidate_completed_Roster=roster,candidate_Main_release=release,candidate_NMI_return=ret,baseline_acceptance=oldfirst,baseline_release=oldrelease,baseline_Roster=oldroster,
                candidate_Roster_completion_later_than_baseline_cycles=roster['construction']['ppu']['cpu']-oldroster['construction']['ppu']['cpu'],
                interpretation='At the first real transfer deficit385, a801 had completedRoster14 but Main369 remained protectedFF, interrupted at actual stackedPC86E0/bank126. Baseline369 had already released and its NMI transferred. The candidate later releases after that lagNMI. This is an actual Main-release deadline miss, not a completion-label-only error. NMI callback entry is after hardware entry; no invented exact uninterrupted saving target is derived.')
    put(a.output/'first-actual-deferral385.json',causal)
    pairs=json.loads((N/'review-v2/all275-pairs.json').read_text());pubs={x['DMA']:x for x in json.loads((N/'review-v2/actual-owned-publications.json').read_text())}
    runs=[];current=[]
    for x in pairs:
        p=pubs.get(x['candidate_completed_DMA']);bad=p is not None and p['body_first8']['rejected_record_scanlines']>0
        if bad:current.append(x['frame'])
        elif current:runs.append(current);current=[]
    if current:runs.append(current)
    put(a.output/'actual-visible-first8-record-runs.json',dict(body_record_rejection_runs=runs,max_visible_frame_run=max(map(len,runs),default=0),limits='Actual displayed full-OAM Y-based first8 exclusion. No captured CHR/alpha oracle; not opaque pixel absence or per-live-projectile guarantee.'))
    (a.output/'proofs').mkdir();(a.output/'tools').mkdir()
    for p,label in[(N/'native-receipt.json','native-launch.json'),(N/'result.json','original-mechanical-guards.json'),(N/'review-v2/proof.json','independent-review.json'),(V/'proof.json','vine-partial-image.json')]:shutil.copyfile(p,a.output/'proofs'/label)
    tools=['mm_proto_publication_native_prepare_v1.py','mm_proto_publication_candidate_observer_v1.lua','mm_proto_publication_candidate_mock_v1.py','mm_proto_publication_native_review_v1.py','mm_proto_publication_native_review_v2.py','mm_proto_publication_vine_chain_v1.py','mm_proto_publication_vine_chain_v2.py','mm_proto_publication_vine_chain_v3.py',Path(__file__).name]
    for n in tools:shutil.copyfile(R/'tools/audit'/n,a.output/'tools'/n)
    (a.output/'images').mkdir()
    for n in['paired-wholeframes-1.png','paired-wholeframes-2.png','paired-wholeframes-3.png','paired-global-diff-actual.png']:
        shutil.copyfile(N/'review-v2'/n,a.output/'images'/n)
    report='''a801 publication-aware body/shot priority -- HELD, not installed

ONE granted450 same-input MegaEasy native pilot. Worker released, no retry.
ROMa801f8e397a416e1b12cb6b78bad25774670c8f9fea0e8334cd0c830cf8a3d56
Parent/reference731c918b0f448564587d90fca2979afc9fc0e5eb9b26616f4241801e2e73e16c
Source packet7d8aa2433f882e65718d1dccd845c63a60ce54656eaea79189f8918bf890cab6

MECHANICAL PASSES:399/399 real256-byte source/physical OAM pages exact,
442 NMI checks,79 IRQ31 checks,449 exact controller polls,69 safe enables,
zero late enables or hardware mismatches.275 actual rawPPU frames retained.
The source/CPU/canonical/ordinary qualification remains separately true.

RELEASE FAIL:731 has402 transfers, a801399, net3 fewer.63 actual visible
capture cutoffs have a negative cumulative physical-transfer prefix. At
385, both runs completed theirRoster14, but the candidate's completion was
274 CPUcycles later. BaselineMain369 had released before NMI; candidate369
was still protectedFF at the actual NMI, interrupted at bank126:86E0. It
releases only after the lag NMI. This is a genuine Main release/transfer
miss, not endFrame bookkeeping. No exact saving target is invented from
post-hardware-entry hook timestamps. Endpoint Main432 is still unfinished
in a801 (431 releases), while baseline432 releases;48 vs51 Rosters.

ACTUAL PROTOCOL:46 owned completed images reach real physical DMA:23 body
and23 shot phases in strict alternation. All46 source images exactly match
their completedRoster image; actual ObjectVerticalFlip is0 throughout.
46 actual bank66 acknowledgement writes alternate64/0. All108 bytewrites
bind to genuine compiled direct/indexed STA or ASL/LSR instructions. The
final body construction48 remains pending. This is real consumed-image
alternation in this route, not merely source/frame parity.

VISIBILITY TRADEOFF: Y-based first8 evaluation of actual hardware pages
rejects no body records on all23 body turns, but rejects body records on
15 shot turns. It rejects shot records on16 body turns and no shot records
on23 shot turns. Thus priority alternates in actual hardware data, with
the intended sacrifice. Native46-image evidence does not guarantee every
body/shot/world opaque pixel; no full CHR/palette/alpha owner was captured.
All275 RGB pairs are compared (209 exact,66 different); all79 active
bottom-frame pairs372..450 and selected wholeframes were visually viewed.
Actual403 is hair/face-only in a801 while404 has its body; other paired
frames show the opposite exchange of body and bullet priority. The late
whole-image differences435/444/446/448 show differing camera/time/update
positions, not an asserted new tile-corruption cause. Their exact images
and source/cadence context remain retained. Startup/menu through first
active372 matches731, including its pre-existing face/palette appearance.

VINE COUNTEREXAMPLE, SOURCE ONLY:12 configured legal growing16px vine
chains execute real VineObjectHandler/DrawVine/native leaf, genuine
no-draw Main admission/release and a full regular NMI/actual4014 store.
Native PlayerOAMReservation returns40 for both variants. Three shot-turn
cases overwrite8 or24 real body bytes during the partial source edit,
retain the tag, then acknowledge that partial image. The body-turn
standing cases have no body overlap. This disproves an intact-body/
whole-page guarantee from the tag; no native vine/campaign is claimed.
The setup explicitly supplies actor and post-physics caller context; it
does not fake a natural spawn, DMA result, acknowledgement or outcome.

No next patch, native retry, production/default/settings or Git mutation.
Earlier c5/00fb failures, source negatives and this399vs402 result remain
immutable. Reviewer1 had an offline syntax failure; reviewer2 made the
same finite comparison after fixing separators only. Vine tool1 had a
syntax failure, tool2's Proto44 native-reservation assumption failed;
tool3 records the actual40 and all body overlaps without suppressing any.
'''
    reportpath=R/'docs/qa/mm-proto-publication-native-2026-10-26.txt';reportpath.write_text(report);shutil.copyfile(reportpath,a.output/'report.txt')
    ready=json.loads((N/'readiness.json').read_text());deps={Path(p)for p in ready['bindings']}
    deps|={p for p in N.rglob('*')if p.is_file()and not p.is_relative_to(a.output)}
    deps|={p for p in V.iterdir()if p.is_file()};deps|={p for folder in['vine-chain-v1','vine-chain-v2']for p in(V.parent/folder).iterdir()if p.is_file()}
    deps|={R/'tools/audit'/n for n in tools};deps.add(reportpath)
    for p,h in ready['bindings'].items():assert sha(p)==h,p
    put(a.output/'bindings.json',{str(p.resolve()):dict(bytes=p.stat().st_size,sha256=sha(p))for p in sorted(deps)})
    catalog={p.relative_to(a.output).as_posix():dict(bytes=p.stat().st_size,sha256=sha(p))for p in sorted(a.output.rglob('*'))if p.is_file()};put(a.output/'catalog.json',catalog)
    receipt=dict(passed=True,freeze_verified=True,native_run=True,game_release_suitable=False,adopted=False,ROM_sha256=run['ROM_sha256'],launches=1,retries=0,worker_released=True,
                 mechanical_guards_pass=True,physical_DMA_net_delta=-3,cumulative_prefix_deficit_frames=63,real_consumed_priority_turns=46,Vine_partial_body_counterexample=True,
                 catalog_files=len(catalog),catalog_sha256=sha(a.output/'catalog.json'),bindings=len(deps),bindings_sha256=sha(a.output/'bindings.json'),report_sha256=sha(reportpath),tool_sha256=sha(__file__))
    put(a.output/'receipt.json',receipt);print(json.dumps(dict(receipt_sha256=sha(a.output/'receipt.json'),**receipt),indent=2))
if __name__=='__main__':main()
