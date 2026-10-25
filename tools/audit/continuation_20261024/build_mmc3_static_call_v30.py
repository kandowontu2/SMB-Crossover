from pathlib import Path
import configparser,hashlib,json,shutil,subprocess,sys
R=Path('C:/Users/kando/Documents/ChatGPT/SMB Crossover');D=Path(__file__).resolve().parent;V=D/'mmc3-ship-lives-v25';O=D/'mmc3-static-call-v30';O.mkdir(exist_ok=False);sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();tools=O/'tools';shutil.copytree(V/'tools',tools);recipe=tools/'mmc3_oversized/repairs.json';m=json.loads(recipe.read_text())
def add(path,old,new):
 row=next((z for z in m['text_repairs']if z['path']==path),None)
 if row is None:row=dict(path=path,chunks=[]);m['text_repairs'].append(row)
 row['chunks'].append(dict(old=old,new=new))
add('smb1base-mmc3-oversized.cfg','    SRAM_00:start = $6000,  size = $2000, type = rw, file = "";','    SRAM_00:start = $6000,  size = $2000, type = rw, file = "";\n    M3_CALL_RAM:start=$73fa,size=6,type=rw,file=""; # Explicit final six-byte alignment gap before history.')
add('smb1base-mmc3-oversized.cfg','    SMCCODE:    load = PRGA_01, type = rw,  run = SP,     define = yes;','    SMCCODE:    load = PRGA_01, type = rw,  run = M3_CALL_RAM, define = yes;\n    M3_CALL_PADDING: load=PRGA_01,type=ro;')
old=(V/'source/src/mmc3.s').read_text();begin=old.index('.segment "SMCCODE"');end=old.index('\n  rts',begin)+len('\n  rts\n');old=old[begin:end]
new='''.segment "SMCCODE"
SMCCODE:
; Tiny dynamically addressed call: its return address remains on the ordinary
; CPU stack, while executable bytes live in a proven SRAM alignment gap.
.include "smc.inc"
SMC SafecallA, { lda #SMC_Value }
SMC FarcallJmpTarget, { jmp SMC_AbsAdr }
M3FarReturn: .byte $42
NextBank_SMC=NextBank-1
SafereturnA_SMC=M3FarReturn-1
.export NextBank_SMC,SafereturnA_SMC
.assert SMCCODE=$73fa,error,"MMC3 tiny call uses only the final six-byte gap"
.assert Z2UiState+1<=SMCCODE,error,"Tiny call does not overlap preceding live state"
.assert M3FarReturn+1<=XgLzHistory,error,"Tiny call stays below native audio/history"
.segment "M3_CALL_PADDING"
.res 43,$ea                    ; Preserve the original49-byte A-bank load span.
.segment "LOWCODE"
FarCallCommon:
  ; NextBank is an existing reserved cell. Original code addressed its SMC
  ; immediate instead; all named operand writers retain the same source ABI.
  sta NextBank
  lda CurrentBank
  pha
    lda #7 | PRG_FIXED_8
    sta BankShadow
    sta BANK_SELECT
    lda NextBank
    sta CurrentBank
    sta BANK_DATA
    jsr SMCCODE
    sta M3FarReturn
    lda #7 | PRG_FIXED_8
    sta BankShadow
    sta BANK_SELECT
  pla
  sta CurrentBank
  sta BANK_DATA
  lda M3FarReturn
  rts
'''
tiny,common=new.split('.segment "LOWCODE"\n',1)
assert common.startswith('FarCallCommon:')
common=common.replace('FarCallCommon:','::FarCallCommon:',1)
add('src/mmc3.s',old,tiny)
# Reuse the unreachable48-byte status wrapper tail. Its49-byte dispatcher
# needs one additional byte; remove one unreachable side-query NOP so the
# following FIXED labels, DPCM start and tail helpers retain their old layout.
add('src/characters.s','  .res 48,$ea\n  .assert *-CrossoverPatchStatusName=66,error,"Status wrapper original span"',common+'  .assert *-CrossoverPatchStatusName=67,error,"MMC3 resident bank dispatcher uses status tail"')
add('src/characters.s','  farcall TnFastSideGate,jmp\n  .res 10,$ea','  farcall TnFastSideGate,jmp\n  .res 9,$ea')
add('src/characters.s','  .assert *-CrossoverSourceSideProbe=28,error,"Original side leaf footprint"','  .assert *-CrossoverSourceSideProbe=27,error,"One unreachable byte funds resident dispatcher"')
recipe.write_text(json.dumps(m,indent=2));source=O/'source' 
with(O/'prepare.log').open('w')as log:p=subprocess.run([sys.executable,str(tools/'prepare_mmc3_oversized.py'),'--source-root',str(R),'--output',str(source),'--reference-rom',str(D/'native-probes-qa-v2/candidate.nes')],cwd=R,stdout=log,stderr=subprocess.STDOUT)
assert p.returncode==0,(O/'prepare.log').read_text()[-2000:]
# Reuse the same frozen external compile/options/header/CHR-differential steps.
helper=D/'build_mmc3_ship_lives_v25.py';suffix=helper.read_text().split('config=configparser.ConfigParser()',1)[1].split('q=dict(',1)[0];exec(compile('config=configparser.ConfigParser()'+suffix,str(helper),'exec'),globals())
q=dict(compiled=True,adopted=False,goal_complete=False,ROM_sha256=sha(rom),parent_ROM_sha256=sha(V/'candidate.nes'),changed_ROM_bytes=len(diff),changed_PRG_banks=sorted(set((i-16)//8192 for i in diff)),new_physical_RAM_bytes=0,new_CHR_bytes=0,tiny_call_and_return_gap=[0x73fa,0x7400],existing_reserved_NextBank=0x13f,hardware_stack_code_bytes=0,compile_helper_sha256=sha(helper),scope='Private architectural MMC3 candidate: resident immutable bank dispatcher in the existing status tail calls a five-byte LDA/JMP trampoline plus one private return byte in the six-byte alignment gap after Z2UiState/before XgLzHistory. Original49-byte A-bank load span padded, no source character physics or board RAM/CHR expansion. All five named operand data fields, register/flag/bank/IRQ behavior, stack ownership, full native routes and current-hash qualification must be verified. No adoption or gameplay-pass claim.')
(O/'build-proof.json').write_text(json.dumps(q,indent=2));print(json.dumps(q),flush=True)
