"""Assemble independent real host service component against immutable Sunny55e.

No shared edits, source/ROM clone, emulator, mock native-integration claim.
"""
from pathlib import Path
import argparse,hashlib,json,re,subprocess,sys
from py65.disassembler import Disassembler
from py65.devices.mpu6502 import MPU
import rogue_dawn_map_v1 as ref
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/audit'))
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location
HOST=ROOT/'build/sunny-integrated-final.nes'
HOST_SHA='55e874822160c3ab20f9ccfbca8b46cfe3b71c00bc4466a9fa8c5789bf7c0217'
NAMES='''SelectedCharacter SavedJoypadBits R0 R1 R2 R3 R4 R5 R6 R7
Player_X_Position Player_PageLoc Player_Y_Position Player_Y_HighPos
Player_X_Speed Player_Y_Speed PlayerFacingDir ScreenLeft_PageLoc
ScreenRight_PageLoc ScreenLeft_X_Pos Block_Buffer_1 Block_Buffer_2
MTileAttribute MTILE_SOLID MTILE_CLIMB Enemy_Flag Enemy_ID Enemy_State
Enemy_Y_HighPos Enemy_Y_Position Enemy_X_Position Enemy_PageLoc PowerUpType
InvPickup InvPickupOwner AreaType SafecallA_SMC FarcallJmpTarget_SMC FarCallCommon
CurrentBank CurrentBankC'''.split()
NAMES+='Enemy_BoundBoxCtrl BoundBoxCtrlData'.split()
NAMES+='SmPosePtr SmChrBank ObjectMetasprite METASPRITE_SAMUS_BODY'.split()
NAMES+='Player_X_Scroll Player_XSpeedAbsolute Player_State'.split()
def labels(p):
 return {m[2]:int(m[1],16)for l in p.read_text().splitlines()if(m:=re.match(r'al ([\da-fA-F]+) \.(\S+)',l))}
def bcd_source(raw):
 m=ref.cpu_image(raw,lower_bank=2);d=Disassembler(MPU(memory=m));lines=[]
 replacements={0xc3da:'RdHsDecimalAdd',0xc3fb:'RdHsDecimalSub',0xc41d:'RdHsSplitBCD'}
 # Literal instructions, relocated direct labels/real scratch operands only.
 for lo,hi in [(0xc3da,0xc42c)]:
  pc=lo
  while pc<hi:
   size,text=d.instruction_at(pc)
   if pc in replacements:lines+=['.export '+replacements[pc],replacements[pc]+':']
   if text.startswith(('BCC ','BCS ','BEQ ','BNE ','BMI ','BPL ','JMP ','JSR ')):
    dest=int(text.split('$')[1],16)
    assert lo<=dest<hi,hex(dest)
    text=text[:4]+'RdHsBCD_'+f'{dest:04X}'
   else:
    text=re.sub(r'\$([0-9a-fA-F]{2})(?![0-9a-fA-F])',lambda z:{1:'Rh2',2:'Rh3',3:'Rh4'}.get(int(z[1],16),z[0]),text)
   lines+=[f'RdHsBCD_{pc:04X}: {text} ; actual62:{pc:04X} {bytes(m[pc:pc+size]).hex()}']
   pc+=size
 # Native damage admission excludes only7/8/FF, with explicit damage operands
 # delivered by the actual host injury boundary (not ordinary Samus HP).
 lines+=['''
.proc RdHsDamage
 pha
 jsr RdHostEnabled
 bcc Foreign
 pla
 sta Rh6
 sty Rh7
 lda Rh6
 ora Rh7
 beq No
 lda RdAction
 cmp #7
 beq No
 cmp #8
 beq No
 cmp #$ff
 beq No
 lda RdGear
 and #$20
 beq Debit
 lsr Rh6
 lsr Rh7
 bcc Debit
 lda #$4f
 adc Rh6
 sta Rh6
Debit:
 lda RdHealthLo
 sta Rh4
 lda Rh6
 sec
 jsr RdHsDecimalSub
 sta RdHealthLo
 lda RdHealthHi
 sta Rh4
 lda Rh7
 jsr RdHsDecimalSub
 sta RdHealthHi
 RdHsLeaf RD_LEAF_DAMAGE_COMPLETE
 lda #0
 sta Rh6
 sta Rh7
 sec
 rts
No:clc
 rts
Foreign:
 pla
 clc
 rts
.endproc
.proc RdHsAddBCD
 lda RdHealthLo
 sta Rh4
 lda Rh6
 clc
 jsr RdHsDecimalAdd
 sta RdHealthLo
 lda RdHealthHi
 sta Rh4
 lda Rh7
 jsr RdHsDecimalAdd
 sta RdHealthHi
 lda RdTanks
 asl
 asl
 asl
 asl
 ora #$0f
 cmp RdHealthHi
 bcs Done
 and #$f9
 sta RdHealthHi
 lda #$99
 sta RdHealthLo
Done:
 lda #0
 sta Rh6
 sta Rh7
 rts
.endproc
''']
 return '; Generated literal BCD instructions from authenticated1.21; do not hand edit.\n'+'\n'.join(lines)+'\n'
