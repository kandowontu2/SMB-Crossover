"""Correct only the statue observer's native Y-page convention; no emulator."""
from pathlib import Path
import inspect,json,re
import current_smb3_powerups_prepare_v1 as prior
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location
from current_roster_compact_11_v1 import ROOT,sha,lua
ROM=ROOT/'build/roster-20261028-fixes.nes';EXPECTED='ee1152a49deae31e82d202159310fa3719cbcfd85de571fd1b9ac15a1cd2a7b3'
put=lambda p,z:p.write_text(json.dumps(z,indent=2)+'\n',newline='\n')
OLD=" local parts={};local x=r('R4')+256*r('R5');local y=r('R6')+256*r('R7');assert(x<256 and y<256,'Visible staged statue origin')"
NEW=""" local parts={};local x=r('R4')+256*r('R5');local rawY=r('R6')+256*r('R7');local y=rawY-256
 local originEvidence={stamp=stamp(),pointer=pointer,record_bank=bank(0xc000),raw_x_low=r('R4'),raw_x_high=r('R5'),raw_y_low=r('R6'),raw_y_high=r('R7'),raw_x=x,raw_y=rawY,screen_x=x,OAM_y=y,first_visible_line=y+1,origin_attr=r('R3'),logical_OAM=r('CurrentOAMOffset'),rotation=r('RgOamRotation'),physical_CHR=r('SmChrBank')+256*r('M3SpritePageHi')}
 assert(originRows<64,'Bounded64 statue-origin diagnostic rows');local line=json(originEvidence)..'\\n';assert(#line<2048,'Bounded origin diagnostic row');originLog:write(line);originLog:flush();originRows=originRows+1
 assert(r('R5')==0 and r('R7')==1 and x>=0 and x<256 and y>=0 and y<240,'Visible staged statue origin uses native Xpage0/Ypage1')"""

