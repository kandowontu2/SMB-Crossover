"""Verify frozen inputs/relink/native evidence, archive sources and install MMC5."""
from pathlib import Path
import hashlib,json,re,shutil,subprocess,sys,zipfile
from collections import Counter

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'build/full-roster-menu-v3'
REPORT=ROOT/'docs/qa/full-roster-menu-2026-10-30.json'
EXPECTED='979cff78f5f7fbcd78187f1f72f198ba311f1d436d1e6d09ee3d85983cd07544'


def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def bind(p):p=Path(p).resolve();return dict(path=str(p),bytes=p.stat().st_size,sha256=sha(p))
def write(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,indent=2)+'\n')


def main():
    assert not REPORT.exists(),'Preserve finalized evidence'
    p=json.loads((OUT/'build-proof.json').read_text());assert p['candidate']==sha(OUT/'candidate.nes')==EXPECTED
    for f,h in p['bindings'].items():assert sha(f)==h,f
    deps={}
    for f in OUT.glob('*.d'):
        rhs=f.read_text().split(':\t',1)[1].splitlines()[0].strip().removesuffix(':')
        for word in re.split(r'(?<!\\)\s+',rhs):
            path=Path(word.replace('\\ ',' '));path=(path if path.is_absolute()else ROOT/path).resolve()
            assert path.is_file(),path;deps[str(path)]=sha(path)
    assert len(deps)>470 and str(OUT/'src/full_roster_menu.s')in deps
    independent=ROOT/'build/full-roster-menu-independent-v3'
    previous=json.loads((OUT/'source-closure.json').read_text())if(OUT/'source-closure.json').exists()else None
    if previous:assert previous['actual_ASM_dependencies']==deps
    else:independent.mkdir()
    commands=previous['commands']if previous else []
    for original in ([]if previous else p['commands']):
        command=list(original)
        if Path(command[0]).name.lower()=='ca65.exe':
            for key in ['-o','--create-full-dep']:
                ix=command.index(key)+1;command[ix]=str(independent/Path(command[ix]).name)
        else:
            for i,a in enumerate(command):
                if a.startswith('--dbgfile,'):command[i]='--dbgfile,'+str(independent/'candidate.dbg')
                elif a in [str(OUT/n)for n in ['main.o','skin.o','gb.o','candidate.nes','candidate.lbl']]:command[i]=str(independent/Path(a).name)
        z=subprocess.run(command,cwd=ROOT,capture_output=True,text=True)
        assert z.returncode==0,z.stdout+z.stderr;commands.append(command)
    sys.path.insert(0,str(ROOT/'tools'));from prepare_cv3_dmc_mirror import prepare
    prepare(ROOT,independent/'candidate.nes')
    assert sha(independent/'candidate.nes')==EXPECTED
    assert(independent/'candidate.lbl').read_bytes()==(OUT/'candidate.lbl').read_bytes()
    closure=dict(passed=True,independent_relink_byte_exact_ROM_and_LBL=True,commands=commands,actual_ASM_dependencies=deps,
                 candidate=bind(OUT/'candidate.nes'),independent=bind(independent/'candidate.nes'))
    write(OUT/'source-closure.json',closure)
    cpu=ROOT/'build/full-menu-source-controls-v1/receipt.json';c=json.loads(cpu.read_text());assert c['ROM_sha256']==EXPECTED
    for f,h in c['bindings'].items():assert sha(f)==h,f
    evidence=[];native={}
    for tag,folder in [('sweep','full-roster-menu-native-v3'),('reentry','full-roster-menu-reentry-v4')]:
        d=ROOT/'build'/folder;result=json.loads((d/'result.json').read_text());assert result['passed']
        budget=json.loads((d/'capture-budget.json').read_text());assert budget['returncode']==0 and not budget['violations']
        assert '--testRunner'in budget['command']
        assert len(list(d.glob('*.png')))<=8 and sum(f.stat().st_size for f in d.iterdir()if f.is_file())<2_000_000_000
        assert not list(d.glob('*failure*'))
        native[tag]=result;evidence += [f for f in d.iterdir()if f.is_file()]
    assert native['sweep']['slots']==31 and native['sweep']['alternates']==77
    assert native['sweep']['late_enables']==native['sweep']['visible_ppu_writes']==0
    parent=ROOT/'build/menu-fourth-row-fix-v2/candidate.nes';a=parent.read_bytes();b=(OUT/'candidate.nes').read_bytes()
    assert len(a)==len(b)==2097168 and a[:16]==b[:16]
    banks=dict(Counter((i-16)//8192 for i,(x,y)in enumerate(zip(a[:1048592],b[:1048592]))if x!=y))
    assert set(banks)=={66,76,124}
    assert a[16+76*8192:16+76*8192+0x1979]==b[16+76*8192:16+76*8192+0x1979]
    menu_ranges=[(0,224)]
    debug=(OUT/'candidate.dbg').read_text()
    for name in ['NrMenuCharacter','NrMenuNavigate','NrQueueCursor']:
        row=next(line for line in debug.splitlines()if line.startswith('sym\t')and 'name="'+name+'"'in line and 'size='in line)
        start=int(re.search(r',val=(0x[0-9A-F]+)',row)[1],16)-0xa000
        size=int(re.search(r',size=(\d+)',row)[1]);menu_ranges.append((start,start+size))
    for i,(x,y)in enumerate(zip(a[16+124*8192:16+125*8192],b[16+124*8192:16+125*8192])):
        if x!=y:assert any(lo<=i<hi for lo,hi in menu_ranges),hex(i+0xa000)
    assert not any(x['placeholder']for x in p['pending_profiles'])
    report=dict(status='PASS full roster menu; pending entries visible but gameplay blocked',candidate=EXPECTED,parent=p['parent'],
        menu=dict(slots=31,columns=8,rows=4,identities=77,playable=47,pending=30,portrait_tiles=169,
                  pending_marker='Star prefix and COMING SOON legend; A/Start remain in menu.',
                  art='Original-game source pixels or hardware captures; Contra Force uses authentic selection faces pending full-body integration.',
                  select_alternates=True,individual_thumbnail_names=False),
        repair='Accepted22xx cursor commands retained. Added ready-owner CHR mode/page restoration after pending preview, including Proto Man.',
        native=native,CPU_receipt=bind(cpu),source_closure=bind(OUT/'source-closure.json'),
        changed_PRG_banks=banks,changed_CHR_pages=p['CHR_changed'],original_gameplay_and_NMI_IRQ_instruction_bytes_unchanged=True,
        memory=dict(new_RAM_bytes=0,menu_only_ExRAM=['5FE5','5FE8'],menu_only_PRG='bank76 A-view B979..<C000',preview_CHR=[700,703]),
        visual_review='Root reviewed all eight selected sweep screenshots as a contact sheet, plus restored Proto gameplay. Finite menu and launch checks; no full new-character gameplay qualification claim.',
        limits='Thirty starred identities still require gameplay integration; this menu publication does not admit their private component builds. Native Mario/Proto launches checked, not a full campaign replay.',
        source_build=bind(OUT/'build-proof.json'),evidence=[bind(f)for f in evidence],
        workspace_cap_bytes=70_000_000_000)
    write(REPORT,report)
    files={Path(f)for f in deps}|{Path(f)for f in p['bindings']}|{Path(f)for f in c['bindings']}
    files|={REPORT,OUT/'build-proof.json',OUT/'source-closure.json',OUT/'full-menu.cfg',OUT/'entrypoint.s',OUT/'menu.nam',OUT/'menu.rle',OUT/'packed.chr',OUT/'pending-previews.chr',OUT/'native-review-contact.png',cpu,Path(__file__),ROOT/'README.md',ROOT/'tools/prepare_cv3_dmc_mirror.py'}
    files|=set(evidence)
    files|=set((ROOT/'build/full-menu-source-controls-v1').rglob('*.py'))|set((ROOT/'build/full-menu-source-controls-v1').rglob('*.json'))
    files|={ROOT/'tools/audit'/n for n in ['build_full_roster_menu_v1.py','full_roster_menu_native_v1.lua','full_roster_menu_reentry_v1.lua']}
    files|={f for d in ['build/full-roster-menu-reentry-v3','build/full-menu-known-art-v1','build/full-menu-source-art-v1','build/wwf-menu-art-v1']for f in (ROOT/d).rglob('*')if f.is_file()and f.suffix in ['.png','.json','.py','.lua','.bin']}
    target=ROOT/'docs/qa/checkpoints/2026-10-30/full-roster-menu';assert not target.exists();target.mkdir(parents=True)
    archive=target/'frozen-source-packet.zip';members={}
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=9)as z:
        for f in sorted(files):
            if not f.is_relative_to(ROOT)or f.suffix.lower()in ['.nes','.dbg','.map','.o','.exe']:continue
            data=f.read_bytes();name=f.relative_to(ROOT).as_posix();info=zipfile.ZipInfo(name,(2026,10,30,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED
            z.writestr(info,data);members[name]=hashlib.sha256(data).hexdigest()
    with zipfile.ZipFile(archive)as z:assert {n:hashlib.sha256(z.read(n)).hexdigest()for n in z.namelist()}==members
    write(target/'root-review.json',dict(status=report['status'],candidate=EXPECTED,report=bind(REPORT),archive=bind(archive),members=members,actual_ASM_dependencies=deps,limits=report['limits']))
    downloads=Path('C:/Users/kando/Downloads');latest=downloads/'SMB-Crossover-Latest-WIP-MMC5.nes'
    assert sha(latest)==p['parent'],'Unexpected newer installed build'
    backup=downloads/'SMB-Crossover-Backup-c0269e15-MMC5.nes'
    if backup.exists():assert sha(backup)==p['parent']
    else:shutil.copy2(latest,backup)
    versioned=downloads/'SMB-Crossover-2026-10-30-Full-Roster-Menu-MMC5.nes'
    if versioned.exists():assert sha(versioned)==EXPECTED
    else:shutil.copy2(OUT/'candidate.nes',versioned)
    shutil.copy2(OUT/'candidate.nes',latest);assert sha(latest)==sha(versioned)==EXPECTED
    write(OUT/'install.json',dict(passed=True,installed=bind(latest),versioned=bind(versioned),backup=bind(backup),verification=bind(REPORT)))
    progress=ROOT/'docs/qa/new-character-source-progress-2026-10-28.json';state=json.loads(progress.read_text())
    state['shared_playable_build'].update(sha256=EXPECTED,latest_user_change='Full4x8 character menu:31slots/77variants visible;47playable,30starredpending; no newly admitted gameplay owners.')
    state['full_roster_menu']=dict(status=report['status'],report=bind(REPORT),checkpoint=str(target.relative_to(ROOT)))
    state['additional_confirmed_requests_2026_10_29']['status']='Visible in menu with original art and Select alternates; starred pending gameplay integration'
    write(progress,state)
    print(json.dumps(dict(installed=bind(latest),source_dependencies=len(deps),checkpoint_files=len(members),archive_bytes=archive.stat().st_size,verification=bind(REPORT))))


if __name__=='__main__':main()
