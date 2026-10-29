"""Private linker-only Roll prerequisite. No shared edits, samples or native."""
from pathlib import Path
import difflib, hashlib, json, re, subprocess, sys
import smb2_roster_audio_plan_v1 as P

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'build/smb2-roll-relocation-v1'
BASE = P.PARENT
PLAN = ROOT/'build/smb2-roster-audio-plan-v1.json'
SHIFTS = {119:(79,0xb00),120:(78,0x1000)}

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def bind(p):return P.binding(p)

def check_parent():
    assert sha(BASE)==P.PARENT_SHA
    source=ROOT/'build/celeste-small-chr-adopted-source-v1.json'
    j=json.loads(source.read_text());assert j['ROM_sha256']==P.PARENT_SHA
    for p,digest in j['bindings'].items():assert sha(p)==digest,('source drift',p)
    assert sha(ROOT/'src/entrypoint.s')==sha(BASE.parent/(BASE.stem+'-objects')/'entrypoint.s')
    assert sha(ROOT/'src/main.c')==sha(BASE.parent/(BASE.stem+'-objects')/'main.c')
    return source,j

def expected_rom():
    plan=json.loads(PLAN.read_text());raw=BASE.read_bytes();wanted=bytearray(raw)
    # Reclaim complete old banks, which have no second emitted owner.
    for bank in SHIFTS:wanted[16+bank*8192:16+(bank+1)*8192]=bytes([255])*8192
    for segment in plan['exact_Roll_segments']:
        old=segment['bank'];new,delta=SHIFTS[old]
        source=16+old*8192;dest=16+new*8192+delta
        wanted[dest:dest+segment['bytes']]=raw[source:source+segment['bytes']]
    for row in plan['internal_absolute_operands']:
        old=row['bank'];new,delta=SHIFTS[old]
        off=16+new*8192+(int(row['pc'],16)+delta &8191)
        operand=int(row['proposed_operand'],16)
        wanted[off+1:off+3]=operand.to_bytes(2,'little')
    # All94 exact macro edges include incoming, cross-moved and outgoing stubs.
    for row in plan['emitted_farcall_edges']:
        bank=row['source_bank'];new,delta=SHIFTS.get(bank,(bank,0))
        off=16+new*8192+(int(row['pc'],16)+delta &8191)
        q=bytearray.fromhex(row['original_bytes']);target=int(row['proposed_target'],16)
        q[4]=target&255;q[9]=target>>8;q[14]=row['proposed_target_bank']|128
        wanted[off:off+18]=q
    # Existing producer will rebuild125 after actual link. The only changed
    # current fixed127 bytes are incoming stubs, outside all125 overlays.
    for i in range(8192):
        old,new=raw[16+127*8192+i],wanted[16+127*8192+i]
        if old!=new:
            assert i<0x1140 or i>=0x1e11
            wanted[16+125*8192+i]=new
    return bytes(wanted)

