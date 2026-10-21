"""Private F-based Samus head/side axis candidate; no shared ROM mutation."""
from pathlib import Path
import hashlib, importlib.util, json, shutil, subprocess, sys

R=Path(__file__).resolve().parents[2]
V=R/'build/verification'
H=V/'root49-samus-head-axis-g2'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
LEAF='''; HitTester.checkLastHitPoints uses the previous head for Ground's underside.
; A side cell already beside that head is not a ceiling. Keep each original
; full-width sample, including walking coins and the native effect-cell ABI.
.pushseg
.segment "LEGACY_COLD"
.proc SamusHeadAxisProbe
  clc
  lda Player_X_Position
  adc #8
  and #$f0
  sta SmHeadX
  lda Player_PageLoc
  adc #0
  sta SmHeadPage
  ldy SmTemp
  jsr BlockBufferColli_Head
  beq Done
  pha
  cmp #$26
  beq Keep
  cmp #$c2
  beq Keep
  cmp #$c3
  beq Keep
  lda Player_Y_Speed
  bpl Keep
  ; Undo the actual Q8.16 movement without quantizing its fractional borrow.
  sec
  lda MmYFraction
  sbc MmVY
  lda MmYFraction+1
  sbc MmVY+1
  lda Player_Y_Position
  sbc MmVY+2
  bcs Keep                       ; Previous origin crossed below screen byte.
  clc
  adc BlockBuffer_Y_Adder,y
  bcs Keep                       ; Previous head is at/below256.
  sta SmClearance
  lda R2
  clc
  adc #48                        ; Actual sampled cell bottom, including HUD.
  bcs Reject                     ; Bottom256, previous head below256.
  cmp SmClearance
  bcc Keep
  beq Keep                       ; Previous head >= cell bottom.
Reject:
  pla
  lda #0
  rts
Keep:
  pla
Done:
  rts
.endproc
.assert *-SamusHeadAxisProbe<=101, error, "Samus axis leaf exceeds MMC5 cold gap"
.popseg
'''

def main():
    assert not H.exists();H.mkdir()
    cp=R/'build/checkpoints/roster-audit-v49-freeze-render-fast-f/manifest.json'
    assert sha(cp)=='c0f31e09027aad704fc539e95adc0a53abb035fef647206b61bb10d94c8068e2'
    c=json.loads(cp.read_text())
    for n,h in c['source_hashes'].items():
        assert sha(R/n)==h,n
        p=H/'source'/n;p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(R/n,p)
    for n,h in c['generated11'].items():
        p=H/'source/build/generated'/n;p.parent.mkdir(parents=True,exist_ok=True)
        assert sha(R/'build/generated'/n)==h;shutil.copyfile(R/'build/generated'/n,p)
    p=H/'source/src/samus.s';code=p.read_text()
    start=code.index('Probe:\n',code.index('.proc SamusHeadProbe'))
    end=code.index('.endproc',start)
    old=code[start:end]
    assert old.endswith('  jmp BlockBufferColli_Head\n')
    code=code[:start]+'''Probe:
  farcall SamusHeadAxisProbe, jmp
  .res 5, $ea
  .assert *-Probe=23, error, "Original head probe footprint must remain23"
'''+code[end:];p.write_text(code)
    p=H/'source/src/entrypoint.s';p.write_text(p.read_text()+'''
; Preserve all old contribution addresses; reuse the bank11 cold tail.
.if ::ENABLE_CROSSOVER
.include "samus_head_axis.s"
.endif
''')
    (H/'source/src/samus_head_axis.s').write_text(LEAF)
    shutil.copyfile(V/'root49-sophia-head-axis-d/build.py',H/'build.py')
    names=list(c['source_hashes'])+['src/samus_head_axis.s']
    hashes={n:sha(H/'source'/n)for n in names}
    changed=[n for n in c['source_hashes']if hashes[n]!=c['source_hashes'][n]]
    assert set(changed)=={'src/samus.s','src/entrypoint.s'},changed
    pre=dict(script_sha256=sha(__file__),checkpoint_F_sha256=sha(cp),source_hashes=hashes,
      generated11=c['generated11'],changed_sources=changed,added_sources=['src/samus_head_axis.s'],old_probe=old,
      primary_source_sha256=sha(R/'reference/crossover2/extracted/scripts/com/smbc/data/HitTester.as'),
      phase_cap_bytes=300000000,reserve_bytes=50000000,global_cap_bytes=80000000000,
      scope='Private source-axis candidate. Must pass authored and ordinary replay checks before adoption.',main_changed=False,goal_complete=False)
    (H/'preparation.json').write_text(json.dumps(pre,indent=2)+'\n')
    helper=V/'agent49g-samus-crouch-fix-proposal-b/image.py'
    sp=importlib.util.spec_from_file_location('axis_image',helper);im=importlib.util.module_from_spec(sp);sp.loader.exec_module(im)
    builds=[]
    for mp in ['mmc3','mmc5']:
        for base in [False,True]:
            stem=f'smb-crossover-{mp}'+('-baseline'if base else'')
            with(H/(stem+'.log')).open('wb')as log:
                q=subprocess.run([sys.executable,str(H/'build.py'),'--mapper',mp]+(['--baseline']if base else[]),cwd=R,stdout=log,stderr=subprocess.STDOUT)
            assert q.returncode==0,(stem,q.returncode)
            rom=H/'source/build'/(stem+'.nes');oldrom=cp.parent/rom.name
            delta=[];spans=[];leaf_size=0
            if base:assert rom.read_bytes()==oldrom.read_bytes()
            else:
                now,oldim=im.Image(rom),im.Image(oldrom)
                assert now.ram==oldim.ram,'No RAM addresses change'
                h=now.hook('Probe',scope='SamusHeadProbe');prev=oldim.hook('Probe',scope='SamusHeadProbe')
                assert h['address']==prev['address']and h['physical_bank']==prev['physical_bank']==10
                assert now.sym('SamusAfterBGCollision')['val']==oldim.sym('SamusAfterBGCollision')['val']
                leaf=now.hook('SamusHeadAxisProbe');leaf_size=now.sym('SamusHeadAxisProbe')['size']
                spans=[[h['rom_offset'],h['rom_offset']+23],[leaf['rom_offset'],leaf['rom_offset']+leaf_size]]
                assert leaf['physical_bank']==11 and leaf_size<=101
                for i,(a,b)in enumerate(zip(oldrom.read_bytes(),rom.read_bytes())):
                    if a!=b:delta.append(dict(offset=i,old=a,new=b))
                assert delta and all(any(a<=z['offset']<b for a,b in spans)for z in delta)
            builds.append(dict(mapper=mp,baseline=base,leaf_bytes=leaf_size,changed_bytes=len(delta),allowed_ROM_spans=spans,delta=delta,
              artifacts={ext:dict(path=str(rom.with_suffix('.'+ext).relative_to(R)),sha256=sha(rom.with_suffix('.'+ext)),bytes=rom.with_suffix('.'+ext).stat().st_size)for ext in ['nes','lbl','dbg','map']}))
            print(stem,'built; leaf',leaf_size,'delta',len(delta),flush=True)
    for n,h in c['source_hashes'].items():assert sha(R/n)==h,n
    out=H/'build-review.json';out.write_text(json.dumps(dict(status='PASS_PRIVATE_G_BUILDS_EXACT_TWO_ROM_SPANS_BASELINES_LITERAL',preparation_sha256=sha(H/'preparation.json'),builds=builds,main_changed=False,goal_complete=False),indent=2)+'\n')
    print('PRIVATE_BUILDS',sha(out),flush=True)
if __name__=='__main__':main()
