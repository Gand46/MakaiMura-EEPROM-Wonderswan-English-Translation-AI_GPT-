local f=0
local base=assert(os.getenv('OUT'))
local wr=emu.memType.wsWorkRam
local function shot(n) local p=assert(io.open(base..n..'.png','wb'));p:write(emu.takeScreenshot());p:close() end
local log=assert(io.open(base..'states.tsv','w'))
local function dump(n, mt,sz)
 local q=assert(io.open(base..n,'wb'));for i=0,sz-1 do q:write(string.char(emu.read(i,mt))) end;q:close()
end
local phase='seek';local age=0
emu.resetAccessCounters()
emu.addEventCallback(function()
 f=f+1;age=age+1
 if phase=='seek' and f>4200 and emu.read(0x1E92,wr)==2 then phase='hold';age=0 end
 if f==3910 or f==3980 or f==4100 then shot('checkpoint'..f)end
 if (phase=='hold' and age==75) or f>6200 then
  shot('checkpoint_saved')
  local diff=0;for i=0,644 do if emu.read(0x370+i,wr)~=emu.read(i,emu.memType.wsCartEeprom)then diff=diff+1 end end
  local writes=0;for _,v in pairs(emu.getAccessCounters(emu.memType.wsCartEeprom,emu.counterType.writeCount))do writes=writes+v end
  log:write(string.format('frame=%d state=%04X mode=%d pause=%d diff=%d writes=%d\n',f,emu.read16(0x1E33,wr),emu.read16(0x1B74,wr),emu.read(0x1E92,wr),diff,writes));log:close()
  emu.stop(diff==0 and writes>0 and emu.read(0x1E92,wr)==2 and 0 or 2)
 end
end,emu.eventType.endFrame)
emu.addEventCallback(function()
 local k={start=false,up=false,down=false,left=false,right=false,a=false,b=false,up2=false,down2=false,left2=false,right2=false,sound=false}
 if f>=3505 and f<3515 then k.start=true end
 if (f>=3570 and f<3576) or (f>=3590 and f<3596) or (f>=3610 and f<3616) then k.down=true end
 if f>=3640 and f<3650 then k.a=true end
 if (f>=3700 and f<3706) or (f>=3720 and f<3726) or (f>=3740 and f<3746) then k.down=true end
 if f>=3770 and f<3780 then k.left2=true;k.right2=true end
 if f>=3880 and f<3886 then k.right=true end
 if (f>=3920 and f<3926)or(f>=3950 and f<3956)then k.down=true end
 if f>=4000 and f<4008 then k.a=true end
 if phase=='seek' and f>4200 and f%120<10 then k.start=true end
 if phase=='hold' and age>=15 and age<65 then k.start=true end
 emu.setInput(k,0)
end,emu.eventType.inputPolled)
