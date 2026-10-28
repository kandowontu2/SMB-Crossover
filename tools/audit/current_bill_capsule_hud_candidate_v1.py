"""Sparse Bill/Lance anchor repair on frozen44204; source build only."""
from pathlib import Path
import argparse,difflib,hashlib,json,subprocess,sys
from check_tmnt_render_oa import address,location
from link_pit_rygar_sophia_audit_cpu import scoped_load

R=Path(__file__).resolve().parents[2];B=R/'build';P='bill_capsule_hud44204'
BASE=B/'bill_inert_pool.nes'
EXPECTED='44204c9b573a82dd4838df1821afeaad8ffab8b264ebb234f31a8e156434ff5a'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(p,z):p.write_text(json.dumps(z,indent=2)+'\n',encoding='utf-8',newline='\n')


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--finish-built',action='store_true');a=ap.parse_args()
    assert sha(BASE)==EXPECTED
    prior=json.loads((B/'bill_inert_pool_verify_build.json').read_text())
    for path,h in prior['bindings'].items():assert sha(path)==h,path
    old=scoped_load(BASE);start=address(old,'SamusFixedMissileHud');record=address(old,'SamusFixedHudRecord')
    assert start==0xbfae and record==0xbfd0
    end=record+9;off=location(old,'SamusFixedHudRecord')+9
    assert old['raw'][off:16+62*8192]==bytes([255])*(0xc000-end)
    source=R/'src/samus_fixed_hud.s';before=source.read_bytes();nl=b'\r\n'if b'\r\n'in before else b'\n'
    needle=b'Native:'+nl+b' jmp RemainingDraw::Draw';assert before.count(needle)==1
    new=before.replace(needle,b'Native:'+nl+b' jmp BillCapsuleHudAnchor',1)
    marker=b'.assert SamusFixedMissileHud=$bfae';assert new.count(marker)==1
    gate=nl.join([b'; Only Bill/Lance use the free upper HUD gap. The existing Samus',
        b'; helper/record keep their addresses. Draw reloads A, and all live',
        b'; outputs/flags are qualified through the complete RemainingDraw caller.',
        b'.proc BillCapsuleHudAnchor',b' lda SelectedCharacter',b' cmp #CHARACTER_BILL',b' bne Original',
        b' lda #120',b' sta R4',b' lda #16',b' sta R6',b'Original:',b' jmp RemainingDraw::Draw',b'.endproc',b''])
    new=new.replace(marker,gate+marker,1)
    helper=B/(P+'_samus_fixed_hud.s');entry=B/(P+'_entrypoint.s');rom=B/(P+'.nes')
    ep=(B/'bill_inert_pool_entrypoint.s').read_bytes();include=b'.include "samus_fixed_hud.s"';assert ep.count(include)==1
    entry_bytes=ep.replace(include,b'.include "'+helper.name.encode()+b'"',1)
    if a.finish_built:
        assert helper.read_bytes()==new and entry.read_bytes()==entry_bytes and rom.exists()
    else:
        assert not any(p.exists()for p in [helper,entry,rom,B/(P+'_build.json')]),'Preserve prior candidate'
        helper.write_bytes(new);entry.write_bytes(entry_bytes)
    command=[]
    for token in prior['command']:
        token=token.replace('bill_inert_pool_verify',P).replace('bill_inert_pool_entrypoint.s',entry.name)
        command.append(token)
    if not a.finish_built:
        z=subprocess.run(command,cwd=R,capture_output=True,text=True)
        rom.with_suffix('.build.log').write_text(z.stdout+z.stderr,encoding='utf-8')
        assert z.returncode==0,z.stdout+z.stderr
        sys.path.insert(0,str(R/'tools'));from prepare_cv3_dmc_mirror import prepare
        prepare(R,rom)
    b=scoped_load(rom);raw=b['raw'];changed=[i for i,(x,y)in enumerate(zip(old['raw'],raw))if x!=y]
    native=location(old,'SamusFixedMissileHud')+int(old['syms']['SamusFixedMissileHud']['size'],0)-3
    assert raw[native]==old['raw'][native]==0x4c
    assert raw[location(b,'SamusFixedHudRecord'):location(b,'SamusFixedHudRecord')+9]==old['raw'][location(old,'SamusFixedHudRecord'):location(old,'SamusFixedHudRecord')+9]
    assert address(b,'BillCapsuleHudAnchor')==end and int(b['syms']['BillCapsuleHudAnchor']['size'],0)==18
    assert all(native+1<=i<native+3 or off<=i<off+18 for i in changed)
    assert all((i-16)//8192==61 for i in changed)
    assert all(b['syms'].get(n,{}).get('val')==s.get('val')and b['syms'].get(n,{}).get('seg')==s.get('seg')for n,s in old['syms'].items())
    assert len(raw)==len(old['raw'])and raw[16+128*8192:]==old['raw'][16+128*8192:]
    patch=B/(P+'.patch');patch.write_text(''.join(difflib.unified_diff(before.decode().splitlines(True),new.decode().splitlines(True),fromfile='a/src/samus_fixed_hud.s',tofile='b/src/samus_fixed_hud.s')),encoding='utf-8',newline='\n')
    proof=dict(passed=True,source_only=True,native_run=False,parent_sha256=EXPECTED,candidate_sha256=sha(rom),ROM=str(rom),
        changed_bytes=len(changed),changed_banks=[61],header_CHR_all_other_banks_exact=True,
        new_gate=dict(pc=end,bytes=18,reservation_start=start,reservation_end=0xc000,previous_used=43,total_used=61,remaining_FF=21),
        original_Samus_entry_and_record_addresses_exact=True,original_Samus_record_bytes_exact=True,
        original_helper_only_Native_JMP_operand_changed=True,all_original_symbols_exact=len(old['syms']),
        no_new_RAM_CHR_or_bank_switch=True,anchor=[120,16],source_overlay={'src/samus_fixed_hud.s':str(helper)},entrypoint=str(entry),
        command=command,patch=str(patch),bindings={str(p):sha(p)for p in [Path(__file__).resolve(),BASE,BASE.with_suffix('.dbg'),BASE.with_suffix('.lbl'),B/'bill_inert_pool_verify_build.json',
            B/'bill_inert_pool_entrypoint.s',B/'bill_inert_pool_remaining_weapons.s',B/'bill_inert_pool_main.c',source,R/'src/entrypoint.s',helper,entry,patch]})
    put(B/(P+'_build.json'),proof)
    print(json.dumps({k:proof[k]for k in ['candidate_sha256','changed_bytes','new_gate','all_original_symbols_exact']}))


if __name__=='__main__':main()
