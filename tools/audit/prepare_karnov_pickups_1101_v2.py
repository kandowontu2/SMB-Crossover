"""Assemble independent source/native pickup component; never change host ROM."""
from pathlib import Path
import hashlib,json,re,subprocess,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit'),str(R/'tools')]
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location
from private_build_outputs_v1 import validate
from recover_karnov_actor_1101_v1 import ROM,EXPECTED
O=R/'build/karnov-pickup-component-1101-v2';BASE=R/'build/karnov-host-resource-base-1101-v1'
SRC=R/'tools/reference/karnov_pickups_1101_v2.inc'
PIN='993d4489b6f944ea42646fda33d046357deb7088332038b97327d3e094f6d6e0'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    assert sha(BASE/'candidate.nes')==PIN,'Mutable parent base changed; pin a terminal base explicitly'
    assert sha(ROM)==EXPECTED
    O.mkdir(exist_ok=True);b=scoped_load(BASE/'candidate.nes')
    imported=[]
    for line in SRC.read_text().splitlines():
        if line.startswith('.import '):imported+=line[8:].split(',')
    context=['KrState','KrReady','KrSoundEvent','KrSaved0','KrSaved1']
    start=0xb000
    (O/'component.s').write_text('.setcpu "6502"\n.macpack longbranch\n'+''.join(f'{n}=${address(b,n):04x}\n'for n in context)+f'KrPointer=${address(b,"R0"):02x}\nSfx_PowerUpGrab=$20\nPowerUpObject=$2e\n.segment "PICKUP"\n.include "karnov_pickups_1101_v2.inc"\n')
    host=''.join(f'.export {n}=${address(b,n):04x}\n'for n in imported if n!='KrPickupMarioFallback')
    # This native fallback worker runs the actual original star/1UP consumer;
    # its real bank/entry and SMC helpers are pinned to this base, not guessed.
    for n in ['SafecallA_SMC','FarcallJmpTarget_SMC','FarCallCommon']:
        host+=f'{n}=${address(b,n):04x}\n'
    target=address(b,'MarioSourcePowerupCollision');bank=((location(b,'MarioSourcePowerupCollision')-16)//8192)|128
    host+=f'''.export KrPickupMarioFallback
.segment "PICKUP"
KrPickupMarioFallback:
 sta SafecallA_SMC+1
 lda #${target&255:02x}
 sta FarcallJmpTarget_SMC+1
 lda #${target>>8:02x}
 sta FarcallJmpTarget_SMC+2
 lda #${bank:02x}
 jsr FarCallCommon
 rts
'''
    (O/'host-symbols.s').write_text(host)
    (O/'component.cfg').write_text('MEMORY{LAB:start=$b000,size=$0800,file=%O;}SEGMENTS{PICKUP:load=LAB,type=ro;}\n')
    cc=R/'tools/Windows/cc65/bin';commands=[]
    for name in ['component','host-symbols']:
        cmd=list(map(str,[cc/'ca65.exe','-g','-I',R/'tools/reference',O/(name+'.s'),'-o',O/(name+'.o')]))
        guard=validate(cmd,O,cwd=R);q=subprocess.run(cmd,capture_output=True,text=True);commands.append(dict(command=cmd,guard=guard,code=q.returncode,stderr=q.stderr));assert q.returncode==0,q.stderr
    cmd=list(map(str,[cc/'ld65.exe','-C',O/'component.cfg',O/'component.o',O/'host-symbols.o','-o',O/'component.bin','--dbgfile',O/'component.dbg','-Ln',O/'component.lbl']))
    guard=validate(cmd,O,cwd=R);q=subprocess.run(cmd,capture_output=True,text=True);commands.append(dict(command=cmd,guard=guard,code=q.returncode,stderr=q.stderr));assert q.returncode==0,q.stderr
    def getlabels(path):
        values={}
        for line in path.read_text().splitlines():
            m=re.fullmatch(r'al ([0-9a-fA-F]+) \.(\S+)',line)
            if m:values[m[2]]=int(m[1],16)
        return values
    labels=getlabels(O/'component.lbl')
    (O/'component-thin.s').write_text('KR_PICKUP_NATIVE_HUD=1\n'+(O/'component.s').read_text())
    thinrecipes=[[cc/'ca65.exe','-g','-I',R/'tools/reference',O/'component-thin.s','-o',O/'component-thin.o'],[cc/'ld65.exe','-C',O/'component.cfg',O/'component-thin.o',O/'host-symbols.o','-o',O/'component-thin.bin','--dbgfile',O/'component-thin.dbg','-Ln',O/'component-thin.lbl']]
    for recipe in thinrecipes:
        cmd=list(map(str,recipe));guard=validate(cmd,O,cwd=R);q=subprocess.run(cmd,capture_output=True,text=True);commands.append(dict(command=cmd,guard=guard,code=q.returncode,stderr=q.stderr));assert q.returncode==0,q.stderr
    tl=getlabels(O/'component-thin.lbl')
    # Source-only placement qualification in genuine existing leases. This
    # does NOT modify those host bytes or qualify a complete relinked image.
    align=address(b,'KrCookie')+16;table=address(b,'KrMarioWaterProductHi');worker=address(b,'KrResidentEnd');ram=address(b,'KrKernelEnd')
    assert(table-align,0xbfb0-worker,0xbfe0-ram)==(70,802,132)
    (O/'component-split.s').write_text('KR_PICKUP_SPLIT=1\nKR_PICKUP_NATIVE_HUD=1\n'+(O/'component.s').read_text())
    (O/'component-split.cfg').write_text(f'MEMORY{{ALIGN:start=${align:04x},size=${table-align:04x},file=%O;WORKER:start=${worker:04x},size=${0xbfb0-worker:04x},file=%O;RAM:start=${ram:04x},size=${0xbfe0-ram:04x},file=%O;}}SEGMENTS{{KR_PICKUP_ALIGN:load=ALIGN,type=ro;PICKUP:load=WORKER,type=ro;KR_PICKUP_RAM:load=RAM,type=ro;}}\n')
    recipes=[[cc/'ca65.exe','-g','-I',R/'tools/reference',O/'component-split.s','-o',O/'component-split.o'],[cc/'ld65.exe','-C',O/'component-split.cfg',O/'component-split.o',O/'host-symbols.o','-o',O/'component-split.bin','--dbgfile',O/'component-split.dbg','-Ln',O/'component-split.lbl']]
    for recipe in recipes:
        cmd=list(map(str,recipe));guard=validate(cmd,O,cwd=R);q=subprocess.run(cmd,capture_output=True,text=True);commands.append(dict(command=cmd,guard=guard,code=q.returncode,stderr=q.stderr));assert q.returncode==0,q.stderr
    sl=getlabels(O/'component-split.lbl');alignBytes=sl['KrPickupAlignEnd']-sl['KrPickupSuperFireball'];ramBytes=(sl['KrPickupResetEnd']-sl['KrPickupReset'])+(sl['KrPickupMatureEnd']-sl['KrPickupMature']);workerBytes=len((O/'component-split.bin').read_bytes())-alignBytes-ramBytes
    assert alignBytes==66 and workerBytes<=802 and ramBytes==39,(alignBytes,workerBytes,ramBytes)
    pieces=[dict(name='ROM29align',origin=align,bytes=alignBytes,file_offset=0,capacity=70),dict(name='ROM29tail',origin=worker,bytes=workerBytes,file_offset=alignBytes,capacity=802),dict(name='RAM3spare',origin=ram,bytes=ramBytes,file_offset=alignBytes+workerBytes,capacity=132)]
    result=dict(passed=True,component_only=True,native=False,installed=False,host_modified=False,base_ROM_sha256=PIN,donor_sha256=EXPECTED,origin=start,bytes=len((O/'component.bin').read_bytes()),core_bytes=labels['KrPickupCoreEnd']-start,native_adapter_bytes=labels['KrPickupEnd']-labels['KrPickupCoreEnd'],native_fallback_bytes=len((O/'component.bin').read_bytes())-(labels['KrPickupEnd']-start),labels=labels,thin_labels=tl,thin_bytes=len((O/'component-thin.bin').read_bytes()),split_labels=sl,split_placement=pieces,required_native_exports=imported,source_context_constants=context+['KrPointer'],private_scratch=list(range(0xc860,0xc865)),source_pointer_ZP=[address(b,'R0'),address(b,'R0')+1],new_life_hook='KrPickupReset after original state clear; same-life scene seam retains cycle',services={20:'KrPickupPrepare',23:'KrPickupMature',24:'KrPickupCollect'},commands=commands,bindings={str(p.resolve()):sha(p)for p in[Path(__file__),SRC,BASE/'candidate.nes',BASE/'candidate.dbg',ROM,R/'tools/audit/private_build_outputs_v1.py',cc/'ca65.exe',cc/'ld65.exe',*[p for p in O.iterdir()if p.is_file()and p.name not in ['assembly.json','CPU-controls.json','handoff.json','source-proof.zip']]]})
    (O/'assembly.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items()if k not in ['bindings','commands','labels','thin_labels','split_labels']}))
if __name__=='__main__':main()
