"""Pure pickup-source transformer plus isolated cross-object byte consistency.

No root candidate/source is changed. Import transform_sources() in the owning
builder, write its returned strings/fragments only to that builder's own root,
then perform a complete source relink/loader-cookie/native qualification.
"""
from pathlib import Path
import hashlib,json,re,subprocess,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
from private_build_outputs_v1 import validate
O=R/'build/karnov-pickup-host-component-1101-v3'
V2=R/'build/karnov-pickup-component-1101-v2'
SRC=R/'tools/reference/karnov_pickups_1101_v2.inc'
BASE=R/'build/karnov-host-resource-base-1101-v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

NATIVE=['InvPickupOwner','InvPickup','InvRisePhase','InvPickupSaveLo','InvPickupSaveHi',
        'PowerUpType','Enemy_State','Enemy_ID','Enemy_Flag','EraseEnemyObject',
        'SetupFloateyNumber','Square2SoundQueue','VRAM_Buffer1','VRAM_Buffer1_Offset',
        'FarCallCommon','FarcallJmpTarget_SMC','SafecallA_SMC','MarioSourcePowerupCollision']
CONTEXT=['KrState','KrReady','KrSaved0','KrSaved1','KrSoundEvent']
FRAGMENTS=['kr-pickup-rom-context-v3.inc','kr-pickup-rom-align-v3.inc',
           'kr-pickup-rom-tail-v3.inc','kr-pickup-kernel-v3.inc']

def _preprocess(text):
    flags={'KR_PICKUP_NATIVE_HUD':True,'KR_PICKUP_SPLIT':False}
    stack=[];active=True;result=[]
    for line in text.splitlines():
        m=re.fullmatch(r'\s*\.(ifdef|ifndef)\s+(\w+)\s*',line)
        if m:
            assert m[2]in flags,m[2]
            cond=flags[m[2]]if m[1]=='ifdef'else not flags[m[2]]
            stack.append((active,cond));active=active and cond;continue
        if line.strip()=='.else':
            parent,cond=stack[-1];stack[-1]=(parent,not cond);active=parent and not cond;continue
        if line.strip()=='.endif':
            active,_=stack.pop();continue
        if active:result.append(line)
    assert not stack
    return '\n'.join(result)+'\n'

def _span(text,first,last):
    lo=text.index(first+':\n');hi=text.index(last+':\n',lo)+len(last)+2
    return text[lo:hi]

