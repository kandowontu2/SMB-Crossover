"""Private exact3b Bill/Lance-only capsule anchor; no native hook or install."""
from pathlib import Path
import argparse,difflib,json,shutil,subprocess,sys,traceback
from final_bill_lance_hard_gallery_source_v1 import D,ROOT,SHA,sha,put,PARENT
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();out=a.output.resolve();assert not out.is_relative_to(ROOT);out.mkdir(parents=True,exist_ok=False)
    try:
        assert sha(PARENT/'candidate.nes')==SHA
        baseline=scoped_load(PARENT/'candidate.nes')
        seg=baseline['segs'][baseline['syms']['RemainingDraw']['seg']]
        assert int(seg['size'],0)==0x1fae and (location(baseline,'RemainingDraw')-16)//8192==61
        assert baseline['raw'][16+61*8192+0x1fae:16+62*8192]==b'\xff'*82
        manifest=json.loads((PARENT/'source-manifest.json').read_text());src=out/'source';src.mkdir()
        for name,h in manifest.items():
            assert sha(PARENT/'source'/name)==h,name
            f=src/name;f.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(PARENT/'source'/name,f)
        patch=[];changes=[]
        def edit(name,old,new):
            f=src/name;raw=f.read_bytes();nl='\r\n'if b'\r\n'in raw else'\n';s=raw.decode().replace('\r\n','\n')
            assert s.count(old)==1,(name,s.count(old));s=s.replace(old,new,1);s=s.replace('\n',nl);f.write_bytes(s.encode())
            changes.append(dict(path=name,before=sha(PARENT/'source'/name),after=sha(f),old_CRLF=raw.count(b'\r\n'),new_CRLF=f.read_bytes().count(b'\r\n')))
            patch.extend(difflib.unified_diff(raw.decode().splitlines(True),s.splitlines(True),fromfile='a/'+name,tofile='b/'+name))
        old='''  sta AvDrawArt
  lda #192
  sta R4
  lda #0
  sta R5
  sta R3
  lda #24
  sta R6
  lda #1
  sta R7
  sta AvDrawDirection'''
        new='''  sta AvDrawArt
.if ::ENABLE_MMC5_EXPANDED .and ::MAPPER_MMC5
  ; Same14-byte slot. Y is dead before ArtPointer's TAY; X/P survive
  ; the helper. LDA#1 below restores the original live N/Z state.
  jsr BillHudAnchor
  sta R4
  lda #0
  sta R5
  sta R3
  sty R6
  nop
.else
  lda #192
  sta R4
  lda #0
  sta R5
  sta R3
  lda #24
  sta R6
.endif
  lda #1
  sta R7
  sta AvDrawDirection'''
        edit('src/remaining_weapons.s',old,new)
        entry=src/'src/entrypoint.s';raw=entry.read_bytes();nl=b'\r\n'if b'\r\n'in raw else b'\n'
        extra=b'\n; Append in verified SPECIAL_ROSTER FF tail; all prior entries stay fixed.\n.if ::ENABLE_MMC5_EXPANDED .and ::MAPPER_MMC5\n.include "bill_hud_anchor.s"\n.endif\n'.replace(b'\n',nl)
        entry.write_bytes(raw+extra);changes.append(dict(path='src/entrypoint.s',before=sha(PARENT/'source/src/entrypoint.s'),after=sha(entry),old_CRLF=raw.count(b'\r\n'),new_CRLF=(raw+extra).count(b'\r\n')))
        patch.extend(difflib.unified_diff(raw.decode().splitlines(True),(raw+extra).decode().splitlines(True),fromfile='a/src/entrypoint.s',tofile='b/src/entrypoint.s'))
        helper='''; Bill and Lance share character3. Their24px capsule belongs in the
; free name-row gap; all other characters retain their original anchor.
; Genuine private ABI: returns A=x,Y=y; preserves X and all input P.
; Actual HUD caller's Y is dead before RemainingDraw::ArtPointer TAY.
.pushseg
.segment "SPECIAL_ROSTER"
.proc BillHudAnchor
  php
  lda SelectedCharacter
  cmp #CHARACTER_BILL
  beq Bill
  lda #192
  ldy #24
  plp
  rts
Bill:
  lda #112
  ldy #16
  plp
  rts
.endproc
.assert BillHudAnchor = $bfae, error, "Bill HUD append moved"
.assert *-BillHudAnchor = 20, error, "Bill HUD helper size changed"
.popseg
'''
        hf=src/'src/bill_hud_anchor.s';hf.write_text(helper,newline='\n');changes.append(dict(path='src/bill_hud_anchor.s',before=None,after=sha(hf),new_file=True))
        patch.extend(difflib.unified_diff([],helper.splitlines(True),fromfile='/dev/null',tofile='b/src/bill_hud_anchor.s'))
        (out/'implementation.patch').write_bytes(''.join(patch).encode())
        put(out/'source-manifest.json',{str(f.relative_to(src)).replace('\\','/'):sha(f)for f in src.rglob('*')if f.is_file()})
        cmd=[sys.executable,'-B',str(ROOT/'tools/build_mmc5_expanded.py'),'--source-overlay',str(src),'--output',str(out/'candidate.nes')]
        z=subprocess.run(cmd,cwd=ROOT,capture_output=True,text=True);put(out/'build-command.json',dict(command=cmd,returncode=z.returncode,stdout=z.stdout,stderr=z.stderr));assert z.returncode==0,z.stdout+z.stderr
        candidate=scoped_load(out/'candidate.nes');before=baseline['raw'];after=candidate['raw'];diff=[]
        assert before[:16]==after[:16]and before[16+128*8192:]==after[16+128*8192:]
        for bank in range(128):
            n=sum(x!=y for x,y in zip(before[16+bank*8192:16+(bank+1)*8192],after[16+bank*8192:16+(bank+1)*8192]))
            if n:diff.append(dict(bank=bank,bytes=n))
        assert [r['bank']for r in diff]==[61]
        moved=[];missing=[]
        for name,s in baseline['syms'].items():
            if name not in candidate['syms']:missing.append(name)
            elif s.get('val')!=candidate['syms'][name].get('val'):moved.append(name)
        assert not missing and not moved,(missing,moved)
        assert address(candidate,'BillHudAnchor')==0xbfae
        assert address(candidate,'RemainingDraw::Draw')==address(baseline,'RemainingDraw::Draw')
        assert after[16+61*8192+0x1fc2:16+62*8192]==b'\xff'*62
        put(out/'layout.json',dict(passed=True,source_only=True,native_run=False,ROM_sha256=sha(out/'candidate.nes'),parent_ROM_sha256=SHA,
            changed_banks=diff,changes=changes,all_old_symbol_addresses_exact=True,old_symbols=len(baseline['syms']),
            helper_entry=0xbfae,helper_bytes=20,previous_FF_capacity=82,remaining_FF_capacity=62,
            header_CHR_other_banks_exact=True,new_RAM_bytes=0,all_previous_entrypoints_and_spans_preserved=True,
            limits='Assembled layout only. Full RemainingDraw caller/state/output/IRQ and cost controls still required; no native image or cadence qualification.'))
        print(json.dumps(dict(passed=True,source_only=True,ROM_sha256=sha(out/'candidate.nes'),changed_banks=diff)))
    except Exception as e:
        put(out/'failure.json',dict(passed=False,native_run=False,error=str(e),traceback=traceback.format_exc()));raise


if __name__=='__main__':main()
