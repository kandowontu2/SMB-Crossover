"""Active foreign AudioUpdate differential after Sunny native admission."""
from pathlib import Path
import argparse,json,sys
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R/'tools/audit'))
from sunny_integrated_controls_v1 import *
def main():
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args();assert not a.output.exists()
 oldpath=R/'build/roster-expansion-mac-integrated-v5.nes';newpath=R/'build/sunny-integrated-final.nes';old=scoped_load(oldpath);new=scoped_load(newpath);rows=[];proof=dict(passed=False,source_only=True,native=False)
 try:
  for char in range(22):
   pair=[seed(bundle,char)for bundle in[old,new]]
   for q in pair:q.put(AreaMusicQueue=1,GamePauseStatus=0,Square1SoundQueue=1,Square2SoundQueue=2,NoiseSoundQueue=4)
   for tick in range(6):
    outputs=[]
    for q in pair:
     c,w,_=run(q,'AudioUpdate');outputs.append((registers(c),app(q),cleanwrites(q,w),q.m.banks[:],c.processorCycles))
    assert outputs[0][:4]==outputs[1][:4],(char,tick,outputs[0][0],outputs[1][0])
    rows.append(dict(char=char,tick=tick,old_cycles=outputs[0][4],new_cycles=outputs[1][4],delta=outputs[1][4]-outputs[0][4],ordered_APU_writes=sum(0x4000<=i<=0x4017 or 0x5000<=i<=0x5015 for i,v in outputs[1][2])))
  proof.update(passed=True,paired_calls=len(rows),rows=rows,full_live_AXYP_SP_application_RAM_ordered_stores_banks_exact=True,scope='Six real unpaused updates per raw0..21, default variant, actual native area plus shared SFX requests; Memory CPU model, no waveform/DMC/DMA/PPU timing or every-song claim.')
 except Exception as e:proof['error']=repr(e);raise
 finally:
  proof['bindings']={str(z):sha(z)for z in[Path(__file__),R/'tools/audit/sunny_integrated_controls_v1.py',oldpath,oldpath.with_suffix('.dbg'),newpath,newpath.with_suffix('.dbg')]};a.output.write_text(json.dumps(proof,indent=2)+'\n')
 print(json.dumps(dict(passed=proof['passed'],calls=len(rows),sha256=sha(a.output))))
if __name__=='__main__':main()
