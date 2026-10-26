"""Compiled caller liveness, identical guard-to-Work and full DMC paths."""
from pathlib import Path
import argparse,hashlib,itertools,json,re
from check_tmnt_render_oa import load,address,location
from check_tmnt_audio_fallback_oc import qualified
from cv3_remaining_sfx_queue256_support_v1 import init,sound
from cv3_remaining_sfx_steady_cpu_v4 import invoke,writable_equal
from cv3_dmc_complete_cpu_v1 import apu,regs
from verify_native_relocation import NesMPU
from py65.disassembler import Disassembler

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--prepared',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);old,new=[load(a.prepared/(n+'.nes'))for n in['baseline','candidate']];labels=qualified(a.prepared/'candidate.nes');q=init(new)
 q.m.page(2,28);d=Disassembler(NesMPU(memory=q.m));pc=address(new,'Cv3SaveAudioZp');instructions=[];defined=False
 while True:
  count,text=d.instruction_at(pc);instructions.append(dict(PC=pc,text=text))
  # All indexed/indirectY/readY instructions must be after dominating LDY.
  if re.search(r',Y|\(.*\),Y|\b(?:TYA|STY|CPY|DEY|INY)\b',text,re.I):assert defined,text
  if text.startswith('LDY '):defined=True
  if text=='RTS':break
  assert text.split()[0]in['LDA','STA','LDX','LDY','CPY'];pc+=count
 assert defined and any(t['text']=='LDY #$ff'for t in instructions)
 base=16+28*8192
 def code(b,pc,n):return b['raw'][base+pc-0xc000:base+pc-0xc000+n]
 assert code(old,0xdc06,2)==bytes([0xf0,0x20])and code(new,0xdc06,2)==bytes([0xf0,0x22]);assert code(new,0xdc28,5)==bytes([0xa0,23,0x20,0x37,0xd8]);assert code(new,0xdcdc,3)==bytes([0x20,0x51,0xda])
 assert code(old,address(old,'Cv3FxTick'),67)==code(new,address(new,'Cv3FxTick'),67)
 # The complete source phase/CPY/INC/flag/APU instruction loop is unchanged;
 # only its genuine internal position moved after dead tests were removed.
 ol=qualified(a.prepared/'baseline.nes');start=ol[('Cv3MusicAndNoiseTick','Continue')]+5;end=ol[('Cv3MusicAndNoiseTick','End')];ns=labels[('Cv3MusicAndNoiseTick','Continue')]
 assert code(old,start,end-start)==code(new,ns,end-start)
 work=labels[('Cv3DmcBeforeCv1','Work')];native=address(new,'Cv3FxNativeTick');assert code(old,address(old,'Cv3DmcBeforeCv1'),6)==code(new,native,6)
 source=a.prepared/'source';refs={n:[]for n in['Cv3SaveAudioZp','Cv3FxNativeTick','Cv3DmcBeforeCv1::Work']}
 for f in(source/'src').rglob('*.s'):
  for no,line in enumerate(f.read_text().splitlines(),1):
   for n in refs:
    if re.search(r'\b(?:jsr|jmp) '+re.escape(n)+r'\b',line):refs[n].append(dict(path=f.relative_to(source).as_posix(),line=no,text=line.strip()))
 assert all(len(v)==1 for v in refs.values())
 # Different incoming Y values must produce identical complete Save results;
 # initialized callers may therefore skip only the dead LDY23 instruction.
 saves=[]
 for flags in[0x20,0x69]:
  qs=[init(new)for _ in range(3)];cs=[invoke(q,'Cv3SaveAudioZp',a=0x55,x=7,y=y,flags=flags)for q,y in zip(qs,[0,23,255])]
  for i in[1,2]:assert regs(cs[0])==regs(cs[i]);writable_equal([qs[0],qs[i]])
  saves.append(dict(flags=flags,inputsY=[0,23,255],output=regs(cs[0])))
 rows=[]
 for event,current,pending,sub,flags in itertools.product([0x13,0x15,0x24,0x21,0x1e,0x1f,0x2f],[0,0x72,0x74,0x75,0x76],[0,0x72,0x75],[8,11],[0x20,0x69]):
  qs=[init(b,2 if event in[0x24,0x21,0x1e]else 3)for b in[old,new]]
  for q in qs:
   sound(q,event);invoke(q,'AudioUpdate')
   if current:invoke(q,'Cv3DmcStartGate',a=current);q.m[0x4015]=31
   q.put(Cv3DmcPending=pending,GameEngineSubroutine=sub)
  cs=[invoke(q,'AudioUpdate',a=0x55,x=7,y=84,flags=flags)for q in qs];assert regs(cs[0])==regs(cs[1]);assert apu(qs[0])==apu(qs[1]);writable_equal(qs)
  rows.append(dict(event=event,current=current,pending=pending,sub=sub,flags=flags,delta=cs[1].processorCycles-cs[0].processorCycles))
 assert max(r['delta']for r in rows)<=0
 (a.output/'DMC-paths.json').write_text(json.dumps(rows,indent=2)+'\n');(a.output/'compiled-Save.json').write_text(json.dumps(instructions,indent=2)+'\n')
 result=dict(passed=True,native_executed=False,ROM_sha256=sha(a.prepared/'candidate.nes'),parent_ROM_sha256=sha(a.prepared/'baseline.nes'),actual_hot_branch=dict(PC=0xdc06,old_target=0xdc28,new_target=0xdc2a,skipped_instruction='LDY #23',real_Save_entry=0xd837),actual_roster_Tick_call=dict(PC=0xdcdc,new_real_target=native,old_public_entry_still_callable=address(new,'Cv3MusicAndNoiseTick')),all_compiled_Save_readsY_dominated_by_LDY=True,Save_incoming_Y_cases=saves,sole_actual_source_callers=refs,old_public_Tick67B_byteexact=True,legacy_source_phase_loop_byteexact=True,nonzero_DMC_guard_first6bytes_identical=True,genuine_original_Work_entry=work,whole_DMC_AudioUpdate_cases=len(rows),whole_DMC_cost_range=[min(r['delta']for r in rows),max(r['delta']for r in rows)],all_state_APU_AXYP_SP_and_banks_exact=True,tool_sha256=sha(__file__),scope='Actual compiled callers/Save liveness and full software audio/DMC controls. Work receives the identical original nonzero A/NZ and preserved CV/D/I plus liveXY; only the already-tested guard is omitted. No new RAM or phase assumptions; source/APU sample bytes stay exact. Physical fetching/native deadlines remain unproved on this new hash.')
 (a.output/'proof.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
