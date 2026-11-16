-- Read-only controller arithmetic from the current original ExMotor/AirStep.
-- It chooses when to press A; the actual engine still performs every move.
local function originalHeadForecast(s)
 assert(s.native==0 and s.air==0 and s.y==176 and s.high==1 and s.crash==0 and s.recovery==0 and s.heat==0,'Original flat takeoff domain')
 assert(ram2(0x52)==0 and ram2(0x58)==0 and ram2(0x374)==0 and ram2(0x804)==1,'Original active flat right-facing motor')
 local v,f,tick,x,y=s.speed,ram2(0x394),ram2(0x3f),s.x,s.y
 local accumulator,velocity,half=Forecast.initial_accumulator,nil,ram2(0x388)==2
 local samples={}
 for n=1,24 do
  tick=(tick+1)&255
  if tick&3==0 then
   if n==1 then v=math.min(Forecast.ground_cap,v+Forecast.ground_acceleration)
   else v=math.max(0,v-Forecast.air_up_deceleration)end
  end
  f=f+(v&255);x=x+(v>>8)+(f>=256 and 1 or 0);f=f&255
  if n==1 then velocity=v+Forecast.launch_bias;if half then velocity=velocity//2 end end
  accumulator=accumulator+Forecast.gravity_up
  local dy=(accumulator>>8)-(velocity>>8);y=y+dy
  local hy=y+Forecast.y_adder;local row=(hy//16)*16
  samples[#samples+1]={n=n,x=x,y=y,speed=v,fraction=f,tick=tick,head_x=x+Forecast.x_adder,head_y=hy}
  -- Original native head processing also requires upward motion and Y nibble4+.
  if row==C.target_y and dy<0 and y&15>=4 then
   return{head_x=x+Forecast.x_adder,head_y=hy,steps=n,request=state(),fraction=ram2(0x394),
    quarter=ram2(0x3f),source_pitch=s.angle,half_launch=half,velocity=velocity,samples=samples}
  end
  if dy>=0 or row<C.target_y then return nil end
 end
 error('Original head forecast bound')
end
local function headForecastObserve()
 if not stock.head_forecast or not stock.head_origin or stock.head_forecast_actual then return end
 local n=movementReturns-stock.head_origin
 if n==0 or n==stock.head_trace_last then return end
 stock.head_trace_last=n
 if n<=12 then
  local s=state();s.n=n;s.fraction=ram2(0x394);s.quarter=ram2(0x3f)
  s.head_x=s.x+Forecast.x_adder;s.head_y=s.y+Forecast.y_adder
  stock.head_trace[#stock.head_trace+1]=s
  if n==stock.head_forecast.steps then
   stock.head_forecast_actual=s
   stock.forecast_error={x=s.head_x-stock.head_forecast.head_x,y=s.head_y-stock.head_forecast.head_y}
  end
 end
end
