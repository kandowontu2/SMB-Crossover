"""Checkpoint the source/native-tested four-way SMB3 menu without admission."""
from pathlib import Path
import csv
import json
import shutil
import subprocess
import sys
import zipfile

R=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(R/'tools/audit'))
import prepare_functional_roster_visuals58_v1 as B

O=R/'build/smb3plus-peach-gravity-consumer-1031-v1';J=O/'joint'
D=R/'docs/qa/checkpoints/2026-10-31/smb3plus-menu-controller-native-v1'
N=R/'build/smb3plus-gravity-native-1031-v1'
CANDIDATE='05b1c5a861eaf49fbaea1f8278229f2970defa3e81909178e0eb46e1ad2f2d10'


def main():
    assert not D.exists() and not (O/'handoff.json').exists()
    names=['source-stage.json','regressions-v1.json','menu-controls-v1.json','vectors-v1.json']
    reports={n:json.loads(B.read(O/n)) for n in names}
    for n,d in reports.items():
        B.bound(d);assert d['candidate']==CANDIDATE
        if n!='source-stage.json':assert d['passed']
    source=R/'build/smb3plus-gravity-source-controls-1031-v1/probe.json'
    s=json.loads(B.read(source));B.bound(s)
    assert s['passed'] and s['candidate']==CANDIDATE and len(s['cases'])==224
    assert s['additional_complete_controller_edges']==2016
    assert reports['regressions-v1.json']['foreign_movement_pairs']==1344
    assert reports['regressions-v1.json']['exact_graphics_pairs']==9072
    assert reports['menu-controls-v1.json']['foreign_menu_identities']==81
    assert reports['menu-controls-v1.json']['status_ABI_cases']==768
    assert reports['vectors-v1.json']['real_vectors']==3380
    native=[]
    for name in ['toad','peach']:
        folder=N/name;d=json.loads(B.read(folder/'capture/result.json'))
        binding=json.loads(B.read(folder/'capture/binding.json'));B.bound(binding)
        assert d['passed'] and binding['exit_code']==0 and d['ROM_sha256']==CANDIDATE
        assert d['jumped'] and d['landed'] and d['vector_guards']==720
        assert d['body_P0_source_exact'] and len(list((folder/'capture').glob('*.png')))==4
        native.append(dict(identity=name,Main_updates=d['main_updates'],gameplay_frames=d['gameplay_frames'],
            timing=d['timing'],actual_UI_DMA_checks=d['actual_UI_DMA_checks'],root_reviewed_PNGs=4,
            screenshots={p.name:B.sha(p) for p in (folder/'capture').glob('*.png')},
            result_sha256=B.sha(folder/'capture/result.json')))
    rows=list(csv.DictReader((N/'peach/capture/hover-observations.csv').open()))
    active=[r for r in rows if int(r['timer'])]
    assert len(active)==80 and [int(r['timer']) for r in active]==list(range(2,161,2))
    assert int(active[-1]['expired'])==1 and int(active[-1]['ready'])==1
    files={Path(__file__),source}
    files.update(O/n for n in names)
    # Exact tools introduced since the prior public float checkpoint.
    untracked=subprocess.run(['git','ls-files','--others','--exclude-standard','--',
        'tools/audit/*smb3plus*','tools/reference/*smb3plus*'],cwd=R,capture_output=True,text=True,check=True).stdout.splitlines()
    files.update(R/p for p in untracked)
    # Bound old negatives and successful source stages, without copying their
    # private full trees or any cartridge/object/debug binaries.
    prefixes=['smb3plus-menu-host-1031-v','smb3plus-peach-air-frame-1031-v',
        'smb3plus-peach-complete-controller-1031-v','smb3plus-peach-gravity-consumer-1031-v',
        'smb3plus-whole-controller-','smb3plus-growth-source-probe-1031-v']
    for folder in (R/'build').iterdir():
        if folder.is_dir() and any(folder.name.startswith(p) for p in prefixes):files.update(folder.glob('*.json'))
    for folder in [N,R/'build/smb3plus-menu-native-1031-v1',R/'build/smb3plus-peach-native-braked-1031-v1',R/'build/smb3plus-peach-native-braked-1031-v2']:
        files.update(p for p in folder.rglob('*') if p.is_file())
    files.update(p for p in (J/'src').glob('smb3*') if p.is_file())
    files.update(J/n for n in ['entrypoint.s','private.cfg','smb3plus_body_host.s','smb3plus_kick_host.s',
        'smb3plus_float_state.inc','smb3plus_float_source.s','smb3plus_float_data.s','smb3plus_menu_name.s'])
    files.update(J/'src'/n for n in ['character_select.s','new_roster_dispatch.s'])
    assert all(p.is_file() and p.is_relative_to(R) for p in files)
    allowed={'.py','.s','.inc','.cfg','.json','.csv','.png','.log','.lua','.txt'}
    assert all(p.suffix.lower() in allowed for p in files)
    assert sum(p.stat().st_size for p in files)<20*1024*1024
    bindings={str(p):B.sha(p) for p in sorted(files)}
    bindings.update({str(J/n):B.sha(J/n) for n in ['candidate.nes','candidate.dbg','candidate.lbl']})
    D.mkdir(parents=True);archive=D/'source-and-bounded-native.zip'
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for p in sorted(files):z.write(p,p.relative_to(R).as_posix())
    with zipfile.ZipFile(archive) as z:
        assert len(z.namelist())==len(files)
        for p in files:assert z.read(p.relative_to(R).as_posix())==p.read_bytes()
    limits=['Private candidate descends from corrected64 ancestor. Composition onto current66 and regression/native review are still required before installing.',
        'Donor ground pound/custom stomp-delay, special art consumers and Toad kick audio remain incomplete.',
        'Toad has14 lag NMIs in this bounded run; no full-level, every-powerup or60Hz claim.',
        'The active expanded-roster goal remains incomplete. Installed Downloads ROM stays current66 c6635815.']
    d=dict(status='FROZEN_SOURCE_AND_BOUNDED_NATIVE_MENU_CONTROLLER_NOT_ADMITTED',source=True,native=True,
        installed=False,playable_admission=False,candidate=CANDIDATE,joint=str(J),
        original_complete_controller_cases=224,original_complete_controller_edge_cases=2016,
        foreign_movement_pairs=1344,exact_graphics_pairs=9072,foreign_menu_identities=81,
        status_ABI_cases=768,real_interrupt_cuts=3380,native_checks=native,
        actual_Peach_hover_updates=80,actual_Peach_hover_timer_ticks=160,no_second_ground_hover=True,
        retained_failures='Wrong hover pose; fresh-A hook too late; missing high-form anchor guard; outer callback incorrectly ran on the ground; incorrect fixture overwrote donor7E98 float thresholds. All preserved. Final assertions use actual original instructions, player fields and source pixels.',
        limits=limits,archive_members=len(files),archive_bytes=archive.stat().st_size,archive_sha256=B.sha(archive),bindings=bindings)
    B.write(O/'handoff.json',json.dumps(d,indent=2)+'\n')
    for n in ['handoff.json',*names]:shutil.copy2(O/n,D/n)
    B.write(D/'README.md','Four-way SMB3 Mario/Luigi/Toad/Peach Select and names work through the real menu and lives screen. Toad/Peach controller changes are compared with Infidelity SMB3+ original instructions. The final source cart matches224 ordinary plus2016 boundary updates,1344 old movement pairs and9072 exact graphics pairs.3380 real interrupt cuts preserve live registers/stack/all33SMC/raw maps.\n\nRoot ran and viewed all8 native screenshots. Toad:359 complete Main updates/360 gameplay frames,14 lag NMIs. Peach:360/360,0 lag NMIs, exactly80 hover updates/160 timer ticks and no second ground-hover episode. These are bounded tests, not level clears.\n\n'+ '\n'.join(limits)+'\n')
    B.write(D/'owned-files.json',json.dumps(dict(files=[p.relative_to(R).as_posix() for p in sorted(D.iterdir()) if p.is_file()]+[(D/'owned-files.json').relative_to(R).as_posix()],
        source_tools=untracked),indent=2)+'\n')
    print(json.dumps(dict(checkpoint=str(D),candidate=CANDIDATE,members=len(files),bytes=archive.stat().st_size,handoff_sha256=B.sha(O/'handoff.json'))))


if __name__=='__main__':main()
