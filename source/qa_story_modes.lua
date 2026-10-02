local mt=emu.memType.wsWorkRam
local dest=assert(os.getenv('MESEN_CAPTURE_PATH'))
local report=assert(os.getenv('MESEN_LUA_REPORT'))
local state=tonumber(os.getenv('QA_STATE') or '896')
local marks={240,500,750,1000,1500,2000,2600,3300}
local marked={};for _,v in ipairs(marks) do marked[v]=true end
local function rb(a)return emu.read(a,mt) end
local function frame()
 local f=emu.getState().frameCount
 if f==180 then
  emu.write(0x1e33,state%256,mt)
  emu.write(0x1e34,math.floor(state/256),mt)
 end
 if marked[f] then
  local p=string.format('%s.%04d.png',dest,f)
  local h=assert(io.open(p,'wb'));h:write(emu.takeScreenshot());h:close()
 end
 if f==3300 then
  local h=assert(io.open(dest,'wb'));h:write(emu.takeScreenshot());h:close()
  local r=assert(io.open(report,'w'))
  r:write(string.format('{"injected_state":%d,"final_state":%d,"remaining_lines":%d,"frame":%d}',state,rb(0x1e33)+rb(0x1e34)*256,rb(0x1e35),f))
  r:close();emu.stop(0)
 end
end
emu.addEventCallback(frame,emu.eventType.endFrame)
