"""Assemble selected Tank worker and exact native shoe/pickup publication."""
from pathlib import Path
import hashlib,json,re,subprocess,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location
from private_build_outputs_v1 import validate
O=R/'build/mario-tank-visible-host-1101-v5';P=R/'build/karnov-native-platform-1101-v1';V2=R/'build/mario-tank-host-1101-v2'
PIN='58e50db6ceead7c3706087c92d6e49014f05ff8b80b000be30c27b4e7dfa11f2'
REF=R/'tools/reference/mario_tank_visible_1101_v5.inc'
sha=lambda b:hashlib.sha256(b).hexdigest()
def compact():
 h=(R/'tools/reference/mario_tank_host_1101_v2.inc').read_text();t=(R/'tools/reference/mario_tank_terrain_1101_v2.inc').read_text()
 h=re.sub(r'MtHostSelected:\n.*?(?=MtHostBooted:)', '',h,flags=re.S)
 h=h.replace(' jsr MtHostSelected\n bcc MtHostNo\n','')
 h=h.replace(' beq MtHostYes\n clc\n rts',' beq MtHostYes\n clc\n rts\nMtHostYes:sec\n rts',1)
 for branch,owner in [('Contact','S2BoundaryImmunity'),('Injury','CmHostMarioInjury'),('Movement','BmMarioMovement'),('Powerup','MarioSourceBeginPowerup'),('Growth','MarioSourcePowerupUpdate')]:
  h=h.replace(' jsr MtHostSelected\n bcc MtHost'+branch+'Legacy\n','')
  clause='MtHost'+branch+'Legacy:\n pla\n plp\n MtHostFar '+owner+'\n rts\n';assert clause in h;h=h.replace(clause,'')
 t=t.replace(' php\n pha\n jsr MtHostSelected\n bcc MtTerrainOtherSide\n pla\n plp\n','')
 t=re.sub(r'MtTerrainOtherSide:\n.*?(?=; A=the actual native)', '',t,flags=re.S)
 return h+t
