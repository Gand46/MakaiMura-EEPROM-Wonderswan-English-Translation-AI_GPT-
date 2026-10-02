local mt=emu.memType.wsWorkRam
local dest=assert(os.getenv('MESEN_CAPTURE_PATH'))
local report=assert(os.getenv('MESEN_LUA_REPORT'))
local mode=assert(tonumber(os.getenv('QA_MODE')))
local obs={}
local reads={}
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
 if f==3400 then ww(0x1b74,mode);ww(0x1e33,0x170)end
 if f==3900 then
  -- QA-only active exit marker at actor x+16. See 4000:DEDA-DFB5.
  emu.write(0x1ba4,1,mt);emu.write(0x1bb5,0x44,mt)
  ww(0x1bac,w(0x1a08)+16)
  local sub=os.getenv('QA_SUBSTATE');if sub then emu.write(0x1e2f,tonumber(sub),mt)end
  if os.getenv('QA_FORCE_70')=='1' then ww(0x1e33,0x70) end
 end
 if f>=3880 and f<=4700 and (f%10==0) then
  local a={f=f,state=w(0x1e33),mode=w(0x1b74),actor_x=w(0x1a08),obj_x=w(0x1bac),obj_kind=b(0x1bb5),obj_active=b(0x1ba4)}
  obs[#obs+1]=string.format('{"f":%d,"state":%d,"mode":%d,"sub":%d,"actor_x":%d,"obj_x":%d,"obj_kind":%d,"obj_active":%d}',a.f,a.state,a.mode,b(0x1e2f),a.actor_x,a.obj_x,a.obj_kind,a.obj_active)
 end
 if f==3890 or f==3900 or f==3910 or f==3940 or f==3980 or f==4060 or f==4200 or f==4500 or f==4700 then
  local p=assert(io.open(string.format('%s.%04d.png',dest,f),'wb'));p:write(emu.takeScreenshot());p:close()
 end
 if f==4700 then
  local p=assert(io.open(dest,'wb'));p:write(emu.takeScreenshot());p:close()
  local r=assert(io.open(report,'w'));r:write(string.format('{"method":"synthetic_exit_object","initial_mode":%d,"reads":[%s],"observations":[%s]}',mode,table.concat(reads,','),table.concat(obs,',')));r:close();emu.stop(0)
 end
end
local function onread(addr,val)
 local f=emu.getState().frameCount
 if f>=3900 and f<=4700 and #reads<40 then
  local cpu=emu.getState().cpu
  reads[#reads+1]=string.format('{"f":%d,"a":%d,"v":%d,"cs":%d,"ip":%d}',f,addr,val,cpu.cs or 0,cpu.ip or 0)
 end
end
emu.addMemoryCallback(onread,emu.callbackType.read,0x1bb5,0x1bb5,emu.cpuType.ws,mt)
emu.addEventCallback(input,emu.eventType.inputPolled)
emu.addEventCallback(frame,emu.eventType.endFrame)
