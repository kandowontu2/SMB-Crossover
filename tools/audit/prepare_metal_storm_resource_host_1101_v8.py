"""Compile bounded split cold-loader and world-window correction proposals."""
from pathlib import Path
import hashlib,json,re,subprocess,sys
ROOT=Path(__file__).resolve().parents[2];sys.path[:0]=[str(ROOT/'tools/audit'),str(ROOT/'tools')]
from private_build_outputs_v1 import validate
import audit_metal_storm_resource_host_1101_v8 as A
OUT=A.OUT;V7=A.V7;REF=ROOT/'tools/reference/metal_storm_resource_host_1101_v8.inc'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    ownership=json.loads((OUT/'ownership.json').read_text());assert ownership['passed']and not ownership['granted']
    for p,h in ownership['bindings'].items():assert sha(p)==h,p
    stage=json.loads((V7/'source-stage.json').read_text());assert stage['passed']and sha(V7/'source-proof.zip')==stage['archive_sha256']
    render=(ROOT/'tools/reference/metal_storm_render_host_1101_v7.inc').read_text()
    needle='ora #1                     ; spriteP1/window4';assert render.count(needle)==1;render=render.replace(needle,'ora #0                     ; selected-player P0/window0; world4 retained')
    needle=' ldy #4\n MsRFar X5SetPhysicalChr';assert render.count(needle)==1;render=render.replace(needle,' ldy #0\n MsRFar X5SetPhysicalChr')
    needle='ora #$81                   ; spriteP1/window6';assert render.count(needle)==1;render=render.replace(needle,'ora #$a1                   ; window6, last bodypage patterns16..20')
    render=render[:render.index('.segment "GATE"')].replace('.export MsRenderGate,MsColorsGate,MsGraphicsGate,MsGateEnd\n','')
    (OUT/'renderer-adapted.inc').write_text(render)
    (OUT/'renderer.s').write_text('.setcpu "6502"\n.macpack longbranch\n.import MsState,MsLifeUnsupported\n.include "renderer-adapted.inc"\n')
    (OUT/'loader.s').write_text('.setcpu "6502"\n.macpack longbranch\n.include "metal_storm_resource_host_1101_v8.inc"\n')
    symbols=(V7/'symbols.s').read_text()
    for i in range(5):symbols=symbols.replace(f'MsBodyPhysical{i}={800+i}',f'MsBodyPhysical{i}={495+i}')
    symbols=symbols.replace('MsShotPhysical=805','MsShotPhysical=499')
    w=json.loads((OUT/'native-witness.json').read_text());existing=set(re.findall(r'^\.export(?:zp)? (\w+)=',symbols,re.M))
    for name in 'FamilyMainCommit DisableScreenFlag Mirror_PPUMASK Mirror_PPUCTRL NmiDisable HorizontalScroll VerticalScroll NextBank_SMC SafereturnA_SMC X5PublishChr ReloadCHRBank'.split():
        if name not in existing:symbols+=f'.export {name}=${int(w["syms"][name]["val"],0):04x}\n'
    (OUT/'symbols.s').write_text(symbols)
    body=(V7/'body.chr').read_bytes();shots=(V7/'shots.chr').read_bytes();assert not any(body[4608:]);(OUT/'body-packed.chr').write_bytes(body[:4608]+shots[:160]+bytes(352))
    mem=[f'ACTOR:start=$a000,size=$1fe0,bank=3,file="{(OUT/"actor.bin").as_posix()}";',f'RENDER:start=$cd00,size=$12e0,bank=2,file="{(OUT/"render.bin").as_posix()}";'];seg=['CODE:load=ACTOR,type=ro;','RENDER:load=RENDER,type=ro;']
    for h in ownership['PRG_proposals']:
        name='GATE'if h['role']=='GATE'else'MS8_'+h['role'];mem.append(f'{name}_MEM:start=${h["A_PC"]:04x},size=${h["bytes"]:x},bank={h["bank"]},file="{(OUT/(h["role"].lower()+".bin")).as_posix()}";');seg.append(f'{name}:load={name}_MEM,type=ro;')
    (OUT/'resource.cfg').write_text('MEMORY{'+''.join(mem)+'}SEGMENTS{'+''.join(seg)+'}\n')
    for name in ['cookie.bin','actor-cookie.bin','render-cookie.bin']:(OUT/name).write_bytes(bytes(16))
    cc=ROOT/'tools/Windows/cc65/bin';commands=[]
    def compile():
        for name,source in [('actor',V7/'actor.s'),('renderer',OUT/'renderer.s'),('loader',OUT/'loader.s'),('symbols',OUT/'symbols.s')]:
            cmd=[cc/'ca65.exe','-g','-I',OUT,'-I',V7,'--bin-include-dir',OUT,'--bin-include-dir',V7,'-I',ROOT/'build/metal-storm-objects-host-1101-v6','-I',ROOT/'build/metal-storm-terrain-host-1101-v5','-I',ROOT/'tools/reference',source,'-o',OUT/(name+'.o')]
            g=validate(cmd,OUT,cwd=ROOT);r=subprocess.run(list(map(str,cmd)),capture_output=True,text=True);commands.append(dict(command=list(map(str,cmd)),guard=g,returncode=r.returncode,stderr=r.stderr));assert r.returncode==0,r.stderr
        cmd=[cc/'ld65.exe','-C',OUT/'resource.cfg',OUT/'actor.o',OUT/'renderer.o',OUT/'loader.o',OUT/'symbols.o','-o',OUT/'unused.bin','--dbgfile',OUT/'resource.dbg','-Ln',OUT/'resource.lbl']
        g=validate(cmd,OUT,cwd=ROOT);r=subprocess.run(list(map(str,cmd)),capture_output=True,text=True);commands.append(dict(command=list(map(str,cmd)),guard=g,returncode=r.returncode,stderr=r.stderr));assert r.returncode==0,r.stderr
    compile();actor=(OUT/'actor.bin').read_bytes();renderer=(OUT/'render.bin').read_bytes();cookie=bytes([167,35,8])+hashlib.sha256(actor+renderer+(OUT/'body-packed.chr').read_bytes()+REF.read_bytes()).digest()[:13]
    for name in ['cookie.bin','actor-cookie.bin','render-cookie.bin']:(OUT/name).write_bytes(cookie)
    compile();assert actor==(OUT/'actor.bin').read_bytes()and renderer==(OUT/'render.bin').read_bytes()
    image=bytearray([255])*8192;image[:len(actor)]=actor;image[0x1fe0:0x1ff0]=bytes(16)
    (OUT/'carrier-pack.bin').write_bytes(image+renderer+bytes(3072-len(renderer)))
    labels={m[2]:int(m[1],16)for line in(OUT/'resource.lbl').read_text().splitlines()if(m:=re.fullmatch(r'al ([0-9a-fA-F]+) \.(\S+)',line))}
    actual=[]
    for h in ownership['PRG_proposals']:
        size=(OUT/(h['role'].lower()+'.bin')).stat().st_size;assert size<=h['bytes'];actual.append(dict(role=h['role'],bank=h['bank'],PC=h['A_PC'],compiled_bytes=size,proposed_bytes=h['bytes'],remaining=h['bytes']-size))
    files=[Path(__file__),REF,ROOT/'tools/audit/audit_metal_storm_resource_host_1101_v8.py',V7/'source-stage.json',V7/'source-proof.zip',V7/'actor.s',V7/'symbols.s',ROOT/'tools/reference/metal_storm_render_host_1101_v7.inc',OUT/'ownership.json',OUT/'native-witness.json',OUT/'renderer-adapted.inc',OUT/'renderer.s',OUT/'loader.s',OUT/'symbols.s',OUT/'resource.cfg',OUT/'body-packed.chr',OUT/'cookie.bin']
    result=dict(passed=True,native=False,installed=False,granted=False,actor_bytes=len(actor),renderer_bytes=len(renderer),ROM_fragments=actual,total_ROM_fragment_bytes=sum(x['compiled_bytes']for x in actual),labels=labels,commands=commands,bindings={str(p.resolve()):sha(p)for p in files},scope='Actual compilable9-hole loader/gate proposal, exact5page packed original art and corrected sprite windows0/5/6; no current source/ROM edit or resource grant.')
    (OUT/'assembly.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items()if k not in['labels','commands','bindings']}))
if __name__=='__main__':main()
