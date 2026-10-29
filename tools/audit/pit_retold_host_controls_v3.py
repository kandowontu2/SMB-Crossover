"""Correct true NES Select fixtures; retain all previous source/native negatives."""
from pathlib import Path
import argparse,json,sys,types
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
from sunny_integrated_controls_v1 import *
import pit_retold_host_controls_v1 as H
O=R/'build/pit-retold-host-v3';H.O=O

def full_input():
 old,new=[scoped_load(p/'candidate.nes')for p in[R/'build/pit-retold-host-v2',O]]
 assert address(new,'Select_Button')==32 and address(new,'Down_Dir')==4
 rows=[]
 # The exact original failure: true Select at the complete SelectInput caller
 # leaves variant0 in v2. New version toggles0/1 while staying on Pit slot6.
 for b in[old,new]:
  q=H.C.setup(b,6);q.put(CrossoverMenuState=2,CrossoverMenuIndex=6,CrossoverMenuButtons=0,SavedJoypad2Bits=0)
  q.m[0x5fe0]=0
  for held in[32,32,0,32,0,32]:
   prior=q.m[0x5fe0];q.put(SavedJoypad1Bits=held)
   c,tr,mn=H.C.M.runtrace(q,'CrossoverMenuInput')
   if b is old:assert q.m[0x5fe0]==0
   rows.append([b is new,held,prior,q.m[0x5fe0],q.get('SelectedCharacter'),q.get('CrossoverMenuIndex'),q.get('CrossoverMenuState'),mn])
   q.put(NmiDisable=0);H.T.nmi(q,c);q.put(NmiDisable=255)
  if b is new:assert q.m[0x5fe0]==1 and q.get('SelectedCharacter')==6 and q.get('CrossoverMenuIndex')==6 and q.get('CrossoverMenuState')==2
 # Actual Down must navigate normally, never toggle the Pit alternate.
 parent=scoped_load(H.P/'candidate.nes');down=[]
 for variant in[0,1]:
  pair=[]
  for b in[parent,new]:
   q=H.C.setup(b,6);q.put(CrossoverMenuState=2,CrossoverMenuIndex=6,CrossoverMenuButtons=0,SavedJoypad1Bits=4,SavedJoypad2Bits=0)
   q.m[0x5fe0]=variant;c,tr,mn=H.C.M.runtrace(q,'CrossoverMenuInput')
   assert q.m[0x5fe0]==variant
   pair.append((registers(c),H.C.M.fastapp(q),bytes(q.m[0x100:0x200]),tuple(q.m.banks),[(at,v)for at,v in q.m.writes if not 0x100<=at<0x200]))
   down.append([variant,b is new,q.get('SelectedCharacter'),q.get('CrossoverMenuIndex'),q.get('CrossoverMenuState')])
  # Different wrapper call frames have been consumed. Require actual caller
  # AXYP/SP, every application/mapper/5SMC write and final banks, not dead cells.
  assert pair[0][0:2]==pair[1][0:2] and pair[0][3:]==pair[1][3:]
 return dict(passed=True,true_Select32_complete_input_rows=rows,Down4_complete_input_rows=down,frozen_v2_true_Select_failure_reproduced=True)

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--phase',choices=['core','gameplay'],required=True);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args();assert not a.output.exists()
 # Explicit fixture corrections only: add real Select to the navigation
 # matrix; leave Down4 as an independent foreign-navigation control. The
 # renderer, ABI, IRQ, palette and complete gameplay assertions stay literal.
 path=R/('tools/audit/pit_retold_host_controls_v1.py'if a.phase=='core'else'tools/audit/pit_retold_host_gameplay_v1.py')
 source=path.read_text();changes=[]
 replacements=(
  [("[0,1,2,4,8]","[0,1,2,4,8,32]"),("ch==6 and pressed&4","ch==6 and pressed&address(b,'Select_Button')"),("CrossoverMenuPressed=4,NmiDisable=255","CrossoverMenuPressed=32,NmiDisable=255")]
  if a.phase=='core'else[("[(4,1),(0,1),(4,0),(0,0),(4,1)]","[(32,1),(0,1),(32,0),(0,0),(32,1)]")])
 for before,after in replacements:
  assert source.count(before)==1,(path,before);source=source.replace(before,after);changes.append([before,after])
 module=types.ModuleType('qualified_pit_v3_'+a.phase);module.__file__=str(path)
 exec(compile(source,str(path),'exec'),module.__dict__);module.O=O
 sys.argv=[sys.argv[0],'--output',str(a.output)];module.main()
 proof=json.loads(a.output.read_text());proof['explicit_fixture_corrections']=changes
 if a.phase=='gameplay':proof['actual_select_input_controls']=full_input()
 proof['bindings'][str(Path(__file__).resolve())]=sha(Path(__file__))
 for p in[R/'tools/prepare_pit_retold_host_v3.py',O/'component.s',O/'build-proof.json',O/'select-correction.json']:
  proof['bindings'][str(p.resolve())]=sha(p)
 proof['actual_imports']={str(Path(m.__file__).resolve()):sha(Path(m.__file__)) for m in list(sys.modules.values()) if getattr(m,'__file__',None) and Path(m.__file__).is_file()}
 proof['python']=dict(executable=sys.executable,sha256=sha(Path(sys.executable)),version=sys.version)
 a.output.write_text(json.dumps(proof,indent=2)+'\n')
 print(json.dumps(dict(passed=proof['passed'],phase=a.phase)))
if __name__=='__main__':main()