def main():
 assert sha(ROM)==EXPECTED;b=scoped_load(ROM);raw=ROM.read_bytes();parentfixture=ROOT/'tests/current-smb3-statue-supplement-v6.lua';original=parentfixture.read_text();text=original;changes=[]
 def change(before,after):
  nonlocal text
  assert text.count(before)==1;changes.append((before,after));text=text.replace(before,after)
 change(OLD,NEW)
 change("local csv=assert(io.open(OUTPUT..'components.csv','w'))","local originRows=0;local originLog=assert(io.open(OUTPUT..'statue-origin.jsonl','w'))\nlocal csv=assert(io.open(OUTPUT..'components.csv','w'))")
 change("  parts[#parts+1]={offset=", "  assert(x+dx>=0 and x+dx+8<=256 and y+dy>=0 and y+dy+16<=240,'Every original statue part fully visible before source-OAM proof')\n  parts[#parts+1]={offset=")
 change(" rec.body={update=updates,parts=parts,", " rec.body={origin=originEvidence,update=updates,parts=parts,")
 change("f:close();csv:close();emu.stop(0)","f:close();csv:close();originLog:close();emu.stop(0)")
 reversed_text=text
 for before,after in reversed(changes):assert reversed_text.count(after)==1;reversed_text=reversed_text.replace(after,before)
 assert reversed_text==original,'Exact v6 reversal: coordinate convention and bounded diagnostics only'
 guard='-- All callback registration is startup-static. No callback adds/removes callbacks.';end="hook('DmaComplete',function()\n if not imagePending"
 assert original[original.index(guard):original.index(end)]==text[text.index(guard):text.index(end)],'Literal v6 strict hardware guards unchanged'
 fixture=ROOT/'tests/current-smb3-statue-supplement-v7.lua';assert not fixture.exists();fixture.write_text(text,newline='\n')
 plan=json.loads((ROOT/'build/current-ee1152-mario3-statue-v6/config.json').read_text())['plan'];observed=[];pending={};meta=(address(b,'MetaspriteRenderLoop'),(location(b,'MetaspriteRenderLoop')-16)//8192);ready=(address(b,'RosterOamReady'),(location(b,'RosterOamReady')-16)//8192)
 def oracle(cpu,q,rec):
  if rec is None or rec['kind']!='statue' or not q.get(prior.N['Statue']):return
  pc=cpu.pc;k=q.m.banks[(pc-32768)//8192]if pc>=32768 else-1
  if(pc,k)==meta:
   ptr=q.get('R0')+256*q.get('R1');pose=q.get('SmPosePtr')+256*q.get('SmPosePtr',1)
   if ptr!=pose or q.get('M3RenderFrame')!=30:return
   name='M3Frame1E'+('Left'if q.get('PlayerFacingDir')==2 else'Right');at=location(b,name);ref=list(raw[at:at+17]);assert ptr==address(b,name)and q.m.banks[2]==91 and q.get('M3Poof')==0 and q.get('ObjectMetasprite')==233
   x=q.get('R4')+256*q.get('R5');rawy=q.get('R6')+256*q.get('R7');y=rawy-256
   assert q.get('R5')==0 and q.get('R7')==1 and 0<=x<256 and 0<=y<240
   assert not(x<256 and rawy<256),'Retain exact v6 false predicate on genuine visible page1'
   start=q.get('CurrentOAMOffset');rotation=q.get('RgOamRotation')if q.get('GuestOamRotationActive')else 0;parts=[]
   for j in range(4,0,-1):
    i=1+(j-1)*4;t,a,dy,dx=ref[i:i+4];dx=dx-256 if dx>=128 else dx;dy=dy-256 if dy>=128 else dy
    assert 0<=x+dx<=248 and 0<=y+dy<=224
    parts.append(dict(offset=(start+rotation+(4-j)*4)%256,x=x+dx,y=y+dy,tile=t,attr=(a|q.get('R3'))&0xf3))
   pending.clear();pending.update(age=rec['age'],x_low=q.get('R4'),x_high=q.get('R5'),y_low=q.get('R6'),y_high=q.get('R7'),rawY=rawy,screenY=y,parts=parts,record=ref,pointer=ptr)
  elif(pc,k)==ready and pending:
   for p in pending['parts']:assert list(q.m[512+p['offset']:516+p['offset']])==[p['y'],p['tile'],p['attr'],p['x']]
   observed.append(dict(pending));pending.clear()
 source=inspect.getsource(prior.campaign);assert source.count('        origin(cpu)')==1;source=source.replace('        origin(cpu)','        oracle(cpu,q,rec);origin(cpu)');env=dict(vars(prior));env.update(PLAN=plan,oracle=oracle);exec(compile(source,str(__file__)+'::real_source_coordinate_oracle','exec'),env)
 cases=[env['campaign'](b,1,var)for var in[0,1]];assert len(observed)>2 and all(c['records'][-1]['Defeat']==1 for c in cases)
 negative=ROOT/'build/current-ee1152-mario3-statue-v6/native';log=negative/'roster-20261028-fixes-run.log';assert'FAIL Visible staged statue origin'in log.read_text();assert not(negative/'result.json').exists()and not list(negative.glob('*.png'))
 proof=ROOT/'build/current_smb3_statue_supplement_v7_source.json';assert not proof.exists();put(proof,dict(passed=True,native_run=False,Lua_VM_executed=False,ROM_sha256=EXPECTED,source_cases=cases,actual_source_renderer_and_final_OAM_cases=observed,source_contract='Actual MetaspriteRenderLoop compares calculated Y high byte to1 in both positive/negative branches; screen OAM Y is low byte. Native raw v6 R4..R7 were not serialized: source observations are explicitly not invented native values.',negative=dict(log_sha256=sha(log),CSV_sha256=sha(negative/'components.csv'),last_serialized_source_update=228,next_native_body_origin_assertion=True,result_and_PNGs_absent=True),exact_reverse_normalized_v6=True,hardware_guards_literal_v6=True,scope='Only observer coordinate correction and before-assert raw coordinate/stamp diagnostics; actual genuine three earned cases and all source/DMA/CHR/delay/contact/caps remain. Stronger full-part visibility assertion. No game patch, no native launch.',bindings={str(p):sha(p)for p in[Path(__file__),fixture,parentfixture,ROM,ROM.with_suffix('.dbg'),ROM.with_suffix('.lbl'),ROOT/'src/metasprite_engine.s',ROOT/'tools/audit/current_smb3_powerups_prepare_v1.py',ROOT/'tools/audit/current_smb3_statue_supplement_prepare_v6.py',log,negative/'components.csv']}))
 outputs=[]
 for identity in['mario3','luigi3']:
  parent=ROOT/('build/current-ee1152-'+identity+'-statue-v6');rp=parent/'prepared-not-run.json';old=json.loads(rp.read_text());assert all(sha(Path(f['path']))==f['sha256']for f in old['bindings'])
  out=ROOT/('build/current-ee1152-'+identity+'-statue-v7');assert not out.exists();out.mkdir();cfg=json.loads((parent/'config.json').read_text());cfg['scope']+=' Additivev7 observer uses renderer Ypage1; bounded raw-coordinate diagnostics before assertions; v6 negative retained.'
  refs=set(re.findall(r"(?<![A-Za-z_])[rw]\('([A-Za-z_][A-Za-z_0-9:]*)'",text))|set(re.findall(r'\bC\.ram\.([A-Za-z_][A-Za-z_0-9]*)',text))
  for n in refs:cfg['ram'][n]=address(b,n)
  assert all(isinstance(cfg['ram'][n],int)for n in refs);put(out/'config.json',cfg)
  run=(parent/'run.lua').read_text();m=re.search(r'CURRENT_SMB3_POWERUPS=(\{.*\})\n',run);assert m;run=run[:m.start(1)]+lua(cfg)+run[m.end(1):];assert run.count(parentfixture.as_posix())==1;run=run.replace(parentfixture.as_posix(),fixture.as_posix());assert not re.search(r'\\u[0-9a-fA-F]{4}',run);(out/'run.lua').write_text(run,newline='\n')
  command=json.loads((parent/'command.json').read_text());command['argv']=[str(out/'native')if s==str(parent/'native')else str(out/'run.lua')if s==str(parent/'run.lua')else s for s in command['argv']];put(out/'command.json',command)
  paths={Path(f['path'])for f in old['bindings']if Path(f['path'])not in{parent/'run.lua',parent/'config.json',parent/'command.json'}};paths|={Path(__file__),fixture,proof,rp,log,negative/'components.csv'};paths|={out/n for n in['run.lua','config.json','command.json']}
  z=dict(old);z.update(scope=cfg['scope'],native_run=False,passed=False,parent_readiness_sha256=sha(rp),source_qualification='Fresh complete three-case Main+NMI both Hard variants plus actual renderer→published OAM page1 coordinate/parts proof; exactv6 false preserved. Lua VM not executed offline.',bindings=[dict(path=str(p.resolve()),bytes=p.stat().st_size,sha256=sha(p))for p in sorted(paths)]);put(out/'prepared-not-run.json',z);assert all(sha(Path(f['path']))==f['sha256']for f in z['bindings']);outputs.append(dict(identity=identity,ready=str(out/'prepared-not-run.json'),sha256=sha(out/'prepared-not-run.json'),bindings=len(paths),command=str(out/'command.json')))
 put(ROOT/'build/current_smb3_statue_supplement_v7_handoff.json',dict(native_run=False,proof=str(proof),proof_sha256=sha(proof),readies=outputs,owned_files=[str(Path(__file__)),str(fixture)]));print(json.dumps(outputs),flush=True)
if __name__=='__main__':main()
