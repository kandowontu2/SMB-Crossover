"""Conservative successor: original side route and strict five-SMC contract."""
from pathlib import Path
import argparse,json,shutil
from chip_hot_control_prepare_v4 import D,sha,edit,build
def main():
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);old=D/'chip-hot-control-v4';assert sha(old/'candidate.nes')=='4e52ce11bbbdcafe47d35ff17c59f1e63a810fac42f324b4b35e119ffedaf203';src=a.output/'source';shutil.copytree(old/'source',src)
 edit(src/'src/megaman_weapons.s','''   cmp #14
   beq NativeSide''','''   cmp #14
   beq OtherSide''')
 f=src/'src/tmnt_probe_gates.s';text=f.read_text();start=text.index('.proc Name\n');end=text.index('.endproc\n',start)+len('.endproc\n');original=text[start:end]
 revised='''.if ::MAPPER_MMC5 .and .xmatch(Name,TnFastSideGate)
.proc Name
 ; The only compiled callers use the standard farcall, whose preserved
 ; SafecallA is the incoming A. No intervening calls precede the reload.
 ; Native turtle/Mac leaves load A before consuming it; keep original P.
 php
 lda SelectedCharacter
 cmp #19
 bne CheckMac
 plp
 jmp Own
CheckMac:
 cmp #15
 beq IsMac
 lda SafecallA_SMC+1
 plp
 farcall Other,jmp
IsMac:
 plp
 jmp Mac
 .res 1,$ea
 .assert *-Name=43,error,"Original side-gate span"
.endproc
.else
'''+original+'''.endif
'''
 edit(f,original,revised)
 build(src,a.output/'candidate.nes');parent=(D/'root-chip-native-adapter-v6/candidate.nes').read_bytes();candidate=(a.output/'candidate.nes').read_bytes();banks={str(k):sum(x!=y for x,y in zip(parent[16+k*8192:16+(k+1)*8192],candidate[16+k*8192:16+(k+1)*8192]))for k in range(128)};banks={k:v for k,v in banks.items()if v};assert parent[:16]==candidate[:16]and parent[16+128*8192:]==candidate[16+128*8192:];assert set(banks)=={'86','89','125','126','127'}
 proof=dict(prepared=True,accepted=False,native_run=False,parent_ROM_sha256=sha(D/'root-chip-native-adapter-v6/candidate.nes'),candidate_ROM_sha256=sha(a.output/'candidate.nes'),changed_PRG_banks=banks,all_header_CHR_and_other_banks_exact=True,source_files=[dict(path=str(src/'src'/n),sha256=sha(src/'src'/n))for n in['x5_bounce.s','characters.s','megaman_weapons.s','tmnt_probe_gates.s']],prior_strict_SMC_failure_retained=str(old/'player-cpu-v2/proof.json'),tool_sha256=sha(__file__),scope='Conservative private source/CPU candidate only. Genuine original final side route retained. No native closure/adoption. Allcaller/IRQ/foreign qualification still required.')
 (a.output/'preparation.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(proof,indent=2))
if __name__=='__main__':main()
