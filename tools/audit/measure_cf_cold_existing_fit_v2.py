"""Assemble proposed existing-owner repack only; no link/cart/readiness edit."""
from pathlib import Path
import hashlib,json,subprocess,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
from private_build_outputs_v1 import validate
P=R/'build/cf-owner-retirement-v2';J=P/'joint';O=R/'build/cf-cold-existing-fit-proposal-v2'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 O.mkdir(exist_ok=False);out=O/'joint';out.mkdir();logs=[]
 s=(J/'bowser/router.s').read_text().replace('.export BwBtResolve','.export BwBtResolve,BwCfSceneLoad\n.import CfLoadIfCold')
 old=' BwFar CfOrBtCheck,jsr\n bcc BwResolveBad';new=' BwFar CfOrBtCheck,jsr\n bcc BwResolveColdNative'
 assert s.count(old)==1;s=s.replace(old,new)
 first=s.index('.import FmAlts,FmGroups');last=s.index('; Exact16B already-owned tail;')
 original=s[first:last];body=original[original.index('BwStartFlags:'):original.index('.assert')].replace('BwStartFlags:','FmStartIdentityFlags:').replace('BwStartAlts','FmStartIdentityAlts').replace('BwStartGroups','FmStartIdentityGroups')
 replacement='''; Exact prior51B, only after the sole Start consumer is rebound.
; Actual single importing BtRouter admits only27/31/33 before this resolver.
BwResolveColdNative:
 ldx #1
 cmp #45
 beq BwResolveROM
 ldx #4
 cmp #57
 beq BwResolveROM
 clc
 rts
BwCfSceneLoad:
 lda SelectedCharacter
 cmp #31
 beq Cf
 lda #<BwLoad
 sta FarcallJmpTarget_SMC+1
 lda #>BwLoad
 sta FarcallJmpTarget_SMC+2
 lda #.lobyte(.bank(BwLoad)|$80)
 jmp FarCallCommon
Cf:
 lda #<CfLoadIfCold
 sta FarcallJmpTarget_SMC+1
 lda #>CfLoadIfCold
 sta FarcallJmpTarget_SMC+2
 lda #.lobyte(.bank(CfLoadIfCold)|$80)
 jmp FarCallCommon
.assert BwCfSceneLoad-BwResolveColdNative=14,error,"Exact14B fallback"
.assert *-BwCfSceneLoad=37,error,"Exact37B private loader selector"
'''
 s=s[:first]+replacement+s[last:];s=s.replace('.import BwCheck,','.import BwLoad,BwCheck,');(out/'router.s').write_text(s)
 start='.setcpu "6502"\n.include "common.inc"\n.import FmAlts,FmGroups\n.export FmStartIdentityFlags\n.segment "MEASURE_MENU_START"\n'+body+'.assert *-FmStartIdentityFlags=51,error,"Exact old51B mask"\n'
 (out/'start.s').write_text(start)
 bt=(J/'bt/router.s').read_text().replace('.import BwBtResolve,','.import SelectedCharacter,BwBtResolve,')
 old=' tya\n pha\n tsx';new=''' tya
 pha
 ; Current real native AXYP already saved. Reject all other owner values
 ; before the single-import resolver can use native fallback rows15/19.
 lda SelectedCharacter
 cmp #27
 beq Owner
 cmp #31
 beq Owner
 cmp #33
 bne BtRouterBad
Owner:
 tsx'''
 assert bt.count(old)==1;bt=bt.replace(old,new);(out/'bt-router.s').write_text(bt)
 for stem in['router','start','bt-router']:
  cmd=[str(R/'tools/Windows/cc65/bin/ca65.exe'),'--cpu','6502x','-g','-I',str(J/'bowser'),'-I',str(J),'-I',str(J/'src'),'-I',str(R),'--create-full-dep',str(out/(stem+'.dep')),'-o',str(out/(stem+'.o')),str(out/(stem+'.s'))]
  guard=validate(cmd,O,cwd=R);run=subprocess.run(cmd,cwd=R,capture_output=True,text=True);assert run.returncode==0,run.stderr
  logs.append(dict(command=cmd,output_guard=guard,returncode=run.returncode,stderr=run.stderr))
 dumps={}
 for stem in['router','start','bt-router']:
  d=subprocess.run([str(R/'tools/Windows/cc65/bin/od65.exe'),'--dump-segments',str(out/(stem+'.o'))],capture_output=True,text=True,check=True).stdout;dumps[stem]=d
 q=dict(actual_object_segment_dumps=dumps,source=True,proposal_only=True,host_cart_modified=False,new41B_not_adopted=True,A67_existing51=14+37,old16B_family_tail_preserved=True,B020_worker_entry_and_36rows_fixed=True,BT_partition_used=211,BT_partition_grant=224,BT_remaining=13,menu_current308_plus_Start51=359,menu_grant=400,future_BT_extra34_fits_393=True,
  notes=['This is assembly fit, not CPU/cold proof. No host cart is linked.','BwStartFlags remains consumed in frozen f523; retirement is valid only after real FmStartFlags operand and obsolete import/export rebinding.','BwBtResolve is a pure resolver with single genuine BtRouter importer. New entry contract is enforced by actual B020 owner gate, not trusted from arbitrary direct API calls.','Source row15 still needs own Ensure policy and row19 native-reset-once implementation; neither is inferred from these stubs.'],commands=logs,
  bindings={str(p.resolve()):sha(p)for p in[Path(__file__),R/'tools/audit/measure_cf_cold_existing_fit_v1.py',R/'build/cf-cold-existing-fit-proposal-v1/retained-negative.json',P/'handoff.json',R/'build/cf-cold-warm-resource-proposal-v1/proposal.json',J/'bowser/router.s',J/'bt/router.s',J/'src/cf_menu_body.inc',*out.iterdir()]})
 (O/'proposal.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(dict(path=str(O/'proposal.json'),SHA256=sha(O/'proposal.json'),assembled=True,cart_unchanged=True)))
if __name__=='__main__':main()
