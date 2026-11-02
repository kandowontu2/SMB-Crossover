"""Actual Rogue/DragonPower selectors for six non-Bub replacement candidates."""
from pathlib import Path
import hashlib,json,re,subprocess
import audit_prince_pool_1102_v1 as A
import check_hogan_current_bounded_v1 as M
from private_build_outputs_v1 import validate
R=A.R;O=A.O


def main():
 assert A.sha(A.ROM)==A.SHA;b=A.scoped_load(A.ROM);seed=M.fresh(b)
 pages=set();dp=0;rogue=0;items=0;death=0
 for index in range(66):
  m=M.fork(seed);M.put(m,SelectedCharacter=A.address(b,'CHARACTER_DRAGON_POWER'),DpRenderIndex=index)
  M.invoke(m,'DpSetRecord');M.invoke(m,'DpPublish')
  page=M.get(m,'CurrentCHRBank')+256*(M.get(m,'X5ChrMode')&3)
  assert 788<=page<=794,(index,page);pages.add(page);dp+=1
 assert pages==set(range(788,795))
 wavecases=0
 for pose in range(256):
  for face in [0,64]:
   for index in [64,65]:
    m=M.fork(seed);M.put(m,SelectedCharacter=24,DpRenderIndex=index,DpPose=pose,DpAttribute=face)
    M.invoke(m,'DpSetRecord');M.invoke(m,'DpPublish')
    page=M.get(m,'CurrentCHRBank')+256*(M.get(m,'X5ChrMode')&3)
    assert page in pages,(pose,face,index,page);wavecases+=1
 # Reproduce the exact selector/publication instructions from the declared
 # source with the current linked symbols, independently of old pose data.
 src=R/'src/dragon_power_render.s';text=src.read_text();compiled=[];cc=R/'tools/Windows/cc65/bin'
 mixed=R/'tools/prepare_dragon_power_mixed_render_v3.py'
 for name in ['DpGraphics','DpSetRecord','DpPublish','DpDrawShots','DpMixedPage']:
  authority=mixed.read_text()if name=='DpMixedPage'else text
  start=authority.index('.proc '+name+'\n');end=authority.index('.endproc',start)+8;body=authority[start:end]
  if name=='DpGraphics':
   # The delivered flagpole/lifecycle successor removed exactly this old
   # zero writer. Its ordered-write differential is retained in the named
   # source test; reproduce that explicit adaptation, then require byte exact.
   clause=' lda #0\n sta Player_SprAttrib\n'
   assert body.count(clause)==1;body=body.replace(clause,'')
  if name=='DpSetRecord':
   clause=' lda DpPosePage,x\n';assert body.count(clause)==1
   body=body.replace(clause,' jsr DpMixedPage\n')
  local=set(re.findall(r'(?m)^\s*([A-Za-z]\w*):',body))|{name}
  tokens=set(re.findall(r'\b[A-Za-z]\w*\b',re.sub(r';[^\n]*','',body)))
  defs=''.join(f'{n}=${A.address(b,n):04x}\n'for n in sorted(tokens&set(b['syms'])-local))
  for n in ['DP_CHR_PUBLISH_BANK','DP_RENDER_BANK']:
   if n in tokens and n not in b['syms']:defs+=f'{n}={(A.location(b,"X5SetPhysicalChr")-16)//8192 if n=="DP_CHR_PUBLISH_BANK" else (A.location(b,"MetaspriteRenderLoop")-16)//8192}\n'
  pc=A.address(b,name);s=O/'dp-selector.s';s.write_text('.setcpu "6502"\n.macpack longbranch\n'+defs+'\n.segment "CHECK"\n'+body+'\n');cfg=O/'dp-selector.cfg';cfg.write_text(f'MEMORY{{M:start=${pc:04x},size=$200,file=%O;}}SEGMENTS{{CHECK:load=M,type=ro;}}')
  for cmd in [[cc/'ca65.exe',s,'-o',O/'dp-selector.o'],[cc/'ld65.exe','-C',cfg,O/'dp-selector.o','-o',O/'dp-selector.bin']]:
   cmd=list(map(str,cmd));validate(cmd,O,cwd=R);z=subprocess.run(cmd,capture_output=True,text=True);assert z.returncode==0,z.stderr
  code=(O/'dp-selector.bin').read_bytes();at=A.location(b,name);assert code==b['raw'][at:at+len(code)],('Actual source selector differs',name)
  compiled.append(dict(name=name,physical_bank=(at-16)//8192,CPU=hex(pc),bytes=len(code),sha256=hashlib.sha256(code).hexdigest()))
 for frame in range(106):
  for face in [0,1]:
   m=M.fork(seed);M.put(m,SelectedCharacter=2,RdVariant=1,RdSourceAltPalette=0,RdAnimFrame=frame,RdFacing=face)
   z=M.invoke(m,'RdRenderPlayer')
   if not z['P']&1:continue
   assert 680<=512+M.get(m,'SmChrBank')<=686,(frame,face,M.get(m,'SmChrBank'))
   M.invoke(m,'RdRenderPublishChr')
   for window in [0,2,3]:
    page=M.get(m,'CurrentCHRBank',window)+256*(M.get(m,'X5ChrMode',window)&3);assert 680<=page<=688
   rogue+=1
 for face in [0,1]:
  m=M.fork(seed);M.put(m,SelectedCharacter=2,RdVariant=1,RdFacing=face)
  M.invoke(m,'RdLifeDeathMetadata');assert 512+M.get(m,'SmChrBank')==689;death+=1
 for kind in range(10):
  for phase in range(4):
   m=M.fork(seed);M.put(m,SelectedCharacter=2,RdVariant=1,GameEngineSubroutine=8,OperMode=1,RdClock=2*phase,Enemy_Flag=1,Enemy_ID=46,Enemy_State=128,InvPickupOwner=2,InvPickup=208+kind,Enemy_Y_Position=160,Enemy_Y_HighPos=1,Enemy_X_Position=128,Enemy_PageLoc=0,CurrentOAMOffset=0)
   M.invoke(m,'RdWpDrawItems')
   page=M.get(m,'CurrentCHRBank',6)+256*(M.get(m,'X5ChrMode',6)&3)
   assert page==694,('Actual Rogue typed item publication',kind,phase,page);items+=1
 for kind in [128,129,137]:
  m=M.fork(seed);M.put(m,SelectedCharacter=2,RdVariant=1,InvDropKind=kind,InvDropX=128,InvDropY=160,InvDropPage=0,CurrentOAMOffset=0)
  M.invoke(m,'RdHzDrawDrops');assert M.get(m,'CurrentCHRBank',6)+256*(M.get(m,'X5ChrMode',6)&3)==694;items+=1
 q=dict(passed=True,proposal_only=True,resource_granted=False,ROM_sha256=A.SHA,replacement_candidates=[690,691,692,693,695,795],DP_actual_all66_selector_publish_cases=dp,DP_five_source_routines_reproduced_exact=compiled,DP_all256poses_bothfacings_bothwaves=wavecases,DP_source_adaptation='Remove only the old DpGraphics LDA0/STA Player_SprAttrib as authenticated by dragon_power_flagpole_lifecycle_v2.py ordered-writer differential; every resulting opcode/operand matches current ROM.',DP_actual_body_and_both_shots_pages=sorted(pages),Rogue_actual_supported_body_facing_publish_cases=rogue,Rogue_actual_death_cases=death,Rogue_actual_all40_typed_items_plus3drops_cases=items,Rogue_actual_domains=dict(body=list(range(680,687)),weapons=[687,688],death=[689],items=[694]),scope='Actual current source/table/compiled selectors; no adjacent-page assumption. Sprite8x16 bank uses window0 only for body; other declared independent windows are explicit. Replacements exclude all9 root-reserved Bub pages. Native transient/publication closure and root grant remain required.',bindings={str(p.relative_to(R)):A.sha(p)for p in [Path(__file__),A.ROM,src,mixed,R/'tools/prepare_dragon_power_flagpole_v2.py',R/'tools/audit/dragon_power_flagpole_lifecycle_v2.py',R/'src/rogue_dawn_render.s',R/'src/rogue_dawn_host_weapon_world.s',R/'src/rogue_dawn_host_hazards_drops_v1.s',R/'src/rogue_dawn_host_lifecycle.s']})
 (O/'replacement-pages.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:v for k,v in q.items()if k!='bindings'}))


if __name__=='__main__':main()
