"""Encoding equivalence and reused immutable native/source controls for v32."""
import contextlib,io,json
from pathlib import Path
import measure_dkjr_admission_1102_v11 as A
import check_hogan_current_bounded_v1 as N
R=A.R;O=A.O


def main():
    q=json.loads((O/'native-branches-v32-layout.json').read_text());assert q['semantic_source_normalization_exact']
    # Longbranch = inverse-condition skip3/JMP target; the short instruction
    # has the identical destination choice and leaves all registers/flags.
    mem=[0xea]*65536;cases=0
    for opcode in [0x10,0x30,0x50,0x70,0x90,0xb0,0xd0,0xf0]:
        for flags in range(256):
            for delta in [-128,-1,1,127]:
                target=0x2002+delta;mem[0x2000:0x2002]=[opcode,delta&255]
                mem[0x3000:0x3005]=[opcode^0x20,3,0x4c,target&255,target>>8]
                old=N.NesMPU(memory=mem,pc=0x3000);new=N.NesMPU(memory=mem,pc=0x2000)
                for c in [old,new]:c.a,c.x,c.y,c.p,c.sp=0x55,7,91,flags,224
                old.step()
                if old.pc==0x3002:old.step()
                new.step()
                assert (old.pc==target)==(new.pc==target)
                assert old.pc in [target,0x3005]and new.pc in [target,0x2002]
                assert(old.a,old.x,old.y,old.p,old.sp)==(new.a,new.x,new.y,new.p,new.sp)==(0x55,7,91,flags,224)
                cases+=1
    recipes=[
        ('vector','check_dkjr_native_vector_1102_v23.py',{'native-vector-v22':'native-branches-v32','native-vector-main-v22':'native-branches-main-v32','native-vector-pause-v22':'native-branches-pause-v32','native-vector-v23-CPU':'native-branches-v33-vector'}),
        ('display','check_dkjr_native_display_1102_v25.py',{'native-display-v24':'native-branches-v32','native-display-':'native-branches-','-v24.bin':'-v32.bin','native-branches-v25-CPU':'native-branches-v33-display'}),
        ('powerup','check_dkjr_native_powerup_1102_v27.py',{'native-powerup-v26':'native-branches-v32','native-powerup-':'native-branches-','-v26.bin':'-v32.bin','native-branches-v27-CPU':'native-branches-v33-powerup'}),
        ('lifecycle','check_dkjr_native_lifecycle_1102_v31.py',{'native-lifecycle-v30':'native-branches-v32','native-lifecycle-':'native-branches-','-v30.bin':'-v32.bin','-v31-CPU':'-v33-lifecycle'})]
    receipts={};bindings={}
    for label,recipe,replacements in recipes:
        path=R/'tools/audit'/recipe;text=path.read_text()
        for old,new in replacements.items():text=text.replace(old,new)
        # No earlier receipt/source is modified. Each consumed recipe writes
        # one distinct small successor receipt under this same bounded root.
        env={'__name__':'dk_branch_control','__file__':str(path)}
        with contextlib.redirect_stdout(io.StringIO()):exec(compile(text,str(path),'exec'),env);env['main']()
        bindings[path.relative_to(R).as_posix()]=A.sha(path.read_bytes())
        names={'vector':'native-branches-v33-vector.json','display':'native-branches-v33-display.json','powerup':'native-branches-v33-powerup.json','lifecycle':'native-branches-v33-lifecycle.json'}
        rp=O/names[label];receipt=json.loads(rp.read_text());assert receipt['passed'];receipts[label]=receipt
    out=dict(passed=True,qualified=False,ROM_written=False,native_owner_admitted=False,
        body_bytes=q['body_bytes'],body_end=q['body_end'],header_spare=q['header_spare'],metadata_end=q['metadata_end'],metadata_spare=q['metadata_spare'],
        bytes_recovered=q['bytes_recovered'],shortened_branch_instructions=q['shortened_branches'],full_flag_condition_encoding_cases=cases,
        original_source_text_exact_after_encoding_normalization=True,
        controls=dict(vector=receipts['vector']['checks'],display=receipts['display']['checks'],powerup=receipts['powerup']['checks'],lifecycle=receipts['lifecycle']['checks']),
        scope='Only conditional encodings changed. Complete consumed controls passed without weaker assertions; source counters, original15px/44air latched jump, contact bounds, palette, native powerup60 and original defeat208 remain exact. Shared model remains historicalv65 matching headers. No latest-owner/cold/art/fullstage claim.',
        remaining=receipts['lifecycle']['remaining'],
        bindings={**bindings,**{p.relative_to(R).as_posix():A.sha(p.read_bytes())for p in[Path(__file__),O/'native-branches-v32-layout.json',O/'native-branches-v32.bin',O/'native-branches-pause-v32.bin',O/'native-branches-main-v32.bin',O/'native-branches-ports-v32.bin']}})
    (O/'native-branches-v33-CPU.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:out[k]for k in ['passed','body_bytes','header_spare','bytes_recovered','full_flag_condition_encoding_cases']}))


if __name__=='__main__':main()
