"""Strict 1327/a2 CF observation; bc5 is metadata only, no game composition."""
from functools import lru_cache
from pathlib import Path
from unittest.mock import patch
import compose_sonic_ceiling_complete_1327_1116 as Sonic
import compose_jay_status_size_publication_00bb_1116 as Jay
import compose_metal_life_snapshot_root_1116 as Metal
import compose_dkjr_forced_entry_current_1116 as DK
import compose_dkjr_footer_bt91dc_current_1116 as Footer
import compose_battletoads_mature8_1116 as BT
import compose_bowser_life_gain_signed_1116 as Bowser
import profile_contra_force_current_costs_1115 as Previous

R,ROM,H,N,W,Frames=Previous.C.R,Previous.C.ROM,Previous.C.H,Previous.N,Previous.W,Previous.Frames
PINS={Sonic:'c4456eb759fd35f48022fee64a24b05e37b4968a1ddaf139dceebad154187413',
 Jay:'7f1c0eab5a08a7a7e3fbf922aaff1a1c2b8b7513c9c3bd11ed8eee50d01e8d0c',
 Metal:'c9051abcb700dbb1401c0fdf8de2cfd8da7267cdbb457610454c13f867a5cd54',
 DK:'67b6ccef60386789854c9f5a9634b92f5178301948b2f0004b0f640f2e9cb7b1',
 Footer:'44f7ece4b1501a163d1e6551b0d40609fba5db525d2737ad94ff51d861868ab1',
 BT:'6db3aa513aac81d022efdc881b01bdcb93a639ccd4f99e8671fed3f8986bb27c',
 Bowser:'2b5d81f056991636bf2498d4871645ea1cd80b003d2d986504b46b89d8b013b7',
 Previous:'721d91c5220c20f71d31cb61683b05cfb3612244b4f86aff1d3c6c692d8f1a94'}


@lru_cache(maxsize=2)
def reference(raw):
    assert isinstance(raw,bytes)and H(raw)in(Jay.CANDIDATE,Sonic.CANDIDATE),'Exact owning1327 or a2 only'
    for module,pin in PINS.items():assert H(Path(module.__file__).read_bytes())==pin
    old=raw;chain=[]
    if H(old)==Sonic.CANDIDATE:
        old=Sonic.inverse(old);chain.append(dict(module=Sonic.__name__,restored_SHA256=H(old)))
    for module in(Jay,Metal,DK,Footer,BT,Bowser):
        assert H(old)==module.CANDIDATE
        old=module.inverse(old);assert H(old)==module.PIN
        chain.append(dict(module=module.__name__,restored_SHA256=H(old)))
    assert H(old)==Previous.C.CANDIDATE
    return old,chain


@lru_cache(maxsize=2)
def bindings(raw):
    old,chain=reference(raw);prior=Previous.bindings(old)
    carrier=raw[Previous.CHR+935*1024:Previous.CHR+959*1024]
    assert carrier==prior['carrier']and len(carrier)==24576
    points={}
    for key,item in prior['points'].items():
        row=dict(item)
        if row['tag']>=128:
            at=row['source_file'];assert raw[at:at+8]==old[at:at+8]==bytes(row['bytes'])
            row['owning_bank_SHA256']=H(raw[16+(row['tag']&127)*8192:16+((row['tag']&127)+1)*8192])
        points[key]=row
    cookie_files=[W.location(prior['bundle'],n)for n in('CfExternalCookie','CfLoaderExpectedCookie')]
    assert cookie_files==[573373,642966]
    cookie=raw[cookie_files[0]:cookie_files[0]+16]
    assert cookie==bytes.fromhex('a71f00053a7d2d9a77d5accd30e79766')
    assert all(raw[a:a+16]==old[a:a+16]==cookie for a in cookie_files)
    assert raw[8208:8241]==old[8208:8241]and H(raw[8208:8241])=='c22c9c8d9efbb1836af4549d0601292c8150da3b3609c83d8192e2b0bb51fd4c'
    changed=[bank for bank in range(128)if raw[16+bank*8192:16+(bank+1)*8192]!=old[16+bank*8192:16+(bank+1)*8192]]
    protected=[]
    for bank,pc,n in((87,0xb020,224),(96,0xb799,175),(67,0xb22b,213),(69,0xbf47,185),(124,0xa4fb,0x32)):
        at=16+bank*8192+(pc&8191);assert raw[at:at+n]==old[at:at+n]
        protected.append(dict(bank=bank,PC=pc,bytes=n,SHA256=H(raw[at:at+n])))
    q=dict(prior,bundle=dict(prior['bundle'],raw=raw),points=points,carrier=carrier)
    q['current_proof']=dict(owning_SHA256=H(raw),reference_bc5_only_SHA256=H(old),typed_inverse_chain=chain,
        CF_carrier_SHA256=H(carrier),CF_cookie=cookie.hex(),cookie_files=cookie_files,
        all_CF_carrier_and_profile_point_preimages_exact=True,protected_native_callers=protected,
        shared_SFC33_SHA256=H(raw[8208:8241]),changed_native_PRG_banks_since_bc5=changed,
        actual_current_CPU_bytes_retained=True,old_APIs_unchanged=True)
    return q


def bound(image):
    return bindings(image)if H(image)in(Jay.CANDIDATE,Sonic.CANDIDATE)else OldBindings(image)


OldBindings=Previous.bindings


def cold(raw):
    q=bindings(raw)
    with patch.object(Previous,'bindings',bound):m=Previous.cold(raw)
    assert m.bundle['raw']is raw and type(m)is W.ControllerBus
    return m


def empty(m,key='burns'):
    assert key=='burns';return Previous.empty(m)


def load_current_image():
    raw=ROM.read_bytes();assert H(raw)in(Jay.CANDIDATE,Sonic.CANDIDATE);return raw
