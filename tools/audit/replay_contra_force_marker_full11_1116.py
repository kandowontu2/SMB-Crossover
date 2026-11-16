"""Strict6a3/ffbb CF full routes; frozen completed-return controls unchanged."""
from copy import deepcopy
from functools import lru_cache
from pathlib import Path
import replay_contra_force_completed_full11_1114 as Completed
import replay_contra_force_iron_mount_full11_1114 as Iron
import contra_force_p1_work_marker_model_1116 as Model

C, W, N = Model.C, Model.W, Model.N
R, ROM, PIN = C.R, C.ROM, C.CANDIDATE
Frozen = Completed.Frozen
IDENTITIES = Completed.IDENTITIES
COMPLETED_SHA = '01b9a2b2960861be35f1d6c8686e8feafbb200bf5f61c5c1c4ef20c22ee1e1e6'
IRON_SHA = 'e69013b75bbfc56cc96b3b50a8c43fced25eb29478f2b90e5364f6eb959c1749'


@lru_cache(maxsize=2)
def legacy(raw):
    parent=Model.parent(raw);z,_=C.Plan.inputs(parent)
    # The existing strict Hot118/family reference chain returns the original
    # typed421 object. Observe its original input; do not reconstruct archives
    # or relax any frozen factory's accepted whole-image pins.
    typed=Model.P.Model.F.normalize(z['reference'])
    assert C.H(typed.original)==Completed.PIN
    return typed.original


def previous(key):
    assert key in IDENTITIES
    assert C.H(Path(Completed.__file__).read_bytes())==COMPLETED_SHA
    assert C.H(Path(Iron.__file__).read_bytes())==IRON_SHA
    return Iron if key=='iron'else Completed


def normalize(raw):
    return Completed.normalize(legacy(raw))


@lru_cache(maxsize=8)
def bindings(raw,key):
    old=legacy(raw);prior=previous(key);q=deepcopy(prior.bindings(old,key));b=Model.symbols(raw)
    assert(q['name'],q['variant'])==Model.IDENTITIES[key]
    q['sha']=C.H(raw)
    for name,at in q['ram'].items():assert W.address(b,name)==at,(name,'Moved current RAM binding')
    for name,h in q['hooks'].items():
        at=16+h['offset'];h['bytes']=list(raw[at:at+len(h['bytes'])])
        if'bank'in h:
            at=16+h['bank']*8192;h['bank_SHA256']=C.H(raw[at:at+8192])
    carrier=raw[C.Plan.Audit.P.CHR+935*1024:C.Plan.Audit.P.CHR+959*1024]
    for name,h in q['cf']['hooks'].items():
        at=16384+(h['pc']&8191);assert carrier[at:at+len(h['bytes'])]==bytes(h['bytes']),(name,'CF worker/source hook changed')
        assert h['raw']==3*8192+(h['pc']&8191)
    cookie=bytearray(raw[573373:573389]);cookie[2]=q['variant']
    q['cf']['cookie']=list(cookie);q['cf']['carrier_SHA256']=C.H(carrier)
    return q


@lru_cache(maxsize=8)
def controller(raw,key):
    old=legacy(raw);prior=previous(key);text=prior.controller(old,key)
    assert C.H(text.encode())==prior.LUA_SHA[key]
    body=text.split('\n',1)[1];result='local C='+Frozen.lua(bindings(raw,key))+'\n'+body
    Frozen.LuaRuntime().compile(result)
    assert '\r'not in result and result.split('\n',1)[1]==body
    assert not any(word in result for word in('emu.write','emu.setState','io.open','dofile','saveState','loadState','takeScreenshot'))
    return result


def metadata(raw,key):
    q=bindings(raw,key);prior=previous(key);text=controller(raw,key)
    return dict(actual_ROM_SHA256=C.H(raw),identity=key,compiled_name=q['name'],slot=q['slot'],variant=q['variant'],
        controller_SHA256=C.H(text.encode()),body_SHA256=C.H(text.split('\n',1)[1].encode()),
        original_frozen_controller_SHA256=prior.LUA_SHA[key],frozen_completed_worker_Main_and_Iron_mount_controls_byte_identical=True,
        current_actual_CPU_execution_required=True,legacy421_normalization_for_bindings_only=True,
        whole_CF_cookie=q['cf']['cookie'],ordinary_full_nonshortcut1_1_plus25living_grounded1_2=True,
        gameplay_seeds=0,outputs=0,native=False)
