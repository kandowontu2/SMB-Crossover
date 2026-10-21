"""Privately unroll the measured active Ice OAM scans over exact working E."""
from pathlib import Path
import hashlib,json,shutil,subprocess,sys
R=Path(__file__).resolve().parents[2];V=R/'build/verification';H=V/'root49-freeze-render-fast-f'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
SCAN='''  ; Four sequential OAM entries per iteration preserve exact bus-write order.
  .repeat 4, I
    .scope
      lda Sprite_Y_Position+I*4,x
      cmp #240
      bcs Next
      lda Sprite_Attributes+I*4,x
      and #$10
      beq Ordinary
      inc SmFreezeVisible
      bne Next
Ordinary:
      lda Sprite_Attributes+I*4,x
      and #3
      cmp #1
      bne Next
      inc SmFreezeConflict
Next:
    .endscope
  .endrepeat
  txa
  clc
  adc #16
  tax
  jne Scan
'''
PAINT='''  .repeat 4, I
    .scope
      lda Sprite_Attributes+I*4,x
      and #$10
      beq NonFrozen
      lda Sprite_Attributes+I*4,x
      and #$ef
      sta Sprite_Attributes+I*4,x
      lda SmFreezeBlue
      beq Hide
      lda Sprite_Attributes+I*4,x
      and #$fc
      ora #1
      sta Sprite_Attributes+I*4,x
      jmp Advance
NonFrozen:
      lda SmFreezeBlue
      beq Advance
      lda Sprite_Attributes+I*4,x
      and #3
      cmp #1
      bne Advance
Hide:
      lda #$f8
      sta Sprite_Y_Position+I*4,x
Advance:
    .endscope
  .endrepeat
  txa
  clc
  adc #16
  tax
  jeq PaintDone
  jmp Actor
PaintDone:
'''
def main():
    assert not H.exists();H.mkdir()
    cp=R/'build/checkpoints/roster-audit-v49-ice-over-sophia-e/manifest.json'
    assert sha(cp)=='65072e56ce25e03e748248cb1efdc51312378e23d099259261bc02d71a76d64b';c=json.loads(cp.read_text())
    for n,h in c['source_hashes'].items():
        assert sha(R/n)==h,n;q=H/'source'/n;q.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(R/n,q)
    for n,h in c['generated11'].items():
        q=H/'source/build/generated'/n;q.parent.mkdir(parents=True,exist_ok=True)
        assert sha(R/'build/generated'/n)==h;shutil.copyfile(R/'build/generated'/n,q)
    target=H/'source/src/samus_freeze_render.s';code=target.read_text()
    a=code.index('Scan:\n',code.index('.proc SamusFreezeRenderFinish'))+len('Scan:\n')
    z=code.index('  lda SmFreezeVisible\n  beq Paint',a)
    old_scan=code[a:z];assert old_scan.endswith('  bne Scan\n')
    code=code[:a]+SCAN+code[z:]
    a=code.index('Actor:\n',code.index('.proc SamusFreezeRenderFinish'))+len('Actor:\n')
    z=code.index('  lda SmFreezeBlue\n  cmp SmFreezeLastBlue',a)
    old_paint=code[a:z];assert old_paint.endswith('  bne Actor\n')
    code=code[:a]+PAINT+code[z:];target.write_text(code)
    driver=V/'root49-sophia-head-axis-d/build.py';shutil.copyfile(driver,H/'build.py')
    catalog={n:sha(H/'source'/n)for n in c['source_hashes']}
    assert [n for n,h in catalog.items()if h!=c['source_hashes'][n]]==['src/samus_freeze_render.s']
    pre=dict(status='PREPARED_PRIVATE_ACTIVE_ICE_OAM_SCAN_UNROLL',script_sha256=sha(__file__),
      checkpoint_E_sha256=sha(cp),source_hashes=catalog,generated11=c['generated11'],
      changed_sources=['src/samus_freeze_render.s'],old_scan=old_scan,old_paint=old_paint,
      phase_cap_bytes=300000000,reserve_bytes=50000000,global_cap_bytes=70000000000,
      main_changed=False,goal_complete=False)
    (H/'preparation.json').write_text(json.dumps(pre,indent=2)+'\n')
    sys.path.insert(0,str(V/'agent49g-samus-crouch-fix-proposal-b'));from image import Image
    builds=[]
    for mp in ['mmc3','mmc5']:
        for base in [False,True]:
            stem=f'smb-crossover-{mp}'+('-baseline'if base else'')
            print('START',stem,flush=True)
            with(H/(stem+'.log')).open('wb')as log:
                q=subprocess.run([sys.executable,str(H/'build.py'),'--mapper',mp]+(['--baseline']if base else[]),cwd=R,stdout=log,stderr=subprocess.STDOUT)
            assert q.returncode==0,(stem,q.returncode)
            rom=H/'source/build'/(stem+'.nes');old=cp.parent/rom.name
            if base:
                assert rom.read_bytes()==old.read_bytes();delta=[];span=None
            else:
                im=Image(rom);prev=Image(old);newh=im.hook('SamusFreezeRenderFinish');oldh=prev.hook('SamusFreezeRenderFinish')
                assert newh['address']==oldh['address']and newh['physical_bank']==oldh['physical_bank']==11
                assert im.ram==prev.ram,'No RAM layout or symbol address changes'
                first=newh['rom_offset'];size=im.sym('SamusFreezeRenderFinish')['size'];span=[first,first+size]
                x,y=old.read_bytes(),rom.read_bytes();assert len(x)==len(y)
                delta=[dict(offset=i,old=a,new=b)for i,(a,b)in enumerate(zip(x,y))if a!=b]
                assert delta and all(span[0]<=z['offset']<span[1]for z in delta),'Only the single existing active leaf and its grown trailing tables may change'
            builds.append(dict(mapper=mp,baseline=base,changed_bytes=len(delta),allowed_ROM_span=span,delta=delta,
              artifacts={ext:dict(path=str(rom.with_suffix('.'+ext).relative_to(R)),sha256=sha(rom.with_suffix('.'+ext)),bytes=rom.with_suffix('.'+ext).stat().st_size)for ext in ['nes','lbl','dbg','map']}))
            (H/'build-progress.json').write_text(json.dumps(dict(status='RUNNING',builds=builds),indent=2)+'\n')
            print('END',stem,len(delta),sha(rom),flush=True)
    for n,h in c['source_hashes'].items():assert sha(R/n)==h,n
    (H/'build-review.json').write_text(json.dumps(dict(status='PASS_FOUR_PRIVATE_F_BUILDS_SINGLE_ACTIVE_LEAF_ONLY',
      preparation_sha256=sha(H/'preparation.json'),builds=builds,main_changed=False,goal_complete=False),indent=2)+'\n')
    print('DONE',sha(H/'build-review.json'),flush=True)
if __name__=='__main__':main()