def labels(p):return {q[2][1:]:int(q[1],16)for line in p.read_text().splitlines()if len(q:=line.split())==3}
def main():
 O.mkdir(exist_ok=True);b=scoped_load(P/'candidate.nes');assert sha(b['raw'])==PIN
 text=compact()+REF.read_text();targets=sorted(set(re.findall(r'MtHostFar (\w+)',text)));defined=set(re.findall(r'(?m)^(\w+):',text))|{'MtShoeLookupV5','MtShoeRecordsV5'}
 names=[]
 for line in text.splitlines():
  if line.startswith('.import '):names+=line[8:].split(',')
 names+=['Sprite_Data','FrameCounter','CurrentBankC','CurrentOAMOffset','ObjectMetasprite','ObjectVerticalFlip','Player_SprAttrib','ScreenLeft_X_Pos','ScreenLeft_PageLoc','Player_Y_Position','Player_Y_HighPos','PlayerFacingDir']
 fixtures=dict(MtTerrainSave=0xa880,MtTerrainY=0xa888,MtTerrainA=0xa889,MtRemovedTile=0xa88a,MtTerrainHeadMode=0xa88b)
 names=sorted(set(names+targets+['SafecallA_SMC','FarcallJmpTarget_SMC','FarCallCommon'])-defined-set(fixtures)-{'MtHostSelected'})
 bind=''.join(f'{n}=${address(b,n):04x}\n'for n in names)+''.join(f'{n}=${v:04x}\n'for n,v in fixtures.items())
 bind+=''.join(f'{n}_BANK={128|((location(b,n)-16)//8192)}\n'for n in targets)
 macro='''.macro MtHostFar Target
 sta SafecallA_SMC+1
 lda #<Target
 sta FarcallJmpTarget_SMC+1
 lda #>Target
 sta FarcallJmpTarget_SMC+2
 lda #.ident(.concat(.string(Target),"_BANK"))
 jsr FarCallCommon
.endmacro
'''
 q=json.loads((V2/'shoe-mask-candidate.json').read_text());rows=[];lookup=[]
 for rec in q['records']:
  v=[]
  for i,p in enumerate(rec['parts']):v.extend([p['mask']|((p['hardware_flip']>>1)&0x60)|(0x80 if i==len(rec['parts'])-1 else 0),p['x']&255,p['y']&255])
  v=bytes(v)
  if v not in rows:rows.append(v)
  lookup.append(sum(map(len,rows[:rows.index(v)])))
 packed=bytes(lookup)+b''.join(rows);assert len(rows)==28 and len(packed)==224
 source='.setcpu "6502"\n.macpack longbranch\n'+bind+macro+re.sub(r'(?m)^\.(?:import|export) .+\n','',text)
 source+='\n.segment "MT_METADATA"\nMtShoeLookupV5:\n.byte '+','.join(map(str,lookup))+'\nMtShoeRecordsV5:\n.byte '+','.join(map(str,b''.join(rows)))+'\n'
 exports=['MtHostBooted','MtHostContact','MtHostInjury','MtHostMovement','MtHostBeginPowerup','MtHostGrowthUpdate','MtTerrainHeadProbe','MtTerrainSideProbe','MtTerrainDestroyCell','MtTerrainTileChecks','MtHostEnd','MtTerrainEnd','MtArtPostV5','MtArtPostEndV5','MtShoeLookupV5','MtShoeRecordsV5']
 source+='\n.export '+','.join(exports)+'\n'
 (O/'visible.s').write_text(source)
 (O/'visible.cfg').write_text('MEMORY { WORK:start=$b600,size=$320,type=ro,file="'+(O/'worker.bin').as_posix()+'"; META:start=$b920,size=$e0,type=ro,file="'+(O/'metadata.bin').as_posix()+'"; VISIBLE:start=$bca0,size=$160,type=ro,file="'+(O/'visible.bin').as_posix()+'"; } SEGMENTS { MT_HOST:load=WORK,type=ro; MT_TERRAIN:load=WORK,type=ro; MT_METADATA:load=META,type=ro; MT_VISIBLE:load=VISIBLE,type=ro; }\n')
 cc=R/'tools/Windows/cc65/bin';commands=[]
 for cmd in [[str(cc/'ca65.exe'),'-g','-o',str(O/'visible.o'),str(O/'visible.s')],[str(cc/'ld65.exe'),'-C',str(O/'visible.cfg'),'-o',str(O/'unused.bin'),'-Ln',str(O/'visible.lbl'),str(O/'visible.o')]]:
  guard=validate(cmd,O,cwd=R);p=subprocess.run(cmd,cwd=R,capture_output=True,text=True);commands.append(dict(command=cmd,guard=guard,returncode=p.returncode,stderr=p.stderr));assert not p.returncode,p.stderr
 worker=(O/'worker.bin').read_bytes();visible=(O/'visible.bin').read_bytes();metadata=(O/'metadata.bin').read_bytes();assert metadata==packed
 page501=worker+bytes([255])*(800-len(worker))+packed
 art=(V2/'shoe-mask-candidate.chr').read_bytes()+(R/'build/mario-tank-source-1101-v1/boots-pickup.chr').read_bytes();assert len(art)==672
 page502=art+visible+bytes([255])*(352-len(visible))
 (O/'code501.bin').write_bytes(page501);(O/'art-code502.bin').write_bytes(page502)
 result=dict(passed=True,current_ROM_sha256=PIN,selected_only_worker_bytes=len(worker),prior_worker_bytes=908,saved_worker_bytes=908-len(worker),metadata_bytes=len(packed),unique_metadata_records=len(rows),shoe_pose_faces=56,visible_worker_bytes=len(visible),carriers=[501,502],conditional_RAM2=dict(context=[0x880,0x88c],worker=[0x1600,0x1e00],lease_granted=False),loader_requires_two_rows=True,owning_link=False,installed=False,commands=commands,source_bindings={str(p.relative_to(R)):sha(p.read_bytes())for p in[REF,Path(__file__),R/'tools/reference/mario_tank_host_1101_v2.inc',R/'tools/reference/mario_tank_terrain_1101_v2.inc']})
 (O/'assembly.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items()if k not in['commands','source_bindings']}))
if __name__=='__main__':main()
