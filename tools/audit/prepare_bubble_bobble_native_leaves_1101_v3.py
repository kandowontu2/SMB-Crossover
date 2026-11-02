"""Compile real native input/world/query/draw leaves into the private image."""
import json,re,subprocess
import prepare_bubble_bobble_component_1101_v2 as P
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location
R=P.R;O=P.O;BASE=R/'build/excitebike-pose-1101-v3/current4.nes'
PIN='cf1412eb78ed6531d2f7478c9790f96314a95f2f3fdd6c2b80bfbefd24fca3a8'


def main():
 b=scoped_load(BASE);assert P.B.sha(b['raw'])==PIN;core=P.labels(O/'component.lbl')
 names=['R0','R1','R2','R3','R4','R5','R6','R7','Player_X_Position','Player_PageLoc','Player_Y_Position','Player_Y_HighPos','Player_State','PlayerFacingDir','Player_X_Scroll','Player_X_Speed','Player_Y_Speed','Player_Pos_ForScroll','ScreenLeft_X_Pos','ScreenLeft_PageLoc','OperMode','GameEngineSubroutine','GamePauseStatus','FrameCounter','SavedJoypadBits','Block_Buffer_1','Block_Buffer_2','MTileAttribute','CurrentOAMOffset','GuestOamRotationActive','RgOamRotation','ObjectMetasprite','SmPosePtr','SafecallA_SMC','FarcallJmpTarget_SMC','FarCallCommon','NextBank_SMC','SafereturnA_SMC','MetaspriteRenderLoop']
 names+=['Enemy_Flag','Enemy_ID','Enemy_State','Enemy_X_Position','Enemy_PageLoc','Enemy_Y_Position','Enemy_Y_HighPos','Enemy_X_Speed','Enemy_Y_Speed','Enemy_MovingDir','EnemyIntervalTimer']
 names+=['KillPlayer','ShellOrBlockDefeat','ObjectOffset','BoundingBox_UL_Corner','NumberofLives']
 names+=['FmGroups']
 source='.setcpu "6502"\n.macpack longbranch\n'+''.join(f'{n}=${address(b,n):04x}\n'for n in names)
 source+=''.join(f'{n}=${core[n]:04x}\n'for n in ['BbReject','BbInput','BbOriginal_C43E','BbOriginal_DAB2','BbHurtBub','BbHurtBob','BbSourceInit','BbSourceSprites','BbPlayerStep','BbBubbleStep','BbTrappedEnemyStep','BbSourceClock'])
 source+=f'Bank_MetaspriteRenderLoop=${((location(b,"MetaspriteRenderLoop")-16)//8192)|128:02x}\n'
 source+=f'Bank_KillPlayer=${((location(b,"KillPlayer")-16)//8192)|128:02x}\n'
 source+=f'Bank_ShellOrBlockDefeat=${((location(b,"ShellOrBlockDefeat")-16)//8192)|128:02x}\n'
 native=(R/'tools/reference/bubble_bobble_native_leaves_1101_v3.inc').read_text().replace('.include "bubble_bobble_native_frame_1101_v3.inc"',(R/'tools/reference/bubble_bobble_native_frame_1101_v3.inc').read_text())
 sites=[]
 def mark(match):
  name=f'BbRelaxNative{len(sites)}';sites.append((name,match[2],match[3]));return name+':\n'+match[0]
 native=re.sub(r'(?m)^(\s*)j(eq|ne|cc|cs|mi|pl|vc|vs) ([A-Za-z_]\w*)([^\n]*)$',mark,native)
 native+='\n.export '+','.join(sorted(set([n for n,_,_ in sites]+[t for _,_,t in sites])))+'\n'
 (O/'native-leaves.cfg').write_text('MEMORY{A:start=$a071,size=$f,file="'+(O/'native-actor-hole.bin').as_posix()+'";B:start=$a0b0,size=$50,file="'+(O/'native-box-hole.bin').as_posix()+'";S:start=$b53a,size=6,file="'+(O/'native-sound-hole.bin').as_posix()+'";H:start=$b540,size=$b00,file=%O;}SEGMENTS{BB_ACTOR_HOLE:load=A,type=ro;BB_BOX_HOLE:load=B,type=ro;BB_SOUND_HOLE:load=S,type=ro;BB_HOST:load=H,type=ro;}')
 cc=R/'tools/Windows/cc65/bin'
 relaxed=[]
 for iteration in range(8):
  (O/'native-leaves.s').write_text(source+native)
  for cmd in [[cc/'ca65.exe','-I',R/'tools/reference',O/'native-leaves.s','-o',O/'native-leaves.o'],[cc/'ld65.exe','-C',O/'native-leaves.cfg',O/'native-leaves.o','-o',O/'native-leaves.bin','-Ln',O/'native-leaves.lbl']]:
   p=subprocess.run(list(map(str,cmd)),capture_output=True,text=True);assert p.returncode==0,'\n'.join(p.stderr.splitlines()[:12])
  labels=P.labels(O/'native-leaves.lbl');changes=[]
  for name,condition,target in sites:
   old=name+':\n j'+condition+' '+target
   if old not in native:continue
   delta=labels[target]-(labels[name]+2)
   if -128<=delta<=127:changes.append((old,name+':\n b'+condition+' '+target,name,target,delta))
  if not changes:break
  for old,new,name,target,delta in changes:native=native.replace(old,new,1);relaxed.append(dict(site=name,target=target,initial_short_displacement=delta,saved_bytes=3))
 else:raise AssertionError('native branch relaxation did not converge')
 lab=P.labels(O/'native-leaves.lbl');host=(O/'native-leaves.bin').read_bytes();base=(O/'component.bin').read_bytes();blob=bytearray(base)
 assert lab['BbNativeEnd']<=0xbfe0,'Final relaxed body must fit before granted header'
 blob[0x1540:0x1540+len(host)]=host
 reclaimed=0
 for off,name in[(0x71,'native-actor-hole.bin'),(0xb0,'native-box-hole.bin'),(0x153a,'native-sound-hole.bin')]:
  part=(O/name).read_bytes();assert base[off:off+len(part)]==bytes([255])*len(part);blob[off:off+len(part)]=part;reclaimed+=len(part)
 bindings={n:lab['BbNative'+n]for n in ['Tile23','Tile84']}
 bindings.update(Sound=lab['BbNativeSound'],EnemyDraw=lab['BbNativeEnemyDraw'])
 bindings.update({n:lab['BbNativeNoop']for n in['Score','LivesUI','Yield','EnemyRelease','StageBubbles']})
 for name,target in bindings.items():at=core['BbImport'+name]-0xa000;blob[at:at+3]=bytes([76,target&255,target>>8])
 vectors={0:'BbNativeUpdate',2:'BbNativeDraw',15:'BbNativeFresh',36:'BbNativeFresh'}
 for row,name in vectors.items():target=lab[name];blob[3*row:3*row+3]=bytes([76,target&255,target>>8])
 from prepare_bubble_bobble_helpers_1102_v1 import build as build_helpers
 helper=build_helpers(b,lab);helperrows={1:'BbHelperGraphics',17:'BbHelperPortrait',18:'BbHelperName',26:'BbHelperColors',30:'BbHelperName'}
 for row,name in helperrows.items():target=helper[name];blob[3*row:3*row+3]=bytes([76,target&255,target>>8])
 (O/'native-private.bin').write_bytes(blob)
 q=dict(passed=True,base_ROM_SHA256=PIN,core_SHA256=P.B.sha(base),private_image_SHA256=P.B.sha(blob),code_start=0xb540,code_end=lab['BbNativeEnd'],native_extension_bytes=len(host),source_declared_prefix_holes_reclaimed=reclaimed,native_leaf_bytes=len(host)+reclaimed,total_used_bytes=lab['BbNativeEnd']-0xa000,header_start=0xbfe0,contiguous_body_spare=0xbfe0-lab['BbNativeEnd'],physical_code_carriers_needed=(lab['BbNativeEnd']-0xa000+1023)//1024,additional_carriers_over_six=max(0,(lab['BbNativeEnd']-0xa000+1023)//1024-6),state_bytes=1024,public37rows_still_reject=True,actual_6502_import_bindings=bindings,exports=lab,ROM_written=False,physical_resources_granted=True,resident_resources_granted=False,remaining_model_boundaries=['Owner/authentication/shared admission, loader and actual Main/scene/new-life/retire routing','Actual native actor-birth, AI suppression and body-contact ingresses','Trapped native victim art and circle overlay orchestration','Sound/score/UI/stage imports'],scope='Independent linked image only. Whole update ordering, source cadence, signed camera transport for21actors, input/world/query/bounds, proxy capture/observe/restore/pop-credit/contact iteration, actor-birth invalidation, solid-head sweep, exactly-once death, initialization/retirement and bounded body/15-bubble drawing execute as6502. Shared ingress remains unwired and every public row still rejects. No ROM/shared routing/menu change.')
 q.update(public37rows_still_reject=False,native_service_vectors={row:dict(target=name,CPU=lab[name])for row,name in vectors.items()},all_other_native_rows_reject=True,shared_owner_admitted=False,branch_relaxation=dict(cases=relaxed,bytes_saved=3*len(relaxed),equivalence='Same6502condition and target; only inverse-branch-over-JMP becomes a directly reachable branch. No donor/core operation changed.'))
 q['native_service_vectors'].update({row:dict(target=name,CPU=helper[name],immutable_bank2_helper=True)for row,name in helperrows.items()})
 q['scope']='Independent linked8KB image. Whole update/camera/source/native adapter leaves execute as6502. Real private vectors0/2/15/36 are bound; all other33rows reject. Actual shared Hu/Main/scene/contact/birth/AI ingress and owner admission are absent. No ROM/shared routing/menu change.'
 (O/'native-leaves-layout.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:q[k]for k in ['passed','native_leaf_bytes','total_used_bytes','physical_code_carriers_needed','additional_carriers_over_six','ROM_written']}));print(json.dumps(dict(short_branches=len(relaxed),bytes_saved=3*len(relaxed),actual_private_vectors=list(vectors))))


if __name__=='__main__':main()
