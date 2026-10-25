"""Check decoded poses against the cartridge's actual OAM drawing program."""
from pathlib import Path
import importlib.util
import json

ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('pn_art',ROOT/'tools/reference/export_parodius_art.py')
art=importlib.util.module_from_spec(spec);spec.loader.exec_module(art)
from py65.devices.mpu6502 import MPU


def main():
    raw,_=art.native.source_cpu()
    prg=raw[16:131088]
    cpu=MPU();cpu.memory[0x8000:0xc000]=prg[4*8192:6*8192]
    passed=0;source_sprites=0
    cases=[(group,frame,record)for group in (0,1)for frame,record in art.records(raw,group).items()]
    for group,frame,record in cases:
        for override in range(4):
            cpu.memory[:0x8000]=[0]*0x8000
            cpu.memory[0x200:0x300]=[0xee]*256
            cpu.memory[0x01]=64
            cpu.memory[0x1f]=255 # avoid source per-frame OAM suppression
            cpu.memory[0x63e0]=1
            cpu.memory[0x6260]=96
            cpu.memory[0x62c0]=80
            cpu.memory[0x6440]=override
            cpu.memory[0x66e0]=group
            cpu.a=frame;cpu.x=0;cpu.y=0;cpu.p=0x30
            cpu.sp=0xfd;cpu.memory[0x1fe]=0xef;cpu.memory[0x1ff]=0x7f
            cpu.pc=0x85d9
            steps=0
            while cpu.pc!=0x7ff0:
                cpu.step();steps+=1
                assert steps<20000,(frame,override,'native renderer did not return',hex(cpu.pc))
            actual=[]
            for slot in range(64):
                y,tile,attr,x=cpu.memory[0x200+slot*4:0x204+slot*4]
                if y!=0xee:actual.append((y,tile,attr,x))
            expected=[((80+part['dy'])&255,part['tile'],
                       (part['attr']&0xc0)|override if override else part['attr'],
                       (96+part['dx'])&255) for part in record['parts']]
            assert sorted(actual)==sorted(expected),(group,frame,override,actual,expected)
            passed+=1;source_sprites+=len(expected)
    output=ROOT/'build/verification/parodius-native-ni/art-oracle.json'
    report=dict(source_sha256=art.native.SHA,frames=len(cases),groups=[0,1],palette_cases=passed,
                source_OAM_sprites=source_sprites,all_original_records_match=True,
                cpu_renderer_entry=0x85d9,prg_banks=[4,5],
                scope='Exact original relative offsets, tiles, hardware flip bits and palette override; not a packed-ROM or gameplay test.')
    output.write_text(json.dumps(report,indent=2)+'\n')
    print('PASS',passed,'native pose/palette cases;',source_sprites,'OAM sprites')


if __name__=='__main__':main()
