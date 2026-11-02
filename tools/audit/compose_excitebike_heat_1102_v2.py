"""Write only the source/CPU/ISR-qualified private continuation successor."""
from pathlib import Path
import hashlib,json,os,re
from prepare_selected_native_packet_v1 import R,sha
from prepare_excitebike_dispatch_1101_v1 import O,labels,save
from prepare_excitebike_heat_1102_v2 import memory_image


def main():
    raw,_=memory_image();digest=hashlib.sha256(raw).hexdigest()
    for name in ['heat-CPU.json','heat-ISR-CPU.json']:
        q=json.loads((O/name).read_text());assert q['passed']and q['memory_candidate_SHA256']==digest
        for p,h in q['bindings'].items():assert sha(R/p)==h,p
    base=R/'build/arthur-side-clamp-1101-v8/weapon-tail-candidate.nes';old=base.read_bytes()
    delta=[dict(offset=i,old=a,new=b)for i,(a,b)in enumerate(zip(old,raw))if a!=b]
    allowed=lambda i:16+65*8192+0x1016<=i<16+65*8192+0x1026 or 1048592+728*1024<=i<1048592+734*1024
    assert all(allowed(p['offset'])for p in delta)
    assert raw[580983:580985]==bytes([0x92,0xbd])
    dest=O/'current4.nes';dest.write_bytes(raw)
    overrides=labels(O/'heat-host.lbl');lines=[]
    for line in base.with_suffix('.lbl').read_text().splitlines():
        m=re.fullmatch(r'al ([0-9A-Fa-f]+) \.(\S+)',line)
        if not m or m[2]not in overrides:lines.append(line)
    lines.extend(f'al {a:06X} .{n}'for n,a in sorted(overrides.items()))
    dest.with_suffix('.lbl').write_text('\n'.join(lines)+'\n')
    if not dest.with_suffix('.dbg').exists():os.link(base.with_suffix('.dbg'),dest.with_suffix('.dbg'))
    save('current4-composition.json',dict(passed=True,ROM_SHA256=digest,base_ROM_SHA256=sha(base),
        private_candidate=True,changed_bytes=len(delta),delta=delta,
        new_resident_bytes=0,new_carriers=0,new_private_code_bytes=105,no_public_entry_moved=True,
        all_foreign_ROM_exact=True,Arthur_row34_retained=True,native_verified=False,installed=False,
        scope='Exact original timer/cooling/postair phases restored. All resident gates/UI/graphics/CHRmetadata/body and foreign bytes retain installedd8; only six private code carriers and complete own16B cookie change. Exact candidate native controls and overheat/recovery remain required.',
        bindings={p.relative_to(R).as_posix():sha(p)for p in [Path(__file__),base,O/'heat-assembly.json',O/'heat-CPU.json',O/'heat-ISR-CPU.json',O/'heat-kernel.bin']}))
    print(json.dumps(dict(passed=True,ROM_SHA256=digest,changed_bytes=len(delta),candidate=str(dest))))


if __name__=='__main__':main()
