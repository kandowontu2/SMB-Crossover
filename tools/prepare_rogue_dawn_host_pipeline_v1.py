"""Sparse private actual movement/BG hooks; no canonical edit or native run."""
from pathlib import Path
import hashlib,json,runpy,sys
R=Path(__file__).resolve().parents[1];O=R/'build/rogue-dawn-host-pipeline-v1'
sys.path.insert(0,str(R/'tools'))
from prepare_rogue_dawn_host_deferred_v1 import once

def main():
 old=R/'build/rogue-dawn-host-transactions-v3'
 h=json.loads((old/'handoff.json').read_text())
 assert hashlib.sha256((old/'handoff.json').read_bytes()).hexdigest()=='2b599acf5fdecec07b91c9e1eaef5a89767d9dd2591908e3a669972fe9c76fd5'
 for row in h['bindings']:assert hashlib.sha256(Path(row['path']).read_bytes()).hexdigest()==row['sha256']
 assert (R/'build/rogue-dawn-host-deferred-v1/control-SP192-deferred-negative.json').exists()
 # Literal same transactions, but a distinct actual-movement entry whose
 # scratch ABI is qualified at the real caller instead of eight stack saves.
 src=(R/'src/rogue_dawn_host_deferred.s').read_text();a=src.index('.proc RdTxAfterMovement\n');z=src.index('.endproc',a)+len('.endproc')
 lean=once(src[a:z],'.proc RdTxAfterMovement','.proc RdTxMovementFlush')
 lean=once(lean,' RdTxSaveNative\n','');lean=once(lean,' RdTxRestoreNative\n','')
 O.mkdir(exist_ok=True);assert not(O/'build.json').exists()
 (O/'movement-flush.s').write_text('.export RdTxMovementFlush\n.pushseg\n.segment "ROGUE_DAWN_HOST"\n'+lean+'\n.popseg\n',newline='\n')
 builder=(old/'frozen-prepare_rogue_dawn_host_transactions_v1.py').read_text()
 builder=once(builder,"R=Path(__file__).resolve().parents[1]",'R=Path('+repr(R.as_posix())+')')
 builder=builder.replace("R/'build/rogue-dawn-host-transactions-v1'","R/'build/rogue-dawn-host-pipeline-v1'")
 builder=builder.replace('rogue_dawn_host_transactions.s','rogue_dawn_host_deferred.s')
 insertion='''
 player=(R/'src/player.s').read_text();luigi=(R/'src/luigi_native.s').read_text()
 player=once(player,'    farcall SamusMovement\\n','.if ::ENABLE_MMC5_EXPANDED\\n    farcall RdTxMovement\\n.else\\n    farcall SamusMovement\\n.endif\\n')
 player=once(player,'  jsr PlayerBGCollision       ;do collision detection and process\\n','.if ::ENABLE_MMC5_EXPANDED\\n  jsr RdNativeBGGate         ; source Rogue already collided; exact foreign tail\\n.else\\n  jsr PlayerBGCollision       ;do collision detection and process\\n.endif\\n')
 luigi=once(luigi,'  .res 83-(*-::LuigiNativeTraction),$ea',"""::RdNativeBGGate:
  .assert RdNativeBGGate=$b958,error,"Approved exact B1 padding"
  php
  pha
  lda SelectedCharacter
  cmp #2
  bne Native
  lda RdVariant
  cmp #1
  bne Native
  pla
  plp
  rts
Native:
  pla
  plp
  jmp PlayerBGCollision
  .assert *-RdNativeBGGate=24,error,"Exact private gate footprint"
  .res 83-(*-::LuigiNativeTraction),$ea""")
'''
 builder=once(builder,' overlays={}\n',' overlays={}\n'+insertion)
 builder=once(builder,"[('megaman_weapons.s',weapons),('object.s',objects),('new_roster_dispatch.s',gates)]","[('player.s',player),('luigi_native.s',luigi),('megaman_weapons.s',weapons),('object.s',objects),('new_roster_dispatch.s',gates)]")
 builder=once(builder,'.include "rogue_dawn_host_deferred.s"','.include "rogue_dawn_host_deferred.s"\n.include "movement-flush.s"\n.include "rogue_dawn_host_pipeline.s"')
 builder=once(builder," pickup=range(location(a,'NrPrepare'),location(a,'NrPrepare')+5)"," pickup=range(location(a,'NrPrepare'),location(a,'NrPrepare')+5)\n hookdata=bytes(a['raw']);mov=bytes.fromhex('8d5b01a9') if False else b''\n # Actual macro bytes derive from the linked genuine old target and SMC addresses.\n def farpre(target):\n  return bytes([0x8d])+address(a,'SafecallA_SMC').__add__(1).to_bytes(2,'little')+bytes([0xa9,address(a,target)&255,0x8d])+(address(a,'FarcallJmpTarget_SMC')+1).to_bytes(2,'little')+bytes([0xa9,address(a,target)>>8,0x8d])+(address(a,'FarcallJmpTarget_SMC')+2).to_bytes(2,'little')+bytes([0xa9,128|(location(a,target)-16)//8192,0x20])+address(a,'FarCallCommon').to_bytes(2,'little')\n mov=farpre('SamusMovement');at=hookdata.find(mov,16+8192,16+16384);assert at>=0 and hookdata.find(mov,at+1,16+16384)<0\n movement=range(at,at+18)\n bg=bytes([0x20])+address(a,'PlayerBGCollision').to_bytes(2,'little');j=hookdata.find(bg,location(a,'PlayerCtrlRoutine'),location(a,'PlayerCtrlRoutine')+400);assert j>=0\n bgcall=range(j,j+3);padding=range(16+8192+0x1958,16+8192+0x1970)\n assert hookdata[padding.start:padding.stop]==bytes([0xea])*24")
 builder=once(builder,'if i in head or i in plat or i in pickup:continue','if i in head or i in plat or i in pickup or i in movement or i in bgcall or i in padding:continue')
 builder=once(builder,"paths=[Path(__file__),", "paths=[R/'tools/prepare_rogue_dawn_host_pipeline_v1.py',R/'src/rogue_dawn_host_pipeline.s',O/'movement-flush.s',R/'src/player.s',R/'src/luigi_native.s',Path(__file__),")
 builder=builder.replace("at=hookdata.find(mov,16+8192,16+16384);assert at>=0 and hookdata.find(mov,at+1,16+16384)<0","at=hookdata.find(mov,location(a,'PlayerMovementSubs'),location(a,'PlayerMovementSubs')+256);assert at>=0 and hookdata.find(mov,at+1,location(a,'PlayerMovementSubs')+256)<0")
 flags=['--qualify-existing'] if '--qualify-existing' in sys.argv else []
 p=O/'build-private.py';p.write_text(builder,newline='\n');sys.argv=[str(p),'--output',str(O),*flags];runpy.run_path(str(p),run_name='__main__')
if __name__=='__main__':main()
