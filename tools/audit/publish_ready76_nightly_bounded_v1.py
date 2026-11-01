"""Freeze compact verification and replace the one Downloads nightly, no backup."""
from pathlib import Path
import csv,hashlib,json,os,zipfile
R=Path(__file__).resolve().parents[2]
J=R/'build/ready76-menu-fixed-v5';P=R/'build/ready76-visible'
O=R/'build/nightly-ready76'
CHECK=R/'docs/qa/checkpoints/2026-11-01/ready76-menu-native-v1'
DEST=Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes')
EXPECTED='28693c0bf61926f5bef62511b5da0b71f97543170d27d0e03e59bb5e70edf0ca'
PARENT='d1c4973cf69702ba02d83706aadda72a2a63a6f0cec6018ec5fa63735ff75393'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
save=lambda p,v:p.write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8')
OWN_TOOLS='''join_hogan_thomas_bounded_v1 fix_ready76_roster_dispatch_bounded_v1
check_ready76_menu_bounded_v1 check_ready76_menu_bounded_v2
prepare_thomas_native_platform_pixels_bounded_v2 prepare_thomas_native_platform_pixels_bounded_v3
prepare_thomas_native_platform_pixels_bounded_v4 prepare_cf_regression_bounded_v1
prepare_roster_flicker_native_bounded_v1 prepare_roster_flicker_native_bounded_v2 prepare_roster_flicker_native_bounded_v3
fix_roster_nmi_budget_bounded_v1 fix_roster_nmi_budget_bounded_v2 fix_roster_nmi_budget_bounded_v3 fix_roster_nmi_budget_bounded_v4 fix_roster_nmi_budget_bounded_v5
relink_menu_main_bounded_v1 check_roster_palette_prune_bounded_v1 check_roster_menu_semantics_bounded_v1
publish_ready76_nightly_bounded_v1'''.split()


def bound(path):
    q=json.loads(path.read_text())
    for p,h in q['bindings'].items():assert sha(p)==h,p
    return q


def native(root,expected):
    ready=bound(root/'ready.json');q=json.loads((root/'capture/result.json').read_text())
    binding=json.loads((root/'capture/binding.json').read_text())
    assert q['passed']and q['ROM_sha256']==expected==ready['ROM_sha256']==binding['ROM_sha256']
    assert binding['exit_code']==0 and binding['ready_sha256']==sha(root/'ready.json')
    return q


def archive(path,paths):
    members={str(p.relative_to(R)).replace('\\','/'):p for p in paths}
    assert len(members)<256 and sum(p.stat().st_size for p in members.values())<20_000_000
    with zipfile.ZipFile(path,'w',zipfile.ZIP_DEFLATED,compresslevel=9)as z:
        for name,p in sorted(members.items()):z.write(p,name)
    return dict(path=str(path.relative_to(R)),sha256=sha(path),bytes=path.stat().st_size,members=len(members))


