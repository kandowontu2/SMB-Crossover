"""Delegate Arthur's death update to the existing timed native guest owner."""
from pathlib import Path
import json,re,subprocess
import prepare_arthur_camera_1101_v3 as P
import prepare_arthur_pit_death_1101_v3 as D
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location
from private_build_outputs_v1 import validate
from prepare_selected_native_packet_v1 import prepare,sha
O=P.P.R/'build/arthur-death-1101-v4'


def main():
 O.mkdir(exist_ok=True);b=scoped_load(P.O/'candidate.nes');raw=bytearray(b['raw'])
 pc=address(b,'ArHostNativeDeath');at=location(b,'ArHostNativeDeath');cc=P.P.R/'tools/Windows/cc65/bin'
 names=['SafecallA_SMC','FarcallJmpTarget_SMC','FarCallCommon']
 pre=''.join(f'{n}=${address(b,n):04x}\n' for n in names)
 cfg=f'MEMORY{{M:start=${pc:04x},size=19,file=%O;}}SEGMENTS{{DEATH:load=M,type=ro;}}'
 (O/'death.cfg').write_text(cfg)
 def assemble(name,target):
  source=pre+f'''Target=${address(b,target):04x}
.segment "DEATH"
sta SafecallA_SMC+1
lda #<Target
sta FarcallJmpTarget_SMC+1
lda #>Target
sta FarcallJmpTarget_SMC+2
lda #${((location(b,target)-16)//8192)|128:02x}
jsr FarCallCommon
rts
'''
  (O/(name+'.s')).write_text(source)
  for cmd in [[cc/'ca65.exe','-g',O/(name+'.s'),'-o',O/(name+'.o')],[cc/'ld65.exe','-C',O/'death.cfg',O/(name+'.o'),'-o',O/(name+'.bin')]]:
   cmd=list(map(str,cmd));validate(cmd,O,cwd=P.P.R);z=subprocess.run(cmd,capture_output=True,text=True);assert z.returncode==0,z.stderr
  return (O/(name+'.bin')).read_bytes()
 old=assemble('old-death','NativePlayerDeath');assert len(old)==19 and raw[at:at+19]==old
 new=assemble('new-death','MegaManDeathUpdate');assert len(new)==19
 raw[at:at+19]=new;(O/'candidate.nes').write_bytes(raw)
 for ext in ['.lbl','.dbg']:(O/('candidate'+ext)).write_bytes((P.O/('candidate'+ext)).read_bytes())
 q=dict(assembled=True,installed=False,ROM_sha256=sha(O/'candidate.nes'),base_sha256=sha(P.O/'candidate.nes'),source_reproduced_previous_leaf=True,owner=dict(physical_bank=(at-16)//8192,start=pc,end=pc+19),changed_ROM_bytes=sum(x!=y for x,y in zip(old,new)),change='Only Arthur own death leaf changes target/bank immediates NativePlayerDeath to MegaManDeathUpdate. Existing native MmDeathAge/MmDeathPit owner supplies150pit/168normal updates then engine6. No new state/timer, shared pit-hook or cache change. Native controller confirmation required.')
 (O/'assembly.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(q))
 text,ref=D.controller()
 prepare(O/'pit-death',O/'candidate.nes',text,[Path(__file__),Path(D.__file__),ref],expected=sha(O/'candidate.nes'),timeout=180,scope='Unchanged controller-earned firstpit death/restart observer on Arthur-local death delegation successor. Requireactualone-life loss/reset andresumedcontrol; noRAMseeds,4PNGs,12-frameCSV.')
 ref=P.O/'full11-stairs/controller.lua'
 prepare(O/'full11-stairs',O/'candidate.nes',ref.read_text(),[Path(__file__),ref],expected=sha(O/'candidate.nes'),timeout=240,scope='Unchanged full1-1 stair-staging controller on Arthur-local death successor. Fullstage/allcrossings/no-life-loss required. No seeds/helpers;4PNGs,12-frameCSV. Nativepending.')


if __name__=='__main__':main()
