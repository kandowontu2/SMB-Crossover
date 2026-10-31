"""Direct source successor with original3 alignment and persistent pound phase."""
from pathlib import Path
import hashlib,json,shutil,subprocess,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
from private_build_outputs_v1 import validate
P=R/'build/bowser-source-core-v3';O=R/'build/bowser-source-core-v5'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,s):p.write_text(s,encoding='utf-8',newline='\n')
def main():
 assert not O.exists();O.mkdir()
 for p in P.iterdir():
  if p.suffix in ['.s','.inc','.chr','.cfg','.asm']:shutil.copyfile(p,O/p.name)
 p=O/'state.inc';s=p.read_text().replace('BwStateEnd=$601f','BwPound=$601f\nBwTargetX=$6020\nBwTargetPage=$6021\nBwStateEnd=$6022');write(p,s)
 p=O/'core.s';s=p.read_text().replace('ldx #30','ldx #33')
 s=s.replace('Air:\n lda BwVariant\n bne FireInput','Air:\n lda BwVariant\n bne FireInput\n lda BwPound\n bne FireInput')
 s=s.replace('lda #10                    ; original AlignAndFall wait','''lda #1
 sta BwPound
 lda BwPos
 clc
 adc #8
 and #$f0
 sta BwTargetX
 lda BwPage
 adc #0
 sta BwTargetPage
 lda #10                    ; original AlignAndFall wait''')
 s=s.replace('Motion:\n ldx #0','''Motion:
 lda BwPound
 beq Integrate
 lda #0
 sta BwBreath
 sta BwVel
 lda #6
 sta BwPose
 lda BwSlam
 beq Integrate
 dec BwSlam
 jsr BwAlign
 jmp Done
Integrate:
 ldx #0''')
 s=s.replace('lda BwSlam\n beq Landed','lda BwPound\n beq Landed').replace('sta BwSlam\nLanded:','sta BwSlam\n sta BwPound\nLanded:')
 s=s.replace('lda BwSlam\n beq Gravity\n dec BwSlam\n lda #0\n sta BwVel\nGravity:','''lda BwPound
 beq Gravity
 lda BwVel+1
 bmi PoundGravity
 cmp #$70
 bcs Pose
PoundGravity:
 clc
 adc #6
 sta BwVel+1
 jmp Pose
Gravity:''')
 s=s.replace('Pose:\n lda BwVariant','Pose:\n lda BwPound\n beq :+\n lda #6\n sta BwPose\n jmp Done\n:lda BwVariant')
 s=s.replace('HopFrames:.byte','''; Original one-pixel align extended to actual world/page coordinates.
BwAlign:
 lda BwPage
 cmp BwTargetPage
 beq AlignLow
 bcc AlignRight
 bcs AlignLeft
AlignLow:
 lda BwPos
 cmp BwTargetX
 beq AlignDone
 bcc AlignRight
AlignLeft:
 lda BwPos
 sec
 sbc #1
 sta BwPos
 lda BwPage
 sbc #0
 sta BwPage
 rts
AlignRight:
 inc BwPos
 bne AlignDone
 inc BwPage
AlignDone:rts
HopFrames:.byte''');write(p,s)
 cc=R/'tools/Windows/cc65/bin/ca65.exe';commands=[]
 for n in ['core','art','arena']:commands.append((n+'-build',[str(cc),'-g','-I',str(O),'--create-full-dep',str(O/(n+'.dep')),'-o',str(O/(n+'.o')),str(O/(n+'.s'))]))
 commands.append(('arena-link',[str(cc.with_name('ld65.exe')),'-C',str(O/'arena.cfg'),'-o',str(O/'arena.bin'),'-Ln',str(O/'arena.lbl'),'--dbgfile',str(O/'arena.dbg'),'-m',str(O/'arena.map')]+[str(O/(n+'.o'))for n in ['core','art','arena']]))
 write(O/'output-preflight.json',json.dumps([dict(step=n,validation=validate(c,O,cwd=R))for n,c in commands],indent=2)+'\n')
 for n,c in commands:
  validate(c,O,cwd=R);z=subprocess.run(c,cwd=R,text=True,capture_output=True);write(O/(n+'.json'),json.dumps(dict(command=c,returncode=z.returncode,stdout=z.stdout,stderr=z.stderr),indent=2)+'\n');assert z.returncode==0,(n,z.stderr)
 q=dict(source=True,host=False,native=False,parent=sha(P/'source-stage.json'),same_original_body_assets=True,SMB3_pound='Original10-tick alignment, source6pose, signed +6 rapid fall/cap70, retained activephase until actual landing. World-page extension authored.',bindings={str(p.resolve()):sha(p)for p in [Path(__file__),P/'source-stage.json',P/'controls-v4.json']+list(O.glob('*'))if p.is_file()})
 write(O/'source-stage.json',json.dumps(q,indent=2)+'\n');print(json.dumps(dict(path=str(O),source=True,host=False,native=False)))
if __name__=='__main__':main()
