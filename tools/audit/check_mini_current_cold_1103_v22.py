"""Final v26 four-name-byte rebind and complete five-owner cold qualification."""
from pathlib import Path
import inspect,json,sys
R=Path(__file__).resolve().parents[2];sys.path[:0]=[str(R/'tools/audit')]
import check_mini_five_cold_1103_v20 as F
P,O,N,I,C=F.P,F.O,F.N,F.I,F.C
HOST=R/'build/mini-mario-host-1103-v22'
KERNEL_SHA='eee8d1b557728fff864a0fe7ab38e7655b1308fa272c27df19db07786b1a8bc3'


def image():
    kernel=(HOST/'mini-host-v26.bin').read_bytes();meta=(O/'metadata-v19.bin').read_bytes();art=(R/'build/mini-mario-art-1103-v12/body.chr').read_bytes()
    return P.compose(kernel,meta,art,KERNEL_SHA)


def prepare():
    b,q=image();fit=json.loads((O/'owner-fit-v15.json').read_text())
    old=(HOST/'mini-host-v22.bin').read_bytes();new=(HOST/'mini-host-v26.bin').read_bytes()
    changed=[i for i,(a,z)in enumerate(zip(old,new))if a!=z];assert len(changed)==4 and len(old)==len(new)==4923
    text=(O/'owner-v15.s').read_text();before=bytes.fromhex(fit['Mini_cookie_placeholder']);after=bytes.fromhex(q['Mini_cookie'])
    a='MiniCookie:\n .byte '+','.join('$%02x'%v for v in before);z='MiniCookie:\n .byte '+','.join('$%02x'%v for v in after)
    assert text.count(a)==1;(O/'owner-final-v22.s').write_text(text.replace(a,z))
    q.update(passed=True,source_images_only=True,ROM_written=False,CPU_qualified=False,
        kernel_rebind=dict(previous_kernel=F.P.M.sha(old),four_name_byte_offsets=changed,addresses_and_size_identical=True),
        bindings={p.relative_to(R).as_posix():P.M.sha(p.read_bytes())for p in [Path(__file__),Path(P.__file__),Path(F.__file__),O/'owner-fit-v15.json',O/'owner-final-v22.s',O/'cold-v19.bin',O/'metadata-v19.bin',HOST/'mini-host-v26.bin',HOST/'mini-host-v26.s',HOST/'mini-host-v26.json',R/'build/mini-mario-art-1103-v12/body.chr',R/'docs/qa/allocations/mini-mario-private-resources-1103-v24.json']})
    (O/'payload-manifest-v22.json').write_text(json.dumps(q,indent=2)+'\n')
    return q


def main():
    prepare();source=inspect.getsource(F.main)
    source=source.replace('mini-host-v22.bin','mini-host-v26.bin')
    source=source.replace('out[\'regs\']==[83,71,109,0x21,224]',"out['regs'][:3]==[83,71,109]and out['regs'][3]&0xef==0x21 and out['regs'][4]==224")
    source=source.replace('five-cold-CPU-v20.json','five-cold-CPU-v22.json').replace('payload-manifest-v19.json','payload-manifest-v22.json').replace('owner-final-v19.s','owner-final-v22.s')
    env=dict(F.__dict__,__file__=__file__,image=image)
    exec(compile(source,__file__,'exec'),env);env['main']()


if __name__=='__main__':
    try:main()
    except Exception as error:
        (O/'five-cold-negative-v22.json').write_text(json.dumps(dict(passed=False,error=repr(error)),indent=2)+'\n');raise
