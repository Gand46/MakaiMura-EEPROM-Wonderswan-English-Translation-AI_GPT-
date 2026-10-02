local finished=false
local stop=emu.stop
local function finish(code) if not finished then finished=true;stop(code) end end
local base=assert(os.getenv('OUT'))
local frame=0
local phase='seek_pause'
local age=0
local baselineWrites=0
local firstSaveWrites=0
local result={}
local function diffCount()
  local c=0
  for i=0,0x284 do
    if emu.read(0x370+i,emu.memType.wsWorkRam)~=emu.read(i,emu.memType.wsCartEeprom) then c=c+1 end
  end
  return c
end
local function writeCount()
  local wc=emu.getAccessCounters(emu.memType.wsCartEeprom,emu.counterType.writeCount)
  local total=0
  for i=0,2047 do total=total+(wc[i] or 0) end
  return total
end
local function log(msg)
  local f=assert(io.open(base..'phase41d_test.log','a')); f:write(string.format('%d\t%s\t%s\n',frame,phase,msg)); f:close()
end
local function shot(name)
  local p=assert(io.open(base..name..'.png','wb'));p:write(emu.takeScreenshot());p:close()
end
local function fail(msg)
  log('FAIL '..msg); finish(2)
end
os.remove(base..'phase41d_test.log')
emu.resetAccessCounters()

emu.addEventCallback(function()
  if finished then return end
  frame=frame+1
  age=age+1
  local ps=emu.read(0x1E92,emu.memType.wsWorkRam)
  local wc=writeCount()
  local df=diffCount()

  if phase=='seek_pause' and frame>1500 and ps==2 then
    phase='a_test'; age=0; baselineWrites=wc
    log(string.format('FIRST_PAUSE diff=%d writes=%d',df,wc)); shot('start_hold_pause_ui')
  elseif phase=='a_test' and age==35 then
    if ps~=2 then fail('A test exited pause') return end
    if wc~=baselineWrites then fail('A press caused EEPROM write') return end
    log(string.format('A_SAFE pause=%d diff=%d writes=%d',ps,df,wc))
    phase='tap_start'; age=0
  elseif phase=='tap_start' and age>24 and ps==0 then
    if wc~=baselineWrites then fail('tap START caused EEPROM write') return end
    log(string.format('TAP_RETURN_OK pause=%d writes=%d',ps,wc))
    phase='reenter_pause'; age=0
  elseif phase=='reenter_pause' and ps==2 and age>20 then
    log(string.format('SECOND_PAUSE diff=%d writes=%d',df,wc))
    phase='hold_start'; age=0; baselineWrites=wc
  elseif phase=='hold_start' and age==60 then
    if ps~=2 then fail('HOLD START exited pause') return end
    if wc<=baselineWrites then fail('HOLD START did not write EEPROM') return end
    if df~=0 then fail('HOLD START commit left mirror/eeprom differences '..df) return end
    firstSaveWrites=wc
    log(string.format('HOLD_SAVE_OK pause=%d diff=%d writes=%d',ps,df,wc)); shot('start_hold_saved')
    phase='post_save_release'; age=0
  elseif phase=='post_save_release' and age==20 then
    if ps~=2 then fail('release after SAVE exited pause') return end
    if wc~=firstSaveWrites then fail('release after SAVE added writes') return end
    log(string.format('RELEASE_REARM_OK pause=%d writes=%d',ps,wc))
    phase='noop_hold'; age=0; baselineWrites=wc
  elseif phase=='noop_hold' and age==60 then
    if ps~=2 then fail('second HOLD exited pause') return end
    if wc~=baselineWrites then fail('no-op HOLD SAVE caused redundant EEPROM writes') return end
    log(string.format('NOOP_HOLD_ZERO_WRITES pause=%d writes=%d',ps,wc))
    phase='final_release'; age=0
  elseif phase=='final_release' and age==20 then
    if ps~=2 then fail('final release exited pause') return end
    phase='final_tap'; age=0
  elseif phase=='final_tap' and age>24 and ps==0 then
    if wc~=baselineWrites then fail('final tap changed EEPROM') return end
    log(string.format('FINAL_TAP_RETURN_OK writes=%d',wc))
    shot('start_hold_final')
    finish(0)
  end

  if frame>4200 then fail('global frame limit reached ps='..ps..' age='..age) end
end,emu.eventType.endFrame)

emu.addEventCallback(function()
  if finished then return end
  local start,a,b,right,left=false,false,false,false,false
  if phase=='seek_pause' then
    local cyc=frame%1200
    start=(frame>=120 and frame<140) or (cyc>=20 and cyc<30)
    a=(frame>=190 and frame<210) or (cyc>=180 and cyc<200) or (cyc>=980 and cyc<995)
    b=(cyc>=1030 and cyc<1040)
    right=(cyc>=250 and cyc<900)
    left=(cyc>=910 and cyc<940)
  elseif phase=='a_test' then
    a=(age>=5 and age<15)
  elseif phase=='tap_start' then
    start=(age>=5 and age<13)
  elseif phase=='reenter_pause' then
    start=(age>=30 and age<40)
    right=(age<28)
  elseif phase=='hold_start' then
    start=(age>=5 and age<55)
  elseif phase=='post_save_release' then
    start=false
  elseif phase=='noop_hold' then
    start=(age>=5 and age<55)
  elseif phase=='final_release' then
    start=false
  elseif phase=='final_tap' then
    start=(age>=5 and age<13)
  end
  emu.setInput({start=start,a=a,b=b,right=right,left=left,up=false,down=false,sound=false,up2=false,down2=false,left2=false,right2=false},0)
end,emu.eventType.inputPolled)
