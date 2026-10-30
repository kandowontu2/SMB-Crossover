"""Bind the native menu repair, retain its evidence, and install a separate build."""
from pathlib import Path
import csv,hashlib,json,shutil,subprocess,sys
from checkpoint_roster_packets_v1 import ROOT
OUT=ROOT/'build/menu-fourth-row-fix-v2'
REPORT=ROOT/'docs/qa/menu-fourth-row-fix-2026-10-29.json'


def bind(path):
    p=Path(path).resolve();b=p.read_bytes()
    return dict(path=str(p),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())


def main():
    assert not REPORT.exists(),'Preserve prior review'
    proof=json.loads((OUT/'build-proof.json').read_text())
    controls=json.loads((OUT/'queue-controls.json').read_text())
    assert controls['passed']and controls['cases']==6144 and len(proof['changes'])==4
    assert proof['candidate']=='c0269e1569c95bb78967f9025c7d2a2dbc5b0c147ed9ba75b1847c5c227a2f5f'
    native=ROOT/'build/menu-fourth-row-review-v1';observations={};local=[]
    for name in ['parent','fixed','parent-instrumented','fixed-instrumented']:
        d=native/name
        log=next(d.glob('*.log')).read_text()
        assert 'PASS cold four-row menu navigation' in log
        budget=json.loads((d/'capture-budget.json').read_text())
        assert budget['returncode']==0 and not budget['violations']
        assert any('--testRunner'==x for x in budget['command']),'Headless actual command'
        local += [p for p in d.iterdir()if p.is_file()]
        if name.endswith('instrumented'):
            observations[name]={int(r['slot']):{k:int(v)for k,v in r.items()if k!='slot'}
                for r in csv.DictReader((d/'queue-observations.csv').open())}
    old,new=observations['parent-instrumented'],observations['fixed-instrumented']
    assert old[22]['optimized']==0 and new[22]['optimized']==2
    assert sum(x['lateEnables']for x in old.values())==3
    assert sum(x['lateEnables']for x in new.values())==0
    assert not any(x['visibleWrites']for rows in observations.values()for x in rows.values())
    public=[ROOT/'tools/audit'/n for n in ['build_menu_fourth_row_fix_v1.py',
        'menu_fourth_row_capture_v1.lua','menu_fourth_row_instrumented_v1.lua',
        'menu_fourth_row_controls_v1.py','finalize_menu_fourth_row_v1.py']]
    report=dict(status='PASS four-row menu queue correction; no new roster identities admitted by this repair',
        parent=proof['parent'],candidate=proof['candidate'],actual_ROM_changes=proof['changes'],
        cause='MenuQueueValidate accepted cursor addresses20xx/21xx, but fourth-row cursors are22xx. Row4 and navigation away from it skipped the compactor, preserving excess hint/palette writes and missing the render deadline.',
        correction='Exact8-byte range branch now admits20xx/21xx/22xx only; four ROM bytes change inbank66. Header/CHR and every linked label remain byte-exact toparent.',
        compiled_controls=dict(cases=6144,only_changed_results=6,scope='Actual assembled validator; only fourth-row single-tile cursor commands become valid. Other6138 command shapes retain the original result.'),
        native=dict(headless=True,controller_only=True,no_emulated_writes=True,observations=observations,
            render_enables_during_visible_scanlines_before=3,render_enables_during_visible_scanlines_after=0,
            active_render_PPUDATA_writes_before=0,active_render_PPUDATA_writes_after=0,
            route='Cold Start; rows1/2/3/4; Select onrow4; Up/back and Down/return. Each run322frames, seven selected full screenshots, bounded logs.'),
        visual_review='Root viewed row1/row4 and row4Select before/after. Fixed row4 retains the complete legend and removes the trailing strayB. Other screenshot files are retained; no exhaustive every-frame visual review claim.',
        limits='Front-end repair only. New character units remain separate until their gameplay/source/native checks pass. No full campaign or performance claim beyond this menu route.',
        build=bind(OUT/'build-proof.json'),controls=bind(OUT/'queue-controls.json'),
        tools=[bind(p)for p in public],evidence=[bind(p)for p in local],workspace_cap_bytes=70_000_000_000)
    REPORT.write_text(json.dumps(report,indent=2)+'\n')
    checkpoint=dict(status=report['status'],candidate=bind(OUT/'candidate.nes'),report=bind(REPORT),
        bindings=proof['bindings'],actual_ASM_dependencies={},
        owned_files=[bind(p)for p in public+local+[OUT/'src/menu_vram_budget.s',OUT/'build-proof.json',
            OUT/'queue-controls.json',REPORT]])
    hp=OUT/'root-checkpoint.json';hp.write_text(json.dumps(checkpoint,indent=2)+'\n')
    subprocess.run([sys.executable,'-B',str(ROOT/'tools/audit/checkpoint_roster_component_v5.py'),
        '--handoff',str(hp),'--name','fourth-row-menu-native-vram-repair'],cwd=ROOT,check=True)
    downloads=Path('C:/Users/kando/Downloads');latest=downloads/'SMB-Crossover-Latest-WIP-MMC5.nes'
    assert bind(latest)['sha256']==proof['parent'],'Preserve an unexpected newer shared build'
    backup=downloads/'SMB-Crossover-Backup-ac126b54-MMC5.nes'
    if backup.exists():assert bind(backup)['sha256']==proof['parent']
    else:shutil.copy2(latest,backup)
    versioned=downloads/'SMB-Crossover-2026-10-29-Menu-Fix-MMC5.nes'
    if versioned.exists():assert bind(versioned)['sha256']==proof['candidate']
    else:shutil.copy2(OUT/'candidate.nes',versioned)
    shutil.copy2(OUT/'candidate.nes',latest)
    assert bind(latest)['sha256']==bind(versioned)['sha256']==proof['candidate']
    install=dict(passed=True,installed=bind(latest),versioned=bind(versioned),backup=bind(backup),
        verification=bind(REPORT),checks=[dict(name='Compiled queue6144 cases',passed=True),
            dict(name='Actual headless fourth-row navigation and PPU deadline',passed=True),
            dict(name='Installed bytes match source-built candidate',passed=True)])
    (OUT/'install.json').write_text(json.dumps(install,indent=2)+'\n')
    progress=ROOT/'docs/qa/new-character-source-progress-2026-10-28.json';state=json.loads(progress.read_text())
    state['shared_playable_build'].update(sha256=proof['candidate'],
        latest_user_change='Four-byte row4menu queue-validation fix; native late render enables3->0 and full controls restored. Existing gameplay/CHR unchanged.')
    state['fourth_row_menu_fix']=dict(status=report['status'],report=bind(REPORT),
        checkpoint='checkpoints/2026-10-28/fourth-row-menu-native-vram-repair')
    state['additional_confirmed_requests_2026_10_29']=dict(status='Queued; not implemented or admitted',
        new_slots=['WWF WrestleMania allsixwrestlers, Selectcycles; eachthemethroughoutallareas',
            'ExciteBike withPrinceofPersia alternate','ContraForce allfourcharacters'],
        existing_slot_alternates={'Rygar':'Karnov','Sophia':'MetalStorm protagonist','Ryu':'Shinobi'},
        note='These are confirmed additions, replacing the previous maybe list. Source/CHR/PRG/menu capacity must be allocated before host implementation.')
    progress.write_text(json.dumps(state,indent=2)+'\n')
    print(json.dumps(dict(report=bind(REPORT),installed=bind(latest),backup=bind(backup))))


if __name__=='__main__':main()
