"""Earn Super/Tanooki; bind stone-body render, full DMA and delayed display.

Preparation only. Original v5 mechanics/results/pictures remain immutable.
"""
from pathlib import Path
import copy,inspect,json,re
import current_smb3_powerups_prepare_v1 as prior
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location
from current_roster_compact_11_v1 import ROOT,sha,lua
ROM=ROOT/'build/roster-20261028-fixes.nes';EXPECTED='ee1152a49deae31e82d202159310fa3719cbcfd85de571fd1b9ac15a1cd2a7b3'
put=lambda p,z:p.write_text(json.dumps(z,indent=2)+'\n',newline='\n')

EXTRA=r'''
local function stamp()
 local s=emu.getState();return{wall=wall,update=updates,ppu_frame=s['ppu.frameCount'],line=s['ppu.scanline'],dot=s['ppu.cycle'],cpu=s['cpu.cycleCount'],DMA=dmas}
end
local function liveBody(source,b)
 for _,p in ipairs(b.parts)do
  local i=p.offset+1
  assert(source[i]==p.y and source[i+1]==p.tile and(source[i+2]&0xe3)==p.attr and source[i+3]==p.x,'Every real stone-body part in exact physical OAM slot')
 end
end
local function hardware()
 local o,p,c={},{},{};local s=emu.getState()
 for i=0,255 do o[i+1]=emu.read(i,emu.memType.nesSpriteRam)end
 for i=0,31 do p[i+1]=emu.read(0x3f00+i,emu.memType.nesPpuDebug)end
 for i=0,11 do c[i+1]=s['mapper.chrBanks'..i]end
 return{OAM=o,palette=p,CHR=c,stamp=stamp()}
end
hook('StatueBodyRenderer',function(s)
 if not entered or not rec or phase~='statue'or nr('Statue')==0 or r('M3RenderFrame')~=C.statue_frame then return end
 local pointer=r('R0')+256*r('R1');if pointer~=r('SmPosePtr')+256*r('SmPosePtr',1)then return end
 local ref=assert(C.statue_records[tostring(r('PlayerFacingDir'))]);if pointer~=ref.pointer then return end
 assert(bank(0xc000)==ref.bank and r('ObjectMetasprite')==233 and r('M3Poof')==0,'Real stable statue descriptor owner')
 for i,v in ipairs(ref.bytes)do assert(emu.read(pointer+i-1,emu.memType.nesDebug)==v,'Exact compiled original statue descriptor')end
 assert(r('SmChrBank')+256*r('M3SpritePageHi')==529 and ref.bytes[1]==16,'Four original stone parts on physicalCHR529')
 local parts={};local x=r('R4')+256*r('R5');local y=r('R6')+256*r('R7');assert(x<256 and y<256,'Visible staged statue origin')
 local start=r('CurrentOAMOffset');local rotation=r('GuestOamRotationActive')~=0 and r('RgOamRotation')or 0
 for j=4,1,-1 do local i=2+(j-1)*4;local dx=ref.bytes[i+3];if dx>=128 then dx=dx-256 end;local dy=ref.bytes[i+2];if dy>=128 then dy=dy-256 end
  parts[#parts+1]={offset=(start+rotation+(4-j)*4)%256,y=(y+dy)%256,tile=ref.bytes[i],attr=ref.bytes[i+1]&0xe3,x=(x+dx)%256}
 end
 rec.body={update=updates,parts=parts,pointer=pointer,record_bank=ref.bank,physical_CHR=529,render_stamp=stamp(),native_frame=nr('Frame'),render_frame=r('M3RenderFrame'),poof=r('M3Poof')}
end)
'''
ROSTER=r'''hook('RosterReady',function()
 if entered and rec then
  rec.roster_update=updates
  if phase=='statue'and rec.body and rec.body.update==updates then
   local body=rec.body;body.source={};for i=0,255 do body.source[i+1]=emu.read(0x200+i,emu.memType.nesDebug)end
   liveBody(body.source,body);body.publication_stamp=stamp()
  end
 end
end)'''
PICTURE=r'''hook('DmaComplete',function()
 if not imagePending then return end
 local a=imagePending;local body=rec and rec.body
 if not(body and body.source and body.update==updates and rec.target and(rec.Defeat or 0)>0 and nr('Statue')>0 and r('M3Poof')==0)then return end
 local h=hardware();local yes=true
 for i=1,256 do local want=body.source[i];if(i-1)%4==2 then want=want&0xe3 end;if h.OAM[i]~=want then yes=false end end
 if not yes then return end
 liveBody(h.OAM,body);assert(h.CHR[1]==529,'Actual committed stone-body physicalCHR529')
 for i,v in ipairs(C.statue_chr)do assert(emu.read(529*1024+i-1,emu.memType.nesChrRom)==v,'Actual unchanged original statue CHR bytes')end
 if not a.armed then a.armed={body=body,hardware=h,completed_frames={}};a.verified_DMAs=0 end
 a.verified_DMAs=a.verified_DMAs+1;a.latest={body=body,hardware=h}
end)'''
TAKE=r''' if imagePending and imagePending.armed then
  local a=imagePending;local mark=stamp();local armed=a.armed;local h=hardware()
  if #armed.completed_frames<4 then armed.completed_frames[#armed.completed_frames+1]=mark end
  -- takeScreenshot at the immediate callback may still expose an older
  -- completed image. Wait beyond TWO endFrame epochs following the first
  -- verified stone-body DMA, while requiring a later verified body DMA.
  if a.verified_DMAs>=2 and mark.ppu_frame>armed.hardware.stamp.ppu_frame+1 and nr('Statue')>0 and r('M3Poof')==0 then
   local body=a.latest.body;local same=true;for i=1,256 do if h.OAM[i]~=a.latest.hardware.OAM[i]then same=false end end
   assert(same and h.CHR[1]==529,'Delayed complete display retains the verified hardware body image and CHR')
   liveBody(h.OAM,body);assert(rec.target and(rec.Defeat or 0)==1,'Actual staged source-protected contact/defeat before statue image')
   local f=assert(io.open(OUTPUT..a.name,'wb'));f:write(emu.takeScreenshot());f:close();images=images+1
   assert(images<=8,'At most8 meaningful whole-frame PNGs')
   rec.pictured={wall=wall,update=body.update,DMA=dmas,form=r('M3Form')};rec.statue_display_evidence={first=armed,latest=a.latest,capture=h,verified_body_DMAs=a.verified_DMAs,actual_defeats=rec.Defeat,delay='Two complete PPU frame epochs after first verified stone-body DMA; no screenshot timing equivalence claim before actual native stamps/pixels are reviewed.'}
   imagePending=nil
  end
 end
'''

