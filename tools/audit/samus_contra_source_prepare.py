"""Private exact55 upward Wave world-coordinate repair, no installation."""
from pathlib import Path
import argparse,difflib,hashlib,json,shutil,subprocess,sys
ROOT=Path(__file__).resolve().parents[2]
D=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
BASE='55bcfb8209b628062ce1f833a2ed386bd6f08426d34fed9fa8b5ba1f90694be7'
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--packet',type=Path,required=True);a=p.parse_args();d=a.packet.resolve();d.mkdir(exist_ok=False)
 parent=D/'mac-tmnt-native-v1';assert sha(parent/'baseline.nes')==BASE
 for ext in ['nes','dbg','lbl','map']:shutil.copyfile(parent/f'baseline.{ext}',d/f'baseline.{ext}')
 for n,v in json.loads((parent/'frozen-source.json').read_text()).items():assert sha(parent/'frozen'/n)==v
 source=d/'source';shutil.copytree(parent/'frozen',source)
 changes={}
 def rep(n,old,new):
  f=source/n;s=f.read_text();assert s.count(old)==1,(n,s.count(old));changes.setdefault(n,s);f.write_text(s.replace(old,new))
 rep('src/samus_weapons.s','WaveUp:\n  ; Upward waves are short-lived on screen; spawn X is the fixed center.\n  sta SmShotX,x', 'WaveUp:\n.if ::ENABLE_MMC5_EXPANDED\n  jsr SamusWaveWorldX\n.else\n  sta SmShotX,x\n.endif')
 rep('src/samus_weapons.s','  jsr BridgeShot\n  lda SmShotType,x\n  cmp #3', '''  jsr BridgeShot
.if ::ENABLE_MMC5_EXPANDED
  ; BridgeShot hands the shared projectile over in slot0 and returns X=0.
  ; The bridged type, rather than a now-unrelated Samus pool index, owns
  ; whether this live projectile can collide with terrain.
  lda MmBulletType
  cmp #9
.else
  lda SmShotType,x
  cmp #3
.endif''')
 rep('src/samus.s','  .res 15, $ea', '''.if ::ENABLE_MMC5_EXPANDED
::SamusWaveWorldX:
  ; New low X versus the previous wave position. Source sinusoid motion
  ; changes by less than128px/update, so this is its signed world delta.
  pha
  sec
  sbc SmShotX,x
  jmp SamusWaveWorldPage
  .res 7,$ea
.else
  .res 15, $ea
.endif''')
 rep('src/samus.s','  .res 20,$ea\n  .assert *-SamusAfterBGCollisionBridge=39', '''::SamusWaveWorldPage:
  bmi Negative
  bcs Store
  inc SmShotPage,x
  bcc Store                    ; INC leaves the proven clear carry intact.
Negative:
  bcc Store
  dec SmShotPage,x
Store:
  pla
  sta SmShotX,x
  rts
  .res 1,$ea
  .assert *-SamusAfterBGCollisionBridge=39''')
 patch=''.join(''.join(difflib.unified_diff(old.splitlines(True),(source/n).read_text().splitlines(True),fromfile='a/'+n,tofile='b/'+n))for n,old in changes.items());(d/'implementation.patch').write_text(patch)
 cmd=[sys.executable,str(ROOT/'tools/build_mmc5_expanded.py'),'--workspace',str(source),'--compiler',str(ROOT/'tools/Windows/cc65/bin/cl65.exe')]
 subprocess.run(cmd+['--output',str(d/'candidate.nes')],check=True)
 sys.path.insert(0,str(ROOT/'tools/audit'));from check_tmnt_audio_fallback_oc import qualified
 old,new=(d/'baseline.nes').read_bytes(),(d/'candidate.nes').read_bytes();oldq,newq=qualified(d/'baseline.nes'),qualified(d/'candidate.nes')
 assert all(newq.get(n)==v for n,v in oldq.items()),[(n,v,newq.get(n))for n,v in oldq.items()if newq.get(n)!=v][:10]
 touched=[i for i,(x,y)in enumerate(zip(old,new))if x!=y];assert old[1048592:]==new[1048592:]
 ordinary={}
 for mapper in ['mmc3','mmc5']:
  paths=[]
  for label,workspace in [('baseline',parent/'frozen'),('candidate',source)]:
   dest=d/f'ordinary-{label}-{mapper}.nes';call=cmd[:];call[call.index('--workspace')+1]=str(workspace);subprocess.run(call+['--flag-off',mapper,'--output',str(dest)],check=True);paths.append(dest)
  assert paths[0].read_bytes()==paths[1].read_bytes();ordinary[mapper]=sha(paths[0])
 refs=['reference/crossover/super-mario-crossover.swf','reference/crossover2/source.swf']
 for folder in ['reference/crossover/decompiled/scripts/com/smbc','reference/crossover2/extracted/scripts/com/smbc']:
  refs+=[folder+'/'+n for n in ['characters/Samus.as','characters/Bill.as','projectiles/SamusShot.as','projectiles/SamusBomb.as','projectiles/BillBullet.as','characters/Character.as','data/PickupInfo.as','data/GameSettings.as']if(ROOT/folder/n).exists()]
 (d/'references').mkdir();bindings={}
 for n in refs:
  dest=d/'references'/n;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/n,dest);bindings[n]=sha(dest)
 proof=dict(passed=True,adopted=False,parent_ROM_sha256=BASE,ROM_sha256=sha(d/'candidate.nes'),changed_bytes=len(touched),changed_PRG_banks=sorted({(i-16)//8192 for i in touched}),qualified_old_symbols_exact=len(oldq),CHR_exact=True,new_RAM_bytes=0,ordinary_flagoff_byte_exact=True,ordinary=ordinary,source_files={n:sha(source/n)for n in changes},reference_bindings=bindings,patch_sha256=sha(d/'implementation.patch'),scope='Private source and build only; current55 assembled/native qualification follows. Fixed bank donor is a small unused tail, not permission to replace a later whole fixed bank.')
 (d/'build-proof.json').write_text(json.dumps(proof,indent=2));print(json.dumps(proof,indent=2))
if __name__=='__main__':main()
