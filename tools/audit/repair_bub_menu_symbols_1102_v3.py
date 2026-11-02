"""Repair only native DBG packaging, preserving the failed packet and ROM."""
from pathlib import Path
import sys,json
R=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(R/'tools'),str(R/'tools/audit')]
import audit_bub_menu_frontend_1102_v1 as F
import prepare_bub_menu_qualification_1102_v2 as N
O=N.O;sha=F.sha;PIN='90a7108003343ad9f5f9719f860f44f09d1e1932194d5eac1c89bc473e932dd8'

def parsed(line):return dict(x.split('=',1)for x in line.split('\t',1)[1].split(',')if '='in x)
def fields(d):return ','.join(k+'='+str(v)for k,v in d.items())

def main():
    rom=O/'candidate.nes';dbg=O/'candidate.dbg';assert sha(rom)==PIN
    old=O/'native-menu';terminal=json.loads((old/'capture/binding.json').read_text())
    assert terminal['exit_code']==3221226505 and terminal['ROM_sha256']==PIN
    log=old/'capture/candidate-controller.log';text=log.read_text(errors='replace')
    assert 'DbgImporter'in text and "'900000'"in text and not(old/'capture/observations.csv').exists()
    saved=O/'candidate-importer-negative.dbg'
    if not saved.exists():saved.write_bytes(dbg.read_bytes())
    before=saved.read_text();segments=[];symbols=[];removed=[]
    for line in before.splitlines():
        if line.startswith('seg\t'):
            d=parsed(line)
            if int(d['id'])>=900000:removed.append(d);continue
            segments.append({k:v for k,v in d.items()if k in['id','name','start','size','addrsize','type','oname','ooffs']})
        elif line.startswith('sym\t'):
            d=parsed(line)
            if int(d['id'])>=900000:removed.append(d);continue
            # The compact package has no source lines/scopes. Do not leave
            # dangling def/ref/scope IDs from the full producer's source graph.
            symbols.append({k:v for k,v in d.items()if k in['id','name','addrsize','size','val','seg','type']})
    ids={d['id']for d in segments};assert all('seg'not in d or d['seg']in ids for d in symbols)
    assert len(removed)==8 and all('oname'in d and'addrsize'in d for d in segments if d['type']=='ro')
    lines=['version\tmajor=2,minor=0','info\t'+fields(dict(csym=0,file=0,lib=0,line=0,mod=0,scope=0,seg=len(segments),span=0,sym=len(symbols),type=0))]
    lines+=['seg\t'+fields(d)for d in segments]+['sym\t'+fields(d)for d in symbols]
    dbg.write_text('\n'.join(lines)+'\n')
    # VICE labels retain the four optional typed entry names. No native DBG
    # symbol refers to a fabricated/missing segment, source line or scope.
    b=F.scoped_load(rom);M=F.M;checks=[]
    for bob in[0,128]:
        m=M.fresh(b);M.put(m,CrossoverMenuIndex=32,FmGroups=bob)
        F.invoke(m,'MenuResolveCharacter');F.invoke(m,'QueueSelection')
        assert M.get(m,'SelectedCharacter')==39
        name=[p['bytes']for p in F.commands(m)if p['address']==0x2328][-1]
        expect=[36]*16;expect[6:9]=[11,24 if bob else 30,11];assert name==expect
        for keys in[16,128,48,160]:
            n=M.fork(m);M.put(n,VRAM_Buffer1_Offset=0,CrossoverMenuButtons=0,SavedJoypad1Bits=keys,SavedJoypad2Bits=0)
            F.invoke(n,'CrossoverMenuInput');assert M.get(n,'CrossoverMenuState')==2
        checks.append(dict(Bob=bool(bob),raw=39,blocked_confirmations=4))
    assert sha(rom)==PIN
    receipt=O/'metadata-repair.json'
    q=dict(passed=True,ROM_SHA256=PIN,ROM_changed=False,native=False,menu_admitted=False,confirmation_blocked=True,
        failure_scope='Terminal Mesen DBG importer crash before Lua/gameplay. Symbol packaging failure; not a menu/native gameplay result.',
        negative_packet=old.relative_to(R).as_posix(),negative_exit=terminal['exit_code'],negative_metadata=saved.relative_to(R).as_posix(),
        change='Remove four unused synthetic DBG segment/symbol pairs; retain original complete segment metadata and globals. Strip dangling full-source def/ref/scope IDs. VICE labels/ROM unchanged.',
        native_debug_segments=len(segments),native_debug_symbols=len(symbols),synthetic_records_removed=len(removed),CPU_rebound=checks,
        bindings={p.relative_to(R).as_posix():sha(p)for p in[Path(__file__),rom,dbg,O/'candidate.lbl',O/'candidate.json',saved,log,old/'ready.json',old/'capture/binding.json']})
    receipt.write_text(json.dumps(q,indent=2)+'\n')
    # Bind a distinct packet. The original failed folder is not overwritten.
    original=N.prepare
    def prepare(output,rom,controller,refs,**kw):
        assert output.name=='native-menu'
        refs={p for p in refs if p!=O/'candidate.json'}|{receipt,Path(__file__)}
        kw['scope']='Native DBG-packaging successor only; identical90a710 ROM. '+kw['scope']
        return original(O/'native-menu2',rom,controller,refs,**kw)
    N.prepare=prepare;sys.argv=[str(Path(N.__file__)),'--prepare','browse-blocked','--sha256',PIN]
    try:N.main()
    finally:N.prepare=original
    print(json.dumps({k:v for k,v in q.items()if k not in['bindings']}))
if __name__=='__main__':main()
