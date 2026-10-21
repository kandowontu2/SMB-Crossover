"""Correct the OAM oracle to include native bouncing brick art; retain HQ."""
from pathlib import Path
import hashlib,json,subprocess,sys
R=Path(__file__).resolve().parents[2];O=R/'build/verification/root49-sophia-block-shift-hn'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 src=(O/'sophia-block-regression-hq.lua').read_text(encoding='utf-8')
 src=src.replace(" for i=0,1 do if r('BlockMetasprite',i)==L.METASPRITE_MISC_BLOCK then\n  local tile=emu.read(4*0x2000+(L.MetaspriteData_MISC_BLOCK_RIGHT+1)%0x2000,emu.memType.nesPrgRom)",""" for i=0,1 do
  local art=r('BlockMetasprite',i)
  local ptr=art==L.METASPRITE_MISC_BLOCK and L.MetaspriteData_MISC_BLOCK_RIGHT
   or art==L.METASPRITE_MISC_BRICK_GROUND and L.MetaspriteData_MISC_BRICK_GROUND_RIGHT
   or art==L.METASPRITE_MISC_BRICK_OTHER and L.MetaspriteData_MISC_BRICK_OTHER_RIGHT
  if ptr then
  local tile=emu.read(4*0x2000+(ptr+1)%0x2000,emu.memType.nesPrgRom)""")
 src=src.replace("    current.seen=current.seen+1\n    assert(bx", """    current.seen=current.seen+1
    if current.seen==1 and (current.tile==0xc0 or current.tile==0x58) then
     local m=r('JumpCoinMiscOffset')
     assert(r('Misc_X_Position',m)+256*r('Misc_PageLoc',m)==current.tx+5,'Coin emerges above contacted cell')
    end
    assert(bx""")
 p=O/'sophia-block-regression-hr.lua';assert not p.exists();p.write_text(src,encoding='utf-8')
 (O/'hq-oracle-negative.json').write_text(json.dumps(dict(kind='OAM_ORACLE_OMITTED_NATIVE_BRICK_METASPRITES',original_fixture_sha256=sha(O/'sophia-block-regression-hq.lua'),scope='HQ used-block-only OAM filter passed both question block types then saw zero filtered frames for coin brick. Native DrawBlock intentionally selects MISC_BRICK_GROUND/OTHER while the replacement remains a brick. HR includes those existing art types with the same two-half X checks. Runtime, ROM and all previous collision assertions unchanged.'),indent=2),encoding='utf-8')
 groups=[]
 for mapper in ['mmc3','mmc5']:
  for mode in [0,1]:
   wrapper=O/f'{mapper}-mode{mode}-hr.lua';wrapper.write_text('REGRESSION_MODE='+str(mode)+'\ndofile('+json.dumps(p.as_posix())+')\n',encoding='utf-8')
   rom=O/'source/build'/f'smb-crossover-{mapper}.nes';out=O/f'hr-{mapper}-mode{mode}'
   args=[sys.executable,str(R/'tools/audit/run_mesen_isolated.py'),'--output',str(out),str(wrapper),str(rom),'--timeout','120']
   (O/f'hr-{mapper}-mode{mode}-command.json').write_text(json.dumps(args),encoding='utf-8')
   with(O/f'hr-{mapper}-mode{mode}-host.log').open('wb')as f:q=subprocess.run(args,cwd=R,stdout=f,stderr=subprocess.STDOUT)
   groups.append(dict(mapper=mapper,mode=mode,exit=q.returncode,rom_sha256=sha(rom),files={str(z.relative_to(O)):dict(bytes=z.stat().st_size,sha256=sha(z))for z in out.rglob('*')if z.is_file()}))
   print(mapper,mode,q.returncode,flush=True)
 out=O/'native-review-hr.json';out.write_text(json.dumps(dict(status='PASS_64_NATIVE_JUMP_CASES_WITH_OAM_REWARDS_AND_BUMP_REQUESTS'if all(g['exit']==0 for g in groups)else'RETAINED_NATIVE_FAILURES',script_sha256=sha(__file__),fixture_sha256=sha(p),groups=groups,scope='Explicit authored setup, controller A jumps and native head collision/render/reward/sound-request paths. Native queue request observed, not waveform certification or ordinary fullroute.'),indent=2),encoding='utf-8')
 print('NATIVE',sha(out),flush=True)
if __name__=='__main__':main()
