"""Reproduce an uninitialized-driver CPU fixture fault; no shared engine bug.

No emulator. Initialized pinned55e raw0/2/21 counterchecks are finite and do
not transfer to a different current RCR image or every possible music state.
"""
from pathlib import Path
import argparse,json,sys
import rogue_dawn_map_v1 as ref
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/audit'))
from check_tmnt_render_oa import Memory,address
from link_pit_rygar_sophia_audit_cpu import scoped_load
from verify_native_relocation import NesMPU
HOST=ROOT/'build/sunny-integrated-final.nes'
def call(m,pc):
 c=NesMPU(memory=m,pc=pc);c.sp=240;c.stPushWord(0x5aff)
 for _ in range(50000):
  if c.pc==0x5b00:return
  c.step()
 raise AssertionError(('init timeout',hex(c.pc)))
def run(b,char,initialized,lag):
 m=Memory(b)
 m.page(1,95);m.page(2,94)
 for n,v in [('SelectedCharacter',char),('CurrentBank',223),('CurrentBankC',222),('Player_Y_HighPos',1),('ScreenLeft_PageLoc',0),('ScreenRight_PageLoc',1),('OperMode',1),('GameEngineSubroutine',8),('DisableScreenFlag',1),('Sprite0HitDetectFlag',0)]:m[address(b,n)]=v
 m[0x5fee]=1
 if initialized:
  call(m,address(b,'AudioInit'))
  if char==2:call(m,address(b,'SamusAudioInit'))
  m[address(b,'AreaMusicQueue')]=1
 ticks=[]
 for tick in range(4 if initialized else 1):
  m[address(b,'NmiDisable')]=255 if lag else 0
  m[address(b,'R2')],m[address(b,'R3')]=(0x97,0x83)if initialized else(0,0)
  c=NesMPU(memory=m,pc=0x5b00);c.sp=208;c.nmi();stack=['NonMaskableInterrupt'];writers=[]
  driver_before={n:m[address(b,n)]for n in ['SmAudioBank','SmAudioCurrent']}
  for _ in range(50000):
   if c.pc==0x5b00:break
   pc=c.pc;op=m[pc];operand=m[pc+1]+256*m[pc+2];bank=m.banks[(pc-0x8000)//8192]if pc>=0x8000 else 'RAM';at=len(m.writes);c.step()
   for target,value in m.writes[at:]:
    if target in[address(b,'R2'),address(b,'R3')]:writers.append(dict(PC=f'{pc:04X}',physical_bank=bank,opcode3=bytes(m[pc:pc+3]).hex(),address=f'{target:04X}',value=value,actual_JSR_path=stack[:]))
   if op==0x20:stack.append(f'{pc:04X}->{operand:04X}')
   elif op==0x60 and len(stack)>1:stack.pop()
  else:raise AssertionError('NMI timeout')
  ticks.append(dict(tick=tick,driver_before=driver_before,R2_R3_writers=writers))
 return dict(raw_character=char,initialized=initialized,NmiDisable=255 if lag else 0,init_calls=['AudioInit']+(['SamusAudioInit']if char==2 else[])if initialized else[],AreaMusicQueue_initial=1 if initialized else 0,ticks=ticks)
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,default=ROOT/'build/rogue-dawn-host-services-v1/nmi-scratch-initialized-roles.json');a=p.parse_args();b=scoped_load(HOST)
 assert ref.digest(b['raw'])=='55e874822160c3ab20f9ccfbca8b46cfe3b71c00bc4466a9fa8c5789bf7c0217'
 cold=[run(b,c,False,False)for c in [0,2,21]];warm=[run(b,c,True,l)for c in [0,2,21]for l in [False,True]]
 assert cold[1]['ticks'][0]['R2_R3_writers'][:2]==[
 dict(PC='A529',physical_bank=0,opcode3='8506ad',address='0006',value=72,actual_JSR_path=['NonMaskableInterrupt','E3FA->F05D','F0A2->E874','EA9B->B3B4','B3B9->A504']),
 dict(PC='A530',physical_bank=0,opcode3='8505b5',address='0005',value=1,actual_JSR_path=['NonMaskableInterrupt','E3FA->F05D','F0A2->E874','EA9B->B3B4','B3B9->A504'])]
 assert not any(t['R2_R3_writers']for row in warm for t in row['ticks'])
 assert not cold[0]['ticks'][0]['R2_R3_writers']and not cold[2]['ticks'][0]['R2_R3_writers']
 proof=dict(passed=True,native_run=False,shared_defect_accepted=False,classification='Original service CPU negative is an UNINITIALIZED SamusAudioBank/Current fixture executing gameplay code in physical bank0. No shared NMI/audio repair justified.',active_Main_protocol='Pinned d97e4858 GameLoop begins LDAFF/STANmiDisable. Regular0 NMI injection mid-Main is off-protocol; initialized FF lag is the admitted interrupt path.',cold_negative_rows=cold,initialized_counterchecks=warm,limits=['Four warm ticks with actual AudioInit/selected SamusAudioInit and AreaMusicQueue1; not all tracks/effects.','Raw21 result is pinned55e generic routing, not a claim about current RCR source/native.','Private-temporary implementation is conservative and costs more; not an engine repair/performance gain.'],bindings=[ref.binding(f)for f in[Path(__file__),HOST,HOST.with_suffix('.dbg')]])
 a.output.write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(dict(passed=True,uninitialized_first_writers=['0:A529','0:A530'],initialized_ticks=24,shared_defect=False)))
if __name__=='__main__':main()
