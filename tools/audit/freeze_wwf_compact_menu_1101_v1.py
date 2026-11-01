"""Small source/proof packet for the tested current85 WWF preview repair."""
from pathlib import Path
import hashlib,json,sys,zipfile
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit')]
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address
O=R/'build/menu-wwf-compact-1101-v1';J=R/'build/doki-current-component-1101-v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
save=lambda p,q:p.write_text(json.dumps(q,indent=2)+'\n',encoding='utf-8')

def main():
    stage=json.loads((O/'assembly-stage.json').read_text());cpu=json.loads((O/'menu-CPU-controls.json').read_text())
    assert stage['passed']and cpu['passed']and stage['ROM_sha256']==cpu['ROM_sha256']==sha(O/'candidate.nes')
    for q in [stage,cpu]:
        for p,h in q['bindings'].items():assert sha(p)==h,p
    assert cpu['menu_identities']==90 and cpu['playable']==85 and cpu['Start_A_cases']==720 and cpu['non_WWF_whole_application_contexts_exact']==84 and cpu['X_funding_all_indices_all_status_flags']==8192
    b=scoped_load(J/'candidate.nes');before=(J/'candidate.nes').read_bytes();after=(O/'candidate.nes').read_bytes();delta=[[i,x,y]for i,(x,y)in enumerate(zip(before,after))if x!=y]
    lo,hi=stage['allowed_ROM_range'];assert len(before)==len(after)and len(delta)==193 and all(lo<=i<hi for i,x,y in delta)
    rebuilt=bytearray(before)
    for i,x,y in delta:assert rebuilt[i]==x;rebuilt[i]=y
    assert bytes(rebuilt)==after
    save(O/'ROM-delta.json',dict(parent_ROM_sha256=sha(J/'candidate.nes'),candidate_ROM_sha256=sha(O/'candidate.nes'),size=len(after),format='Each triple is absolute ROM file offset, original byte, replacement byte.',changes=delta,round_trip_exact=True))
    # Verify every changed application byte belongs to a named drawing output.
    # Constants and linker aliases at coincident addresses are not state owners.
    fields={n:(address(b,n),address(b,n)+size)for n,size in [('R0',8),('Player_X_Position',1),('Player_Y_Position',1),('Player_Y_HighPos',1),('PlayerFacingDir',1),('Sprite_Data',256),('VRAM_Buffer1_Offset',1),('VRAM_Buffer1',84),('CurrentOAMOffset',1),('ObjectMetasprite',1),('X5ChrMode',12),('CurrentBankC',1)]}
    fields['MMC5_C_PRG_latch']=(0x5116,0x5117)
    changed={int(q['address'],16)for q in cpu['WWF_draw_local_difference_addresses']}
    assert all(any(a<=p<z for a,z in fields.values())for p in changed),[hex(p)for p in changed if not any(a<=p<z for a,z in fields.values())]
    summary={n:[hex(p)for p in sorted(changed)if a<=p<z]for n,(a,z)in fields.items()}
    save(O/'WWF-draw-delta-summary.json',dict(passed=True,changed_application_addresses=len(changed),exact_changed_draw_fields=summary,persistent_identity_variant_health_gear_lives_options_cheats_Start_unchanged=True,inactive_OAM_note='MoveAllSpritesOffscreen hides all unused sprites byY=248. Invisible tile/attribute/X bytes retain prior native pose data; compact equivalence checks active16B plus every inactiveY, not those invisible stale bytes.'))
    selected=[R/'tools/audit/build_wwf_compact_menu_1101_v1.py',R/'tools/audit/check_wwf_compact_menu_1101_v1.py',Path(__file__).resolve()]
    selected+=[O/n for n in ['entrypoint.s','character_select.s','candidate.cfg','baseline-reproduction.json','baseline-main-build.json','baseline-link.json','compact-main-build.json','compact-link.json','assembly-stage.json','menu-CPU-controls.json','ROM-delta.json','WWF-draw-delta-summary.json']]
    bindings={p.relative_to(R).as_posix():sha(p)for p in selected};target=O/'source-and-proof.zip'
    with zipfile.ZipFile(target,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9)as z:
        for p in selected:z.write(p,p.relative_to(R).as_posix())
        z.writestr('source-file-hashes.json',json.dumps(bindings,indent=2)+'\n')
    handoff=dict(status='CURRENT85_WWF_COMPACT_PREVIEW_SOURCE_CPU_PASS_ROOT_NATIVE_ADMISSION_PENDING',native=False,installed=False,ROM_sha256=stage['ROM_sha256'],parent_ROM_sha256=stage['parent_ROM'],archive=dict(path=target.relative_to(R).as_posix(),sha256=sha(target),bytes=target.stat().st_size,members=len(selected)+1),source_entrypoints_preserved=True,ROM_changed_bytes=193,allowed_ROM_range=[lo,hi],identities=90,playable=85,unchanged_non_WWF_application_contexts=84,Start_A_comparisons=720,X_funding_ABI_cases=8192,authentic_compact_profiles=6,new_stack_bytes=0,new_RAM_bytes=0,funding=stage['funding'],WWF_draw_local_fields=summary,next='Root owns actual native90-identity sweep and six WWF Start/lives/game restoration tests, final checkpoint and nightly replacement. This packet records source/CPU evidence only.',bindings=bindings)
    save(O/'handoff.json',handoff)
    print(json.dumps(dict(passed=True,candidate=stage['ROM_sha256'],archive_bytes=target.stat().st_size,archive_members=len(selected)+1,archive_sha256=sha(target))))

if __name__=='__main__':main()
