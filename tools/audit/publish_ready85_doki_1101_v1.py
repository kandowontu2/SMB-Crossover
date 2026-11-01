"""Freeze exact Doki/USA evidence and overwrite the user's nightly, no backup."""
from pathlib import Path
import csv,hashlib,json,os,re,sys,zipfile
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools'),str(R/'tools/audit')]
from build_storage_guard_v1 import inventory
J=R/'build/doki-current-component-1101-v1';N=R/'build/doki-final-native-1101-v1';M=R/'build/doki-menu-native-1101-v1'
O=R/'build/nightly-ready85-doki-1101-v1';K=R/'docs/qa/checkpoints/2026-11-01/ready85-doki-native-v1'
DEST=Path('C:/Users/kando/Downloads/SMB-Crossover-Latest-WIP-MMC5.nes')
EXPECTED='f6415a64767b9ea1ada79ac5ccab433d7b1f4ae5f8bb13e53f04adeca717a3f1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
save=lambda p,v:p.write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8')


def bound(p):
    q=json.loads(p.read_text(encoding='utf-8'))
    for f,h in q['bindings'].items():assert sha(f)==h,f
    return q


def native(p):
    ready=bound(p/'ready.json');q=json.loads((p/'capture/result.json').read_text());binding=json.loads((p/'capture/binding.json').read_text())
    assert q['passed']and ready['ROM_sha256']==q['ROM_sha256']==binding['ROM_sha256']==EXPECTED
    assert binding['exit_code']==0 and binding['ready_sha256']==sha(p/'ready.json')
    files=[p/'ready.json',p/'controller.lua',p/'run.py',*[f for f in(p/'capture').iterdir()if f.is_file()]]
    assert len(files)<=64 and sum(f.stat().st_size for f in files)<128_000_000 and sum(f.suffix=='.png'for f in files)<=4
    return q,set(files)


def archive(p,files):
    files={f.resolve()for f in files};assert len(files)<256 and sum(f.stat().st_size for f in files)<20_000_000
    with zipfile.ZipFile(p,'w',zipfile.ZIP_DEFLATED,compresslevel=9)as z:
        for f in sorted(files):z.write(f,f.relative_to(R).as_posix())
    with zipfile.ZipFile(p)as z:assert z.testzip()is None
    return dict(path=p.relative_to(R).as_posix(),sha256=sha(p),bytes=p.stat().st_size,members=len(files))


