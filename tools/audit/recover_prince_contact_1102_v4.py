"""Measure original full post-physics terrain/contact selector closure.

Source-specific trap/potion/sword-room actions stay explicit environment
boundaries. The native adapter must never fabricate those original tile kinds.
"""
from pathlib import Path
import hashlib,json,re,subprocess
import recover_prince_landing_1102_v3 as L
from private_build_outputs_v1 import validate
R,O=L.R,L.O


def main():
 p=Path(L.__file__);s=p.read_text()
 changes={
  "'PpCombatLoseHP':(5,0x8710)":"'PpCombatLoseHP':(5,0x8710),'PpTerrainContact':(7,0xd17a)",
  "(7,0xd487):'PpWorldLandingAlign',":"(7,0xd487):'PpWorldLandingAlign',(7,0xd393):'PpSourceTrapContact',(7,0xd6fb):'PpSourceHazardContact',(7,0xf111):'PpSourceSwordPickup',(5,0x8a26):'PpSourcePotionContact',",
  "landing-core":"contact-core",
  "landing-original":"contact-original",
  "landing-recovery.json":"contact-recovery.json",
  'start=$b300':'start=$bc00',
  ' for old,new in replacements.items():':" replacements.update({'size=$2000,file=%O':'size=$3000,file=%O','size=$1000,file=%O':'size=$2000,file=%O'})\n for old,new in replacements.items():",
 }
 for old,new in changes.items():assert old in s,old;s=s.replace(old,new)
 env=dict(__file__=str(p),__name__='prince_contact_candidate')
 exec(compile(s,str(p),'exec'),env);env['main']()
 q=json.loads((O/'contact-recovery.json').read_text())
 # The frozen generic emitter conservatively expands unknown forward
 # branches. Relax only branches already proven local by actual link labels;
 # shrinking intervening instructions cannot increase their distance.
 asm=O/'contact-core.s';text=asm.read_text();cfg=O/'contact-core.cfg'
 cc=R/'tools/Windows/cc65/bin';rounds=[]
 for _ in range(20):
  labels=L.B.P.T.labels(O/'contact-core.lbl');changed=0
  def relax(m):
   nonlocal changed
   label,mn,target=m.groups();a=labels[label];dest=labels[target]
   if -128<=dest-a-2<=127:
    changed+=1;return f'{label}:{m.string[m.start()+len(label)+1:m.start(2)]}{dict(jeq="beq",jne="bne",jmi="bmi",jpl="bpl",jcs="bcs",jcc="bcc",jvs="bvs",jvc="bvc")[mn]} {target}\n'
   return m.group()
  pattern=r'(PpN_\d_[0-9A-F]+):([^\n]*\n )(?:never)'
  # Each exported instruction label has one source comment followed by the
  # single emitted instruction. Preserve that comment byte-for-byte.
  pat=r'(PpN_\d_[0-9A-F]+):[^\n]*\n (jeq|jne|jmi|jpl|jcs|jcc|jvs|jvc) (PpN_\d_[0-9A-F]+)\n'
  text=re.sub(pat,relax,text)
  end=labels['PpCoreEnd'];script_start=(end+255)&~255
  cfg.write_text(f'MEMORY{{M:start=$a000,size=$3000,file=%O;}}SEGMENTS{{CORE:load=M,type=ro;SCRIPTS:load=M,type=ro,start=${script_start:04x};TABLES:load=M,type=ro;}}')
  asm.write_text(text)
  for cmd in [[cc/'ca65.exe','-g',asm,'-o',O/'contact-core.o'],[cc/'ld65.exe','-C',cfg,O/'contact-core.o','-o',O/'contact-core.bin','-Ln',O/'contact-core.lbl']]:
   cmd=list(map(str,cmd));validate(cmd,O,cwd=R);z=subprocess.run(cmd,capture_output=True,text=True);assert z.returncode==0,z.stderr
  rounds.append(dict(branches_shortened=changed,prelink_code_end=end,script_start=script_start))
  if not changed:break
 else:raise AssertionError('Branch relaxation did not reach a fixed point')
 labels=L.B.P.T.labels(O/'contact-core.lbl');q['component_code_bytes']=labels['PpCoreEnd']-0xa000
 q['compact_code_image_bytes']=(O/'contact-core.bin').stat().st_size
 q['compact_code_image_half_open']=['A000',f'{labels["PpTablesEnd"]:04X}']
 q['local_branch_relaxation']=rounds
 q['fits_conditional_code_window']=labels['PpTablesEnd']<=0xbfe0
 q['remaining_before_BFE0']=0xbfe0-labels['PpTablesEnd']
 q['extension_scope']='Original D17A post-physics support/side/landing selector, including D4F5 support-to-fall and D79B floor selection, plus the v3 ledge/landing/HP family. Original traps, hazards, potions and sword-room pickup remain explicit environment callbacks; host material adapter may only publish types whose meaning it implements.'
 q['source_producer_SHA256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
 (O/'contact-recovery.json').write_text(json.dumps(q,indent=2)+'\n')


if __name__=='__main__':main()
