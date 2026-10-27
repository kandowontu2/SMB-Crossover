"""Freeze Bill's offline result and prepare only the unchanged Lance native input."""
from pathlib import Path
import argparse, difflib, json, shutil
from PIL import Image
from final_bill_lance_hard_gallery_source_v1 import D, ROOT, SHA, sha, put
from final_item_abilities_remaining731_run_v1 import verify_manifest
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import location


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--public',type=Path,required=True)
    a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
    prior=D/'final-bill-lance-hard-gallery-ready-v5/final-freeze-v1'
    post=D/'final-bill-hard-v5-postrun-v2';flight=D/'final-bill-hard-v5-actual-flight-v1'
    native=prior.parent/'profiles/bill-hard/native';lance=prior.parent/'profiles/lance-hard/native'
    assert sha(prior/'proof.json')=='10339eb5c0eb6102777cdd448b04c13341840b1e3b9f6c1d4394161c730a8390'
    assert sha(native/'proof.json')=='b8828509a880b703c0ff03d7b9c411507f7aad629fa3f3b8736c261fb308abf6'
    assert sha(post/'proof.json')=='66474f0a35fd1cfa56708f1cedcffc6970b1a33091fa6f626057b2856987d77f'
    review=json.loads((post/'proof.json').read_text())
    assert review['offline_schema_local_comparison_passed'] and not review['original_host_aggregate_passed']
    assert not(lance/'launch.json').exists() and not(lance/'proof.json').exists()
    assert review['hardware']==dict(complete256DMAs=3572,startFrame_epochs=4343,scoped_enables=3246,late_scoped_enables=0)
    assert review['PPU']['frames']==4344 and review['cadence']['entries']==3860 and review['cadence']['finishes']==3859
    old=(ROOT/'tools/audit/final_bill_lance_hard_gallery_run_v1.py').read_text()
    new=(ROOT/'tools/audit/final_bill_lance_hard_gallery_run_v2.py').read_text()
    before="""        for q,p in zip(n['cases'],cfg['cases']):
            assert q['q']==p and q['completed'] and len(q['stages'])==len(p['tasks'])"""
    after="""        for case_index,(q,p) in enumerate(zip(n['cases'],cfg['cases'])):
            observed_plan=copy.deepcopy(q['q'])
            if case_index==0:
                assert p['name']=='normal' and observed_plan['name']=='normal'
                for key in ['grant_sequence','incremental_grants']:
                    assert type(observed_plan[key]) is dict and observed_plan[key]=={}
                    assert type(p[key]) is list and p[key]==[]
                    observed_plan[key]=[]
            assert observed_plan==p and q['completed'] and len(q['stages'])==len(p['tasks'])"""
    restored=new.replace('Run one separately granted profile; interpret only NORMAL two empty Lua arrays.',
                         'Run exactly one separately granted legal Bill/Lance Hard profile.')
    restored=restored.replace('import argparse,copy,csv,datetime,json,subprocess,sys',
                              'import argparse,csv,datetime,json,subprocess,sys')
    assert restored.count(after)==1 and restored.replace(after,before,1)==old
    (a.output/'host-collector-only.patch').write_text(''.join(difflib.unified_diff(old.splitlines(keepends=True),new.splitlines(keepends=True),fromfile='run_v1.py',tofile='run_v2.py')),encoding='utf-8')
    put(a.output/'collector-equality.json',dict(passed=True,native_run=False,exact_reverse_to_frozen_run_v1=True,
        changed_contract='Only source-proven NORMAL plan grant_sequence/incremental_grants exact native{} and expected[] become [] in a deep copy. Every remaining plan field/type/predicate and original hardware/PPU/cadence/case/grant parser remains literal.',
        old_sha256=sha(ROOT/'tools/audit/final_bill_lance_hard_gallery_run_v1.py'),new_sha256=sha(ROOT/'tools/audit/final_bill_lance_hard_gallery_run_v2.py')))
    # Read-only attribution of the selected capsule's HUD placement. OAM is the
    # actual hardware epoch; source record is bound to the exact3b executable.
    ready=json.loads((prior/'proof.json').read_text());rom=Path(ready['ROM']);b=scoped_load(rom)
    value=lambda name,i=0:b['raw'][location(b,name)+i]
    records=[]
    for item in [2,3,4,5]:
        art=value('RemainingDraw::PickupArts',8+item)
        ptr=value('AvArtRightLo',art)+256*value('AvArtRightHi',art)
        bank=value('AvArtBanks',art)&127;at=16+8192*bank+ptr%8192;length=b['raw'][at]
        raw=list(b['raw'][at:at+length+1]);assert length==12
        assert [raw[i]for i in [4,8,12]]==[244,252,4] and [raw[i]for i in [3,7,11]]==[241]*3
        records.append(dict(item=item,art=art,bank=bank,pointer=ptr,bytes=raw,
                            anchor=[192,24],signed_record_offsets=[[-12,-15],[-4,-15],[4,-15]],
                            eight_by_sixteen_sprite_bounds=[180,10,203,25]))
    selected=[];body=[]
    for line in(native/'ability-dma-epochs.jsonl').open():
        q=json.loads(line)
        if q['kind']=='completed-DMA-before-render-enable' and q['complete']['frame'] in [997,998,999]:
            sprites=[dict(slot=i//4,bytes=q['source'][i:i+4])for i in range(0,256,4)if q['source'][i]<32 and 170<=q['source'][i+3]<=210]
            assert sorted(z['bytes'][3]for z in sprites)==[180,188,196]
            selected.append(dict(id=q['id'],stamp=q['complete'],actual_hardware_sprite_bytes=sprites))
        if q['kind']=='startFrame-hardware' and q['stamp']['frame'] in [2131,2132,2133,2134]:
            sprites=[dict(slot=i//4,bytes=q['hardware'][i:i+4])for i in range(0,256,4)if 30<=q['hardware'][i]<220]
            body.append(dict(stamp=q['stamp'],completed_dma_id=q['completed_dma_id'],actual_hardware_sprites=sprites))
    assert len(selected)==3 and len(body)==4 and [z['completed_dma_id']for z in body]==[1866,1866,1866,1867]
    image=lambda name:Image.frombytes('RGBA',(256,240),(native/name).read_bytes(),'raw','BGRA').convert('RGB')
    normal=image('normal-committed-HUD.argb');machine=image('machine-committed-HUD.argb')
    obscured=[dict(x=x,y=y,before=list(normal.getpixel((x,y))),after=list(machine.getpixel((x,y))))
              for y in range(16,24)for x in range(144,232)
              if normal.getpixel((x,y))==(255,254,255) and machine.getpixel((x,y))!=(255,254,255)]
    assert [(z['x'],z['y'])for z in obscured]==[(180,16),(201,16),(202,16),(203,16),(181,17),(182,18)]
    src=Path(ready['source']) if 'source'in ready else rom.parent/'source'
    text=(src/'src/screen_render.s').read_text();assert '.byte $20, $52, $0b, "WORLD  TIME"'in text
    put(a.output/'visual-review.json',dict(agent_reviewed=True,all_frames_graphically_clean=False,
        reviewed_placements=50,whole_frame_sheets=[str(post/'whole-frame-review-1.png'),str(post/'whole-frame-review-2.png'),str(flight/'whole-flight-frames.png'),str(flight/'advanced-adjacent-full-frames.png')],
        positive_scope='35 HUD/emission/contact/terrain/fresh-edge placements plus7 free-flight samples plus8 consecutive advanced-effect frames viewed as full actual PPU images. Normal/Machine/Spread shots and firing poses visible; advanced effect art appears in neighbouring frames. No sampled terrain/block displacement or scene CHR corruption observed.',
        HUD_issue=dict(status='CONFIRMED existing source layout',source='RemainingDraw::Hud uses source pickup art at anchor192,24. Native WORLD is x144..183 and TIME x200..231 on row16. The24px icon spans180..203 and visibly overwrites six white header pixels in this comparison.',records=records,actual_dma=selected,overwritten_native_header_pixels=obscured,
            source_sha256={str(src/n):sha(src/n)for n in ['src/remaining_weapons.s','src/screen_render.s']}),
        advanced_flicker=dict(status='OBSERVED; cause only partially attributed',laser_frames=[2131,2132,2133,2134],flare_frames=[2746,2747,2748,2749],
            observation='Laser absent2131/2132 then visible2133/2134; Flare absent2746/2747 then visible2748/2749. Source has explicit selected-HUD/effect physical-CHR arbitration. Bill body absent in image2133 while adjacent2132/2134 show it; hardware OAM still contains body entries. Exact cause is not established by available endFrame CHR assertions; do not label it clean or blame eight-sprite contention without further evidence.',
            actual_startFrame_OAM=body),
        limits='No new native launch; this does not establish all4344frames graphics clean, waveform fidelity, native acquisition/rise/random drops, matched baseline cadence or universal lag reduction. No game patch made.'))
    report=ROOT/'docs/qa/final-bill-hard-v5-native-and-lance-ready-2026-10-26.txt'
    assert report.exists()
    files={Path(__file__),report,prior/'proof.json',prior/'manifest.json',post/'proof.json',post/'manifest.json',native/'proof.json',
           ROOT/'tools/audit/final_bill_lance_hard_gallery_run_v2.py',ROOT/'tools/audit/final_bill_lance_hard_gallery_postrun_v1.py',ROOT/'tools/audit/final_bill_lance_hard_gallery_postrun_v2.py'}
    files.update(f for f in flight.iterdir()if f.is_file());files.update(f for f in a.output.iterdir()if f.is_file())
    bindings={Path(z['path']):z['sha256']for z in json.loads((post/'manifest.json').read_text())['bindings']}
    assert verify_manifest(post/'manifest.json')==1164
    bindings.update({f:sha(f)for f in files})
    put(a.output/'manifest.json',dict(bindings=[dict(path=str(f.resolve()),sha256=h,bytes=f.stat().st_size)for f,h in sorted(bindings.items())]))
    lance_profile=next(z for z in ready['profiles']if z['profile']=='lance-hard')
    command='python -B tools/audit/final_bill_lance_hard_gallery_run_v2.py --ready "'+a.output.as_posix()+'" --profile lance-hard --native-grant'
    proof=ready|dict(prepared=True,native_run=False,native_granted=False,profiles=[lance_profile],manifest_sha256=sha(a.output/'manifest.json'),bindings=len(bindings),
        old_Bill_host_aggregate_FALSE_preserved=True,Bill_offline_corrected_original_predicates_passed=True,Bill_gameplay_semantic_component_qualified=True,
        visual_issues_remain=['Selected capsule overlaps WORLD/TIME','Advanced effect flicker and one sampled absent Bill body require separate attribution'],
        Bill_original_proof_sha256=sha(native/'proof.json'),Bill_corrected_postrun_sha256=sha(post/'proof.json'),
        fresh_Lance_only_ready=True,old_conditional_Lance_grant_not_portable=True,unchanged_generated_native_Lua_sha256=sha(lance/'run.lua'),
        unchanged_native_config_sha256=sha(lance/'config.json'),new_host_collector_sha256=sha(ROOT/'tools/audit/final_bill_lance_hard_gallery_run_v2.py'),
        commands={'lance-hard':command},freeze_tool_sha256=sha(__file__))
    put(a.output/'proof.json',proof);put(a.output/'commands.json',{'lance-hard':command})
    a.public.mkdir(parents=True,exist_ok=False)
    payload={'original-Bill-host-FALSE.json':native/'proof.json','Bill-offline-qualified.json':post/'proof.json',
        'exact-two-plan-type-differences.json':post/'plan-type-differences.json','offline-negative-controls.json':post/'offline-negative-controls.json',
        'actual-birth-speed-and-cadence.json':post/'actual-speed-cadence-vs-compiled-source.json',
        'visual-review.json':a.output/'visual-review.json','collector-equality.json':a.output/'collector-equality.json','host-collector-only.patch':a.output/'host-collector-only.patch',
        'whole-frame-review-1.png':post/'whole-frame-review-1.png','whole-frame-review-2.png':post/'whole-frame-review-2.png',
        'whole-flight-frames.png':flight/'whole-flight-frames.png','advanced-adjacent-full-frames.png':flight/'advanced-adjacent-full-frames.png',
        'review-placement-provenance.json':post/'review-files.json','flight-provenance.json':flight/'provenance.json','adjacent-provenance.json':flight/'advanced-adjacent-provenance.json',
        'report.txt':report,'Lance-PREPARED-ONLY/proof.json':a.output/'proof.json','Lance-PREPARED-ONLY/commands.json':a.output/'commands.json',
        'external-evidence-bindings.json':a.output/'manifest.json','retained-extra-cross-phase-oracle-FALSE.json':D/'final-bill-hard-v5-postrun-v1/failure.json'}
    copies=[]
    for name,source in payload.items():
        target=a.public/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,target);assert sha(target)==sha(source)
        copies.append(dict(path=name,source=str(source),bytes=source.stat().st_size,sha256=sha(source)))
    owned=[ROOT/'tools/audit'/('final_bill_lance_hard_gallery_'+n)for n in ['run_v2.py','postrun_v1.py','postrun_v2.py','finish_v1.py']]+[report]
    owned_rows=[dict(path=str(f.relative_to(ROOT)).replace('\\','/'),sha256=sha(f),bytes=f.stat().st_size)for f in owned]
    (a.public/'OWNED-FILES.txt').write_text('\n'.join(z['path']for z in owned_rows)+'\n'+str(a.public.relative_to(ROOT)).replace('\\','/')+'/\n',encoding='utf-8')
    (a.public/'README.txt').write_text('Bill exact3b Hard B controlled use: one native launch completed7legal cases/28components. Original host FALSE remains intact: only NORMAL two empty Lua tables serialized{} instead of expected[]. Additive offline collector uses these exact two schema paths; all other predicates/hardware/cadence preserved. It passes. Actual visual review found selected capsule overwriting WORLD/TIME and advanced-effect flicker/one body dropout; no blanket graphics clean claim. Lance is PREPARED ONLY, old conditional grant unused/not portable. No ROM/game/settings changes, no new native from this freeze. Public receipt excludes ROM/audio/raw lossless/settings/3MB native JSON/8MB full collector JSON; exact external bindings preserve those reproduction limits. Four full-frame sheets include50 placements, with explicit contrasting gaps.\n',encoding='utf-8')
    put(a.public/'REVIEW-FILES.json',dict(original_false='original-Bill-host-FALSE.json',typed_comparison=['exact-two-plan-type-differences.json','host-collector-only.patch','collector-equality.json','Bill-offline-qualified.json'],visual_issue=['visual-review.json','whole-frame-review-1.png','whole-frame-review-2.png','whole-flight-frames.png','advanced-adjacent-full-frames.png'],next_ready='Lance-PREPARED-ONLY/proof.json',scope='README.txt'))
    put(a.public/'manifest.json',dict(Bill_original_host_FALSE_preserved=True,Bill_offline_component_qualified=True,Lance_prepared_only=True,
        ROM_sha256=SHA,payloads=copies,stable_owned_files=owned_rows,ready_sha256=sha(a.output/'proof.json')))
    print(json.dumps(dict(Bill_original_host_FALSE_preserved=True,Bill_offline_component_qualified=True,Lance_prepared_only=True,native_run=False,
        proof_sha256=sha(a.output/'proof.json'),manifest_sha256=sha(a.output/'manifest.json'),bindings=len(bindings),
        public_manifest_sha256=sha(a.public/'manifest.json'),public_bytes=sum(f.stat().st_size for f in a.public.rglob('*')if f.is_file()),command=command)))


if __name__=='__main__':main()
