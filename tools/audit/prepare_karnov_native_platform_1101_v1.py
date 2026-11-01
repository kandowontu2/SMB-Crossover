"""Source-assembled extension of the existing native two-pipe elevator owner.

No new platform engine, RAM, CHR or physics constants. Candidate only.
"""
from pathlib import Path
import ast, hashlib, json, re, subprocess, sys
R=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(R/'tools'),str(R/'tools/audit')]
from prepare_ff_current_component_v2 import qualified
from check_tmnt_render_oa import address,location
J=R/'build/kirby-approach-owner-1101-v3'
O=R/'build/karnov-native-platform-1101-v1'
PIN='367266d2ec4e62fcefc15fffb3a05095a16060ad52f9d68348f213d94b31268c'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def old_tick():
    p=R/'tools/prepare_dragon_power_platform_v1.py'
    node=ast.parse(p.read_text())
    source=next(ast.literal_eval(n.value) for n in node.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='ASM' for t in n.targets))
    p2=R/'tools/prepare_dragon_power_two_platforms_v1.py'
    f=next(n for n in ast.parse(p2.read_text()).body if isinstance(n,ast.FunctionDef) and n.name=='main')
    pairs=[]
    for n in f.body:
        if isinstance(n,ast.Assign) and isinstance(n.value,ast.Constant) and isinstance(n.value.value,str):
            for t in n.targets:
                if isinstance(t,ast.Name) and t.id in ['before','after']:pairs.append((t.id,n.value.value))
    for i in range(0,len(pairs),2):
        assert pairs[i][0]=='before' and pairs[i+1][0]=='after'
        a,z=pairs[i][1],pairs[i+1][1];assert source.count(a)==1;source=source.replace(a,z)
    start=source.index('.proc DpPlatformTick');end=source.index('.endproc',start)+len('.endproc')
    return source[start:end]

