"""Keep the full roster/arsenal/media requirements visible without greenwashing."""
from pathlib import Path
import hashlib,json,re
R=Path(__file__).resolve().parents[2];V=R/'build/verification'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
NAMES=['Mario','Mega Man','Samus','Bill','Link','Simon','Pit','Rygar','Luigi','Bass','Ryu','Sophia','Scrooge']


def main():
    out=V/'root49-goal-coverage-aw.json';assert not out.exists()
    path=R/'src/inventory_data.inc';text=path.read_text()
    def table(name):
        block=re.search(r'^'+name+r':\n(.*?)(?=^\w+:|\Z)',text,re.M|re.S).group(1)
        return [int(x)for x in re.findall(r'\b\d+\b',block)]
    counts=table('InvItemCount');assert len(counts)==12
    words={int(i):n.strip()for i,n in re.findall(r'^InvName(\d+): \.byte "([^"]*)"',text,re.M)}
    nblock=re.search(r'^InvNameLo:\n(.*?)^InvNameHi:',text,re.M|re.S).group(1)
    ids=[int(i)for i in re.findall(r'<InvName(\d+)',nblock)];assert len(ids)==192
    itemdata={key:table('Inv'+key)for key in ['InitialAmmo','MaxAmmo','Costs','Availability','Selectable','AutoEquip','AmmoIndex']}
    assert all(len(t)==192 for t in itemdata.values())
    checkpoints={}
    for revision,folder in [('C','roster-audit-v49-combined-ground-audio-samus-c'),('D','roster-audit-v49-sophia-head-axis-d')]:
        p=R/'build/checkpoints'/folder/'manifest.json';q=json.loads(p.read_text())
        checkpoints[revision]=dict(path=str(p.relative_to(R)),sha256=sha(p),ROMs={b['mapper']:b['artifacts']['nes']['sha256']for b in q['builds']})
    images={h:(revision,mapper)for revision,q in checkpoints.items()for mapper,h in q['ROMs'].items()}
    admitted={}
    for p in (R/'build/roster-through-2-2').glob('*/manifest.json'):
        q=json.loads(p.read_text());which=images.get(q.get('rom_sha256'))
        if not which or not q.get('verified_through_2_2'):continue
        assert q['controller_only']and not q['memory_or_register_writes']and q['full_frame_audit']
        assert q['result']['cleared']and q['result']['all_six_stages']and not q['result']['deaths']
        assert sha(p.parent/'inputs.csv')==q['inputs_sha256']
        key=(q['config']['character'],q['config'].get('variant',0))
        admitted.setdefault(key,[]).append(dict(revision=which[0],mapper=which[1],manifest=str(p.relative_to(R)),sha256=sha(p),
                                               frames=q['result']['frames'],recorded=q['config']['record']))
    roster=[]
    for character,variant in [(c,0)for c in range(13)]+[(3,1)]:
        inventory=[]
        if character<len(counts):
            for ident in range(1,counts[character]+1):
                index=character*16+ident
                inventory.append(dict(item_id=ident,name=words[ids[index]],properties={k:v[index]for k,v in itemdata.items()},
                                      current_final_build_complete=False,
                                      required_evidence=['actual pickup/ownership and selection','ground/air/crouch/water use where supported',
                                                         'contact/properties/ammo/lifecycle','graphics/palette/SFX','measured lag and foreign regressions']))
        roster.append(dict(character=character,variant=variant,name='Lance'if variant else NAMES[character],
                           full_route_required=True,full_final_recording_required=True,
                           pinned_full_clear_candidates=admitted.get((character,variant),[]),
                           inventory_2_02=inventory,Easy_legacy_inventory_suppressed=1<=character<=5,
                           base_moves_and_power_tiers_complete=False,all_specials_upgrades_complete=False,
                           final_recording_complete=False,overall_complete=False))
    result=dict(status='INCOMPLETE_FULL_GOAL_ROSTER_ARSENAL_AND_MEDIA_AUDIT_INDEX',script_sha256=sha(__file__),
                checkpoints=checkpoints,source_inventory=dict(path=str(path.relative_to(R)),sha256=sha(path)),roster=roster,
                requirements=['Full ordinary controller playthrough through2-2 for every playable identity, including Luigi/Lance alternates.',
                              'Each attack, special, alternate weapon and upgrade, including base power tiers and ROM-added Pit/Rygar/Scrooge behavior.',
                              'Source-appropriate Easy/Hard behavior, swimming, block/enemy interactions, pickup recovery/refills and death/victory transitions.',
                              'Profile laggy abilities, optimize real bottlenecks, and retain measured CPU/physical-frame/render/audio evidence.',
                              'Final retained lossless playthrough recordings for all identities, validated video frames/audio and inspected for defects.',
                              'Earlier1-1 shortcut and non-shortcut playthrough requirements remain to reconcile; not silently removed.'],
                shared_behavior_checks=['walking/jump/scroll','grounded/air/crouch attacks','swimming','blocks/bricks/question boxes',
                                        'enemy contact/armor/stomping policy','powerup animation and SFX','sprite overflow/flicker/palettes',
                                        'flagpole/axe/trampoline/death/restart','outlines option and menu alternatives'],
                limits=['Inventory names/properties are current generated ROM data, not proof of source conformance.',
                        'Pinned C clears are retained as C; they are not automatically relabelled as D or as final recorded playthroughs.',
                        'Existing detailed character packets remain evidence candidates requiring scope/build admission, not erased or declared failures.',
                        'No arsenal or final movie is declared complete by this index. Both mapper compatibility remains tracked in the detailed packets.'],
                global_cap_bytes=70000000000,retains_lossless=True,goal_complete=False)
    out.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(status=result['status'],identities=len(roster),inventory_entries=sum(len(z['inventory_2_02'])for z in roster),
                          pinned_current_family_full_clear_manifests=sum(len(z['pinned_full_clear_candidates'])for z in roster),sha256=sha(out))))


if __name__=='__main__':main()
