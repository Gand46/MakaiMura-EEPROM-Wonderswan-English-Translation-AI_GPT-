local mt=emu.memType.wsWorkRam
local dest=assert(os.getenv('MESEN_CAPTURE_PATH'))
local report=assert(os.getenv('MESEN_LUA_REPORT'))
local mode=assert(tonumber(os.getenv('QA_MODE')))
local variant=assert(tonumber(os.getenv('QA_VARIANT')))
local obs={}
local marks={3400,3420,3480,3540,3660,3900,4300,4800}
local function b(a)return emu.read(a,mt)end
local function w(a)return b(a)+256*b(a+1)end
local function ww(a,v)emu.write(a,v%256,mt);emu.write(a+1,math.floor(v/256),mt)end
local function input()
 local f=emu.getState().frameCount;local inp={}
 if f<500 then inp.start=(f%90)<3 end
 if f>=520 and f<524 then inp.down=true end
 if f>=610 and f<614 then inp.a=true end
 emu.setInput(inp,0)
end
local function frame()
 local f=emu.getState().frameCount
 if f==3400 then
  ww(0x1b74,mode)
  ww(0x1e33,variant)
 end
 if f>=3399 and f<=4800 and (f%20==0 or f==3399) then
  obs[#obs+1]=string.format('{"f":%d,"state":%d,"mode":%d,"sub":%d,"actor_x":%d,"actor_y":%d}',f,w(0x1e33),w(0x1b74),b(0x1e2f),w(0x1a08),w(0x1a0a))
 end
 for _,m in ipairs(marks) do if f==m then
  local p=assert(io.open(string.format('%s.%04d.png',dest,f),'wb'));p:write(emu.takeScreenshot());p:close()
 end end
 if f==4800 then
  local p=assert(io.open(dest,'wb'));p:write(emu.takeScreenshot());p:close()
  local r=assert(io.open(report,'w'));r:write(string.format('{"mode":%d,"variant":%d,"observations":[%s]}',mode,variant,table.concat(obs,',')));r:close();emu.stop(0)
 end
end
emu.addEventCallback(input,emu.eventType.inputPolled)
emu.addEventCallback(frame,emu.eventType.endFrame)
