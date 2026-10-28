"""Tiny status canary/ABI, future-pipe scene and resident-caller controls.

Read-only actual linked CPU arenas. A false original X contract is retained,
not masked. The resident CPX substitution is a proposal, not an edited ROM.
"""
from pathlib import Path
import argparse
import hashlib
import json
from mac_roster_integrated_controls_v3 import seed
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address, location
from verify_native_relocation import NesMPU

R=Path(__file__).resolve().parents[2]
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--rom',type=Path,required=True)
    p.add_argument('--expected-sha256',required=True)
    p.add_argument('--old',type=Path,default=R/'build/roster-expansion-mac-integrated-v3.nes')
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();assert not a.output.exists();assert sha(a.rom)==a.expected_sha256
    inputs=[Path(__file__),a.rom,a.rom.with_suffix('.dbg'),a.old,a.old.with_suffix('.dbg'),
            R/'tools/audit/mac_roster_integrated_controls_v3.py',
            R/'tools/audit/link_pit_rygar_sophia_audit_cpu.py',
            R/'tools/audit/check_tmnt_render_oa.py',R/'tools/audit/verify_native_relocation.py']
    proof=dict(passed=False,source_only=True,native_run=False,bindings={str(q):sha(q) for q in inputs})
    try:
        b=scoped_load(a.rom);old=scoped_load(a.old)
        rows=[];failures=[]
        for variant,name in enumerate(['L MAC  ','DOC    ','TYSON  ']):
            encoded=bytes(36 if c==' ' else ord(c)-ord('A')+10 for c in name)
            for message in range(6):
                q=seed(b,variant)
                start=address(b,'VRAM_Buffer1')
                initial=bytes((19+i*37)&255 for i in range(100))
                q.m[start:start+100]=initial
                c,_=q.invoke('LmStatusNameGate',a=message,x=message,y=0xa7)
                expect=bytearray(initial)
                if message==0:expect[11:18]=encoded
                assert bytes(q.m[start:start+100])==bytes(expect),(variant,message,'name/canary')
                assert q.m[start+18]==initial[18] and c.a==message and c.y==0xa7 and c.sp==253
                row=dict(variant=variant,message=message,return_AXYP_SP=[c.a,c.x,c.y,c.p,c.sp],
                         expected_live_X=message,canary18=initial[18],seven_name_cells_exact=True)
                rows.append(row)
                if c.x!=message:failures.append(row)
        proof['status_names_and_canaries']=dict(cases=len(rows),passed=True,rows=rows)
        proof['status_original_X_contract']=dict(passed=not failures,unmasked_failures=failures,
            consumer='WriteGameText immediately CMP4/DEX; message0 currently still follows nonzero branch, but original helper X contract is not preserved.')
        scenes=[]
        for bundle,label in [(old,'old_b5'),(b,'candidate')]:
            q=seed(bundle,0);q.put(LmHealth=37,LmHearts=9,LmStars=2,AreaPointer=0xc2,
                                  AreaType=1,AreaAddrsLOffset=5,LmArea=0x25)
            pattern=bytes(i^0xa5 for i in range(256));q.m[0x5c00:0x5d00]=pattern
            c,_=q.invoke('LmEnsure')
            preserved=bytes(q.m[0x5c00:0x5d00])==pattern
            assert preserved==(label=='candidate'),(label,preserved)
            assert [q.get(n) for n in ['LmHealth','LmHearts','LmStars']]==[37,9,2]
            scenes.append(dict(ROM=label,AreaPointer=0xc2,loaded_key=0x25,
                               active_overlay_preserved=preserved,stored_area=q.get('LmArea'),SP=c.sp))
        for offset,world,key in [(6,0,0x26),(5,1,0x25)]:
            q=seed(b,0);q.put(LmHealth=37,LmHearts=9,LmStars=2,AreaPointer=0xc2,
                            AreaAddrsLOffset=offset,WorldNumber=world)
            q.m[0x5c00:0x5d00]=bytes([0xa5]*256)
            q.invoke('LmEnsure')
            want=bytearray(256);want[address(b,'LmDirty')-0x5c00]=1
            assert bytes(q.m[0x5c00:0x5d00])==want
            assert [q.get(n) for n in ['LmHealth','LmHearts','LmStars','LmArea','LmWorld']]==[37,9,2,key,world]
        proof['loaded_scene']=dict(passed=True,old_future_pipe_counterexample=scenes[0],
            current_future_pipe=scenes[1],actual_scene_and_world_reset_cases=2)
        # Literal sole caller normalizes X immediately before the helper.
        at=location(b,'RosterGraphicsBank');pc=address(b,'RosterGraphicsBank')
        helper=address(b,'Cv3ResidentRosterBank')
        code=b['raw'][at:at+32];needle=bytes([0x20,helper&255,helper>>8])
        assert code.count(needle)==1
        i=code.index(needle);selected=address(b,'SelectedCharacter')
        assert code[i-7:i]==bytes([0xad,selected&255,selected>>8,0x38,0xe9,3,0xaa])
        hat=location(b,'Cv3ResidentRosterBank');body=b['raw'][hat:hat+30]
        assert body[:5]==bytes([0xad,selected&255,selected>>8,0xc9,5])
        assert body[5]==0xd0
        target=helper+7+(body[6]-256 if body[6]&128 else body[6])
        tat=hat+target-helper;legacy=address(b,'Cv3LegacyBanks')
        assert b['raw'][tat:tat+4]==bytes([0xbd,legacy&255,legacy>>8,0x60])
        cv3=address(b,'Cv3Variant')
        assert body[7:10]==bytes([0xad,cv3&255,cv3>>8])
        flags_checked=0
        for char in [3,4,5]:
            for flags in range(256):
                if flags&0x30:continue
                # Real NES CMP/CPX primitive equality. Incoming A differs but
                # each genuine helper branch next loads its own A before use.
                outputs=[]
                for opcode,value,aa,xx in [(0xc9,5,char,char-3),(0xe0,2,char-3,char-3)]:
                    m=[0]*65536;m[0x5000:0x5002]=[opcode,value]
                    c=NesMPU(memory=m,pc=0x5000);c.a=aa;c.x=xx;c.p=flags|0x30;c.step()
                    outputs.append(c.p)
                assert outputs[0]==outputs[1]
                flags_checked+=1
        proof['resident_extension_proposal']=dict(passed=True,
            actual_caller_PC=pc+i,actual_caller_prefix=code[i-7:i+3].hex(),
            actual_helper_PC=helper,original_prefix=body[:5].hex(),
            proposed_prefix='e002',saved_bytes=3,
            proposed_table_rows={'22':'FF placeholder','23':'DE physical94'},padding_bytes=1,
            exact_cmp_cpx_flags_cases=flags_checked,
            liveness='Sole actual RosterGraphicsBank caller has X=SelectedCharacter−3; helper A is overwritten by both real next LDA paths; X/Y/SP and comparison flags retain contract for legal IDs3..5.',
            required_followup='Genuine Cv3ResidentRosterBank entry moves+2 when18-byte graphics table grows; rebuild caller operand and map explicitly, then actual candidate whole helper/NMI/caller controls. No shared code or ROM was changed by this proposal.')
        assert all(sha(q)==h for q,h in proof['bindings'].items())
        proof['passed']=not failures
    except Exception as e:
        proof['error']=repr(e)
        raise
    finally:
        a.output.write_text(json.dumps(proof,indent=2)+'\n',newline='\n')
    print(json.dumps(dict(passed=proof['passed'],status_X_failures=len(failures),proof_sha256=sha(a.output))))
    raise SystemExit(0 if proof['passed'] else 1)


if __name__=='__main__':main()