def main():
    source,j=check_parent();OUT.mkdir(exist_ok=True)
    overlay=OUT/'overlay';overlay.mkdir(exist_ok=True)
    cfg=(ROOT/'smb1base-mmc5-expanded.cfg').read_text()
    old1='ROLL_CORE:load=X5_NEW_77,type=ro;';new1='ROLL_CORE:load=X5_NEW_4F,type=ro,start=$ab00;'
    old2='ROLL_WORLD:load=X5_NEW_78,type=ro;';new2='ROLL_WORLD:load=X5_NEW_4E,type=ro,start=$b000;'
    assert cfg.count(old1)==cfg.count(old2)==1
    # ld65 places an automatic segment after the preceding fixed-start one.
    # Append moved owners after their destination's ORIGINAL segments; merely
    # changing the early declarations would move CD_LOGIC/X5_PROFILES.
    marker='}\nSYMBOLS {'
    assert cfg.count(marker)==1
    modified=cfg.replace('    '+old1+'\n','').replace('    '+old2+'\n','')
    modified=modified.replace(marker,'    '+new1+'\n    '+new2+'\n'+marker)
    (overlay/'smb1base-mmc5-expanded.cfg').write_text(modified,newline='\n')
    (OUT/'implementation.patch').write_text(''.join(difflib.unified_diff(cfg.splitlines(True),modified.splitlines(True),
        fromfile='a/smb1base-mmc5-expanded.cfg',tofile='b/smb1base-mmc5-expanded.cfg')),newline='\n')
    commands=[]
    for name,flag in [('candidate',None),('flagoff-mmc3','mmc3'),('flagoff-mmc5','mmc5')]:
        command=[sys.executable,str(ROOT/'tools/build_mmc5_expanded.py'),'--source-overlay',str(overlay),
            '--output',str(OUT/(name+'.nes'))]
        if flag:command+=['--flag-off',flag]
        commands.append(command)
        r=subprocess.run(command,cwd=ROOT,capture_output=True,text=True)
        (OUT/(name+'-launcher.txt')).write_text(r.stdout+r.stderr)
        assert r.returncode==0,(name,r.stdout[-1500:],r.stderr[-1500:])
        if flag:
            # Immutable genuine fresh ordinary controls for this exact f56a
            # source closure. The generic output paths contain older artwork.
            reference=ROOT/('build/celeste-small-chr-'+flag+'.nes')
            assert(OUT/(name+'.nes')).read_bytes()==reference.read_bytes(),('ordinary drift',flag)
    candidate=OUT/'candidate.nes';raw=candidate.read_bytes();expected=expected_rom()
    if raw!=expected:
        wrong=[dict(offset=i,bank=(i-16)//8192,expected=x,actual=y)
            for i,(x,y)in enumerate(zip(expected,raw))if x!=y]
        (OUT/'first-layout-negative.json').write_text(json.dumps(wrong[:100],indent=2)+'\n')
        raise AssertionError(('unexplained ROM diff',len(wrong),wrong[:12]))
    # Stable symbol IDs/segments are genuine products of the same complete
    # source closure; every non-moved routine/data/RAM address must stay exact.
    def metadata(path):
        syms={};segs={}
        for line in path.open():
            if line.startswith('sym\t'):
                d=P.fields(line)
                if 'val'in d:syms[int(d['id'])]=d
            elif line.startswith('seg\t'):
                d=P.fields(line);segs[int(d['id'])]=d
        return syms,segs
    old,oseg=metadata(BASE.with_suffix('.dbg'));new,nseg=metadata(candidate.with_suffix('.dbg'))
    assert old.keys()==new.keys()
    moved,unchanged=0,0
    for key,s in old.items():
        t=new[key];assert(s['name'],s.get('seg'),s.get('scope'))==(t['name'],t.get('seg'),t.get('scope'))
        value=int(s['val'],0);seg=oseg.get(int(s.get('seg',-1)),{})
        bank=(int(seg['ooffs'])-16)//8192 if 'ooffs'in seg else -1
        if bank in SHIFTS:
            assert int(t['val'],0)==value+SHIFTS[bank][1],(s,t);moved+=1
        else:assert t['val']==s['val'],(s,t);unchanged+=1
    _,after=check_parent();assert j==after
    baseline=BASE.read_bytes();diff=bytes(x^y for x,y in zip(baseline,raw))
    inputs=[bind(source),bind(BASE),bind(BASE.with_suffix('.dbg')),bind(BASE.with_suffix('.lbl')),
        bind(BASE.with_suffix('.map')),bind(PLAN),bind(ROOT/'tools/build_mmc5_expanded.py'),
        bind(ROOT/'tools/prepare_cv3_dmc_mirror.py'),bind(ROOT/'build_options.ini'),bind(ROOT/'smb1base.cfg')]
    inputs += [dict(path=p,bytes=Path(p).stat().st_size,sha256=digest)for p,digest in j['bindings'].items()]
    proof=dict(passed=True,source_link_only=True,native_run=False,parent=bind(BASE),candidate=bind(candidate),
        source_closure_parent=bind(source),input_bindings=inputs,commands=commands,
        exact_independent_expected_ROM=True,changed_ROM_bytes=sum(bool(x)for x in diff),
        changed_banks={str(b):sum(bool(x)for x in diff[16+b*8192:16+(b+1)*8192])for b in range(128)
            if any(diff[16+b*8192:16+(b+1)*8192])},
        old119_120_allFF=True,header_CHR_exact=baseline[:16]==raw[:16]and baseline[1048592:]==raw[1048592:],
        true_moved_symbols=moved,all_other_symbols_exact=unchanged,
        ordinary_flagoffs=[bind(OUT/(n+'.nes'))for n in ['flagoff-mmc3','flagoff-mmc5']],
        private_CFG=bind(overlay/'smb1base-mmc5-expanded.cfg'),patch=bind(OUT/'implementation.patch'),
        tool=bind(__file__),limits='No Mesen, audio/E119/120 content, scheduling/menu integration. CPU/interrupt caller controls are a separate receipt on this exact build.')
    (OUT/'build-proof.json').write_text(json.dumps(proof,indent=2)+'\n')
    print(json.dumps(dict(proof=bind(OUT/'build-proof.json'),candidate=proof['candidate'],
        changed=proof['changed_banks'],moved=moved,unchanged=unchanged),indent=2))

if __name__=='__main__':main()
