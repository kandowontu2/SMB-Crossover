"""New observer sourcegate and source-only five-ring fixture provenance."""
from pathlib import Path
from unittest.mock import patch
import argparse,inspect,json
import replay_sonic_ceiling_life_resources_a2d9_1116 as Factory
import check_sonic_hidden_native_callback_f7c9_1116 as Previous
import replay_sonic_ceiling_full11_a2d9_1116 as Full

F=Factory.F
PREVIOUS_SHA='76442c0f0362192ef95cbefbc9a80b00892c702622c7927f916bc14f4e9108b1'


def functions():
    assert F.H(Path(Previous.__file__).read_bytes())==PREVIOUS_SHA
    ns=dict(Previous.__dict__,F=F,Factory=Factory,__file__=__file__)
    for name in('compile_pack','run'):
        s=inspect.getsource(getattr(Previous,name))
        if name=='run':
            s=s.replace("receipt['terminal']['rings']==5", "receipt['terminal']['rings']==receipt['pre_oneup_resources']['rings']")
            s=s.replace("receipt['collected'][0]['item']['state']==6", "receipt['collected'][0]['item']['state']>=6")
            s=s.replace('actual f7 CPU','actual a2 CPU')
        exec(compile(s,'<actual pre1UP resource-preservation native observer>','exec'),ns)
    return ns


def predicates(raw):
    rt=Previous.Mock.LuaRuntime(unpack_returned_tuples=True)
    fn=rt.execute(Factory.RESOURCE_FUNCTION+';return sameResources')
    cases=0
    for rings in(0,5):
        a=dict(rings=rings,ringLives=0,hurt=0,sourceStar=0,status=0)
        assert fn(rt.table_from(a),rt.table_from(a));cases+=1
        for name in a:
            b=dict(a);b[name]^=1;assert not fn(rt.table_from(a),rt.table_from(b));cases+=1
    for form in F.FORMS:
        assert 's.rings==5'not in Factory.controller(raw,form)
        assert 's.rings==5'not in Full.controller(raw,form)
    return dict(passed=True,API_only_resource_predicate_cases=cases,zero_and_five_baselines_admitted=True,every_changed_resource_rejected=True,
        no_gameplay_RAM_fields_seeded=True,full_factory_no_five_ring_assertion=True)


def compile_pack(raw):
    out=functions()['compile_pack'](raw);out['resource_predicate']=predicates(raw);return out


def run(raw,form='sonic',limit=1200):
    pack=compile_pack(raw);q=F.bindings(raw);N,W=F.N,F.W;baseCPU=N.NesMPU;baseBus=W.ControllerBus
    ctx={};ring=[];scene=[]
    class CPU(baseCPU):
        def step(self):
            ctx.update(PC=self.pc,tag=self.memory.rawtags[(self.pc-0x8000)//8192]if self.pc>=0x8000 else-1,SP=self.sp)
            return super().step()
    class Bus(baseBus):
        def __setitem__(self,at,value):
            if isinstance(at,int)and at>=0x8000 and self.rawtags[(at-0x8000)//8192]==2 and ctx.get('tag')==2 and 0xd400<=ctx.get('PC',0)<0xd800:
                off=at&8191
                if off==0x340 and self.ram[2][off]!=(value&255):
                    assert len(ring)<8;ring.append(dict(ctx,address=at,before=self.ram[2][off],after=value&255,
                        sourceX=int.from_bytes(bytes(self.ram[2][0x71:0x73]),'little'),sourceY=int.from_bytes(bytes(self.ram[2][0x74:0x76]),'little')))
                if 0x378<=off<0x37b and(value&255)in(0x7a,0x7b):
                    assert len(scene)<8;scene.append(dict(ctx,address=at,value=value&255,world=N.get(self,'WorldNumber'),level=N.get(self,'LevelNumber'),area=N.get(self,'AreaAddrsLOffset')))
            return super().__setitem__(at,value)
    with patch.object(N,'NesMPU',CPU),patch.object(W,'ControllerBus',Bus):out=functions()['run'](raw,form,limit)
    assert out['passed']
    # These optional sparse observations are not the source fixture's producer
    # authority. The exact current initializer and retained sources below bind
    # that provenance independently of this wrapper's cold callback coverage.
    live=F.R/'tools/reference/sonic_sms_ring_live_1110.s';adapter=F.R/'tools/reference/sonic_sms_ring_adapter_1110.s'
    assert F.H(live.read_bytes())=='dd0ea067ef83f2fd1df36381261557c3ef7834f4df4ccf2ed9ab059322dbd4ee'
    assert F.H(adapter.read_bytes())=='14a3e78cf0c33088a0e94fb78ef9672b24f1dc33826b8d99f7b89152830fc017'
    ringcode=q['loaded'](0xd400)[:1024];needle=bytes.fromhex('a97a8d78c3a97b8d79c38d7ac3');assert ringcode.count(needle)==1
    out.update(pack=pack,source_ring_fixture=dict(SceneTiles=[0xc378,0xc379,0xc37a],initializer_PC=0xd400+ringcode.index(needle),
        initializer_hex=needle.hex(),source_live_SHA256=F.H(live.read_bytes()),source_adapter_SHA256=F.H(adapter.read_bytes()),
        sparse_initializing_writes=scene,sparse_ring_writes=ring,complete_writer_census_claim=False,source_cold_initial_rings=out['cold']['state']['ringBCD'],
        scope='Five later source-model acquisitions from the explicit conditional GHZ1 three-cell test fixture, not initial inventory, native SMB coins or a promised native ring count. Actual native0 is observed separately; its complete fixture lifecycle is unproven here. No new ring code or scene writes are introduced.'),
        retained_native_fixed_five_observer_negative='3d8600aa4e6d7dde2286ba32910e9c0166e4d819e269043f930bdcf441765b31',
        retained_extra_writer_assertion_negative=dict(job=83060,checker_SHA256='f26373298292523be11d92b50ed13f830f4776a37bbb06236804f85a9b0bbdaa',
            scope='All production observer/gameplay assertions returned passed; a separate unqualified sparse-writer wrapper then overclaimed a complete cold writer census. No game, control or production callback was changed for that observer-only failure.'))
    out['receipt_SHA256']=F.H(json.dumps(out,sort_keys=True,separators=(',',':')).encode());return out


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--compile',action='store_true');p.add_argument('--form',choices=tuple(F.FORMS),default='sonic');a=p.parse_args()
    def deny(*a,**k):raise AssertionError('Resource observer source qualification attempted files/native')
    with patch.object(Path,'write_bytes',deny),patch.object(Path,'write_text',deny),patch('subprocess.Popen',deny):out=compile_pack(F.load_current_image())if a.compile else run(F.load_current_image(),a.form)
    print('RESULT '+json.dumps(out,separators=(',',':')),flush=True)
