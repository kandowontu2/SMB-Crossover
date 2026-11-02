"""Publish Arthur's missing native pre-movement camera coordinate."""
import json,re,subprocess
from pathlib import Path
import prepare_arthur_auth_fast_1101_v2 as P
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address
from private_build_outputs_v1 import validate
from prepare_selected_native_packet_v1 import prepare,sha
O=P.R/'build/arthur-camera-1101-v3'

def main():
 O.mkdir(exist_ok=True);b=scoped_load(P.O/'candidate.nes');t=(P.O/'new-own.s').read_text()
 a=t.index('ArOwnStoreNormal:\n');z=t.index('.macro ArMergePolicyInput',a)
 old=t[a:z]
 assert 'ArFastTailBank:' in old and old.count('sta FarcallJmpTarget_SMC+1')==2
 replacement='''ArOwnStoreNormal:
 sta ArDrawPtr+1
 pla
 sta ArDrawPtr
 plp
ArOwnTail:
 pla
 pla
 lda #<ArDispatch
 sta FarcallJmpTarget_SMC+1
 lda #>ArDispatch
 jmp ArCameraTailHigh
ArOwnStoreProbe:
 sta ArDrawPtr+1
 pla
 sta ArDrawPtr
 plp
ArOwnProbeTail:
 pla
 pla
 lda #<ArProbeDispatch
 sta FarcallJmpTarget_SMC+1
 lda #>ArProbeDispatch
ArCameraTailHigh:
 sta FarcallJmpTarget_SMC+2
ArFastTailBank:
 lda #.lobyte(26|$80)
 sta NextBank_SMC+1
 jmp NextBank_SMC
'''
 t=t[:a]+replacement+t[z:]
 old='ArOwnSet0:\n php\n';assert t.count(old)==1
 t=t.replace(old,old+''' lda Player_X_Position
 sec
 sbc ScreenLeft_X_Pos
 sta Player_Pos_ForScroll
''')
 t='\n'.join(f'{n}=${address(b,n):04x}' for n in ['Player_X_Position','ScreenLeft_X_Pos','Player_Pos_ForScroll'])+'\n'+t
 (O/'camera.s').write_text(t);(O/'camera.cfg').write_text((P.O/'own.cfg').read_text())
 cc=P.R/'tools/Windows/cc65/bin'
 for cmd in [[cc/'ca65.exe','-g',O/'camera.s','-o',O/'camera.o'],[cc/'ld65.exe','-C',O/'camera.cfg',O/'camera.o','-o',O/'camera.bin','-Ln',O/'camera.lbl']]:
  cmd=list(map(str,cmd));validate(cmd,O,cwd=P.R);r=subprocess.run(cmd,capture_output=True,text=True);assert r.returncode==0,r.stderr
 labels={n:int(a,16) for a,n in re.findall(r'^al ([0-9A-Fa-f]+) \.(\S+)$',(O/'camera.lbl').read_text(),re.M)}
 previous={n:int(a,16) for a,n in re.findall(r'^al ([0-9A-Fa-f]+) \.(\S+)$',(P.O/'new-own.lbl').read_text(),re.M)}
 for n in ['ArOwnServices','ArOwnUnavailable','ArOwnMenuName','ArHostNmiClock','ArClockPollC70','ArOwnComponentEnd','ArFastSpaceBegin']:assert labels[n]==previous[n],n
 raw=bytearray(b['raw']);start=16+70*8192+0x1d00;code=bytearray((O/'camera.bin').read_bytes());assert len(code)==768
 gap=labels['ArFastSpaceBegin']-0xbd00;code[gap:gap+105]=raw[start+gap:start+gap+105]
 raw[start:start+768]=code
 (O/'candidate.nes').write_bytes(raw)
 for suffix in ['.dbg','.lbl']:(O/('candidate'+suffix)).write_bytes((P.O/('candidate'+suffix)).read_bytes())
 q=dict(assembled=True,installed=False,ROM_sha256=sha(O/'candidate.nes'),base_sha256=sha(P.O/'candidate.nes'),funding='9-byte tail compaction funds9-byte pre-step camera publication inside existing768-byte own services; helper/public/NMI/clock PCs unchanged.',camera_contract='Before actual Arthur movement, publish low-byte(Player_X_Position-ScreenLeft_X_Pos). IncomingP/A ABI retained. No velocity/physics/helper changes.')
 (O/'assembly.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(q))
 ref=P.O/'terrain/controller.lua'
 prepare(O/'terrain',O/'candidate.nes',ref.read_text(),[Path(__file__),ref],expected=sha(O/'candidate.nes'),timeout=150,scope='Exactly unchanged failed first-pipe controller, new camera contract only. Includes preceding authenticated optimization. No RAM writes,2PNGs, first-pipe regression notfull1-1.')
 ref=P.O/'actions/controller.lua'
 prepare(O/'actions',O/'candidate.nes',ref.read_text(),[Path(__file__),ref],expected=sha(O/'candidate.nes'),timeout=120,scope='Exactly unchanged paired twojump/threefire controller with camera publication. No RAM writes,2PNGs; notfull1-1 or attack-outcome qualification.')
if __name__=='__main__':main()
