"""Private ordinary Mega/Proto shot presentation multiplex; no native run."""
from pathlib import Path
import argparse,hashlib,json,shutil,subprocess,sys
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address
from check_tmnt_audio_fallback_oc import qualified

R=Path(__file__).resolve().parents[2]
D=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
BASE=D/'root-chip-hud-composed-v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
HELPER='''
; Ordinary shot presentation only. No new RAM or projectile-state stores.
; Main increments FrameCounter once per game update (game.s), independently
; from skipped display frames. A lone live shot is selected for every phase.
; Original live/type/death/family guards execute before this helper.
.pushseg
.segment "MM_PROTO_SHOT_MUX"
.proc MmProtoShotMuxAdmission
 php
 pha
 txa
 pha
 lda #0
 ldx #3
Mask:
 ldy MmBulletType,x
 cpy #1
 rol
 dex
 bpl Mask
 tax
 asl
 asl
 pha
 lda Population,x
 cmp #3
 bne FourPhase
 ldx FrameCounter
 lda ModuloThree,x
 jmp PhaseReady
FourPhase:
 lda FrameCounter
 and #3
PhaseReady:
 tax
 pla
 ora PhaseIndex,x
 tay
 lda Choice,y
 cmp MmSlot
 bne Skip
 pla
 tax
 pla
 plp
 ldy MmBulletType,x
 lda MmBulletAge,x
 rts
Skip:
 pla
 pla
 plp
 tax ; A is live across the old zero-type path; X is reloaded at Next.
 pla ; discard only this helper's genuine inner JSR return address
 pla
 txa
 ldy #0
 jmp ProtoLegacyDrawShotsCold::Next
PhaseIndex:.byte 0,1,2,3
Population:
POPULATION
Choice:
CHOICE
ModuloThree:
MODULO
.endproc
.popseg
'''

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);out=p.parse_args().output.resolve()
    assert not out.is_relative_to(R);out.mkdir(parents=True,exist_ok=False)
    assert sha(BASE/'candidate.nes')=='3cee18caa732b2e85e3bdb00faf719223324f9bf24e72dd30c56be355da33b99'
    manifest=json.loads((BASE/'source-manifest.json').read_text());src=out/'source';src.mkdir()
    for n,h in manifest.items():
        assert sha(BASE/'source'/n)==h,n
        target=src/n;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(BASE/'source'/n,target)
    population=[i.bit_count()for i in range(16)];choices=[]
    for mask in range(16):
        alive=[i for i in range(3,-1,-1)if mask>>i&1]
        choices.extend([alive[phase%len(alive)]if alive else 0 for phase in range(4)])
    helper=HELPER.replace('POPULATION',' .byte '+','.join(map(str,population))).replace('CHOICE',' .byte '+','.join(map(str,choices))).replace('MODULO',' .byte '+','.join(str(i%3)for i in range(256)))
    file=src/'src/protoman_legacy_shots.inc';raw=file.read_bytes();nl=b'\r\n'if b'\r\n'in raw else b'\n'
    old=b'  lda MmBulletAge,x';assert raw.count(old)==1
    raw=raw.replace(old,b'  jsr MmProtoShotMuxAdmission')+nl+helper.replace('\n',nl.decode()).encode();file.write_bytes(raw)
    cfg=src/'smb1base-mmc5-expanded.cfg';cr=cfg.read_bytes();cn=b'\r\n'if b'\r\n'in cr else b'\n'
    needle=b'    PN_MENU_HINT: load=X5_NEW_42,type=ro,optional=yes;';assert cr.count(needle)==1
    cr=cr.replace(needle,needle+cn+b'    MM_PROTO_SHOT_MUX: load=X5_NEW_42,type=ro,start=$b9a8;');cfg.write_bytes(cr)
    assert set((BASE/'candidate.nes').read_bytes()[16+66*8192+0x19a8:16+67*8192])=={255}
    (out/'source-manifest.json').write_text(json.dumps({n:sha(src/n)for n in manifest},indent=2)+'\n')
    cmd=[sys.executable,str(R/'tools/build_mmc5_expanded.py'),'--source-overlay',str(src),'--output',str(out/'candidate.nes')]
    run=subprocess.run(cmd,cwd=R,capture_output=True,text=True);(out/'build-command.json').write_text(json.dumps(dict(command=cmd,exit=run.returncode,stdout=run.stdout,stderr=run.stderr),indent=2)+'\n')
    assert run.returncode==0,run.stdout+run.stderr
    old,new=scoped_load(BASE/'candidate.nes'),scoped_load(out/'candidate.nes')
    oq,nq=qualified(BASE/'candidate.nes'),qualified(out/'candidate.nes')
    assert all(nq.get(n)==v for n,v in oq.items()),[(n,v,nq.get(n))for n,v in oq.items()if nq.get(n)!=v][:8]
    assert old['raw'][16+128*8192:]==new['raw'][16+128*8192:]
    diffs={bank:sum(a!=b for a,b in zip(old['raw'][16+bank*8192:16+(bank+1)*8192],new['raw'][16+bank*8192:16+(bank+1)*8192]))for bank in range(128)};diffs={k:v for k,v in diffs.items()if v};assert set(diffs)=={66},diffs
    result=dict(passed=True,source_only=True,native_run=False,adopted=False,parent_ROM_sha256=sha(BASE/'candidate.nes'),ROM_sha256=sha(out/'candidate.nes'),
                changed_source=['src/protoman_legacy_shots.inc','smb1base-mmc5-expanded.cfg'],changed_PRG_bytes=diffs,new_helper_PC=address(new,'MmProtoShotMuxAdmission'),
                all_old_addresses_CHR_RAM_and_unrelated_banks_exact=True,new_RAM_bytes=0,
                intended_change='One ordinary visible-shot admission per construction, selected fairly across live slots; one live shot remains always selected. No actor/collision/art/age update changes. Empty/foreign/death guards remain original.',tool_sha256=sha(__file__),
                qualification='Build/layout only; actual helpers/callers/IRQ/art/visibility and CPU costs not yet qualified.')
    (out/'proof.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
