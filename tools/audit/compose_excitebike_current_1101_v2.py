"""Current successor with real UI ingress, stable OAM and the approved shot gate."""
from pathlib import Path
import hashlib,json,os,sys
R=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(R/'tools'),str(R/'tools/audit')]
from compose_excitebike_current_1101_v1 import compose as core
from prepare_excitebike_dispatch_1101_v1 import O,save,sha,labels
from prepare_excitebike_host_1101_v1 import BASE,PIN
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location


def compose():
    raw,patches,receipts=core(require_cpu=False);raw=bytearray(raw);b=scoped_load(BASE)
    def patch(at,old,new,role):
        assert len(old)==len(new)and raw[at:at+len(old)]==old,(role,hex(at))
        raw[at:at+len(new)]=new;patches.append(dict(role=role,offset=at,old=old.hex(),new=new.hex()))
    q=json.loads((O/'shot-owner-assembly.json').read_text());assert q['passed']and q['base_ROM_SHA256']==PIN
    for p in q['patches']:patch(p['offset'],bytes.fromhex(p['old']),bytes.fromhex(p['new']),p['role'])
    for name,oldcallee,row in [('GetPlayerColors','NrColors',26),('CrossoverPatchStatusName','RlNameDispatch',30)]:
        at=location(b,name);old=bytearray(raw[at:at+18]);target=address(b,oldcallee)
        assert old==bytes([141,106,1,169,target&255,141,108,1,169,target>>8,141,109,1,169,((location(b,oldcallee)-16)//8192)|128,76,90,1])
        new=bytearray(old);target=0xb08c+3*row;new[4]=target&255;new[9]=target>>8;new[14]=193
        patch(at,bytes(old),bytes(new),'Actual native '+name+' typed-service ingress')
    return bytes(raw),patches,receipts+['shot-owner-assembly.json']


def bundle():
    raw,_,_=compose();b=scoped_load(BASE);b['raw']=raw
    b['segs']['excitebike_resident']={'start':str(0xa000),'ooffs':str(16+65*8192)}
    for n,a in labels(O/'scene.lbl').items():b['syms'][n]={'val':str(a),'seg':'excitebike_resident'}
    for n,a in labels(O/'shot-owner.lbl').items():b['syms'][n]={'val':str(a),'seg':'excitebike_resident'}
    for row in range(37):b['syms'][f'ExService{row}']={'val':str(0xb08c+3*row),'seg':'excitebike_resident'}
    return b


def main():
    raw,patches,receipts=compose();digest=hashlib.sha256(raw).hexdigest()
    for name in ['shot-owner-CPU.json','UI-ingress-CPU.json','host-CPU.json','cold2-CPU.json','current2-CPU.json']:
        q=json.loads((O/name).read_text());assert q['passed'],name
        if name in ['cold2-CPU.json','current2-CPU.json']:assert q['memory_candidate_SHA256']==digest,(name,'stale image')
        receipts.append(name)
    lab=labels(O/'scene.lbl');call=bytes([32,lab['ExCheckCode']&255,lab['ExCheckCode']>>8])
    assert (O/'dispatch-loader.bin').read_bytes().count(call)==1
    assert (O/'dispatch-body.bin').read_bytes().count(call)==1
    assert (O/'owner-loader.inc').read_text().count('jsr ExCheckCode')==1
    assert (R/'tools/reference/excitebike_resident_dispatch_1101_v1.inc').read_text().count('jsr ExCheckCode')==1
    dest=O/'current2.nes';dest.write_bytes(raw)
    # Native scripts consume VICE labels. Publish the moved Sh bbox and all Ex
    # names explicitly; do not mutate the baseline's hard-linked label file.
    overrides={**labels(O/'scene.lbl'),**labels(O/'host.lbl'),**labels(O/'shot-owner.lbl')}
    import re
    lines=[]
    for line in BASE.with_suffix('.lbl').read_text().splitlines():
        m=re.fullmatch(r'al ([0-9A-Fa-f]+) \.(\S+)',line)
        if not m or m[2]not in overrides:lines.append(line)
    lines.extend(f'al {a:06X} .{n}'for n,a in sorted(overrides.items()))
    dest.with_suffix('.lbl').write_text('\n'.join(lines)+'\n')
    dbg=dest.with_suffix('.dbg')
    if not dbg.exists():os.link(BASE.with_suffix('.dbg'),dbg)
    assert dbg.read_bytes()==BASE.with_suffix('.dbg').read_bytes()
    q=dict(passed=True,private_candidate=True,ROM_SHA256=digest,base_ROM_SHA256=PIN,
           candidate=dest.relative_to(R).as_posix(),prior_native_negatives_preserved=True,
           source_funded_Sh_growth_bytes=1,ShBBoxIngress=0xadd7,ShShotBankGate=0xadb6,
           Ex_resident_used_bytes=960,Ex_resident_granted_bytes=968,Ex_resident_spare_bytes=8,
           private_C_only_header_helper_exact_runtime_callers=['ExLoad','ExDispatch'],
           both_header_commits_after_complete_copy_verify=True,RAM2_header_byte0_final_commit=True,
           original_NrColors_RlName_foreign_tail=True,
           actual_native_UI_ingress=True,stable_zero_native_OAM_header=True,
           patches=patches,native_verified=False,installed=False,
           scope='Successor to terminal native negatives. Exact source/CPU-qualified UI/CHR/OAM repair; root must run exact-hash native cold controller and1-1.',
           bindings={p.relative_to(R).as_posix():sha(p)for p in [Path(__file__),BASE,*[O/n for n in receipts],
               R/'tools/audit/prepare_excitebike_owner_1101_v1.py',R/'tools/audit/prepare_excitebike_dispatch_1101_v1.py',
               R/'tools/audit/prepare_excitebike_scene_1101_v1.py',R/'tools/audit/prepare_excitebike_host_1101_v1.py',
               R/'tools/reference/excitebike_resident_dispatch_1101_v1.inc',R/'tools/reference/excitebike_native_boundary_1101_v1.inc',
               O/'dispatch-loader.bin',O/'dispatch-body.bin',O/'dispatch-foreign.bin',O/'dispatch-foreign-bank.bin',O/'host-kernel.bin',O/'host-metadata.bin']})
    save('current2-composition.json',q);print(json.dumps({k:v for k,v in q.items()if k not in ['patches','bindings']}))

if __name__=='__main__':main()
