-- Menu -> Library -> left from Arthur cover -> A: first book index.
local mt=emu.memType.wsWorkRam
local dest=assert(os.getenv('MESEN_CAPTURE_PATH'))
local report=assert(os.getenv('MESEN_LUA_REPORT'))
local observations={}
local function held(f,t)return f>=t and f<t+4 end
local function input()
 local f=emu.getState().frameCount;local inp={}
 if f<500 then inp.start=(f%90)<3 end
 if held(f,520) or held(f,550) then inp.down=true end
 if held(f,610) or held(f,820) then inp.a=true end
 for i=0,24 do if held(f,920+i*24) then inp.down=true end end
 if held(f,700) then inp.left=true end
 emu.setInput(inp,0)
end
local function frame()
 local f=emu.getState().frameCount
 if f==1300 or f==1450 or f==1550 then
  local p=assert(io.open(string.format('%s.%04d.png',dest,f),'wb'));p:write(emu.takeScreenshot());p:close()
  local s=emu.read(0x1e33,mt)+256*emu.read(0x1e34,mt)
  observations[#observations+1]=string.format('{"frame":%d,"state":%d}',f,s)
 end
 if f==1550 then
  local p=assert(io.open(dest,'wb'));p:write(emu.takeScreenshot());p:close()
  local r=assert(io.open(report,'w'))
  r:write('{"method":"SCRIPTED_NATURAL","inputs":"START <500;DOWN@520,550;A@610;LEFT@700;A@820; DOWN@920+24*i i=0..24","observations":['..table.concat(observations,',')..']}')
  r:close();emu.stop(0)
 end
end
emu.addEventCallback(input,emu.eventType.inputPolled)
emu.addEventCallback(frame,emu.eventType.endFrame)
