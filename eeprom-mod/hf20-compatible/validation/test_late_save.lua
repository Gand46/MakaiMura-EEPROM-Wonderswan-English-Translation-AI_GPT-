-- Synthetic stage initialization; real pause/SAVE input.
local f=0;local wr=emu.memType.wsWorkRam;local ep=emu.memType.wsCartEeprom
local out=assert(os.getenv('OUT'));local mode=tonumber(os.getenv('QA_MODE')) or 17
local log=assert(io.open(out..'late_save.tsv','w'))
local function ww(a,v)emu.write(a,v%256,wr);emu.write(a+1,math.floor(v/256),wr)end
local function shot(n)local p=assert(io.open(out..n..'.png','wb'));p:write(emu.takeScreenshot());p:close()end
emu.resetAccessCounters()
emu.addEventCallback(function()
 f=f+1
 if f==3400 then ww(0x1b74,mode);ww(0x1e33,0x170)end
 if f==4250 then shot('late_pause_before')end
 if f==4320 then
  local diff=0;for i=0,644 do if emu.read(0x370+i,wr)~=emu.read(i,ep)then diff=diff+1 end end
  local writes=0;for _,v in pairs(emu.getAccessCounters(ep,emu.counterType.writeCount))do writes=writes+v end
  local ps=emu.read(0x1e92,wr);local state=emu.read16(0x1e33,wr)
  log:write(string.format('method=SYNTHETIC_STATE+INPUT mode=%d state=%04X pause=%d diff=%d writes=%d\n',emu.read16(0x1b74,wr),state,ps,diff,writes));log:close();shot('late_saved');emu.stop(ps==2 and diff==0 and writes>0 and 0 or 2)
 end
end,emu.eventType.endFrame)
emu.addEventCallback(function()
 local k={}
 if f<500 then k.start=(f%90)<3 end
 if f>=520 and f<524 then k.down=true end
 if f>=610 and f<614 then k.a=true end
 if (f>=4210 and f<4220)or(f>=4260 and f<4315)then k.start=true end
 emu.setInput(k,0)
end,emu.eventType.inputPolled)
