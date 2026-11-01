"""Repair the native background-palette and legacy-inventory ownership boundaries."""
from pathlib import Path
import hashlib,json,re,subprocess,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools'),str(R/'tools/audit')]
from private_build_outputs_v1 import validate
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location
P=R/'build/thomas-platform-ground';W=R/'build/thomas-natural-host-1031-v6';O=R/'build/thomas-native-render'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
save=lambda p,v:p.write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8')


def main():
    assert not(O/'source-stage.json').exists();O.mkdir(exist_ok=True)
    assert sha(P/'candidate.nes')=='5cfc0a7276f47a980e48967cd26c7fabd29e750d35ae40866468e10d99472821'
    b=scoped_load(P/'candidate.nes');cc=R/'tools/Windows/cc65/bin'
    def once(text,old,new):assert text.count(old)==1,old;return text.replace(old,new,1)
    def run(name,cmd):
        cmd=list(map(str,cmd));guard=validate(cmd,O,cwd=R)
        for item in guard['outputs']:Path(item['path']).parent.mkdir(parents=True,exist_ok=True)
        result=subprocess.run(cmd,cwd=R,capture_output=True,text=True)
        save(O/(name+'.json'),dict(command=cmd,guard=guard,returncode=result.returncode,stderr=result.stderr))
        assert result.returncode==0,result.stderr
    def write(name,text):
        (O/name).write_text(text,encoding='utf-8',newline='\n')
    def asm(name):run(name+'-build',[cc/'ca65.exe',O/(name+'.s'),'-I',O,'-I',W/'source','-g','-o',O/(name+'.o'),'--create-full-dep',O/(name+'.dep')])
    # All sixteen load rows are unchanged. Derive the three simple columns
    # instead of storing48 ROM bytes, funding the actual ownership repairs.
    originals={n:list(b['raw'][location(b,n):location(b,n)+16])for n in ['ThLoadBank','ThLoadHigh','ThLoadFill']}
    derived=dict(ThLoadBank=[(i>>3)^3 for i in range(16)],
                 ThLoadHigh=[0xc0|((i&7)<<2)for i in range(16)],
                 ThLoadFill=[((i>>3)-1)&255 for i in range(16)])
    assert originals==derived
    tables=(W/'source/tables.s').read_text()
    for name in originals:tables=re.sub(r'^'+name+r':[^\n]*\n','',tables,flags=re.M)
    tables=tables.replace('ThLoadBank,ThLoadHigh,ThLoadCHR,ThLoadFill,','ThLoadCHR,')
    write('tables.s',tables)
    resident=(P/'resident.s').read_text()
    resident=resident.replace('ThLoadBank,ThLoadHigh,ThLoadCHR,ThLoadFill,','ThLoadCHR,')
    resident='.import AreaType,BackgroundColorCtrl,RlSupportedDispatch\n.export ThInventorySupported\n'+resident
    resident=once(resident,' lda ThLoadBank,x',' txa\n lsr\n lsr\n lsr\n eor #3')
    resident=once(resident,' lda ThLoadHigh,x',' txa\n and #7\n asl\n asl\n ora #$c0')
    resident=once(resident,' lda ThLoadFill,x',' txa\n lsr\n lsr\n lsr\n sec\n sbc #1')
    a=resident.index('ThColors:\n');z=resident.index('ThColdPrepare:',a)
    colors=resident[a:z]
    colors=once(colors,' SaveAX',' Save')
    colors=once(colors,' RestoreAX',' Restore')
    colors=once(colors,' lda #$11',' lda #$10')
    colors=once(colors,' lda #3\n sta VRAM_Buffer1+2,x',' lda #4\n sta VRAM_Buffer1+2,x')
    for old,new in [(6,7),(5,6),(4,5),(3,4)]:colors=colors.replace(f'VRAM_Buffer1+{old},x',f'VRAM_Buffer1+SHIFT{new},x')
    colors=colors.replace('SHIFT','')
    colors=once(colors,' lda #$27',' ldy BackgroundColorCtrl\n bne ThBackgroundIndex\n ldy AreaType\nThBackgroundIndex:\n lda ThBackgroundColors,y\n sta VRAM_Buffer1+3,x\n lda #$27')
    colors=once(colors,' adc #6',' adc #7')
    resident=resident[:a]+colors+resident[z:]
    # Mirror exactly the native table's legal0..10 span (including the two
    # background-control entries that overlap the first player-colour bytes).
    at=location(b,'BackgroundColors');bg=b['raw'][at:at+11]
    (O/'native-background-colors.bin').write_bytes(bg)
    resident=once(resident,'ThResidentEnd:','''ThInventorySupported:
 jsr ThSelected
 bcc ThInventoryLegacy
 lda #10
 tax
 clc
 rts
ThInventoryLegacy:
 ThFar RlSupportedDispatch,jmp
ThBackgroundColors:
.incbin "native-background-colors.bin"
ThResidentEnd:''')
    write('resident.s',resident)
    (O/'cookie.bin').write_bytes((P/'cookie.bin').read_bytes())
    inventory=R/'build/bt-ready-menu-1031-v2/joint/src/inventory.s'
    text=inventory.read_text();a=text.index('.proc InventorySupported');z=text.index('.endproc',a)
    text='.import ThInventorySupported\n'+text[:a]+once(text[a:z],'farcall RlSupportedDispatch,jmp','farcall ThInventorySupported,jmp')+text[z:]
    write('inventory.s',text)
    entry=(W/'source/entrypoint.s').read_text()+'\n.export BackgroundColorCtrl,RlSupportedDispatch\n'
    write('entrypoint.s',entry)
    command=json.loads((W/'main-build.json').read_text())['command'][:]
    old=next(p for p in command if p.endswith('entrypoint.s'));command[command.index(old)]=str(O/'entrypoint.s')
    command[1:1]=['-I',str(O)]
    for flag,name in [('-o','main.o'),('-l','main.lst'),('--create-full-dep','main.dep')]:
        if flag in command:command[command.index(flag)+1]=str(O/name)
    run('main-build',command)
    write('cache.s',(P/'cache.s').read_text());write('carrier.s',(P/'carrier.s').read_text())
    for name in ['resident','tables','cache']:asm(name)
    count=0;outputs={}
    def redirect(m):
        nonlocal count
        if m[1]in['','%O']:return m[0]
        count+=1;target=O/'sideoutputs'/(f'{count:03d}-'+Path(m[1]).name);outputs[Path(m[1]).name]=target
        return 'file="'+target.as_posix()+'"'
    write('candidate.cfg',re.sub(r'file\s*=\s*"([^"\r\n]*)"',redirect,(P/'candidate.cfg').read_text()))
    link=json.loads((P/'final-link.json').read_text())['command'][:]
    for name,old in [('resident',P/'resident.o'),('tables',W/'tables.o'),('cache',P/'cache.o'),('main',W/'main.o')]:link[link.index(str(old))]=str(O/(name+'.o'))
    for flag,name in [('-C','candidate.cfg'),('-o','candidate.nes'),('-Ln','candidate.lbl')]:link[link.index(flag)+1]=str(O/name)
    link[link.index('--ld-args')+1]='--dbgfile,'+str(O/'candidate.dbg')
    def link_stage(name):
        run(name+'-link',link)
        p=O/'candidate.dbg';data=p.read_bytes();keep={'version','info','file','lib','mod','seg','scope','sym'}
        compact=b''.join(s for s in data.splitlines(keepends=True)if s.split(b'\t',1)[0].decode('ascii')in keep)
        p.write_bytes(compact);save(O/(name+'-debug-format.json'),dict(full_sha256=hashlib.sha256(data).hexdigest(),full_bytes=len(data),compact_bytes=len(compact),compact_sha256=sha(p)))
    # The resident's existing cookie reference needs the parent's exact bytes
    # for the first link, then the genuine new relocated kernel digest.
    (O/'cookie.bin').write_bytes((P/'cookie.bin').read_bytes())
    asm('resident');link_stage('provisional')
    kernel=next(p for n,p in outputs.items()if n.endswith('kernel.bin')).read_bytes()
    state=next(p for n,p in outputs.items()if n.endswith('state.bin')).read_bytes()
    (O/'cookie.bin').write_bytes(bytes([167,10,64,1])+hashlib.sha256(kernel+state).digest()[:12])
    (O/'carrier.chr').write_bytes(kernel[:6144]+state[0x1000:0x1800]+(P/'carrier.chr').read_bytes()[8192:])
    for name in ['resident','carrier']:asm(name)
    link[link.index(str(P/'carrier.o'))]=str(O/'carrier.o');link_stage('final')
    final=scoped_load(O/'candidate.nes')
    assert address(final,'ThAllKernelEnd')-0xa000==6141
    assert address(final,'ThAllResidentEnd')<=0xb900
    assert final['raw'][1048592+434*1024:]==b['raw'][1048592+434*1024:]
    # Record every actual native byte change for review, not a broad grant.
    changes=[i for i,(a,z)in enumerate(zip(b['raw'][:1048592],final['raw'][:1048592]))if a!=z]
    refs={Path(__file__),inventory,P/'source-stage.json',P/'final-link.json',W/'main-build.json',W/'source/entrypoint.s',W/'source/tables.s',P/'resident.s',P/'cache.s',P/'carrier.chr'}
    refs|={Path(p)for p in link if p.endswith('.o')};refs|={p for p in O.rglob('*')if p.is_file()}
    save(O/'source-stage.json',dict(passed=True,source=True,native=False,installed=False,candidate=sha(O/'candidate.nes'),parent=sha(P/'candidate.nes'),
        cold_load_rows_exact=derived,resident_bytes=address(final,'ThAllResidentEnd')-0xb33a,kernel_bytes=6141,native_changed_offsets=changes,
        adaptation='Restore native universal background while queuing original Thomas colours; decline legacy Ryu inventory only for the authenticated Thomas identity. Fund ROM space by deriving three exact16row load tables.',
        bindings={str(p.resolve()):sha(p)for p in refs}))
    print(json.dumps(dict(candidate=sha(O/'candidate.nes'),resident_bytes=address(final,'ThAllResidentEnd')-0xb33a,PRG_changes=len(changes))))


if __name__=='__main__':main()
