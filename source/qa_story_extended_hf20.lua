local mt=emu.memType.wsWorkRam
local dest=assert(os.getenv('MESEN_CAPTURE_PATH'))
local report=assert(os.getenv('MESEN_LUA_REPORT'))
local state=assert(tonumber(os.getenv('QA_STATE')))
local frames={240,600,900,1200,1500,1800,2100,2500,3000}
local marks={};for _,f in ipairs(frames)do marks[f]=true end
local obs={}
local function w(a)return emu.read(a,mt)+256*emu.read(a+1,mt)end
local function frame()
 local f=emu.getState().frameCount
 if f==180 then emu.write(0x1e33,state%256,mt);emu.write(0x1e34,math.floor(state/256),mt)end
 if marks[f] then
  local p=assert(io.open(string.format('%s.%04d.png',dest,f),'wb'));p:write(emu.takeScreenshot());p:close()
  obs[#obs+1]=string.format('{"frame":%d,"state":%d,"counter":%d}',f,w(0x1e33),w(0x1e5a))
 end
 if f==3000 then
  local p=assert(io.open(dest,'wb'));p:write(emu.takeScreenshot());p:close()
  local r=assert(io.open(report,'w'));r:write(string.format('{"method":"SYNTHETIC_STATE","target":%d,"observations":[%s]}',state,table.concat(obs,',')));r:close();emu.stop(0)
 end
end
emu.addEventCallback(frame,emu.eventType.endFrame)