def main():
 assert sha(ROM)==EXPECTED;b=scoped_load(ROM);raw=ROM.read_bytes();oldfixture=ROOT/'tests/current-smb3-powerups-v5.lua';text=oldfixture.read_text()
 marker='local function mainImage()';assert text.count(marker)==1;text=text.replace(marker,EXTRA+'\n'+marker)
 old="hook('RosterReady',function()if entered and rec then rec.roster_update=updates end end)";assert text.count(old)==1;text=text.replace(old,ROSTER)
 # Helpers must be lexically visible to the earlier RosterReady closure.
 a=text.index(EXTRA);text=text[:a]+text[a+len(EXTRA)+1:];before=text.index(ROSTER);text=text[:before]+EXTRA+'\n'+text[before:]
 old="(phase=='statue'and nr('Statue')~=0 and rec.protected and r('M3Poof')==0 and nr('Frame')==C.statue_frame)"
 new="(phase=='statue'and nr('Statue')~=0 and rec.target and(rec.Defeat or 0)==1 and rec.body and rec.body.source and rec.body.update==updates and r('M3Poof')==0 and nr('Frame')==C.statue_frame)";assert text.count(old)==1;text=text.replace(old,new)
 old="elseif phase=='statue'then finish=rec.statue and rec.protected and nr('Statue')==0 and quiet()and age>=100";new="elseif phase=='statue'then finish=rec.statue and rec.target and(rec.Defeat or 0)==1 and nr('Statue')==0 and quiet()and age>=100";assert text.count(old)==1;text=text.replace(old,new)
 before="hook('DmaComplete',function()\n if not imagePending";start=text.index(before);end=text.index('emu.addEventCallback(function()',start);original_picture=text[start:end];text=text[:start]+PICTURE+'\n'+text[end:]
 shot=" if screenshot then assert(images<8,'At most8 meaningful whole-frame PNGs');local f=assert(io.open(OUTPUT..screenshot,'wb'));f:write(emu.takeScreenshot());f:close();images=images+1;screenshot=nil end";assert text.count(shot)==1;text=text.replace(shot,shot+'\n'+TAKE)
 for old in["  rec[name]=(rec[name]or 0)+1"]:
  assert text.count(old)==1;text=text.replace(old,old+"\n  if name=='Defeat'and phase=='statue'then assert(rec.target and nr('Statue')>0 and r('M3Poof')==0 and r('GuestInvulTicks')==0 and r('Enemy_ID',0)==6 and r('Enemy_Flag',0)~=0,'Real source statue defeats its actual staged target without invulnerability seed')end")
 marker='-- All callback registration is startup-static. No callback adds/removes callbacks.'
 assert oldfixture.read_text()[oldfixture.read_text().index(marker):oldfixture.read_text().index(before)]==text[text.index(marker):text.index(before.split('\n')[0],text.index(marker)) if False else text.index(PICTURE)],'Literal original hardware guards retained'
 fixture=ROOT/'tests/current-smb3-statue-supplement-v6.lua';assert not fixture.exists();fixture.write_text(text,newline='\n')
 plan=[dict(name='real-super-mushroom',kind='pickup',form=0,to=1),dict(name='real-tanooki-suit',kind='pickup',form=1,to=5),dict(name='tanooki-statue-real-protected-contact-release',kind='statue',form=5,picture='01-stone-statue.png')]
 source=inspect.getsource(prior.campaign);env=dict(vars(prior));env['PLAN']=plan;exec(compile(source,str(__file__)+'::three_real_earned_cases','exec'),env);cases=[env['campaign'](b,1,var)for var in[0,1]]
 assert all(c['records'][-1]['Defeat']==1 for c in cases)
 original=Path('C:/NES/Super Mario Bros. 3 (USA) (Rev 1).nes');orig=original.read_bytes();base=16+orig[4]*16384;chrdata=raw[16+128*8192+529*1024:16+128*8192+530*1024];assert chrdata==orig[base+65*1024:base+66*1024]
 proof=ROOT/'build/current_smb3_statue_supplement_v6_source.json';assert not proof.exists();put(proof,dict(passed=True,native_run=False,Lua_VM_executed=False,ROM_sha256=EXPECTED,cases=cases,scope='Three genuine physically earned Super/Tanooki/real statue target-defeat/release cases in each Hard variant, actual complete Main+NMI. No acquired form/private controller/timers/RNG/resources/outcomes seeded. CPU cannot qualify actual screenshot timing. Original exact hardware guard body retained.',original_CHR65_equals_current_physical529=True,original_ROM_sha256=sha(original),source_chronology=str(ROOT/'build/current_smb3_statue_picture_review_v1.json'),source_chronology_sha256=sha(ROOT/'build/current_smb3_statue_picture_review_v1.json'),new_picture_contract='Actual descriptor owner/16-byte header/four physical source OAM parts, identical committed256DMA and original1024CHR bytes, actual target Defeat exactly1; wait2 PPU frame epochs after first verified body DMA and require a later verified body DMA. Capture full hardware256/CHR/palette/stamps once with result; native run/pixels unqualified.',bindings={str(p):sha(p)for p in[Path(__file__),fixture,oldfixture,ROM,ROM.with_suffix('.dbg'),ROM.with_suffix('.lbl'),original,ROOT/'tools/audit/current_smb3_powerups_prepare_v1.py',ROOT/'tools/audit/current_smb3_statue_picture_review_v1.py']}))
 outputs=[]
 for identity,var in[('mario3',0),('luigi3',1)]:
  parent=ROOT/('build/current-ee1152-'+identity+'-hard-items-v5');rp=parent/'prepared-not-run.json';old=json.loads(rp.read_text());assert all(sha(Path(f['path']))==f['sha256']for f in old['bindings'])
  out=ROOT/('build/current-ee1152-'+identity+'-statue-v6');assert not out.exists();out.mkdir();cfg=json.loads((parent/'config.json').read_text());cfg['plan']=plan;cfg['scope']='Physically earned Super and Tanooki, genuine statue target defeat and release, source descriptor/full256DMA/originalCHR and delayed complete-display evidence. Typed mature source-classified actors and flat terrain; no natural reveal/RNG acquisition claim or seeded forms/resources. Native picture reviewed separately.'
  cfg['statue_records']={}
  for face,suffix in[('1','Right'),('2','Left')]:
   n='M3Frame1E'+suffix;at=location(b,n);cfg['statue_records'][face]=dict(pointer=address(b,n),bank=(at-16)//8192,bytes=list(raw[at:at+17]))
  cfg['statue_chr']=list(chrdata);n='MetaspriteRenderLoop';at=location(b,n);cfg['hooks']['StatueBodyRenderer']=dict(pc=address(b,n),banks=[(at-16)//8192],bytes=list(raw[at:at+3]),source_symbol=n,source_delta=0)
  refs=set(re.findall(r"(?<![A-Za-z_])[rw]\('([A-Za-z_][A-Za-z_0-9:]*)'",text))|set(re.findall(r'\bC\.ram\.([A-Za-z_][A-Za-z_0-9]*)',text))
  for n in refs:cfg['ram'][n]=address(b,n)
  assert all(isinstance(cfg['ram'][n],int)for n in refs);put(out/'config.json',cfg)
  run=(parent/'run.lua').read_text();m=re.search(r'CURRENT_SMB3_POWERUPS=(\{.*\})\n',run);assert m;run=run[:m.start(1)]+lua(cfg)+run[m.end(1):];assert run.count(oldfixture.as_posix())==1;run=run.replace(oldfixture.as_posix(),fixture.as_posix());assert not re.search(r'\\u[0-9a-fA-F]{4}',run);(out/'run.lua').write_text(run,newline='\n')
  command=json.loads((parent/'command.json').read_text());command['argv']=[str(out/'native')if s==str(parent/'native')else str(out/'run.lua')if s==str(parent/'run.lua')else s for s in command['argv']];put(out/'command.json',command)
  paths={Path(f['path'])for f in old['bindings']if Path(f['path'])not in{parent/'run.lua',parent/'config.json',parent/'source-controls.json',parent/'command.json'}};paths|={Path(__file__),fixture,proof,original,rp,ROOT/'build/current_smb3_statue_picture_review_v1.json'};paths|={out/n for n in['run.lua','config.json','command.json']}
  z=dict(old);z.update(scope=cfg['scope'],native_run=False,passed=False,source_qualification='Two fresh Hard variants,3 earned cases each; exact originalCHR65/current529, actual source chronology. Lua VM not executed offline; image timing/new native evidence remains unrun.',parent_readiness_sha256=sha(rp),bindings=[dict(path=str(p.resolve()),bytes=p.stat().st_size,sha256=sha(p))for p in sorted(paths)],picture_evidence_fields='Result record includes actual renderer/publication/frame/DMA stamps, source256+physical256,12CHR latches and32 palette bytes. No extra frame files or raw ROM copies.');put(out/'prepared-not-run.json',z);assert all(sha(Path(f['path']))==f['sha256']for f in z['bindings']);outputs.append(dict(identity=identity,ready=str(out/'prepared-not-run.json'),sha256=sha(out/'prepared-not-run.json'),command=str(out/'command.json'),bindings=len(paths)))
 put(ROOT/'build/current_smb3_statue_supplement_v6_handoff.json',dict(native_run=False,source=str(proof),source_sha256=sha(proof),readies=outputs,owned=[str(Path(__file__)),str(fixture)]));print(json.dumps(outputs),flush=True)
if __name__=='__main__':main()