def source_fragments(text=None):
    """Return context/inline padding/tail/kernel include strings, no writes."""
    text=_preprocess(SRC.read_text()if text is None else text)
    prefix=text[:text.index('KrPickupReset:\n')]
    constants='\n'.join(line for line in prefix.splitlines()if re.fullmatch(r'KrPickup\w+=\$[0-9a-fA-F]+',line))+'\n'
    reset=_span(text,'KrPickupReset','KrPickupResetEnd')
    align=_span(text,'KrPickupSuperFireball','KrPickupAlignEnd')
    core=_span(text,'KrPickupGrantOption','KrPickupCoreEnd')
    prepare=text[text.index('KrPickupPrepare:\n'):text.index('KrPickupMature:\n')]
    mature=_span(text,'KrPickupMature','KrPickupMatureEnd')
    collect=_span(text,'KrPickupCollect','KrPickupEnd')
    main_exports=['KrPickupPrepare','KrPickupCollect','KrPickupSuperFireball','KrPickupGrantOption',
                  'KrPickupOriginal_AD79','KrPickupOriginal_EF61','KrPickupOriginal_CF7E',
                  'KrPickupOriginal_C847','KrPickupPaletteQueue','KrPickupCoreEnd','KrPickupEnd',
                  'KrPickupAlignEnd','KrPickupMarioFallback']
    context='''; Included in the native main object: all native names are owned there.
; Only these source-context values cross from the independently linked kernel.
'''+'.import '+','.join(CONTEXT)+'\n.importzp KrPointer\n.export '+','.join(main_exports)+'\n'+constants
    fallback='''; Real native star/1UP consumer. Never use this for mushroom/flower.
KrPickupMarioFallback:
 sta SafecallA_SMC+1
 lda #<MarioSourcePowerupCollision
 sta FarcallJmpTarget_SMC+1
 lda #>MarioSourcePowerupCollision
 sta FarcallJmpTarget_SMC+2
 lda #.lobyte(.bank(MarioSourcePowerupCollision)|$80)
 jsr FarCallCommon
 rts
'''
    kernel='''; Appended inside the existing KR_KERNEL segment, before KrKernelEnd.
; Existing authenticated rows map C2/C3 before reaching these entries.
.import PowerUpType,Enemy_State,FarCallCommon,FarcallJmpTarget_SMC,SafecallA_SMC
.import KrPickupPrepare,KrPickupCollect
.export KrSaved0,KrSaved1
.export KrPickupReset,KrPickupResetEnd,KrPickupMature,KrPickupMatureEnd
.export KrPickupPrepareThunk,KrPickupCollectThunk,KrPickupKernelEnd
KrPickupCycle=$c860
'''+reset+mature
    for name,target in [('KrPickupPrepareThunk','KrPickupPrepare'),('KrPickupCollectThunk','KrPickupCollect')]:
        kernel+=f'''{name}:
 sta SafecallA_SMC+1
 lda #<{target}
 sta FarcallJmpTarget_SMC+1
 lda #>{target}
 sta FarcallJmpTarget_SMC+2
 lda #.lobyte(.bank({target})|$80)
 jmp FarCallCommon            ; tail:3 live bytes, never JSR+RTS's5
'''
    kernel+='KrPickupKernelEnd:\n'
    return dict(zip(FRAGMENTS,[context,align,core+prepare+collect+fallback,kernel]))

def transform_sources(*,kernel,resident,terrain,entrypoint,cf_menu,pickup_source=None):
    """Return revised strings and four includes; do not read/write the host."""
    assert 'kr-pickup-'not in kernel+resident+terrain,'Pickup graft already present'
    assert cf_menu.count('.include "kr-resident.inc"')==1
    assert '.res $b22-$0d-(FmCfHelperEnd-FmCfHelperStart)-(KrResidentEnd-KrResidentBegin),$ff'in cf_menu
    assert '.assert * = $bfb0'in cf_menu,'Whole source-owned resident lease must stay bounded'
    fragments=source_fragments(pickup_source)
    start=kernel.index('KrCacheServices:\n');end=kernel.index('KrReject:',start)
    block=kernel[start:end];rows=list(re.finditer(r'(?m)^ jmp (\w+)\s*$',block));assert len(rows)==37,len(rows)
    edits={20:'KrPickupPrepareThunk',23:'KrPickupMature',24:'KrPickupCollectThunk'}
    for index,target in sorted(edits.items(),reverse=True):
        m=rows[index];assert m[1]=='KrReject',(index,m[1]);block=block[:m.start(1)]+target+block[m.end(1):]
    kernel=kernel[:start]+block+kernel[end:]
    assert kernel.count('KrKernelEnd:\n')==1
    kernel=kernel.replace('KrKernelEnd:\n','.include "kr-pickup-kernel-v3.inc"\nKrKernelEnd:\n')
    anchor=' bne KrClearState\nKrKeepLife:\n';assert terrain.count(anchor)==1
    terrain=terrain.replace(anchor,' bne KrClearState\n jsr KrPickupReset         ; new life only; same-life seam bypasses\nKrKeepLife:\n')
    assert resident.count('.align 256,$ff')==1 and resident.count('KrResidentEnd:\n')==1
    resident='.include "kr-pickup-rom-context-v3.inc"\n'+resident
    resident=resident.replace('.align 256,$ff','.include "kr-pickup-rom-align-v3.inc"\n.align 256,$ff')
    resident=resident.replace('KrResidentEnd:\n','.include "kr-pickup-rom-tail-v3.inc"\nKrResidentEnd:\n')
    # Native main owns these names already; export only any missing interface
    # needed by the separate A3 kernel. Never import an own-main definition.
    existing=set()
    for line in entrypoint.splitlines():
        if line.startswith('.export '):existing.update(line[8:].split(','))
    missing=[n for n in NATIVE if n not in existing]
    if missing:entrypoint+='\n.export '+','.join(missing)+'\n'
    return dict(kernel=kernel,resident=resident,terrain=terrain,entrypoint=entrypoint,cf_menu=cf_menu,
                fragments=fragments,additional_native_exports=missing,
                required_kernel_exports=['KrSaved0','KrSaved1'],service_rows=edits,
                added_kernel_bytes=78,added_kernel_detail=dict(ResetMature=39,tail_thunks=36,new_life_JSR=3),
                expected_resident=dict(align=[0xbb48,0xbb8a],water=[0xbb8e,0xbc8e],worker=[0xbc8e,0xbf57],lease_end=0xbfb0),
                constraints=['Resident .align and CF helper .res remain sole owners; no overlapping linker segments',
                             'Real kernel append origin moves by3 from newlifeJSR; complete relink, never paste frozen absolute RAM bytes',
                             'Rows20/24 stay authenticated normal A3 services with C2mapped, then tail-farcall ROM29; never cold menu bypass',
                             'Native main object owns native symbols and fallback; kernel exports source context and pointer',
                             'Menu edits must preserve at least66B actual padding before original water table; fail full source asserts otherwise'])