def main():
    assert sha(J/'candidate.nes')==PIN
    O.mkdir(exist_ok=True);b=qualified(J/'candidate.nes');raw=bytearray(b['raw'])
    constants={n:address(b,n) for n in b['syms'] if re.fullmatch(r'[A-Za-z_][A-Za-z_0-9]*',n)}
    def assemble(name,source,start,size):
        source=source.replace(' phx\n',' txa\n pha\n').replace(' plx\n',' pla\n tax\n')
        names=set(re.findall(r'\b[A-Za-z_][A-Za-z_0-9]*\b',source))
        local=set(re.findall(r'\.proc\s+(\w+)|^(\w+):',source,re.M));local={s for pair in local for s in pair if s}
        defs='\n'.join(f'{n}=${constants[n]:04x}' for n in sorted(names&constants.keys()-local))
        text='.setcpu "6502x"\n.macpack longbranch\n'+defs+f'\n.segment "PATCH"\n.org ${start:04x}\nPatchStart:\n'+source+f'\n.res {size}-(*-PatchStart),$ea\n'
        (O/(name+'.s')).write_text(text)
        (O/(name+'.cfg')).write_text(f'MEMORY {{ M:start=${start:04x},size=${size:04x},file=%O; }} SEGMENTS {{ PATCH:load=M,type=ro; }}')
        commands=[[str(R/'tools/Windows/cc65/bin/ca65.exe'),str(O/(name+'.s')),'-o',str(O/(name+'.o'))],
          [str(R/'tools/Windows/cc65/bin/ld65.exe'),'-C',str(O/(name+'.cfg')),str(O/(name+'.o')),'-o',str(O/(name+'.bin'))]]
        for cmd in commands:
            z=subprocess.run(cmd,cwd=R,capture_output=True,text=True);assert z.returncode==0,z.stderr
        return (O/(name+'.bin')).read_bytes()
    original=old_tick();at=location(b,'DpPlatformTick')
    baseline=assemble('original-tick',original,0xb198,217)
    assert baseline==raw[at:at+217], 'Original source reconstruction must match current native bytes'
    new=original.replace(' cmp #24\n jne Done',' cmp #24\n beq Owner\n cmp #34\n jne Done\nOwner:')
    new=new.replace(' lda HpCharacter\n cmp #24',' lda HpCharacter\n cmp SelectedCharacter')
    for prefix in [' lda HpKey\n',' cmp SelectedCharacter\n',' cmp CrossoverBehaviorVersion\n']:
        assert prefix+' jne Outside' in new;new=new.replace(prefix+' jne Outside',prefix+' bne Outside')
    new=new.replace(' jpl Done',' bpl Done')
    changed=[]
    def patch(role,offset,data):
        old=bytes(raw[offset:offset+len(data)]);raw[offset:offset+len(data)]=data
        changed.append(dict(role=role,offset=offset,size=len(data),old=old.hex(),new=data.hex()))
    patch('shared original elevator, admit Karnov with matching scene owner',at,assemble('shared-tick',new,0xb198,217))
    dispatcher='''lda SelectedCharacter
cmp #34
beq DpPlatformTick
jmp HpSpawnAndTrack'''
    start=16+26*8192+0x1134;assert raw[start:start+12]==b'\xff'*12
    patch('existing twelve-byte helper padding',start,assemble('dispatch',dispatcher,0xb134,12))
    constants['KrPlatformDispatch']=0xb134
    bridge='''jsr ProcFireball_Bubble
lda HpCount
bne Call
lda SelectedCharacter
cmp #34
bne Done
Call:
; Incoming A is dead in both target owners, as at HpGraphicsBankCopy.
lda #<KrPlatformDispatch
sta FarcallJmpTarget_SMC+1
lda #>KrPlatformDispatch
sta FarcallJmpTarget_SMC+2
lda #$9a
jsr FarCallCommon
Done:rts'''
    offset=location(b,'HpProcessFireballsBridge')
    assert raw[offset+27:offset+31]==b'\xea'*4
    patch('existing resident bridge and four-byte padding',offset,assemble('bridge',bridge,address(b,'HpProcessFireballsBridge'),31))
    # Native platforms establish support after the earlier BG callback.
    # Reconcile that genuine grounded state before the next original actor
    # update, rather than leaving its unsupported-ledge state active.
    kernel=(J/'kr-kernel.bin').read_bytes();image=raw.find(kernel)
    assert image>=0 and raw.find(kernel,image+1)<0
    needle=bytes.fromhex('a51ed005a9028d8bc0')
    pos=kernel.find(needle);assert pos>=0 and kernel.count(needle)==1
    assert kernel[0x1fc5:0x1fcb]==b'\xff'*6
    constants['KrPlatformGrounded']=0xbfc5
    patch('source actor genuine ground reconciliation call',image+pos+6,
          assemble('ground-call','jsr KrPlatformGrounded',0xa000+pos+6,3))
    patch('six bytes inside existing Karnov actor allocation',image+0x1fc5,
          assemble('ground-helper','sta $c08b\njmp KrPostTerrain',0xbfc5,6))
    cookie_at=location(b,'KrCookie');cookie=bytes(raw[cookie_at:cookie_at+16])
    assert cookie==kernel[0x1fe0:0x1ff0]
    revised=cookie[:4]+hashlib.sha256(bytes(raw[image:image+0x1fe0])).digest()[:12]
    patch('ROM complete owner revision',cookie_at,revised)
    patch('actor image complete owner revision',image+0x1fe0,revised)
    (O/'candidate.nes').write_bytes(raw)
    (O/'kr-kernel.bin').write_bytes(raw[image:image+8192])
    # Public PCs/segments stay fixed. Drop obsolete private locals rather than
    # exposing incorrect disassembly locations; patch sources own new locals.
    obsolete={s['id'] for n,s in b['syms'].items() if n.startswith('DpPlatformTick::') or n=='HpProcessFireballsBridge::Done'}
    dbg=(J/'candidate.dbg').read_text()
    dbg=''.join(line for line in dbg.splitlines(keepends=True) if not(line.startswith('sym\t') and re.search(r'\bid=(\d+)',line).group(1) in obsolete))
    dbg=dbg.replace(str(J/'kr-kernel.bin').replace('\\','/'),str(O/'kr-kernel.bin').replace('\\','/'))
    (O/'candidate.dbg').write_text(dbg)
    (O/'candidate.lbl').write_bytes((J/'candidate.lbl').read_bytes())
    proof=dict(passed=True,source_assembled=True,native_verified=False,installed=False,base_sha256=PIN,candidate_sha256=sha(O/'candidate.nes'),original_tick_exact=True,patches=changed,
       scope='Karnov34 shares existing native25 elevator placements704/888 and reconciles native grounded contact before source update. No source physics constants changed. Both owner cookie copies revised. Main/ISR, passenger carry, lifecycle and Goku regression pending.')
    (O/'assembly.json').write_text(json.dumps(proof,indent=2)+'\n')
    print(json.dumps({k:v for k,v in proof.items() if k!='patches'}))

if __name__=='__main__':main()
