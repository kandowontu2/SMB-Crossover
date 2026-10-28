"""Offline pose74 ordering bound. No ROM patch, emulator or new image epochs."""
from pathlib import Path
import collections
import itertools
import json
from current_roster_compact_11_v1 import ROOT, sha
from current326_octopus_visibility_review_v1 import pixels

FOLDER=ROOT/'build/verification/compact-326942-octopus-visibility-v1'
OUTPUT=FOLDER/'core-order-counterfactual.json'


def main():
    assert not OUTPUT.exists()
    actual=json.loads((FOLDER/'body-final-review.json').read_text())
    assert all(sha(ROOT/p)==h for p,h in actual['owned'].items())
    rows=[json.loads(s) for s in (FOLDER/'octopus-visibility.jsonl').read_text().splitlines()]
    start=next(q for q in rows if q['kind']=='start-frame' and q['stamp']['ppu_frame']==3261)
    body=next(q for q in rows if q['kind']=='body-native-renderer' and q['body_id']==2)
    d=start['data'];hw=bytes.fromhex(d['physical256']);rompath=ROOT/'build/zelda2_easy_glove.nes';rom=rompath.read_bytes()
    sprites,patterns=pixels(hw,d['state']['chr_banks'],bytes.fromhex(d['palette32']),rom,16+rom[4]*16384)
    slots=list(range(56,63));parts=[sprites[s] for s in slots]
    union=set().union(*parts);assert sum(map(len,parts))==len(union)==218
    # Disjoint opaque masks preserve body image for EVERY record permutation,
    # independently of current palette coincidences. Rectangles still overlap.
    record=bytes.fromhex(body['data']['record']['mapped_record']);original_parts=[record[i:i+4] for i in range(1,len(record),4)]
    assert len(original_parts)==7
    ys=range(51,86);other={}
    for i in range(56):
        for p,color in sprites[i].items():other.setdefault(p,(i,color))
    counts=[[sum(y==yy and (x,y)not in other for x,y in part) for yy in ys] for part in parts]
    eligible=[[hw[(56+j)*4]+1<=y<=hw[(56+j)*4]+16 for j in range(7)] for y in ys]
    before=[sum(hw[i*4]+1<=y<=hw[i*4]+16 for i in range(56)) for y in ys]
    def score(perm):
        total=0
        for row,y in enumerate(ys):
            capacity=8-before[row]
            for j in perm:
                if eligible[row][j]:
                    if capacity>0:total+=counts[j][row]
                    capacity-=1
        return total
    scores=collections.Counter(score(p) for p in itertools.permutations(range(7)))
    assert sum(scores.values())==5040 and max(scores)==144 and scores[144]==240
    permutation=sorted(range(7),key=lambda i:(-len(parts[i]),i))
    assert permutation==[5,4,2,3,0,6,1] and score(permutation)==144 and score(range(7))==45
    # The real renderer consumes record entries in reverse. Disclose the exact
    # hypothetical source bytes; NEVER write them to a source/ROM candidate.
    source_order=[6-i for i in reversed(permutation)]
    proposed=bytes([28])+b''.join(original_parts[i] for i in source_order)
    assert collections.Counter(original_parts)==collections.Counter(proposed[i:i+4] for i in range(1,29,4))
    original_order=list(range(64));new_order=original_order.copy()
    for i,j in enumerate(permutation):new_order[56+i]=56+j
    def model(order,rotation,limited):
        order=order[-rotation:]+order[:-rotation] if rotation else order
        first={}
        for y in range(240):
            candidates=[index for index,identity in enumerate(order) if hw[identity*4]+1<=y<=hw[identity*4]+16]
            first[y]=set(candidates[:8] if limited else candidates)
        image={}
        for index,identity in enumerate(order):
            for p,color in sprites[identity].items():
                if index in first[p[1]]:image.setdefault(p,(identity,color))
        return image
    comparisons=[]
    for rotation in range(64):
        old=model(original_order,rotation,True);new=model(new_order,rotation,True)
        unlimited_old=model(original_order,rotation,False);unlimited_new=model(new_order,rotation,False)
        body_before=sum(q[0] in slots for q in old.values());body_after=sum(q[0] in slots for q in new.values())
        other_lost=[p for p,q in old.items() if q[0] not in slots and new.get(p,(-1,-1))[1]!=q[1]]
        full_changed=[p for p in unlimited_old.keys()|unlimited_new.keys() if unlimited_old.get(p,(-1,-1))[1]!=unlimited_new.get(p,(-1,-1))[1]]
        physical_start=(224+rotation*4)&255;wrap=physical_start+28>256
        if not wrap:assert body_after>=body_before and not other_lost and not full_changed
        comparisons.append(dict(hypothetical_ring_shift_slots=rotation,physical_body_start=physical_start,body_span_wraps=wrap,
            actual_order_body_winners=body_before,core_first_body_winners=body_after,other_actor_NES_color_pixels_lost=len(other_lost),
            unlimited_full_scene_color_pixels_changed=len(full_changed),
            guard_fallback_body_winners=body_before if wrap else body_after))
    assert sum(q['body_span_wraps'] for q in comparisons)==6
    regression=[q for q in comparisons if q['core_first_body_winners']<q['actual_order_body_winners']]
    other_regression=[q for q in comparisons if q['other_actor_NES_color_pixels_lost']]
    full_changes=[q for q in comparisons if q['unlimited_full_scene_color_pixels_changed']]
    assert len(regression)==4 and len(other_regression)==5 and len(full_changes)==5
    assert all(q['body_span_wraps'] for q in regression+other_regression+full_changes)
    assert all(q['guard_fallback_body_winners']>=q['actual_order_body_winners'] for q in comparisons)
    # Negative controls demonstrate that this is not an unconditional image
    # equality rule: displaced or removed authenticated pixels must differ.
    shifted={(x+1,y) for x,y in parts[5]};removed=union-{next(iter(union))}
    assert shifted!=set(parts[5]) and removed!=union
    bindings=[Path(__file__).resolve(),ROOT/'tools/audit/current326_octopus_visibility_review_v1.py',
        FOLDER/'body-attribution.json',FOLDER/'body-final-review.json',FOLDER/'octopus-visibility.jsonl',
        rompath,rompath.with_suffix('.dbg'),rompath.with_suffix('.lbl'),ROOT/'src/metasprite_engine.s',
        ROOT/'src/parodius_render.s',ROOT/'src/parodius_adapter.s']
    result=dict(passed=True,source_only_counterfactual=True,native_run=False,ROM_sha256=sha(rompath),
        actual_evidence_unchanged=True,pose=74,bank=76,pointer=0xc89d,header=28,
        opaque_masks_disjoint=True,complete_body_pixels=218,all_5040_permutations_full_body_image_identical=True,
        score_histogram=dict(sorted(scores.items())),maximum_body_winners=144,maximum_tied_orders=240,
        actual_priority_parts=[dict(old_physical_part=i,source_part=6-i,opaque_pixels=len(parts[i]),**patterns[56+i]) for i in range(7)],
        proposed_physical_part_order=permutation,proposed_source_part_order=source_order,
        hypothetical_record=proposed.hex(),original_record=record.hex(),
        actual3261=dict(body_winners_before=45,body_winners_after=144,additional_body_pixels=99,
            otherwise_visible_body_pixels_still_excluded=54,projectile_occlusion_unchanged=20,
            all_earlier_projectile_pixels_unchanged=True),
        hypothetical_same_scene_all64_rotations=comparisons,body_regression_rotations=len(regression),
        other_actor_loss_rotations=len(other_regression),unlimited_scene_changed_rotations=len(full_changes),
        nonwrapped_rotations=58,nonwrapped_body_regressions=0,nonwrapped_other_actor_color_losses=0,
        unconditional_data_only_reorder_qualified=False,
        reason='Wrapped physical spans move differently colored overlapping body/projectile pixels across the hardware priority boundary and can sharply reduce body readability. At start248,213 body winners become61.',
        conditional_bound='Literal original order on all wrapped spans and proposed core order only nonwrapped eliminates these negatives in this one captured-scene64-ring model. Such a selector adds runtime/source work; it is NOT a data-only qualified implementation.',
        generalization_constraints=['This exact pose74/current pool0/page834/mode0/facing1 geometry only; no other source frame is inferred.',
            'Fully-visible body equality is palette-independent here because opaque masks are disjoint. Foreign overlap priority still changes on wrap.',
            'A generalized change must freshly bind every body/facing/Big/tier alias, source palette/CHR, outline-filtered version and offscreen clipping.',
            'ObjectVerticalFlip is0 in the witness; the DrawMetasprite post-render3/4-part vertical-flip tail relies on record ordering and is not qualified.',
            'Main/interrupt/liveness and per-path CPU costs need actual assembled controls before any candidate; no zero-cycle/cadence improvement follows from this model.',
            'The held e11/2dc actual negatives remain valid and unchanged. This narrow mask result does not clear them.'],
        no_new_images_or_epochs=True,no_ROM_source_patch=True,bindings={str(p):sha(p) for p in bindings})
    OUTPUT.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(proof=str(OUTPUT),sha256=sha(OUTPUT),bindings=len(bindings),actual45_to144=True,unconditional_reorder_qualified=False),indent=2))


if __name__=='__main__':main()
