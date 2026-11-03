"""Complete the owning pickup callback through the genuine native collector."""
import inspect,json
from pathlib import Path
import prepare_bub_original_upgrades_1102_v48 as U
from check_tmnt_render_oa import location
R=U.R;O=R/'build/bub-upgrades-root-1102-v56';PIN=U.PIN;labels=U.labels

def main():
    text=inspect.getsource(U.main);assert text.count('image[14*3:14*3+3]')==1
    text=text.replace('image[14*3:14*3+3]','image[24*3:24*3+3]')
    marker="    worker,wl=assemble('pickup',pickup,"
    assert text.count(marker)==1
    added='''    native_pc=address(bundle,'MarioSourcePowerupCollision');native_bank=((location(bundle,'MarioSourcePowerupCollision')-16)//8192)|128
    gateway=f' sta $016a\\n lda #${native_pc&255:02x}\\n sta $016c\\n lda #${native_pc>>8:02x}\\n sta $016d\\n lda #${native_bank:02x}\\n jsr $015a\\n sec\\n rts\\nPickupImmature:'
    assert pickup.count(' clc\\n rts\\nPickupImmature:')==1
    pickup=pickup.replace(' clc\\n rts\\nPickupImmature:',gateway)
'''
    text=text.replace(marker,added+marker)
    env=dict(U.__dict__,O=O,__file__=str(Path(__file__)),location=location);exec(compile(text,str(Path(__file__)),'exec'),env);env['main']()
    path=O/'proposal.json';q=json.loads(path.read_text());q['public_pickup_row']=24;q['native_side_row14_retained']=True
    q['retained_negative']='v53 rare classifier absent;v55 joint classifier reaches owning24 and original flags but native item remains. Native rare pickup does not run generic bookkeeping after C0. Owner must invoke genuine MarioSourcePowerupCollision itself.'
    q['scope']='Private image only: original-flag upgrade adapter24 maps mushroom->originalitem4 bit01,flower->item2 bits06. After restoring AXYP it explicitly calls genuine native MarioSourcePowerupCollision for all mature pickups and returnsSEC; this supplies item erase, native bookkeeping/SFX/power animation,star/1up. Immature regular pickups restoreAXYP andclaimwithoutconsuming. Direct-onlyC0 fallback fromv51 is superseded. Full native ingress/effects/lifecycle/ISR/render/fullstage remain unqualified.'
    q['bindings'][str(Path(U.__file__).relative_to(R))]=U.sha(Path(U.__file__));path.write_text(json.dumps(q,indent=2)+'\n')
if __name__=='__main__':main()
