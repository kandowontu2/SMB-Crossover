"""Current ordinary Star takeoff from measured original head trajectory."""
from functools import lru_cache
from pathlib import Path
from types import SimpleNamespace
import replay_excitebike_star_return_91dc_1116 as Previous
import replay_excitebike_stock_91dc_1116 as Stock

R,ROM,PIN,W,N,Current,digest=Previous.R,Previous.ROM,Previous.PIN,Previous.W,Previous.N,Previous.Current,Previous.digest
BASE_SHA='6b133a91d3accc927b3787f7e8cadeee61b9afe98b5b1bf021f02ce25eede053'
CONTROL=R/'tools/playthroughs/excitebike_star_head_feedback_91dc_1116.lua'


@lru_cache(maxsize=1)
def bindings(raw):
    b=Current.bundle(raw)
    # Read the exact owning collision profile, not a guessed head-box overlap.
    at=Current.START+(W.address(b,'ExHostAdder')&8191)
    assert raw[at:at+4]==bytes.fromhex('a0033860')
    group=raw[W.location(b,'BlockBufferAdderData')+3]
    head_x=raw[W.location(b,'BlockBuffer_X_Adder')+group]
    head_y=raw[W.location(b,'BlockBuffer_Y_Adder')+group]
    assert(head_x,head_y)==(8,8)
    # Whole kernel pin already binds these code/data bytes. Keep the arithmetic
    # constants explicit for the read-only controller forecast.
    start=Current.START
    assert raw[start+0x900:start+0x91e]==bytes.fromhex('183f282028380c003c1cc07f06020a0b01b020407f030301060434341834')
    return dict(x_adder=head_x,y_adder=head_y,profile=group,
        ground_acceleration=63,ground_cap=832,air_up_deceleration=60,
        launch_bias=175,gravity_up=24,initial_accumulator=15)


@lru_cache(maxsize=1)
def controller(raw,key='star'):
    assert key=='star'and digest(Path(Previous.__file__).read_bytes())==BASE_SHA
    text=Previous.controller(raw,key);forecast=bindings(raw)
    text=Stock.once(text,'local function stockDrive()\n',
        'local Forecast='+Stock.Previous.Text.lua(forecast)+'\n'+CONTROL.read_text()+'\nlocal function stockDrive()\n')
    text=Stock.once(text,"stock.prelean=mainReturns;stock.prelean_request=state();buttons=73;travelJump=nil",
        "stock.prelean=mainReturns;stock.prelean_movement=movementReturns;stock.prelean_request=state();buttons=73;travelJump=nil")
    old="""  if mainReturns-stock.prelean>=4 then
   stock.phase='head';phase='stock-head';stock.head=mainReturns;stock.head_request=state()
   stock.authored_tile=block(C.target_x,C.target_y);if C.stock_type==3 then assert(stock.authored_tile==96,'Actual hidden60 before head')end
   buttons=201
  end"""
    new="""  assert(mainReturns-stock.prelean<32,'One ordinary responsive prelean bound')
  if movementReturns-stock.prelean_movement>=4 then
   local predicted=originalHeadForecast(s);stock.head_forecast_last=predicted
   if predicted and predicted.head_x>=C.target_x+3 then
    assert(predicted.head_x<=C.target_x+13,'Actual head cell has admission margin')
    stock.phase='head';phase='stock-head';stock.head=mainReturns;stock.head_request=state()
    stock.head_forecast=predicted;stock.head_origin=movementReturns
    stock.authored_tile=block(C.target_x,C.target_y);assert(stock.authored_tile==87,'Actual authored Star brick57')
    stock.head_trace={};buttons=201
   end
  end"""
    text=Stock.once(text,old,new)
    text=Stock.once(text," identity();stockObserve();buttons=0;routeEpoch=routeEpoch+1",
        " identity();stockObserve();headForecastObserve();buttons=0;routeEpoch=routeEpoch+1")
    Stock.Previous.LuaRuntime().compile(text)
    assert'\r'not in text and not any(s in text for s in('emu.write','emu.setState','io.open','takeScreenshot','loadState','saveState'))
    return text


def metadata(raw,key='star'):
    q=Previous.metadata(raw,key);q.update(controller_SHA256=digest(controller(raw,key).encode()),
        head_feedback_factory_SHA256=digest(Path(__file__).read_bytes()),
        head_feedback_control_SHA256=digest(CONTROL.read_bytes()),original_head_forecast=bindings(raw),
        retained_native_head_negative='ef73e0c5444250b5abd8f38ce2eeeefcf1536bacce7283ac3091d89672bf0db5',
        controls_identical=False,ordinary_head_policy='At least4 completed original prelean updates, then actual head-cell forecast before freshA',
        source_control='Read actual quarter/fraction/speed and original half-launch flag; preserved Up36 and real native head adders8/8',
        controls_change='Hold existing ordinary prelean until actual speed/quarter/fraction project head into real Star cell; no game changes',
        collector_credit_carry_and25_unchanged=True)
    return q


def family():return SimpleNamespace(W=W,N=N,controller=lambda raw,key:controller(raw),metadata=lambda raw,key:metadata(raw))