def main():
    a=json.loads((V2/'assembly.json').read_text());cpu=json.loads((V2/'CPU-controls.json').read_text());assert a['passed']and cpu['passed']
    assert sha(SRC)==cpu['bindings'][str(SRC.resolve())]
    O.mkdir(exist_ok=True)
    names=dict(kernel='kr-kernel.s',resident='kr-resident.inc',terrain='kr-terrain.inc',entrypoint='entrypoint.s',cf_menu='cf_menu_body.inc')
    inputs={n:(BASE/f).read_text()for n,f in names.items()};q=transform_sources(**inputs)
    for name,text in q['fragments'].items():(O/name).write_text(text)
    # The isolated link uses the frozen v2 addresses/bank contracts only. No
    # candidate ROM is rewritten, and this is not a full-host link receipt.
    src=(V2/'component.s').read_text();constants={m[1]:int(m[2],16)for m in re.finditer(r'(?m)^(\w+)=\$([0-9a-fA-F]+)$',src)}
    frozen_host=(V2/'host-symbols.s').read_text();native={m[1]:int(m[2],16)for m in re.finditer(r'(?m)^(?:\.export )?(\w+)=\$([0-9a-fA-F]+)$',frozen_host)}
    imm=[int(x,16)for x in re.findall(r' lda #\$([0-9a-fA-F]+)',frozen_host)];assert len(imm)==3
    mario=imm[0]+256*imm[1];mario_bank=imm[2]&127
    host=''.join(f'.export {n}=${native[n]:04x}\n'for n in NATIVE if n!='MarioSourcePowerupCollision')
    host+=' .segment "MARIO"\n.export MarioSourcePowerupCollision\nMarioSourcePowerupCollision:.byte 0\n'
    (O/'native-symbols.s').write_text(host)
    native_imports='.import '+','.join(NATIVE)+'\n'
    (O/'main-fragments.s').write_text('.setcpu "6502"\n.macpack longbranch\n'+native_imports+'Sfx_PowerUpGrab=$20\nPowerUpObject=$2e\n.include "kr-pickup-rom-context-v3.inc"\n.segment "ALIGN"\n.include "kr-pickup-rom-align-v3.inc"\n.segment "WORKER"\n.include "kr-pickup-rom-tail-v3.inc"\n')
    k='.setcpu "6502"\n.macpack longbranch\n'+''.join(f'{n}=${constants[n]:04x}\n.export {n}\n'for n in CONTEXT if n not in ['KrSaved0','KrSaved1'])
    k+=''.join(f'{n}=${constants[n]:04x}\n'for n in ['KrSaved0','KrSaved1'])+'KrPointer=$03\n.exportzp KrPointer\n.segment "RAM"\n.include "kr-pickup-kernel-v3.inc"\n'
    (O/'kernel-fragments.s').write_text(k)
    (O/'fragments.cfg').write_text(f'MEMORY{{ALIGN:start=$bb48,size=$46,file=%O,bank=$1d;WORKER:start=$bc8e,size=$322,file=%O,bank=$1d;RAM:start=$bf5c,size=$84,file=%O,bank=3;MARIO:start=${mario:04x},size=1,file="",bank={mario_bank};}}SEGMENTS{{ALIGN:load=ALIGN,type=ro;WORKER:load=WORKER,type=ro;RAM:load=RAM,type=ro;MARIO:load=MARIO,type=ro;}}\n')
    cc=R/'tools/Windows/cc65/bin';commands=[]
    recipes=[[cc/'ca65.exe','-g','-I',O,O/(n+'.s'),'-o',O/(n+'.o')]for n in ['main-fragments','kernel-fragments','native-symbols']]
    recipes.append([cc/'ld65.exe','-C',O/'fragments.cfg',*[O/(n+'.o')for n in ['main-fragments','kernel-fragments','native-symbols']],'-o',O/'fragments.bin','--dbgfile',O/'fragments.dbg','-Ln',O/'fragments.lbl'])
    for recipe in recipes:
        cmd=list(map(str,recipe));guard=validate(cmd,O,cwd=R);p=subprocess.run(cmd,capture_output=True,text=True);commands.append(dict(command=cmd,guard=guard,code=p.returncode,stderr=p.stderr));assert p.returncode==0,p.stderr
    actual=(O/'fragments.bin').read_bytes();frozen=(V2/'component-split.bin').read_bytes();assert len(frozen)==818 and len(actual)==854
    assert actual[:818]==frozen,'Cross-object fragment bytes differ from final frozen split'
    labels={m[2]:int(m[1],16)for m in re.finditer(r'(?m)^al ([0-9a-fA-F]+) \.(\S+)$',(O/'fragments.lbl').read_text())}
    def word(value):return bytes([value&255,value>>8])
    expected=b''
    for target in ['KrPickupPrepare','KrPickupCollect']:
        addr=labels[target];expected+=b'\x8d'+word(native['SafecallA_SMC']+1)+bytes([0xa9,addr&255])+b'\x8d'+word(native['FarcallJmpTarget_SMC']+1)+bytes([0xa9,addr>>8])+b'\x8d'+word(native['FarcallJmpTarget_SMC']+2)+b'\xa9\x9d\x4c'+word(native['FarCallCommon'])
    assert len(expected)==36 and actual[818:]==expected
    result=dict(passed=True,pure_source_transform=True,root_modified=False,ROM_modified=False,native=False,installed=False,frozen_base=a['base_ROM_sha256'],frozen_source_trace=cpu['source_trace_sha256'],frozen_split_bytes_compared=818,new_tail_thunk_bytes_compared=36,fragment_total_bytes=len(actual),fragments=list(q['fragments']),additional_native_exports=q['additional_native_exports'],required_kernel_exports=q['required_kernel_exports'],service_rows=q['service_rows'],added_kernel_bytes=q['added_kernel_bytes'],expected_resident=q['expected_resident'],real_root_kernel_append_origin='old KrKernelEnd +3 due newlifeJSR; fragment model uses frozen BF5C only for exact byte consistency',constraints=q['constraints'],input_and_transformed_hashes={n:dict(before=hashlib.sha256(inputs[n].encode()).hexdigest(),after=hashlib.sha256(q[n].encode()).hexdigest())for n in names},commands=commands,bindings={str(p.resolve()):sha(p)for p in [Path(__file__),SRC,V2/'assembly.json',V2/'CPU-controls.json',V2/'component-split.bin',V2/'component.s',V2/'host-symbols.s',*[O/n for n in FRAGMENTS],O/'fragments.bin',O/'fragments.cfg',O/'main-fragments.s',O/'kernel-fragments.s',O/'native-symbols.s']})
    (O/'integration.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items()if k not in ['bindings','commands','input_and_transformed_hashes']}))
if __name__=='__main__':main()