def build(output,generate=False):
 output.mkdir(parents=True,exist_ok=True)
 raw=ref.ROM.read_bytes();assert ref.digest(raw)==ref.EXPECTED
 host=scoped_load(HOST);assert ref.digest(host['raw'])==HOST_SHA
 inc=ROOT/'src/rogue_dawn_host_services_bcd.inc';text=bcd_source(raw)
 if generate:inc.write_text(text,newline='\n')
 else:assert inc.read_text()==text
 s={n:address(host,n)for n in NAMES}
 frozen=ROOT/'build/rogue-dawn-control-v1'
 q=labels(frozen/'control.lbl')
 leaf={'RD_LEAF_RENDER_PLAYER':q['RdRenderPlayer'],'RD_LEAF_ADD_MISSILE_TANK':q['RdAddMissileTank'],'RD_LEAF_DAMAGE_COMPLETE':q['RdControlDamageComplete']}
 leaf.update({n:q[n]for n in ['RdBodyIndex0','RdBodyIndex1','RdBodyRadiusY','RdBodyRadiusX','RdArtRecordLo','RdArtRecordHi','RdArtRecordPage','RdArtEmpty']});leaf['RD_FIRST_CHR']=680
 wrapper='\n'.join(f'{n}=${v:04x}'for n,v in {**s,**leaf}.items())+'\n.include "rogue_dawn_host_services.s"\n.include "rogue_dawn_host.s"\n'
 (output/'services-wrapper.s').write_text(wrapper,newline='\n')
 (output/'services.cfg').write_text('MEMORY { H:start=$A600,size=$1A00,bank=95,file=%O; }\nSEGMENTS { ROGUE_DAWN_HOST:load=H,type=ro; }\n')
 cc=ROOT/'tools/Windows/cc65/bin';commands=[
 [str(cc/'ca65.exe'),'-g','-I',str(ROOT/'src'),str(output/'services-wrapper.s'),'-o',str(output/'services.o')],
 [str(cc/'ld65.exe'),'-C',str(output/'services.cfg'),'-o',str(output/'services.bin'),'-Ln',str(output/'services.lbl'),'--dbgfile',str(output/'services.dbg'),str(output/'services.o')]]
 for cmd in commands:
  z=subprocess.run(cmd,capture_output=True,text=True)
  if z.returncode:raise RuntimeError(z.stdout+z.stderr)
 code=(output/'services.bin').read_bytes();assert len(code)<=6656
 s.update(labels(output/'services.lbl'));s.update(leaf)
 for line in (output/'services.dbg').read_text().splitlines():
  if not line.startswith('sym\t'):continue
  n=re.search(r'name="(Rh[2-7])"',line);v=re.search(r'val=0x([0-9A-Fa-f]+)',line)
  if n and v:s[n[1]]=int(v[1],16)
 assert s['RdHostDispatch']==0xa600 and [s[f'Rh{i}']for i in range(2,8)]==[0x5c31,0x5c32,0x5c33,0x5c35,0x5c36,0x5c37]
 return code,s,host,raw
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,default=ROOT/'build/rogue-dawn-host-services-v1');p.add_argument('--generate',action='store_true');a=p.parse_args()
 code,s,host,raw=build(a.output,a.generate)
 proof=dict(status='assembled independent host services; no shared integration/native',native_run=False,host_component_bytes=len(code),start='95:A600',end_exclusive=f'95:{0xa600+len(code):04X}',free_bytes=6656-len(code),frozen_bridge_unchanged=True,entry_points={k:f'95:{v:04X}'for k,v in s.items()if k.startswith('RdHs')or k=='RdHostDispatch'},source_authority=ref.binding(ref.ROM),host=ref.binding(HOST),host_DBG=ref.binding(HOST.with_suffix('.dbg')),commands=commands if False else 'see recipe build()',bindings=[ref.binding(p)for p in[Path(__file__),ROOT/'src/rogue_dawn_host_services.s',ROOT/'src/rogue_dawn_host_services_bcd.inc',ROOT/'src/rogue_dawn_host.s',ROOT/'src/rogue_dawn_host_context.inc',a.output/'services.bin']])
 (a.output/'build.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(dict(bytes=len(code),end=f'{0xa600+len(code):04X}',free=6656-len(code))))
if __name__=='__main__':main()
