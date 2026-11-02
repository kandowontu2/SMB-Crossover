"""Actual native shot/bbox/head/side ports; complete foreign ABI differentials."""
import itertools,json
from pathlib import Path
import check_bubble_bobble_native_proxy_1102_v5 as Q
from check_bubble_bobble_typed_contact_1102_v5 import same_application
P=Q.P;C=Q.C;N=Q.N;R=Q.R;O=Q.O;address=Q.address


def main():
 old,q,route=Q.bundle(False);new,_,_=Q.bundle(True);checks={};seeds=[N.fresh(b)for b in[old,new]]
 foreign=0
 for char,(x,y,crouch,pose),flags in itertools.product([i for i in range(256)if i!=39],[(0,32,0,0),(120,176,1,1),(250,239,0,1)],[0x30,0xf1]):
  pair=[]
  for seed in seeds:
   m=N.fork(seed);N.put(m,SelectedCharacter=char,Player_Rel_XPos=x,Player_Rel_YPos=y,Player_X_Position=x,Player_Y_Position=y,Player_Y_HighPos=1,CrouchingFlag=crouch,Cv3Variant=pose)
   z=N.invoke(m,'LmBoundingBoxGate',a=0xa5,x=0,y=0,p=flags);pair.append((m,z))
  a,az=pair[0];b,bz=pair[1]
  assert[az[k]for k in['A','X','Y','P']]==[bz[k]for k in['A','X','Y','P']]and same_application(a,b),('Foreign bbox full state',char,x,y,flags,az,bz,bytes(a[0x15a:0x17b]).hex(),bytes(b[0x15a:0x17b]).hex())
  foreign+=1
 checks['all_255_foreign_native_bbox_ABI_ZP_application_SMC_maps_cases']=foreign
 shots=0
 for char,flags in itertools.product(range(256),[0x30,0xf1]):
  pair=[]
  for seed in seeds:
   m=N.fork(seed);N.put(m,SelectedCharacter=char);z=N.invoke(m,'MegaManFullShotBank',a=0xa5,x=0,y=0,p=flags);pair.append((m,z))
  a,az=pair[0];b,bz=pair[1]
  if char!=39:
   assert[az[k]for k in['A','X','Y','P']]==[bz[k]for k in['A','X','Y','P']]and same_application(a,b),('Foreign shot full state',char,flags,az,bz)
   shots+=1
  else:
   bypass=N.fork(seeds[1]);N.put(bypass,SelectedCharacter=37);ref=N.invoke(bypass,'MegaManFullShotBank',a=0xa5,x=0,y=0,p=flags)
   assert[bz[k]for k in['A','X','Y','P']]==[ref[k]for k in['A','X','Y','P']]
 checks['all_255_foreign_native_shot_full_state_ABI_cases']=shots
 # The original authenticated Shinobi row16 must remain exact at every
 # original pose index, with stale renderer coordinates and a current camera.
 sh=[]
 for bb in[old,new]:
  m=C.ready(bb);N.put(m,SelectedCharacter=36);C.call(m,0xac1d);assert m.ram[2][0x1fe0]==0xa7 and m.ram[3][0x1fe0]==0xa7
  sh.append(m)
 shposes=0
 source_poses=sorted(set(z['pose']for z in json.loads((R/'build/shinobi-hurt-layout-1101-v5/pose-packets.json').read_text())['poses']))
 for pose,x,y,camera,flags in itertools.product(source_poses,[3,120,250],[8,176,239],[0,506],[0x30,0xf1]):
  pair=[]
  for seed in sh:
   m=N.fork(seed);world=camera+x;N.put(m,Player_X_Position=world&255,Player_PageLoc=world>>8,Player_Y_Position=y,Player_Y_HighPos=1,Player_Rel_XPos=x,Player_Rel_YPos=y,ScreenLeft_X_Pos=camera&255,ScreenLeft_PageLoc=camera>>8)
   m.ram[2][0x300]=pose;m.ram[2][0x363]=4
   for at,v in[(0x379,177),(0x384,0),(0x38f,201),(0x39a,0)]:m.ram[2][at]=v
   z=N.invoke(m,'LmBoundingBoxGate',a=0xa5,x=0,y=0,p=flags);pair.append((m,z))
  a,az=pair[0];b,bz=pair[1]
  assert[az[k]for k in['A','X','Y','P']]==[bz[k]for k in['A','X','Y','P']]and same_application(a,b),('Authenticated Sh bbox full state',pose,x,y,camera,flags,az,bz,bytes(a[0x15a:0x17b]).hex(),bytes(b[0x15a:0x17b]).hex())
  shposes+=1
 checks['authenticated_Sh_original_pose_bbox_full_state_ABI_cases']=dict(cases=shposes,source_pose_indices=source_poses)
 # Head/side public vectors must be identical to the genuine lower-fixed
 # native probe, including query scratch/output flags, solid and air tiles.
 query=0;seeds=[Q.fresh(new,route,i)for i in[0,1]]
 for identity,seed in enumerate(seeds):
  for head,x,y,probe,tile in itertools.product([True,False],[0,15,127,240,255],[32,80,176],[30,33,34,35,36],[0,0x54,0x61]):
   if(head and probe!=30)or(not head and probe==30):continue
   a=N.fork(seed);N.put(a,Player_X_Position=x,Player_PageLoc=1,Player_Y_Position=y,Player_Y_HighPos=1)
   for name in['Block_Buffer_1','Block_Buffer_2']:
    for j in range(208):a[address(new,name)+j]=tile
   b=N.fork(a);az=N.invoke(a,'HuHead'if head else'HuSide',a=176,x=0,y=probe,p=0x31);bz=N.invoke(b,'BlockBufferColli_Head'if head else'BlockBufferColli_Side',a=176,x=0,y=probe,p=0x31)
   assert[az[k]for k in['A','X','Y','P']]==[bz[k]for k in['A','X','Y','P']]and bytes(a[:11])==bytes(b[:11])and a.ram==b.ram,(identity,head,x,y,probe,tile,az,bz)
   query+=1
 checks['actual_public_head_side_fixed_native_query_differentials']=query
 box=0
 for identity,seed in enumerate(seeds):
  for world,camera,y in itertools.product([64,255,256,506,700],[0,32,255,506],[32,176,208]):
   if not 0<=world-camera<=240:continue
   m=N.fork(seed);N.put(m,Player_X_Position=world&255,Player_PageLoc=world>>8,Player_Y_Position=y,Player_Y_HighPos=1,Player_Rel_XPos=17,Player_Rel_YPos=19,ScreenLeft_X_Pos=camera&255,ScreenLeft_PageLoc=camera>>8)
   N.invoke(m,'LmBoundingBoxGate',a=0xa5,x=0,y=0,p=0x31)
   expected=[world-camera,(y+16)&255,world-camera+15,(y+31)&255]
   assert list(m[address(new,'BoundingBox_UL_Corner'):address(new,'BoundingBox_UL_Corner')+4])==expected,(identity,world,camera,y,expected)
   box+=1
 checks['actual_native_visible16_fullbox_current_camera_cases']=box
 out=dict(passed=True,ROM_written=False,admitted=False,checks=checks,base_ROM_SHA256=P.PIN,scope='Actual native LmBoundingBoxGate/MegaManFullShotBank and fixed query ingresses in explicit legal CPU fixtures; all255 foreign raw IDs and authenticated original Shinobi pose cases preserve full application/SMC/maps. No Mesen/stage-clear/install claim.',bindings={p.relative_to(R).as_posix():P.sha(p.read_bytes())for p in[Path(__file__),R/'tools/audit/prepare_bubble_bobble_native_proxy_1102_v5.py',O/'native-proxy.bin',O/'native-proxy-helper.chr',O/'native-proxy-ports.bin',O/'native-proxy-bbox.bin']})
 (O/'native-proxy-ports-CPU.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(dict(passed=True,checks=checks)))


if __name__=='__main__':main()
