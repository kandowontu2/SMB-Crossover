"""Freeze the camera repair and list all proposed1-1 pipe assists before editing."""
from pathlib import Path
import hashlib,json,zipfile,sys
R=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
import check_hogan_current_bounded_v1 as C
P=R/'build/thomas-natural-host-1031-v6';J=R/'build/thomas-adapter'
O=R/'build/thomas-camera-review';D=R/'docs/qa/checkpoints/2026-10-31/thomas-camera-source-v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
save=lambda p,q:Path(p).write_text(json.dumps(q,indent=2)+'\n',encoding='utf-8')


def main():
    assert not O.exists()and not D.exists()
    stage=J/'source-stage.json';test=J/'checks/controls-crouch.json';pipe=J/'pipe-analysis/analysis.json'
    s,c,a=[json.loads(p.read_text())for p in [stage,test,pipe]]
    for q in [s,c,a]:
        for p,h in q['bindings'].items():assert sha(p)==h,p
    assert s['passed']and c['passed']and c['original_actor_frame_pairs']==399 and c['native_defeats']==1
    assert a['completed']and len(a['cases'])==9 and all(not z['cleared_first_pipe']for z in a['cases'])
    old,new=(P/'candidate.nes').read_bytes(),(J/'candidate.nes').read_bytes()
    changes=[i for i,(x,y)in enumerate(zip(old,new))if x!=y and i<1048592]
    assert len(changes)==12 and all(16+85*8192+0x133a<=i<16+85*8192+0x1900 for i in changes)
    assert old[1048592+434*1024:1048592+442*1024]==new[1048592+434*1024:1048592+442*1024]
    # Correct the earlier audit's warp-only cap classifier. Re-decode actual
    # columns; decorative and usable pipe caps both need accommodations.
    b=C.scoped_load(J/'candidate.nes');m=C.fresh(b)
    C.put(m,AreaPointer=37,WorldNumber=0,Hidden1UpFlag=1);C.invoke(m,'GetAreaDataAddrs')
    for i in range(3):m[C.address(b,'AreaObjectLength')+i]=255
    at=C.location(b,'VerticalPipeData');tiles=list(b['raw'][at:at+8]);cols=[]
    for x in range(72):
        C.invoke(m,'AreaParserCore');at=C.address(b,'MetatileBuffer');cols.append(list(m[at:at+13]));C.invoke(m,'IncrementColumnPos')
    pipes=[]
    for x,col in enumerate(cols[:-1]):
        for y,tile in enumerate(col):
            if any(tile==tiles[left]and cols[x+1][y]==tiles[right]for left,right in [(1,0),(5,4)]):
                pipes.append(dict(X=x*16,top=(y+2)*16,width=32,height=208-(y+2)*16))
    assert pipes==[dict(X=x,top=t,width=32,height=208-t)for x,t in [(448,176),(608,160),(736,144),(912,144)]]
    O.mkdir();D.mkdir(parents=True)
    plan=dict(source_CPU=True,changes_applied=False,scope='Complete list of proposed new pipe assists for Thomas1-1 only. Other stages/gaps still require route investigation.',
              reason='Actual donor jump27px; decoded pipe heights32/48/64/64. Nine natural-state controller policies reachX433/434 but do not clear the first pipe.',
              existing_level_cells_unchanged=True,reuse='Native SMB enemy25: genuine InitEnemyObject, vertical platform AI, collisions, player carry and renderer. No painted-only platforms or raised donor jump.',
              additions=[dict(pipe=p,platform_X=p['X']-48,initial_Y=192,type=37,character='Thomas only',stage='1-1',width='native platform default')for p in pipes],
              unresolved=['Prove constructor timing and empty-slot ownership','Prove support/carry and all four pipe crossings','End gaps, shortcut room and full1-1 remain unqualified'],
              candidate=sha(J/'candidate.nes'),bindings={str(p):sha(p)for p in [Path(__file__),Path(C.__file__),J/'candidate.nes',J/'candidate.dbg',pipe]})
    save(D/'pipe-assists-before-changes.json',plan)
    files={Path(__file__),R/'tools/audit/fix_thomas_camera_bounded_v1.py',R/'tools/audit/check_thomas_camera_bounded_v1.py',R/'tools/audit/inspect_thomas_pipes_bounded_v1.py',stage,test,pipe,J/'checks/negative/standing-kick-attempt.zip'}
    files|={p for p in J.iterdir()if p.is_file()and p.suffix in ['.s','.cfg','.dep','.json']}
    assert len(files)<35 and sum(p.stat().st_size for p in files)<1_000_000
    archive=D/'source-only.zip'
    with zipfile.ZipFile(archive,'x',zipfile.ZIP_DEFLATED,compresslevel=9)as z:
        for p in sorted(files):z.write(p,p.relative_to(R).as_posix())
    with zipfile.ZipFile(archive)as z:
        for p in files:assert hashlib.sha256(z.read(p.relative_to(R).as_posix())).hexdigest()==sha(p)
    q=dict(source=True,native=False,installed=False,candidate=sha(J/'candidate.nes'),parent=sha(P/'candidate.nes'),
           original_actor_object_unchanged=True,PRG_changed_bytes=12,PRG_changes='Own16byte constructor-cookie digest only; all native PRG instruction bytes remain exact.',
           source_checks={k:v for k,v in c.items()if k not in ['rows','bindings','traceback']},
           source_adaptation=s['adaptation'],pipe_plan_sha256=sha(D/'pipe-assists-before-changes.json'),
           source_archive_sha256=sha(archive),archive_bytes=archive.stat().st_size,
           original_source_checkpoint='docs/qa/checkpoints/2026-10-31/thomas-natural-host-source-v3/handoff.json',
           original_source_checkpoint_sha256=sha(R/'docs/qa/checkpoints/2026-10-31/thomas-natural-host-source-v3/handoff.json'),
           members={p.relative_to(R).as_posix():sha(p)for p in sorted(files)},
           limits=['Not composed into installed74-character f476 cartridge','Mesen reserved for ADOFAI at user request; no native emulator qualification','Original27px jump is retained and first pipe remains blocked in nine finite policies','No full1-1, all-powerup, audio or entire-roster completion claim'])
    save(D/'handoff.json',q)
    (D/'README.md').write_text('''# Thomas camera correction — source only

The adapter now supplies the pre-movement camera position and actual pixel
displacement consumed by SMB. Its old source corridor distance is rebased to
the genuine interior cold anchor, because SMB owns terrain and stage bounds.
Original actor, jump and attack instruction bodies remain unchanged.

Actual parser167Main plus399Main/normal NMI updates pass. Every one of399
accepted actor frames matches the original NES instructions with the declared
host projection. Reversal, original27px jump and one crouching-punch native
Goomba defeat pass; world369/camera265 is reached. The native PRG instruction
bytes are unchanged: only12bytes of the own constructor cookie differ.

Nine controller policies expose the next gap: Thomas cannot cross the first
32px pipe with his27px source jump. The earlier map classifier saw only the
usable pipe. A fresh native-parser decode includes decorative caps and proves
all four pipes at448/608/736/912, heights32/48/64/64. The complete proposed1-1
pipe-assist list is recorded before edits, reusing native vertical platform25.
No platform or terrain change has been applied in this checkpoint.

The failed standing-kick contact attempt is retained compactly. The passing
policy uses original crouching punch. Native emulator testing is deferred while
the user keeps ADOFAI in Mesen. No full1-1, upgrades or audio qualification.
''',encoding='utf-8')
    save(O/'freeze.json',dict(passed=True,checkpoint=str(D),handoff_sha256=sha(D/'handoff.json'),archive_bytes=q['archive_bytes'],members=len(files)))
    print((O/'freeze.json').read_text())


if __name__=='__main__':main()
