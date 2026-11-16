"""Strict6a3 life controllers; frozen currentbc5 inputs/body provenance retained."""
from functools import lru_cache
from copy import deepcopy
from pathlib import Path
import compose_bowser_life_gain_signed_1116 as C
import current_bowser_life_gain_1116 as Current
import replay_bowser_natural_stock_bc5_1115 as Previous
import replay_bowser_star_landing_bc5_1115 as Star

R,ROM,PIN,W,N=C.R,C.ROM,C.CANDIDATE,Current.W,Current.N
PARENT_FACTORY_SHA='2d4fe5399d4da143fcfb8d1db40d62315bec5403ed65073eaf7c9d3d9cdfd48f'

@lru_cache(maxsize=4)
def bindings(raw,identity=0,kind='oneup'):
    parent=C.inverse(raw);assert C.digest(Path(Previous.__file__).read_bytes())==PARENT_FACTORY_SHA
    q=deepcopy(Previous.bindings(parent,identity,kind));q['sha']=PIN;image=Current.image(raw);q['code_hex']=image[:2615].hex()
    q['cookie']=C.lease()['cookie_views']['new_hex'];b=Current.bundle(raw);pc=W.address(b,'BwConstruct')
    q['hooks']['BwConstruct']=dict(pc=pc,offset=3*8192+(pc&8191),space='work',bytes=list(image[pc&8191:(pc&8191)+8]))
    q['life_fields']={n:W.address(b,n)for n in('BwPersistent','BwPlayerKey')}
    return q

@lru_cache(maxsize=4)
def controller(raw,identity=0,kind='oneup'):
    parent=C.inverse(raw)
    if kind=='star':
        assert C.digest(Path(Star.__file__).read_bytes())=='a994b304d1785b0ac8609062c6e38e91813d0f2c469e9df77abdbb691d319c6a'
        text=Star.controller(parent,identity)
    else:text=Previous.controller(parent,identity,kind)
    prefix='local BStock='+Previous.Text.lua(Previous.bindings(parent,identity,kind))+'\n';assert text.startswith(prefix);body=text[len(prefix):]
    assert body.count(C.PIN)==1;body=body.replace(C.PIN,PIN,1)
    marker="hook('BwMovement',function()"
    body=Previous.once(body,marker,"hook('BwConstruct',function()assert(not stock.credit,'Earned life must not invoke fresh construction')end)\n"+marker)
    old="    assert(work3(0xbe28)==stock.collector.s.tier and r('PlayerStatus')==stock.collector.s.power,'Stock preserves earned Bowser tier')"
    new=old+"\n    if BStock.kind==3 then\n     assert(work3(0xbe29)==stock.credit.s.health,'Life gain preserves current HP')\n     local saved=BStock.life_fields.BwPersistent+2+work3(BStock.life_fields.BwPlayerKey)\n     assert(work3(saved)==3,'Existing active-player saved-life snapshot updated')\n     stock.preserved_HP=work3(0xbe29);stock.saved_life=work3(saved)\n    end"
    body=Previous.once(body,old,new)
    text='local BStock='+Previous.Text.lua(bindings(raw,identity,kind))+'\n'+body
    Previous.Old.Base.LuaRuntime().compile(text)
    assert not any(s in text for s in('emu.write','emu.setState','io.open','loadState','saveState','takeScreenshot'))
    return text

def metadata(raw,identity=0,kind='oneup'):
    parent=C.inverse(raw);q=Previous.metadata(parent,identity,kind);text=controller(raw,identity,kind)
    q.update(ROM_SHA256=PIN,parent_ROM_SHA256=C.PIN,controller_SHA256=C.digest(text.encode()),factory_SHA256=C.digest(Path(__file__).read_bytes()),
        composer_SHA256=C.digest(Path(C.__file__).read_bytes()),grant_SHA256=C.GRANT_SHA,full16cookie=bindings(raw,identity,kind)['cookie'],
        actual_candidate_execution=True,old_current_factory_unchanged=True,life_preserves_current_HP_and_tier_required=True)
    return q

def family(identity,kind):
    from types import SimpleNamespace
    return SimpleNamespace(W=W,N=N,controller=lambda raw,key:controller(raw,identity,kind),metadata=lambda raw,key:metadata(raw,identity,kind))
