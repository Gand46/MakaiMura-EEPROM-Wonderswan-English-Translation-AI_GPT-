local mt=emu.memType.wsWorkRam
local path=assert(os.getenv('MESEN_CAPTURE_PATH'))
local report=assert(os.getenv('MESEN_LUA_REPORT'))
local fh=assert(io.open(report,'w'))
fh:write('frame,event,state,mode,coord90,coord92,x,y,prev_x,prev_y,flags,cs,ip\n')
local function b(a)return emu.read(a,mt)end
local function w(a)return b(a)+256*b(a+1)end
local function ww(a,v)emu.write(a,v%256,mt);emu.write(a+1,math.floor(v/256),mt)end
local function log(e)
 local s=emu.getState();local f=s.frameCount
 fh:write(string.format('%d,%s,%04X,%04X,%04X,%04X,%04X,%04X,%04X,%04X,%02X,%04X,%04X\n',
 f,e,w(0x1e33),w(0x1b74),w(0x1b90),w(0x1b92),w(0x1a08),w(0x1a0a),w(0x1a0c),w(0x1a0e),b(0x1a11),s['cpu.cs'] or 0,s['cpu.ip'] or 0))
end
local function input()
 local f=emu.getState().frameCount;local inp={}
 if f<500 then inp.start=(f%90)<3 end
 if f>=520 and f<524 then inp.down=true end
 if f>=610 and f<614 then inp.a=true end
 emu.setInput(inp,0)
end
local function statewrite(addr,val)
 local f=emu.getState().frameCount
 if f>=3400 then log(string.format('write_%04X_%02X',addr,val))end
end
local fixing=false
local function coordwrite(addr,val)
 local f=emu.getState().frameCount
 if f>=3501 and f<3550 and not fixing then
  fixing=true
  ww(0x1b90,tonumber(os.getenv('QA_AX') or '336'))
  ww(0x1b92,tonumber(os.getenv('QA_CX') or '304'))
  fixing=false
 end
end
local function frame()
 local f=emu.getState().frameCount
 if f==3500 then
  log('before_poke')
  ww(0x1a08,tonumber(os.getenv('QA_X') or '560'))
  if os.getenv('QA_Y') then ww(0x1a0a,tonumber(os.getenv('QA_Y')))end
  ww(0x1a0c,tonumber(os.getenv('QA_X') or '560'))
  if os.getenv('QA_Y') then ww(0x1a0e,tonumber(os.getenv('QA_Y')))end
  ww(0x1b90,tonumber(os.getenv('QA_AX') or '336'))
  ww(0x1b92,tonumber(os.getenv('QA_CX') or '304'))
  log('after_poke')
 end
 if f>=3500 and f%60==0 then log('sample')end
 if f==4200 then
  log('final')
  local g=assert(io.open(path,'wb'));g:write(emu.takeScreenshot());g:close()
  fh:close();emu.stop(0)
 end
end
emu.addMemoryCallback(statewrite,emu.callbackType.write,0x1e33,0x1e34,emu.cpuType.ws,mt)
if os.getenv('QA_FREEZE')=='1' then
 emu.addMemoryCallback(coordwrite,emu.callbackType.write,0x1b90,0x1b93,emu.cpuType.ws,mt)
end
emu.addEventCallback(input,emu.eventType.inputPolled)
emu.addEventCallback(frame,emu.eventType.endFrame)
