"""Rebind the separate menu/scene proposal to root-approved current80d3.

No recipe emits a ROM. Full101/83 source remains read-only.
"""
from pathlib import Path
import inspect,json
import measure_dkjr_current_scene_1103_v4 as S
import prepare_bub_combined_auth_review_1103_v90 as A
R,O,N,F,V=S.R,S.O,S.N,S.F,S.V
sha,off,address=S.sha,S.off,S.address


def stage():
    b,_,_=V.current();raw,recipe,_=A.image();grant=json.loads((R/'docs/qa/allocations/combined-owner-auth-1103-v116.json').read_text());assert grant['granted'] and sha(raw)==recipe['expected_memory_SHA256']==grant['expected_candidate_SHA256']
    assert sha(raw)=='80d3ae95894f5ddb430c3e753dd95f3fc2eca6a87d8e1afdb4b8ce8376ec795a'
    source=b['raw'];ui=json.loads((O/'current-menu-v2.json').read_text());post=bytearray(raw)
    for row in ui['patches']:
        at=row['file_offset'];old=bytes.fromhex(row['old_hex']);new=bytes.fromhex(row['new_hex']);assert raw[at:at+len(old)]==source[at:at+len(old)]==old;post[at:at+len(new)]=new
    # All root105frontend finalbytes are retained, including its native
    # Ex/Prince resolver and family mask; none is borrowed for DK storage.
    fg=json.loads((R/'docs/qa/allocations/prince-current-frontend-1103-v105.json').read_text())
    for row in fg['approved_exact_patches']:
        at=row['file_offset'];final=bytes.fromhex(row['new_hex']);assert post[at:at+len(final)]==final
    scene=json.loads((O/'current-scene-v4-CPU.json').read_text())['scene_patch'];at=scene['file_offset'];assert post[at]==3
    before=dict(b,raw=bytes(post));post[at]=4
    # The earlier6c9e UI-only CPU prototype did not contain the DK reserved
    # carrier payload. Current80d3 does: its actual source idle pixels must
    # match before this menu can produce the proposed genuine portrait.
    at=1048592+960*1024+256;assert post[at:at+128]==S.UI.B.D.donor()[16400+1280:16400+1408]
    return before,dict(b,raw=bytes(post)),dict(expected_memory_only_SHA256=sha(raw)),scene


def main():
    text=inspect.getsource(S.main).replace("'current-scene-v4-CPU.json'","'current-current-v6-CPU.json'")
    env=dict(S.__dict__,__file__=__file__,stage=stage);exec(compile(text,__file__,'exec'),env);env['main']()
    before,after,base,scene=stage();path=O/'current-current-v6-CPU.json';q=json.loads(path.read_text())
    q.update(current_input_type='Root-approved116 exact101+83+159+105 source composition',current_auth116_input_SHA256=base['expected_memory_only_SHA256'],current_actual_native_ROM_claim=False,previous_v2_UI_model_scope='V2/v3/v5 test menu code/state over6c9e159+105 without DK carrier publication. Thisv6 binds identical menu preimages to current80d3 carrying all11DK pages and proves its actual128sourceportrait bytes.',source_portrait_actual_backing_bytes_verified=True,all9_Prince105_frontend_finalbytes_exact=True)
    # Actual cold initializer/relocated target, with all three family selector
    # bytes dirty. No extra persistent Jr selector is introduced.
    older=dict(before,raw=A.image()[0]);pairs=[]
    for baseimage in [older,after]:
        m=N.fresh(baseimage);N.put(m,SelectedCharacter=40,FmAlts=255,FmGroups=255,CmActive=83,FamilyMainCommit=113);m[0x5ffe]=2
        out=F.invoke(m,'CrossoverInit');assert m[0x5ffe]==m[0x5fe5]==m[0x5fe8]==0 and N.get(m,'FamilyMainCommit')==113;pairs.append((m,out))
    assert pairs[0][1]==pairs[1][1] and S.UI.P.view(pairs[0][0])==S.UI.P.view(pairs[1][0])
    q['actual_CrossoverInit_relocated_Cold_AXYP_fullstate_exact']=True
    q['bindings'].update({p.relative_to(R).as_posix():sha(p.read_bytes())for p in [Path(__file__),Path(S.__file__),Path(A.__file__),R/'docs/qa/allocations/combined-owner-auth-1103-v116.json',A.O/'combined-auth-v90-composition.json',O/'current-menu-funding-v5.json']})
    path.write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(dict(passed=True,current80d3=base['expected_memory_only_SHA256'],UI_scene_expected_memory_SHA256=sha(after['raw']),source128pixels_verified=True,CrossoverInit_AXYP_state_exact=True)))


if __name__=='__main__':
    try:main()
    except Exception as e:
        (O/'current-current-v6-negative.json').write_text(json.dumps(dict(passed=False,exception=repr(e)),indent=2)+'\n');raise