def main():
    assert not(J/'source-stage.json').exists()
    assert not O.exists()or not any(O.iterdir())
    assert not K.exists()or not any(K.iterdir())
    assert sha(J/'candidate.nes')==EXPECTED
    assembly=bound(J/'graphics-assembly.json');graphics=bound(J/'graphics-controls.json');physics=bound(J/'physics-controls.json');suite=bound(N/'suite-results.json')
    assert all(q['passed']for q in [assembly,graphics,physics,suite])
    assert graphics['candidate']==physics['candidate']==suite['candidate']==EXPECTED
    assert graphics['playable']==85 and graphics['menu_identities']==90 and graphics['Start_A_cases']==720
    runs={};proof={N/'suite-results.json'}
    for name,v in [('imajin',4),('lina',5),('papa',6),('mama',7),('mario',0),('luigi',1),('toad',2),('peach',3)]:
        q,files=native(N/name);proof|=files;runs[name]=q
        assert q['variant']==v and q['Main']==q['source_movement']and q['Main']>300
        assert q['jumped']and q['landed']and q['maximum_camera']>=257 and q['ISR_returns']>1000
        assert all(q['display'][n]['visible']and q['graphics_checks'][n]>0 for n in ['selected','lives','game'])
    menu,files=native(M);proof|=files
    assert menu['heading_errors']==menu['visible_mask_writes']==0 and len(menu['transitions'])==124
    with(M/'capture/frames.csv').open()as f:frames=list(csv.DictReader(f))
    assert len(frames)==2480 and len({q['header_hash']for q in frames})==1
    O.mkdir(exist_ok=True);K.mkdir(parents=True,exist_ok=True)
    # Only direct current compiler inputs: do not recursively restore old trees.
    deps=assembly['bindings'].copy();deps[str(J/'graphics-assembly.json')]=sha(J/'graphics-assembly.json')
    line=(J/'main.dep').read_text().splitlines()[0].split('\t',1)[1]
    direct=[Path(s.replace('\\ ', ' '))for s in re.split(r'(?<!\\)\s+',line.strip())]
    direct=[p if p.is_absolute()else R/p for p in direct]
    link=json.loads((J/'graphics-link.json').read_text())['command']
    direct += [Path(x)for x in link if x.endswith('.o')]
    assert direct and len(direct)<1000
    for p in direct:assert p.is_file(),p;deps[str(p.resolve())]=sha(p)
    deps[str(Path(__file__).resolve())]=sha(__file__)
    save(J/'source-stage.json',dict(passed=True,source=True,native=True,installed=False,candidate=EXPECTED,private_playable=85,total_identities=90,parent='429b9f3c3fb551ec023d997f9e83515a2c68f1447a2d4a7cad43c029ff5ee3e2',bindings=deps,scope='Four original Doki modes and four USA regressions, opening native routes and all90 menu choices. Full levels, shortcuts, every powerup, original Doki music and constant60Hz remain unqualified.'))
    source={p for p in(J/'src').iterdir()if p.is_file()}|{p for p in(J/'menu').iterdir()if p.is_file()}
    source|={J/n for n in ['source-stage.json','graphics-assembly.json','graphics-controls.json','physics-controls.json','graphics-build.json','graphics-main-build.json','graphics-asset-build.json','graphics-link.json','candidate.cfg','asset.s','doki12k.chr','main.dep','before-graphics-sources.json']}
    source|={R/'tools/audit'/n for n in ['integrate_doki_graphics_current_1101_v1.py','check_doki_current_physics_1101_v1.py','check_doki_graphics_current_1101_v1.py','prepare_doki_native_1101_v1.py','prepare_doki_menu_native_1101_v1.py','run_doki_native_suite_1101_v1.py','publish_ready85_doki_1101_v1.py']}
    source|={R/'tools/reference'/n for n in ['doki_current_draw_v1.s','doki_native_bounded_1101_v1.lua']}
    src=archive(K/'source.zip',source);proof|={J/'graphics-controls.json',J/'physics-controls.json'};native_zip=archive(K/'native-results.zip',proof)
    limits=['Opening camera routes only; full1-1, shortcut and every-powerup checks remain unfinished','Doki motion/carry/health-mode and art match the declared original-source fixtures; this is an SMB1 integration, not the complete Doki game','Doki uses the existing SMB2 audio; an original Doki audio port is not qualified','No constant60Hz, hardware-console, complete combat/upgrade or full-roster campaign claim','Five existing menu identities and additional original-goal characters/campaigns remain unfinished','Reviewed source grafts/recipes reuse prior frozen inputs; canonical prepared builder still has37 identities']
    summary=dict(complete=False,ROM_sha256=EXPECTED,playable=85,total_identities=90,source=src,native=native_zip,physics={k:v for k,v in physics.items()if k not in ['bindings','health_transition_prefixes','scope']},graphics={k:v for k,v in graphics.items()if k not in ['bindings','scope']},menu=dict(transitions=124,transition_frames=2480,heading_errors=0,visible_mask_writes=0),characters={name:suite['rows'][name]for name in runs},limits=limits)
    save(K/'handoff.json',summary)
    (K/'README.md').write_text('''# 85-character Doki nightly

The SMB2 slot cycles Mario, Luigi, Toad, Peach, Imajin, Lina, Papa and Mama.
The four Doki modes use original FDS character graphics, palettes and frame
data. Their conditional original movement has no B speed boost, Mama's
original jump table, original carry offsets, and no USA small-form transition.
Changing between lineages with the same native class resets the right stats.

All eight characters pass cold controller routes through selection, lives,
idle, jump/landing and the opening camera boundary. Actual DMA descriptors,
CHR patterns, displayed sprites and interrupt register/SMC restoration are
observed with the normal eight-sprites-per-scanline limit. These are opening
routes, not full1-1, shortcut, combat or every-powerup clears.

CPU comparisons cover192 jump,32 movement, four lift and720 carry contexts,
plus3,360 old USA carry cases across both sizes and all seven lift stages.
There are10,512 engine executions. All128 original Doki drawing packets,
256 USA pose cases,73 old art records, four original palettes,16 HUD/title
names and720 Start/A cases pass. The90-identity native menu sweep covers124
transitions and2,480 frames with identical heading pixels and no visible
PPUMASK writes. Harmless portrait-preview overlap hashes are diagnostic.

Original vegetable tiles are preserved. Doki art fits existing CHR804..807
without expanding the12KB S2 segment. Duplicate USA record/pointer tables
and branch encodings fund the code within the existing banks. The17-byte
draw packet reuses a mutually exclusive active-character buffer; no new
host-global or zero-page state is allocated.

Full levels, all upgrades, original Doki music, steady60Hz and other remaining
goal characters are unfinished. Doki currently uses the SMB2 audio path.
`source.zip` contains the current reviewed compilation unit, menu override
and recipes; it reuses prior frozen inputs, not an expanded source forest.
It does not replace the canonical37-identity prepared builder. Native proof
keeps four PNGs per run and small aggregate logs; no videos or frame dumps.
''',encoding='utf-8')
    readme=R/'README.md';text=readme.read_text(encoding='utf-8')
    text=text.replace('**81 playable identities**','**85 playable identities**').replace('**81-playable development nightly**','**85-playable development nightly**')
    text=text.replace('| SMB2 | Mario / Luigi / Toad / Peach | — |','| SMB2 / Doki Doki Panic | Mario / Luigi / Toad / Peach / Imajin / Lina / Papa / Mama | — |')
    text=text.replace('current 86-individual count','current 90-individual count')
    text=text.replace('all 86 identities through 120 D-pad/Select transitions','all 90 identities through 124 D-pad/Select transitions')
    text=text.replace('SMB2J and All Night Nippon campaigns and the original Doki Doki Panic characters are still being developed. Their private source checkpoints do not add playable identities or campaigns to this build.','**Doki Doki Panic:** Select on the SMB2 slot continues after Peach to **Imajin → Lina → Papa → Mama**. Their original graphics, palettes, movement and carry behavior are integrated. All eight SMB2/Doki identities pass cold selection/lives/jump/landing/camera checks. Doki stays large and does not get the USA B-button speed boost. Music currently uses the SMB2 path. See the [85-character verification](docs/qa/checkpoints/2026-11-01/ready85-doki-native-v1/README.md). SMB2J and All Night Nippon campaigns remain in development.')
    text=text.replace('| Expanded MMC5 nightly | 76 playable / 86 individual identities |','| Expanded MMC5 nightly | 85 playable / 90 individual identities |')
    start=text.index('The latest delivered nightly is ');end=text.index('\n\n',start)
    text=text[:start]+'The latest delivered nightly is `f6415a64` (November 1), with **85 playable identities**. It adds the four original Doki characters and preserves all six WWF wrestlers from the prior build. The exact ROM passes 720 source Start/A cases, original Doki movement/art comparisons, eight SMB2/Doki cold emulator routes, and a 90-identity menu sweep with unchanged heading pixels across 2,480 transition frames. Full stages, shortcuts, all powerups, original Doki audio and steady 60 Hz remain unfinished. See the [verification](docs/qa/checkpoints/2026-11-01/ready85-doki-native-v1/README.md) and [delivery receipt](docs/qa/nightly-2026-11-01-ready85.json).'+text[end:]
    readme.write_text(text,encoding='utf-8',newline='\n')
    assert sha(DEST)=='429b9f3c3fb551ec023d997f9e83515a2c68f1447a2d4a7cad43c029ff5ee3e2'
    before=sha(DEST);DEST.write_bytes((J/'candidate.nes').read_bytes());assert sha(DEST)==EXPECTED
    receipt=dict(installed=True,backup_created=False,destination=str(DEST),output_sha256=EXPECTED,replaced_sha256=before,playable_identities=85,new_identities=['Imajin','Lina','Papa','Mama'],checkpoint=K.relative_to(R).as_posix(),checkpoint_sha256=sha(K/'handoff.json'),verification=summary)
    save(O/'installed.json',receipt);save(R/'docs/qa/nightly-2026-11-01-ready85.json',receipt)
    hand=R/'docs/qa/continuation-current.json';q=json.loads(hand.read_text(encoding='utf-8'));q.update(goal_status='ACTIVE_INCOMPLETE',previous_goal_turn_classification='progress',installed_nightly=receipt,Doki_current=summary,current_priority='Continue the five remaining menu identities and original goal characters; full1-1, shortcuts, every-powerup and campaign work remain. Installed85 Doki nightly is exact-hash qualified for the documented finite checks.')
    q['completion']='Not complete.85 playable/90 menu identities; remaining characters, campaigns, full1-1/shortcuts/every-upgrade still required.';save(hand,q)
    build_size,build_files=inventory(R/'build',5_000_000_000,20_000);workspace_size,workspace_files=inventory(R,70_000_000_000,500_000)
    save(O/'storage.json',dict(build_bytes=build_size,build_files=build_files,workspace_bytes=workspace_size,workspace_files=workspace_files,deleted=False,cleanup_note='Automatic approval review rejected removal of the small failed Doki capture folder; it remains untouched. No video or frame sequence created.'))
    print(json.dumps(dict(installed=True,path=str(DEST),ROM_sha256=EXPECTED,playable=85,menu=90,backup=False,source_archive_bytes=src['bytes'],native_archive_bytes=native_zip['bytes'],build_bytes=build_size,build_files=build_files)))


if __name__=='__main__':main()
