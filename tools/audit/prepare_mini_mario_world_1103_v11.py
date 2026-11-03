"""Select only indispensable source headers and relocate the proven842B core.

All addresses are proposed private fixture addresses, not native allocation.
No cartridge, menu, shared source or emulator output is produced.
"""
from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED
import base64,hashlib,json,re,subprocess
from py65.devices.mpu6502 import MPU

R=Path(__file__).resolve().parents[2];O=R/'build/mini-mario-world-1103-v11'
REF=R/'docs/qa/checkpoints/2026-11-02/mini-mario-reference-v1/reference.zip'
VERT=R/'docs/qa/checkpoints/2026-11-03/mini-mario-vertical-v8/inputs.zip'
CORE='49563d9ab3e8d78e10b0fc7b0797f23676d3045f'
GBVM='0757ea9ffb28969beb1f5502337cbd2560b8a34c'
sha=lambda data:hashlib.sha256(data).hexdigest()
EXTERNAL=[('chrismaltby/gb-studio',CORE,'src/lib/project/loadSpriteData.ts','f9cdbbd4c644705ff49e545b47d7b7d9fbf9d730'),('chrismaltby/gb-studio',CORE,'src/shared/lib/entities/entitiesTypes.ts','7754ae6f64ad24daa460690508ce30b51d636cce'),('chrismaltby/gbvm',GBVM,'include/collision.h','f050d5cf8f2173d5fb72cb5e57c46dbb66fa0a86'),('chrismaltby/gbvm',GBVM,'include/gbs_types.h','5232021edc87a1652ccc8fe09bd8bd0bdb7946ce'),('chrismaltby/gbvm',GBVM,'include/math.h','e9e3074b1b039b20b4fabc5cef1dba7ab55f4605')]


def api(repo,route):return json.loads(subprocess.check_output(['gh','api','repos/'+repo+'/'+route]))


def sources():
    with ZipFile(O/'selected-inputs-v11.zip')as z:return {n:z.read(n)for n in z.namelist()}


def assemble(stem,source,start=0xa000):
    p=O/stem;p.with_suffix('.s').write_text(source);p.with_suffix('.cfg').write_text('MEMORY{P:start=$%04x,size=$1fe0,file=%%O;}SEGMENTS{CODE:load=P,type=ro;}'%start)
    cc=R/'tools/Windows/cc65/bin'
    for cmd in [[cc/'ca65.exe',p.with_suffix('.s'),'-o',p.with_suffix('.o')],[cc/'ld65.exe','-C',p.with_suffix('.cfg'),p.with_suffix('.o'),'-o',p.with_suffix('.bin'),'-Ln',p.with_suffix('.lbl')]]:
        c=subprocess.run(list(map(str,cmd)),capture_output=True,text=True);assert c.returncode==0,c.stderr
    L={n:int(v,16)for v,n in re.findall(r'^al ([0-9A-Fa-f]+) \.(\S+)$',p.with_suffix('.lbl').read_text(),re.M)}
    return p.with_suffix('.bin').read_bytes(),L


