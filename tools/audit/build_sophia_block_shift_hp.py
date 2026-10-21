"""Bounded Sophia head-origin fix on immutable H; keep old entry addresses."""
from pathlib import Path
import hashlib,importlib.util,json,shutil,subprocess,sys
R=Path(__file__).resolve().parents[2];V=R/'build/verification';O=V/'root49-sophia-block-shift-hn'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 cp=R/'build/checkpoints/roster-audit-v49-samus-audio-scan-h/manifest.json'
 assert sha(cp)=='8de2e8a7799087b1889433123f50352684de3f164148e8d9f8ad0dcb655f387c'
 c=json.loads(cp.read_text());H=Path(c['source_directory']);D=O/'source';assert not D.exists()
 for n,h in c['source_hashes'].items():
  assert sha(R/n)==sha(H/n)==h
  d=D/n;d.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(H/n,d)
 for n,h in c['generated11'].items():
  assert sha(H/'build/generated'/n)==h
  d=D/'build/generated'/n;d.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(H/'build/generated'/n,d)
 p=D/'src/bill_native_rare.s';text=p.read_text(encoding='utf-8')
 old='    jsr InitBlock_XY_Pos     ;get block object horizontal coordinates saved'
 assert text.count(old)==1
 text=text.replace(old,'    jsr SophiaHeadBlockOrigin ;same native initialization, then exact source-head cell')
 text+='''
; Append in the existing bank9 tail. Only an admitted ordinary Sophia head
; collision overrides Mario's center-derived block position. Projectile
; callers already publish their own contacted cell and remain unchanged.
.pushseg
.segment "BILL_BODY_COLD"
.proc SophiaHeadBlockOrigin
  jsr InitBlock_XY_Pos
  php
  pha
  lda SelectedCharacter
  cmp #CHARACTER_SOPHIA
  bne Done
  lda MmBlockAttack
  bne Done
  bit SmCeilingHit
  bpl Done
  lda RgTempX
  and #$f0
  sta Block_X_Position,x
  lda RgTempPage
  sta Block_PageLoc,x
  sta Block_PageLoc2,x
Done:
  pla
  plp
  rts
.endproc
.popseg
'''
 p.write_text(text,encoding='utf-8')
 shutil.copyfile(V/'root49-lag-combined-i/build.py',O/'build.py')
 prep=dict(checkpoint_sha256=sha(cp),script_sha256=sha(__file__),source={n:sha(D/n)for n in c['source_hashes']},generated=c['generated11'],scope='H plus single-file Sophia admitted head-contact origin. No main install. Preserve all old source entry addresses, RAM, CHR and baseline bytes.',private_cap=100000000,reserve=20000000,global_cap=100000000000)
 (O/'build-preparation-hp.json').write_text(json.dumps(prep,indent=2),encoding='utf-8')
 helper=V/'agent49g-samus-crouch-fix-proposal-b/image.py';spec=importlib.util.spec_from_file_location('sophia_hp_image',helper);im=importlib.util.module_from_spec(spec);spec.loader.exec_module(im)
 builds=[]
 for mapper in ['mmc3','mmc5']:
  for baseline in [False,True]:
   stem='smb-crossover-'+mapper+('-baseline'if baseline else'')
   with(O/(stem+'-build-hp.log')).open('wb')as log:
    q=subprocess.run([sys.executable,str(O/'build.py'),'--mapper',mapper]+(['--baseline']if baseline else[]),cwd=R,stdout=log,stderr=subprocess.STDOUT)
   assert q.returncode==0,(mapper,baseline)
   after=D/'build'/(stem+'.nes');before=cp.parent/after.name;a,b=before.read_bytes(),after.read_bytes();layout={}
   if baseline:assert a==b
   else:
    old,new=im.Image(before),im.Image(after)
    assert old.ram==new.ram and a[:16]==b[:16]and a[16+512*1024:]==b[16+512*1024:]
    old_global={(s['name'],s['val'])for s in old.data['sym']if s.get('scope')==1 and 'seg'in s and 'val'in s}
    new_global={(s['name'],s['val'])for s in new.data['sym']if s.get('scope')==1 and 'seg'in s and 'val'in s}
    assert old_global<=new_global
    hook=new.hook('SophiaHeadBlockOrigin');oldcore=old.sym('NativeRarePlayerHeadCollisionCore');newcore=new.sym('NativeRarePlayerHeadCollisionCore')
    assert oldcore['val']==newcore['val'] and oldcore['size']==newcore['size']
    changes=[i for i,(x,y)in enumerate(zip(a,b))if x!=y]
    assert len([i for i in changes if not hook['rom_offset']<=i<hook['rom_offset']+new.sym('SophiaHeadBlockOrigin')['size']])<=2
    layout=dict(old_global_PC_RAM_literal=True,helper=hook,helper_size=new.sym('SophiaHeadBlockOrigin')['size'],nonhelper_changed_bytes=2,all_changed_bytes=len(changes))
   builds.append(dict(mapper=mapper,baseline=baseline,rom=str(after.relative_to(R)),sha256=sha(after),layout=layout))
   print(stem,'PASS',layout,flush=True)
 for n,h in c['source_hashes'].items():assert sha(R/n)==h
 out=O/'build-review-hp.json';out.write_text(json.dumps(dict(status='PASS_FOUR_PRIVATE_BUILDS_OLD_GLOBAL_PC_RAM_CHR_AND_BASELINES_LITERAL',preparation_sha256=sha(O/'build-preparation-hp.json'),builds=builds,installed=False,native_pending=True),indent=2),encoding='utf-8')
 print('BUILD',sha(out),flush=True)
if __name__=='__main__':main()
