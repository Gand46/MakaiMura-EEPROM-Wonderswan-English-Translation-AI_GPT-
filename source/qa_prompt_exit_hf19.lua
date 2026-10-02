local mt=emu.memType.wsWorkRam
local dest=assert(os.getenv('MESEN_CAPTURE_PATH'))
local report=assert(os.getenv('MESEN_LUA_REPORT'))
local button=os.getenv('QA_BUTTON') or 'b'
local obs={}
local function input()
 local f=emu.getState().frameCount
 local inp={}
 if f>=320 and f<325 then inp[button]=true end
 emu.setInput(inp,0)
end
local function frame()
 local f=emu.getState().frameCount
 if f==180 then emu.write(0x1e33,0x10,mt);emu.write(0x1e34,0x01,mt) end
 if f==240 or f==320 or f==360 or f==600 then
  local s=emu.read(0x1e33,mt)+256*emu.read(0x1e34,mt)
  local h=assert(io.open(string.format('%s.%04d.png',dest,f),'wb'));h:write(emu.takeScreenshot());h:close()
  obs[#obs+1]=string.format('{"frame":%d,"state":%d}',f,s)
 end
 if f==600 then
  local h=assert(io.open(dest,'wb'));h:write(emu.takeScreenshot());h:close()
  local r=assert(io.open(report,'w'));r:write('{"method":"SYNTHETIC_STATE","injected_frame":180,"button":"'..button..'","button_frames":"320..324","observations":['..table.concat(obs,',')..']}');r:close()
  emu.stop(0)
 end
end
emu.addEventCallback(input,emu.eventType.inputPolled)
emu.addEventCallback(frame,emu.eventType.endFrame)
