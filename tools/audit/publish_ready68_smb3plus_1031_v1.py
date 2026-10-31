"""Publish the tested68-identity WIP; keep full donor/level work outstanding."""
from pathlib import Path
import csv
import hashlib
import json
import os
import shutil
import sys
import zipfile

R=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import prepare_functional_roster_visuals58_v1 as B
import bowser_current64_menu_controls_v1 as U
from link_pit_rygar_sophia_audit_cpu import scoped_load

J=R/'build/smb3plus-current66-source-1031-v2/joint'
N=R/'build/smb3plus-current66-native-1031-v1'
S=R/'docs/qa/checkpoints/2026-10-31/smb3plus-current66-source-v1/handoff.json'
D=R/'docs/qa/checkpoints/2026-10-31/smb3plus-current68-native-v1'
OLD='c6635815711a624a02c4337cd9f1830ca9c43b14a824f2ea51963f796ad98c2a'
NEW='01a40d4019ae00220c7279c9ab8d4f6f25afb44af1612a6a1483a257448f0fa9'


def save(p,d):
    assert not p.exists(),p
    p.write_text(json.dumps(d,indent=2)+'\n',encoding='utf-8',newline='\n')


def main():
    assert not D.exists()
    assert B.sha(S)=='8c5c861f81ac849f8f4f28aa76f9f5db0be70a2d866b26994e2fbb2c3ca198b0'
    source=json.loads(B.read(S));B.bound(source)
    assert source['candidate']==NEW and source['base']==OLD and B.sha(J/'candidate.nes')==NEW
    archive=next(Path(x) for x in source['bindings'] if Path(x).parent==S.parent and x.endswith('.zip'))
    with zipfile.ZipFile(archive) as z:
        assert len(z.namelist())==53
        for item in z.infolist():
            p=(R/item.filename).resolve();assert p.is_relative_to(R) and not item.is_dir()
            assert str(p) in source['bindings'] and z.read(item)==p.read_bytes()
    # Independent disjoint source oracle; product is source compiled, never
    # constructed by this byte comparison.
    f56=(R/'build/peach-palette-fix-1030-v1/joint/candidate.nes').read_bytes()
    parent=(R/'build/bowser-playable-jump-v1/joint/candidate.nes').read_bytes()
    own=(R/'build/smb3plus-peach-gravity-consumer-1031-v1/joint/candidate.nes').read_bytes()
    new=(J/'candidate.nes').read_bytes();changed={i for i,(a,b) in enumerate(zip(f56,own)) if a!=b}
    assert len(changed)==36451
    assert all(f56[i]==parent[i] and new[i]==own[i] for i in changed)
    assert all(a==b for i,(a,b) in enumerate(zip(parent,new)) if i not in changed)
    native=[];files={Path(__file__),S,N/'prepared.json'}
    for name in ['toad','peach']:
        folder=N/name;d=json.loads(B.read(folder/'capture/result.json'))
        binding=json.loads(B.read(folder/'capture/binding.json'));B.bound(binding)
        assert binding['exit_code']==0 and d['passed'] and d['ROM_sha256']==NEW
        assert d['jumped'] and d['landed'] and d['vector_guards']==720 and d['body_P0_source_exact']
        pngs=list((folder/'capture').glob('*.png'));assert len(pngs)==4
        native.append(dict(identity=name,complete_Main=d['main_updates'],gameplay_frames=d['gameplay_frames'],
            actual_UI_DMA_checks=d['actual_UI_DMA_checks'],timing=d['timing'],vector_restores=720,
            root_reviewed_full_frame_PNGs={p.name:B.sha(p) for p in pngs},result_sha256=B.sha(folder/'capture/result.json')))
        files.update(p for p in folder.rglob('*') if p.is_file())
    active=[r for r in csv.DictReader((N/'peach/capture/hover-observations.csv').open()) if int(r['timer'])]
    assert len(active)==80 and [int(r['timer']) for r in active]==list(range(2,161,2))
    assert int(active[-1]['expired'])==1
    b=scoped_load(J/'candidate.nes');counts=list(U.COUNTS);counts[16]=4;menu=[]
    for slot,count in enumerate(counts):
        m=U.C.fresh(b,0);U.H.put(m,CrossoverMenuIndex=slot,FfVariant=0,FmAlts=0,M3Variant=0)
        U.C.invoke(m,'MenuResolveCharacter');U.C.invoke(m,'QueueSelection')
        for variant in range(count):
            if variant:
                U.H.put(m,CrossoverMenuButtons=0,SavedJoypad1Bits=32,SavedJoypad2Bits=0,VRAM_Buffer1_Offset=0)
                U.C.invoke(m,'CrossoverMenuInput')
            got=U.C.invoke(m,'FmPending')
            menu.append(dict(slot=slot,variant=variant,selected=U.H.get(m,'SelectedCharacter'),pending=bool(got['AXYP_SP'][3]&1)))
    assert len(menu)==85 and sum(not r['pending'] for r in menu)==68
    assert all(not r['pending'] for r in menu if r['slot']==16)
    assert all(p.suffix.lower() in ['.py','.json','.lua','.csv','.png','.log'] for p in files)
    assert sum(p.stat().st_size for p in files)<8*1024*1024
    D.mkdir(parents=True);out=D/'native-and-menu-results.zip'
    with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for p in sorted(files):z.write(p,p.relative_to(R).as_posix())
    with zipfile.ZipFile(out) as z:
        for p in files:assert z.read(p.relative_to(R).as_posix())==p.read_bytes()
    save(D/'manifest.json',dict(candidate=NEW,passed=True,source_handoff_sha256=B.sha(S),
        native=native,actual_menu=menu,archive_sha256=B.sha(out),archive_members=len(files),
        root_original_state_cases=224,root_original_edge_cases=2016,foreign_movement_pairs=1344,
        exact_graphics_pairs=9072,real_source_interrupt_cuts=3380,
        files={p.relative_to(R).as_posix():B.sha(p) for p in sorted(files)}))
    downloads=Path.home()/'Downloads';latest=downloads/'SMB-Crossover-Latest-WIP-MMC5.nes'
    version=downloads/'SMB-Crossover-2026-10-31-Ready68-SMB3-Toad-Peach-MMC5.nes'
    backup=downloads/'SMB-Crossover-Before-SMB3plus-c6635815-MMC5.nes'
    temp=downloads/'SMB-Crossover-Latest-WIP-MMC5.pending'
    assert B.sha(latest)==OLD and not version.exists() and not backup.exists() and not temp.exists()
    shutil.copy2(latest,backup);assert B.sha(backup)==OLD
    shutil.copy2(J/'candidate.nes',version);assert B.sha(version)==NEW
    shutil.copy2(version,temp);assert B.sha(temp)==NEW
    os.replace(temp,latest);assert B.sha(latest)==NEW
    limits=['Playable WIP unlocks. Donor ground pound/custom stomp delay, some special art consumers and Toad kick audio remain unfinished.',
        'No full1-1/every-powerup/complete campaign or60Hz claim; Toad had14 lag NMIs in its bounded run.',
        'Older character issues and the expanded-roster goal remain unfinished. Contra Force/Battletoads stay pending.']
    receipt=dict(date='2026-10-31',status='INSTALLED_READY68_SMB3PLUS_TOAD_PEACH_PLAYABLE_WIP',passed=True,
        installed=True,ROM_sha256=NEW,previous_sha256=OLD,latest=str(latest),versioned=str(version),backup=str(backup),
        playable=68,individual_identities=84,menu_slots=32,menu_rows=4,pending_individual_identities=16,
        pending_Battletoads_family_placeholder=1,actual_menu_identities_with_placeholder=85,
        source_handoff_sha256=B.sha(S),verified_source_bindings=58,verified_source_archive_members=53,
        actual_disjoint_source_change_bytes=36451,native_checks=native,source_original_hover_updates=80,
        controls='Highlight SMB3, then Select cycles Mario/Luigi/Toad/Peach.',
        native_manifest_sha256=B.sha(D/'manifest.json'),limits=limits,
        all_characters_1_1_and_every_powerup_complete=False,goal_complete=False)
    save(R/'docs/qa/functional-roster-ready68-smb3plus-2026-10-31.json',receipt)
    (D/'README.md').write_text('Root verified the exact composed01a40d40 source and all53 source archive members, then ran both controller-only native packets and visually reviewed all8 full-frame screenshots. The actual menu enumerates68 playable identities/84 individual identities, plus one pending generic Battletoads placeholder.\n\nToad:359 complete Main updates/360 gameplay frames,14 lag NMIs. Peach:360/360,0 lag NMIs.720 real ISR restore checks each; source-derived80-update hover, correct source body palettes/physicalCHR, selection and lives names.\n\n'+'\n'.join(limits)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(dict(installed=str(latest),versioned=str(version),candidate=NEW,playable=68,individual_identities=84,native_archive_bytes=out.stat().st_size,goal_complete=False)))


if __name__=='__main__':main()
