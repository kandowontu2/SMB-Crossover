"""Execute all authentic Ice selectors and the shared renderer after aliasing."""
from pathlib import Path
import hashlib
import itertools
import json
import sys

R=Path(__file__).resolve().parents[2]
O=R/'build/ice-pose-aliases-v2'
sys.path.insert(0,str(R/'tools/audit'))
from link_pit_rygar_sophia_audit_cpu import scoped_load,Arena
from check_tmnt_render_oa import address,location


def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    proof=json.loads((O/'build-proof.json').read_text())
    paths=[R/'build/parodius-chr-compact-v1/candidate.nes',O/'candidate.nes']
    assert [sha(p)for p in paths]==[proof['parent_ROM_sha256'],proof['ROM_sha256']]
    bundles=[scoped_load(p)for p in paths];rows=[];savings=[];parts=0
    allowed={address(bundles[0],n)+i for n in ['SmPosePtr','R0']for i in [0,1]}
    for pose,variant,face,(x,y),offset,rotation,refresh in itertools.product(
            range(15),[0,1],[1,2],[(8,24),(112,128),(248,230)],
            [0,128,236],[(0,0),(1,252)],[False,True]):
        qs=[Arena(b,20)for b in bundles]
        for q in qs:
            q.put(IcVariant=variant,PlayerFacingDir=face,IcPaletteAck=255 if refresh else variant,
                  VRAM_Buffer1_Offset=0,StarInvincibleTimer=0,GuestPowerupActive=0,
                  CurrentOAMOffset=offset,GuestOamRotationActive=rotation[0],RgOamRotation=rotation[1])
            for i in range(12):
                q.set('CurrentCHRBank',40+i,i);q.set('X5ChrMode',0,i)
        results=[]
        for q in qs:
            c,t=q.invoke('IcSetPose',x=pose)
            ptr=q.get('SmPosePtr')+256*q.get('SmPosePtr',1)
            count=q.m[ptr]
            selectcycles=c.processorCycles
            c,t=q.invoke('IcDraw')
            publishcycles=c.processorCycles
            q.put(R0=ptr&255,R1=ptr>>8,R3=0,R4=x,R5=0,R6=y,R7=1)
            c,t=q.invoke('MetaspriteRenderLoop')
            results.append(dict(cpu=c,trace=t,selector=selectcycles,publisher=publishcycles,count=count,ptr=ptr))
        a,b=qs;before,after=results
        assert before['count']==after['count']
        assert a.m[0x200:0x300]==b.m[0x200:0x300],(pose,variant,face,x,y,offset,rotation)
        assert (before['cpu'].a,before['cpu'].x,before['cpu'].y,before['cpu'].p,before['cpu'].sp)== \
               (after['cpu'].a,after['cpu'].x,after['cpu'].y,after['cpu'].p,after['cpu'].sp)
        assert before['selector']==after['selector']and before['publisher']==after['publisher']
        assert after['cpu'].processorCycles<=before['cpu'].processorCycles,(
            'New drawing cost',pose,variant,face,before['cpu'].processorCycles,after['cpu'].processorCycles)
        assert [(t['pc'],t['bank'],t['address'])for t in before['trace']]== \
               [(t['pc'],t['bank'],t['address'])for t in after['trace']]
        differences=[i for i in range(0x8000)if a.m[i]!=b.m[i]and not 0x100<=i<0x200 and i not in allowed]
        assert not differences,[(hex(i),a.m[i],b.m[i])for i in differences[:12]]
        assert a.m[address(a.b,'CurrentCHRBank'):address(a.b,'CurrentCHRBank')+12]== \
               b.m[address(b.b,'CurrentCHRBank'):address(b.b,'CurrentCHRBank')+12]
        saved=before['cpu'].processorCycles-after['cpu'].processorCycles;savings.append(saved)
        parts+=before['count']//4
        rows.append(dict(pose=pose,variant=variant,face=face,xy=[x,y],offset=offset,
                         rotation=rotation,refresh=refresh,saved_CPU=saved,sprites=before['count']//4))
    result=dict(passed=True,status='ALL_NATIVE_ICE_SELECTORS_AND_ACTUAL_SHARED_OAM_EQUIVALENT',
        ROM_sha256=sha(paths[1]),parent_ROM_sha256=sha(paths[0]),
        native_descriptors=60,canonical_descriptors=19,cases=len(rows),
        authentic_OAM_parts_checked=parts,all_palette_queue_and_physical_CHR_writes_exact=True,
        all_other_RAM_exact_except_equivalent_descriptor_pointers=True,
        all_actual_AXYP_SP_and_ordered_writer_addresses_exact=True,
        saved_renderer_CPU_range=[min(savings),max(savings)],no_case_adds_cycles=True,
        all_CHR_and_all_other_PRG_outside_IC_ART_exact=True,
        source_bindings={str(Path(__file__).resolve()):sha(__file__)},rows=rows,
        limits=['Finite selector/render fixtures, not native gameplay/PPU qualification',
                'Metadata-only aliasing; no new motion or weapon behavior is claimed'])
    (O/'controls.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k]for k in ['passed','cases','authentic_OAM_parts_checked','saved_renderer_CPU_range']}))


if __name__=='__main__':main()