def main():
    assert not O.exists()and not CHECK.exists()
    assert sha(J/'candidate.nes')==EXPECTED
    bound(J/'source-stage.json')
    menu=native(J/'menu-native',EXPECTED)
    assert menu['heading_errors']==menu['visible_mask_writes']==0 and len(menu['transitions'])==120
    rows=list(csv.DictReader((J/'menu-native/capture/frames.csv').open()))
    assert len(rows)==2400 and len({r['header_hash']for r in rows})==1
    admission=bound(J/'menu-checks/controls.json');semantics=bound(J/'semantics/result.json')
    assert admission['passed']and admission['playable']==76 and admission['Start_A_cases']==688
    assert semantics['passed']and semantics['identities']==86
    hogan=native(J/'hogan-native',EXPECTED);thomas=native(J/'thomas-native',EXPECTED)
    assert hogan['main_updates']==663 and hogan['counters']['defeat']==1
    assert len(thomas['pipe_clears'])==1 and thomas['counters']['defeat']>0
    four=native(P/'thomas-pixel-route',PARENT)
    assert len(four['pipe_clears'])==4 and four['counters']['defeat']==3
    cf={name:native(P/('cf-'+name),PARENT)for name in['burns','smith','iron','beans']}
    # Final changes are confined to the menu's one bank; both selected source
    # images and every CHR byte remain identical to the four-pipe/CF parent.
    old,new=[(p/'candidate.nes').read_bytes()for p in[P,J]]
    assert all(a==z or 16+66*8192<=i<16+67*8192 for i,(a,z)in enumerate(zip(old,new)))
    O.mkdir();CHECK.mkdir(parents=True)
    source={R/'tools/audit'/f'{n}.py'for n in OWN_TOOLS}
    source.add(R/'tools/reference/roster_flicker_native_bounded_v1.lua')
    source|={p for p in(R/'build/hogan-thomas-current/src').glob('*')if p.is_file()}
    source.add(R/'build/hogan-thomas-current/entrypoint.s')
    source.add(P/'new_roster_dispatch.s')
    for joint in[R/'build/hogan-thomas-current',P,*[R/f'build/ready76-menu-fixed{s}'for s in['','-v2','-v3','-v4','-v5']]]:
        source|={joint/n for n in['source-stage.json','candidate.cfg','main-build.json','final-link.json']}
        if(joint/'menu_vram_budget.s').exists():source.add(joint/'menu_vram_budget.s')
    source_archive=archive(CHECK/'source.zip',source)
    native_paths=set()
    for root in[J/'menu-native',J/'hogan-native',J/'thomas-native',P/'thomas-pixel-route',*[P/('cf-'+n)for n in cf],P/'menu-nmi-timing']:
        native_paths|={root/n for n in['ready.json','controller.lua','run.py']}
        native_paths|={p for p in(root/'capture').iterdir()if p.is_file()and p.suffix in['.json','.png','.csv','.log']}
    for rel in['menu-checks/controls.json','semantics/result.json']:native_paths.add(J/rel)
    native_archive=archive(CHECK/'native-results.zip',native_paths)
    summary=dict(complete=False,ROM_sha256=EXPECTED,playable=76,total_identities=86,source=source_archive,native=native_archive,
                 menu=dict(transitions=120,physical_frames_observed=2400,identical_heading=True,visible_mask_writes=0,source_admission_cases=688,source_preview_equivalence_cases=86),
                 Hogan=dict(ROM=EXPECTED,Main=hogan['main_updates'],frames=hogan['frames'],defeats=hogan['counters']['defeat']),
                 Thomas=dict(final_ROM=EXPECTED,final_pipe_clears=1,final_Main=thomas['Main'],four_pipe_parent=PARENT,parent_Main=four['Main'],parent_frames=four['frames'],parent_defeats=3,parent_pipes=[v['pipe_X']for v in four['pipe_clears']],body_pixel_frames=four['counters']['body_pixels'],platform_pixel_frames=four['counters']['platform_pixels']),
                 Contra_Force=dict(native_parent=PARENT,variants=list(cf),source_images_and_native_imports_unchanged=True),
                 limits=['Opening routes, not full1-1/shortcut or every powerup','Hogan and Thomas original audio/advanced moves remain incomplete','Ten menu identities remain pending; broader roster/campaign work remains active','Whole-menu heading flash regression checked; colored preview overlap in static portrait hashes is not counted as a heading error'])
    save(CHECK/'handoff.json',summary)
    (CHECK/'README.md').write_text('''# 76-character nightly and character-select timing repair

The final ROM adds Thomas alongside Hogan. Thomas is the second Select alternate
in Ryu's slot. Ten of the86 individual menu identities remain coming soon.

The original combined ROM had17 menu transitions whose rendering/scroll work
ran past the safe update window. Accept the actual palette packet shapes, reuse
the static legend, omit unused palette writes based on actual OAM, and coalesce
duplicate portrait colors. Alex's forced outlines are retained.

The final cold-controller sweep covers120 D-pad/Select transitions and2400
physical transition frames: every heading pixel is identical and no PPUMASK
write reaches a visible scanline. Actual source CPU execution verifies688
Start/A cases and86 unchanged preview OAM/displayed-palette results.

On the final ROM, Hogan repeats his663-update jump/punch/Goomba/camera route;
Thomas repeats selection/lives/source melee and the first native moving-platform
pipe crossing. The combined gameplay parent also clears all four1-1 pipes with
Thomas and earns pistol defeats with all four Contra Force characters. Subsequent
changes are confined to the menu bank; all CHR and selected source images are exact.

These are bounded opening-route checks. Full stages, every upgrade, original
audio and the remaining roster/campaign work are still incomplete.

`source.zip` stores the exact source grafts and recipes, not a standalone prepared
builder. Reuse existing frozen component inputs; recover only exact missing
source paths from the indexed recovery archive. Do not recursively extract old
proof trees. `native-results.zip` stores compact controllers, receipts and at most
four PNGs per run. No videos or frame-image sequences were created.
''',encoding='utf-8')
    before=sha(DEST)if DEST.exists()else None;temporary=DEST.with_name(DEST.name+'.publishing')
    assert not temporary.exists();temporary.write_bytes(new);assert sha(temporary)==EXPECTED
    os.replace(temporary,DEST);assert sha(DEST)==EXPECTED
    receipt=dict(installed=True,backup_created=False,destination=str(DEST),output_sha256=EXPECTED,replaced_sha256=before,playable_identities=76,new_identity='Thomas',checkpoint=str(CHECK.relative_to(R)),checkpoint_sha256=sha(CHECK/'handoff.json'),verification=summary)
    save(O/'installed.json',receipt);save(R/'docs/qa/nightly-2026-11-01-ready76.json',receipt)
    (R/'docs/images/character-select.png').write_bytes((J/'thomas-native/capture/selected.png').read_bytes())
    handoff_path=R/'docs/qa/continuation-current.json';handoff=json.loads(handoff_path.read_text())
    handoff['date']='2026-11-01'
    handoff['current_priority']='Menu heading-flash repair and76-character nightly delivered. Continue remaining pending source characters and the original full-roster/full-stage objective.'
    handoff['installed_nightly']=dict(path=str(DEST),sha256=EXPECTED,playable_identities=76,new_identity='Thomas',backup_created=False,source_joint=str(J.relative_to(R)),receipt='docs/qa/nightly-2026-11-01-ready76.json',native_checkpoint=str(CHECK.relative_to(R)),scope=summary)
    handoff['combined76']=dict(final_joint=str(J.relative_to(R)),candidate=EXPECTED,gameplay_parent=PARENT,source_admissions=688,preview_semantics=86,native_menu_transitions=120,native_transition_frames=2400,heading_errors=0,visible_PPUMASK_writes=0,Thomas_parent_four_pipe_Main=2080,CF_parent_variants=list(cf),final_Hogan_Main=663,final_Thomas_first_pipe_Main=thomas['Main'],all_native_queues_terminal=True)
    handoff['Thomas_final_component']['installed_as_part_of']=EXPECTED
    handoff['Thomas_final_component']['installed']=True
    handoff['Thomas_final_component']['still_required']=['Full1-1 and shortcut','All powerups and native objects/effects','Original audio and remaining source moves','Other stages/pipe and gap compatibility']
    handoff['composition_notes']['composition_completed']=True
    handoff['menu_flicker_followup']=dict(reproduced=17,final_heading_errors=0,final_visible_mask_writes=0,notes='Accept actual palette packets; remove static hint; prune only unused palettes; coalesce universal/final colors and discard fully shadowed3F11/3. Alex/Ryan required outlines retained. Harmless colored-preview overlap still changes the broader static-portrait hash; no claim of complete menu layout polish.')
    handoff['storage']['build_last_bytes_approx']=1_450_000_000
    handoff['Mesen']='All owned SMB queues are terminal. External projects may run Mesen concurrently. Root owns one SMB queue; --doNotSaveSettings, original sprite limits, owned-process watchdog and bounded storage rules remain required.'
    save(handoff_path,handoff)
    print(json.dumps(dict(installed=True,destination=str(DEST),sha256=EXPECTED,playable=76,backup_created=False,checkpoint=str(CHECK.relative_to(R)))))


if __name__=='__main__':main()
