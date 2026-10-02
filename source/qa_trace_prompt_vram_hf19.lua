local mt=emu.memType.wsWorkRam
local target=assert(tonumber(os.getenv('QA_STATE') or '272'))
local out=assert(os.getenv('MESEN_LUA_REPORT'))
local dst=assert(os.getenv('MESEN_CAPTURE_PATH'))
local counters={}
local function wr(addr,val)
 local f=emu.getState().frameCount
 if f<180 or f>250 then return end
 local s=emu.getState();local key=string.format('%04X:%04X',s['cpu.cs'] or 0,s['cpu.ip'] or 0)
 local q=counters[key]
 if not q then
  q={n=0,lo=addr,hi=addr,frame=f,ds=s['cpu.ds'] or 0,si=s['cpu.si'] or 0,ax=s['cpu.a'] or 0,cx=s['cpu.cx'] or 0}
  counters[key]=q
 end
 q.n=q.n+1;q.lo=math.min(q.lo,addr);q.hi=math.max(q.hi,addr)
end
local function frame()
 local f=emu.getState().frameCount
 if f==180 then emu.write(0x1e33,target%256,mt);emu.write(0x1e34,math.floor(target/256),mt)end
 if f==300 then
  local h=assert(io.open(dst,'wb'));h:write(emu.takeScreenshot());h:close()
  local keys={};for k in pairs(counters) do keys[#keys+1]=k end;table.sort(keys)
  local r=assert(io.open(out,'w'))
  r:write('pc,n,lo,hi,first_frame,ds,si,ax,cx\n')
  for _,k in ipairs(keys) do
   local q=counters[k]
   r:write(string.format('%s,%d,%04X,%04X,%d,%04X,%04X,%04X,%04X\n',k,q.n,q.lo,q.hi,q.frame,q.ds,q.si,q.ax,q.cx))
  end
  r:close();emu.stop(0)
 end
end
emu.addMemoryCallback(wr,emu.callbackType.write,0x2000,0x3fff,emu.cpuType.ws,mt)
emu.addEventCallback(frame,emu.eventType.endFrame)
