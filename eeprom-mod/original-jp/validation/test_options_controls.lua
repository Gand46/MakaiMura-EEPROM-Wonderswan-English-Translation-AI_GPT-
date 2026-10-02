local f=0
local base=assert(os.getenv('OUT'))
local wr=emu.memType.wsWorkRam
local function shot(n) local p=assert(io.open(base..n..'.png','wb'));p:write(emu.takeScreenshot());p:close() end
local log=assert(io.open(base..'states.tsv','w'))
local function dump(n, mt,sz)
 local q=assert(io.open(base..n,'wb'));for i=0,sz-1 do q:write(string.char(emu.read(i,mt))) end;q:close()
end
emu.addEventCallback(function()
 f=f+1
 if f==3680 or f==3730 or f==3810 or f==3860 or f==3910 or f==3950 or f==3990 or f==4030 then
  local st=emu.read16(0x1E33,wr);local cur=emu.read(0x1E37,wr)
  log:write(string.format('%d\tstate=%04X\tcursor=%d\tmode=%d\toam_ptr=%04X\toam_count=%d\n',f,st,cur,emu.read(0x5FC,wr),emu.read16(0x1A40,wr),emu.read(0x1A42,wr)));log:flush()
  shot('frame'..f)
  dump('ram'..f..'.bin',wr,16384)
 end
 if f==4030 then
  log:close();emu.stop(emu.read16(0x1E33,wr)==0x50 and emu.read(0x1E37,wr)==3 and 0 or 2)
 end
end,emu.eventType.endFrame)
emu.addEventCallback(function()
 local k={start=false,up=false,down=false,left=false,right=false,a=false,b=false,up2=false,down2=false,left2=false,right2=false,sound=false}
 if f>=3505 and f<3515 then k.start=true end
 if (f>=3570 and f<3576) or (f>=3590 and f<3596) or (f>=3610 and f<3616) then k.down=true end
 if f>=3640 and f<3650 then k.a=true end
 -- Hold START on LEVEL: no ERASE allowed.
 if f>=3690 and f<3760 then k.start=true end
 if (f>=3790 and f<3796) or (f>=3840 and f<3846) or (f>=3890 and f<3896) then k.right=true end
 if (f>=3820 and f<3826) or (f>=3870 and f<3876) or (f>=4010 and f<4016) then k.down=true end
 if f>=3930 and f<3936 then k.left=true end
 emu.setInput(k,0)
end,emu.eventType.inputPolled)