def main():
    O.mkdir(exist_ok=True);assert sha(REF.read_bytes())=='bd61928508a253037e420a1bbd18a8ee7e68679a5632b9ded23b2aa84a8dc543'
    assert sha(VERT.read_bytes())=='f3cad6b0782406f22b3e16cbb5e7fe2ed1e8236a543e2a4c68bd75ddebc720ba'
    chosen={};provenance={};trees={}
    with ZipFile(REF)as z:
        for path in ['plugins/PlatformerPlus/engine/src/states/platform.c','plugins/PlatformerPlus/engine/src/states/playerstates.c','plugins/PlatformerPlus/engine/include/states/platform.h','plugins/PlatformerPlus/engine/include/states/playerstates.h']:
            chosen['Mini/'+path]=z.read(path)
    for repo,tree,path,blob in EXTERNAL:
        if(repo,tree)not in trees:
            q=api(repo,'git/trees/'+tree+'?recursive=1');assert not q.get('truncated');trees[repo,tree]={r['path']:r for r in q['tree']}
        assert trees[repo,tree][path]['sha']==blob
        q=api(repo,'git/blobs/'+blob);data=base64.b64decode(q['content']);assert hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()==blob
        name=repo+'/'+path;chosen[name]=data;provenance[name]=dict(tree_or_commit=tree,git_blob=blob,SHA256=sha(data),bytes=len(data))
    assert trees['chrismaltby/gb-studio',CORE]['appData/engine/gbvm']['sha']==GBVM
    archive=O/'selected-inputs-v11.zip'
    with ZipFile(archive,'w',ZIP_DEFLATED,compresslevel=9)as z:
        for name,data in chosen.items():z.writestr(name,data)
    with ZipFile(VERT)as z:
        source=z.read('build/mini-mario-motion-1103-v5/motion-xy.s').decode();old=z.read('build/mini-mario-motion-1103-v5/motion-xy.bin');oldlabels=z.read('build/mini-mario-motion-1103-v5/motion-xy.lbl').decode()
    assert len(old)==842 and sha(old)=='aadbb7eb45b0c00e92f1c39a4e16d10b8a6f7f21207e05a127a47f50d898d598'
    source=re.sub(r'\$02([0-3][0-9A-Fa-f])',lambda m:'$C2'+m[1],source)
    new,L=assemble('motion-proposed-v11',source);assert len(new)==842
    size={'imp':1,'acc':1,'imm':2,'zpg':2,'zpx':2,'zpy':2,'inx':2,'iny':2,'rel':2,'abs':3,'abx':3,'aby':3,'ind':3};i=0;instructions=0;translated=0
    while i<len(old):
        assert new[i]==old[i];op,mode=MPU.disassemble[old[i]];n=size[mode];a=int.from_bytes(old[i+1:i+n],'little');b=int.from_bytes(new[i+1:i+n],'little');wanted=a
        if n==3:
            if 0x0200<=a<=0x0230:wanted=a+0xc000
            elif 0x8000<=a<0x8000+842:wanted=a+0x2000
        assert b==wanted,(hex(i),op,mode,a,b,wanted);translated+=a!=b;instructions+=1;i+=n
    flags=chosen['chrismaltby/gbvm/include/collision.h'].decode();types=chosen['chrismaltby/gbvm/include/gbs_types.h'].decode();loader=chosen['chrismaltby/gb-studio/src/lib/project/loadSpriteData.ts'].decode()
    selected_lines={name:[dict(line=i+1,text=line)for i,line in enumerate(data.decode().splitlines())if any(word in line for word in ['COLLISION_','bounds','canvasOrigin','point16_t','direction_e'])]for name,data in chosen.items()if name.startswith('chrismaltby/')}
    out=dict(passed=True,source_inputs_only=True,ROM_written=False,native_allocation=False,menu_admitted=False,source_tree='56d5a30ff8f58096c074ca59656efc5f787d0edb',core_tree=CORE,actual_gbvm_submodule_commit=GBVM,archive_bytes=archive.stat().st_size,archive_SHA256=sha(archive.read_bytes()),selected_files=len(chosen),selected_uncompressed_bytes=sum(map(len,chosen.values())),external_provenance=provenance,motion=dict(bytes=842,old_SHA256=sha(old),proposed_SHA256=sha(new),instructions=instructions,translated_operands=translated,proposed_code=[0xa000,0xa000+842],proposed_state=[0xc200,0xc231],opcode_and_relative_controlflow_exact=True,labels=L),source_relevant_lines=selected_lines,scope='Only fourdirect Mini stateinputs plus fiveofficialpinnedGBS/GBVMheaders/loader/types. No whole tree/archive extraction. Same842B originalmotion instructions with typedRAM+codeaddress translation only. Full dispatch/collision/actor lifecycle and originalC/6502 tests remain successorwork.',bindings={p.relative_to(R).as_posix():sha(p.read_bytes())for p in [Path(__file__),REF,VERT,R/'docs/qa/mini-mario-source-1102.md',R/'tools/audit/port_mini_mario_ground_x_1103_v2.py',R/'tools/audit/port_mini_mario_air_y_1103_v5.py']})
    (O/'world-inputs-v11.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:out[k]for k in ['passed','selected_files','selected_uncompressed_bytes','archive_bytes','archive_SHA256','motion']}));print(json.dumps(selected_lines))


if __name__=='__main__':main()
