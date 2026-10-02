local mt=emu.memType.wsWorkRam
local dest=assert(os.getenv('MESEN_CAPTURE_PATH'))
local report=assert(os.getenv('MESEN_LUA_REPORT'))
local mode=assert(tonumber(os.getenv('QA_MODE')))
local frames={3400,3440,3500,3600,3800,4200}
local marks={};for _,f in ipairs(frames)do marks[f]=true end
local obs={}
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
  if os.getenv('QA_FORCE_STATE')=='1' then ww(0x1e33,0x170)end
 end
 if marks[f] then
  local p=assert(io.open(string.format('%s.%04d.png',dest,f),'wb'));p:write(emu.takeScreenshot());p:close()
  obs[#obs+1]=string.format('{"frame":%d,"state":%d,"mode":%d,"x":%d,"y":%d}',f,w(0x1e33),w(0x1b74),w(0x1a08),w(0x1a0a))
 end
 if f==4200 then
  local p=assert(io.open(dest,'wb'));p:write(emu.takeScreenshot());p:close()
  local r=assert(io.open(report,'w'))
  r:write(string.format('{"method":"WRAM_POKE","target_mode":%d,"observations":[%s]}',mode,table.concat(obs,',')))
  r:close();emu.stop(0)
 end
end
emu.addEventCallback(input,emu.eventType.inputPolled)
emu.addEventCallback(frame,emu.eventType.endFrame)
