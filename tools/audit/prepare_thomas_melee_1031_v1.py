"""Source-link original Thomas body/melee geometry in the isolated source lab."""
from pathlib import Path
import argparse,hashlib,json,shutil,subprocess,sys
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(Path(__file__).resolve().parent))
import thomas_original_cpu_1031_v1 as t
from prepare_thomas_component_1031_v3 import code
from private_build_outputs_v1 import validate
P=R/'build/thomas-original-component-v5';O=R/'build/thomas-melee-component-v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
dump=lambda p,v:Path(p).write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8')

def main():
    global O
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,default=O);args=ap.parse_args();O=args.output.resolve()
    assert not O.exists();O.mkdir(parents=True);(O/'source').mkdir()
    assert sha(P/'source-stage.json')=='5fbb2358fb8b5a8dcc9a3c0744899095737b6bef0ae9fc19e67dd620f14a71d0'
    c=t.machine();body,bi,bc=code(c,0xc0b6,0xc125,'ThGeom');strike,si,sc=code(c,0xc65b,0xc6fe,'ThGeom')
    data=[]
    for lo,hi in [(0xbb94,0xbbb4),(0xbc0c,0xbc24)]:
        for a in range(lo,hi):data.append(f'ThomasOriginal_{a:04X}: .byte ${c.memory[a]:02X}')
    imports=bi|si;assert all((0xbb94<=v<0xbbb4)or(0xbc0c<=v<0xbc24)for v in imports.values()),imports
    # Body and overlap are contiguous in the donor. The query below returns a
    # typed Boolean from the actual C208..<C224 attack-window branch predicate.
    query='''
 .export ThomasAttackActive
ThomasAttackActive:
 lda $69
 cmp #$0f
 bcc ThomasAttackInactive
 and #4
 bne ThomasAttackYes
 lda $68
 cmp #1
 beq ThomasAttackYes
ThomasAttackInactive:
 lda #0
 rts
ThomasAttackYes:
 lda #1
 rts
'''
    (O/'source/melee.s').write_text(''' .setcpu "6502"
 .export ThomasBodyBox,ThomasAttackBox,ThomasOverlap
 ThomasBodyBox=ThGeom_C0B6
 ThomasOverlap=ThGeom_C0F3
 ThomasAttackBox=ThGeom_C65B
 .segment "THOMAS_GEOM"
'''+body+strike+query+' .segment "THOMAS_GEOM_TABLES"\n'+'\n'.join(data)+'\n',encoding='utf-8')
    cfg=(P/'source/component.cfg').read_text(encoding='utf-8').replace('start=$6800;','start=$6800; THOMAS_GEOM: load=LAB,type=ro,start=$6a00; THOMAS_GEOM_TABLES: load=LAB,type=ro,start=$6c00;')
    (O/'source/component.cfg').write_text(cfg,encoding='utf-8')
    cc=R/'tools/Windows/cc65/bin';commands=[]
    def run(cmd):
        g=validate(cmd,O,cwd=O);p=subprocess.run([str(v)for v in cmd],cwd=O,capture_output=True,text=True);commands.append(dict(command=[str(v)for v in cmd],guard=g,returncode=p.returncode,stderr=p.stderr));assert not p.returncode,p.stderr
    run([cc/'ca65.exe',O/'source/melee.s','-g','-o',O/'melee.o','-l',O/'melee.lst','--create-full-dep',O/'melee.dep'])
    run([cc/'ld65.exe','-C',O/'source/component.cfg',P/'component.o',P/'health.o',P/'lab_native_import.o',O/'melee.o','-o',O/'component.bin','--dbgfile',O/'component.dbg','-Ln',O/'component.lbl','-m',O/'component.map'])
    # Preserve every existing source-core/health/table byte outside this child.
    before=(P/'component.bin').read_bytes();after=(O/'component.bin').read_bytes()
    assert after[:0xa00]==before[:0xa00]and after[0xc38:]==before[0xc38:]
    dump(O/'build-commands.json',commands)
    dump(O/'component-api.json',dict(status='ISOLATED_THOMAS_SOURCE_NO_HOST_ALLOCATION',parent_source_stage=sha(P/'source-stage.json'),
      genuine_geometry_bytes=274,tables_bytes=56,query_bytes=24,
      source_ranges=['C0B6..<C125 body+inclusiveAABB','C65B..<C6FE stance/facing melee rectangle','BB94..<BBB4 body bounds','BC0C..<BC24 melee bounds'],
      entries=dict(ThomasBodyBox='X selects scratch rectangle offset;94 screenX;69 stance;68 airphase; outputs00+X..03+X',
          ThomasAttackBox='0A rectangle scratch offset, X native actor slot;69 stance/facing;94 screenX; writes0379 attackkind and rectangle; returns original actorX',
          ThomasOverlap='00..03 and04..07 inclusive rectangles; returns1 overlapping/0 separate',
          ThomasAttackActive='Typed Boolean from genuine C208 branch: attack69>=0F AND (airbit4 OR phase68==1). Adapter query; not original callbackAXYP ABI'),
      integration='Reuse this real window/geometry before native host damage/defeat, not a permanent generic Ryu hitbox. No enemy pool, boss, healthupgrade or host contact hooks are installed.',
      packed_payload_floor=1204+166+411+274+56+24+4672+1230,
      storage_warning='This is source/data size only, not an8KB allocation proof; host adapters, lifecycle, wrappers and per-pose CHR packing still require measured resources.',
      bindings={str(p):sha(p)for p in [Path(__file__),P/'source-stage.json',P/'component.o',P/'health.o',P/'lab_native_import.o',O/'source/melee.s',O/'source/component.cfg',O/'component.bin',O/'component.lbl',O/'build-commands.json']}))
    dump(O/'source-stage.json',dict(result='SOURCE_LINKED',source_api_sha256=sha(O/'component-api.json'),files={str(p):sha(p)for p in O.rglob('*')if p.is_file()and p.suffix!='.o'}))
    print(json.dumps(dict(result='PASS',source_stage_sha256=sha(O/'source-stage.json'),component_sha256=sha(O/'component.bin'))))

if __name__=='__main__':main()
