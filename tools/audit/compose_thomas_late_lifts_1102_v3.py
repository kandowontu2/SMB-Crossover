"""Compose only latest-source Thomas kernel changes onto the installed roster."""
import json, re
from pathlib import Path
from prepare_selected_native_packet_v1 import R,sha
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address

def main():
    base=R/'build/bub-menu-candidate-1102-v2/combined-event.nes'
    parent=R/'build/thomas-platform-chr/candidate.nes'
    source=R/'build/thomas-current-lifts-1102-v2/candidate.nes'
    out=R/'build/thomas-current-candidate-1102-v3';out.mkdir(exist_ok=True)
    assert sha(base)=='613b3300b09e530ec920835b95df53f3115d865ed854e273809d4cafa52407ce'
    assert sha(source)=='ab5cce9047b1b5b9d1464cdd9abadd16d1c8d1991f22ff7f5de1957cab0e791b'
    a,b=parent.read_bytes(),source.read_bytes();raw=bytearray(base.read_bytes())
    start=1048592+426*1024;cookie=702649
    changes=[i for i,(x,y) in enumerate(zip(a,b)) if x!=y]
    assert len(changes)==1028
    for i in changes:
        assert start<=i<start+6144 or cookie+4<=i<cookie+16
        assert raw[i]==a[i],('Source preimage mismatch',i)
        raw[i]=b[i]
    rom=out/'candidate.nes';rom.write_bytes(raw)
    syms=scoped_load(source)['syms']
    # Preserve current global layout; update only source-owned private symbols.
    debug=base.with_suffix('.dbg').read_text();lines=[];updated=[]
    for line in debug.splitlines(keepends=True):
        if line.startswith('sym\t'):
            match=re.search(r'name="([^"]+)"',line)
            if match and match[1].startswith(('Th','Thomas')) and match[1] in syms:
                n=match[1];v=int(syms[n]['val'],0)
                if 0xa000<=v<0xb800:
                    line=re.sub(r'val=[^,\s]+','val='+hex(v),line);updated.append(n)
        lines.append(line)
    rom.with_suffix('.dbg').write_text(''.join(lines))
    labels=base.with_suffix('.lbl').read_text()
    for n,s in syms.items():
        if n.startswith(('Th','Thomas')) and '::' not in n and 0xa000<=int(s['val'],0)<0xb800:
            labels += '\nal %06X .%s' % (int(s['val'],0),n)
    rom.with_suffix('.lbl').write_text(labels+'\n')
    q=dict(passed=True,private=True,native=False,installed=False,ROM_sha256=sha(rom),base_sha256=sha(base),source_sha256=sha(source),changed_bytes=len(changes),
           all_other_bytes_preserved=True,debug_private_symbols_updated=sorted(set(updated)),
           remaining=['Whole caller/SMC and interrupts','Both late assisted crossings','Full1-1'],
           bindings={str(p):sha(p) for p in [Path(__file__),base,parent,source,source.with_suffix('.dbg'),rom,rom.with_suffix('.dbg'),rom.with_suffix('.lbl')]})
    (out/'composition.json').write_text(json.dumps(q,indent=2)+'\n')
    print(json.dumps({k:v for k,v in q.items() if k not in ['bindings','debug_private_symbols_updated']}))

if __name__=='__main__':main()
