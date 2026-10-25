"""Repair only the obsolete title-menu inputs in the retained beam fixture."""
from pathlib import Path
import argparse,hashlib,json,subprocess,sys
ROOT=Path(__file__).resolve().parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('--rom',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
 fixture=ROOT/'tests/samus-beam-rendering.lua';s=fixture.read_text();old=" emu.setInput({right=frame==80 or frame==100,start=frame==200,b=current and(age>=10 and age<14 or age>=30 and age<34),";assert s.count(old)==1
 s="local beamMenuPhase='options-focus'\nlocal morphTestPhase=0\n"+s
 s=s.replace(old,''' if frame<550 then
  local b={}
  if frame>=60 and frame%12==0 then
   if beamMenuPhase=='options-focus'then b.down=true;beamMenuPhase='options-open'
   elseif beamMenuPhase=='options-open'then b.a=true;beamMenuPhase='mode-focus'
   elseif beamMenuPhase=='mode-focus'then
    if r('CrossoverMenuState')==4 then
     if r('CrossoverOptionsFocus')~=1 then b.down=true
     elseif r('CrossoverBehaviorVersion')==0 then b.a=true;beamMenuPhase='back'
     else beamMenuPhase='back'end
    end
   elseif beamMenuPhase=='back'then b.b=true;beamMenuPhase='start'
   elseif beamMenuPhase=='start'then
    if r('CrossoverMenuState')==2 then beamMenuPhase='select'else b.start=true end
   elseif r('CrossoverMenuState')==2 then
    if r('CrossoverMenuIndex')~=2 then b.right=true else b.a=true end
   end
  end
  emu.setInput(b,0);return
 end
 emu.setInput({b=current and(age>=10 and age<14 or age>=30 and age<34),''')
 old='down=frame==1000 or(frame>=1003 and frame<1005)';assert s.count(old)==1
 s=s.replace(old,"down=frame>=1000 and(morphTestPhase==0 or morphTestPhase==2)")
 old=' emu.setInput({b=current';assert s.count(old)==1
 s=s.replace(old," if frame>=1000 then\n  if morphTestPhase==0 and r('SmCrouch')~=0 then morphTestPhase=1\n  elseif morphTestPhase==1 and(r('SmPreviousDirections')&4)==0 then morphTestPhase=2 end\n end\n"+old)
 assert s.count(' if frame==1010 then')==1;s=s.replace(' if frame==1010 then',' if frame==1030 then')
 old=' if frame<550 then return end';assert s.count(old)==1;s=s.replace(old,old+"\n if frame==550 then assert(r('SelectedCharacter')==2 and r('OperMode')==1 and r('GameEngineSubroutine')==8 and r('CrossoverBehaviorVersion')==1,'Actual cold menu entered live Hard Samus before arranging inventory beam/pickup cases')end")
 script=a.output/'bound.lua';script.write_text(s)
 z=subprocess.run([sys.executable,str(ROOT/'tools/audit/run_mesen_isolated.py'),'--output',str(a.output),str(script),str(a.rom.resolve()),'--timeout','90','--option=--nes.ramPowerOnState=AllZeros','--option=--nes.randomizeCpuPpuAlignment=false','--option=--nes.randomizeMapperPowerOnState=false'],capture_output=True,text=True,cwd=ROOT)
 (a.output/'host.log').write_text(z.stdout+z.stderr);q=dict(passed=z.returncode==0,ROM_sha256=sha(a.rom),original_fixture_sha256=sha(fixture),bound_fixture_sha256=sha(script),exit=z.returncode,assertions_removed=False,
  scope='Actual cold Hard/Samus selection and native-observed Down/release/Down edges replace obsolete title inputs, Easy-only setup and one-frame pulses. Private Morph Ball is a Hard inventory upgrade. All beam, physical collection and transformation assertions retained; observation ends at1030 rather than1010.')
 (a.output/'proof.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(q));return z.returncode
if __name__=='__main__':raise SystemExit(main())
