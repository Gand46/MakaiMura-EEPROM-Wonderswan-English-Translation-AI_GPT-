.code16
.intel_syntax noprefix
.section .text
.global aux_start, options_entry, render_options_ui, aux_end
.global main_reset_off, main_commit_off, main_draw_glyph_off

/* OPTIONS-only ERASE confirmation, 5000:DF38. No fifth row, no cursor rewrite.
 * 05FC: 0 native, 1 confirm, 2 done, 3 cancel/release, 4 reset pending commit
 * 05FD: armed after release (normal START / modal confirmation)
 * 05FE: hold count (normal) / feedback timer (done)
 * 05FF: reserved, zeroed on boot by the main shim.
 * Enter only with cursor EXIT (3), START ALONE for 45 updates after release.
 * All normal menu keys incl. Tip 10 Y2+Y4 are passed through unchanged.
 */
aux_start:
options_entry:
    /* Native prologue already saved registers; DS=0. */
    cmp byte ptr ds:0x05FC, 0
    jne modal
    cmp byte ptr ds:0x1E37, 3
    jne reset_hold
    cmp byte ptr ds:0x1E32, 0
    jne reset_hold
    mov ax, word ptr ds:0x1E39
    test ax, 0x0200
    jz arm_start
    cmp ax, 0x0200
    jne reset_hold
    cmp byte ptr ds:0x05FD, 1
    jne native
    inc byte ptr ds:0x05FE
    cmp byte ptr ds:0x05FE, 45
    jb native
    mov byte ptr ds:0x05FC, 1
    mov byte ptr ds:0x05FD, 0
    mov byte ptr ds:0x05FE, 0
    jmp redraw
arm_start:
    mov byte ptr ds:0x05FD, 1
    mov byte ptr ds:0x05FE, 0
    jmp native
reset_hold:
    mov byte ptr ds:0x05FD, 0
    mov byte ptr ds:0x05FE, 0
native:
    /* Exactly the displaced instructions, including mirror segment selector. */
    mov ax, 0x0037
    mov es, ax
    .byte 0xEA
    .word 0x103E, 0x4000

modal:
    mov ax, word ptr ds:0x1E39
    cmp byte ptr ds:0x05FC, 1
    je confirm
    cmp byte ptr ds:0x05FC, 3
    je wait_release
    cmp byte ptr ds:0x05FE, 0
    je wait_release
    dec byte ptr ds:0x05FE
    jmp redraw
wait_release:
    test ax, ax
    jnz redraw
    mov byte ptr ds:0x05FC, 0
    mov byte ptr ds:0x05FD, 1
    mov byte ptr ds:0x05FE, 0
    jmp redraw
confirm:
    cmp byte ptr ds:0x05FD, 1
    je confirmed_armed
    test ax, ax
    jnz redraw
    mov byte ptr ds:0x05FD, 1
    jmp redraw
confirmed_armed:
    test ax, 0x0800               /* B wins over simultaneous A+B. */
    jnz cancel
    cmp ax, 0x0400                /* Only A alone can erase. */
    je yes
    jmp redraw
cancel:
    mov byte ptr ds:0x05FC, 3
    mov byte ptr ds:0x05FD, 0
    jmp redraw
yes:
    /* Logical reset, not a forensic erase of unused EEPROM bytes.
     * Clear all 645 bytes before invoking the game's native initializer.
     */
    cld
    mov ax, 0x0037
    mov es, ax
    xor ax, ax
    xor di, di
    mov cx, 0x0285
    rep stosb
    .byte 0x9A
main_reset_off:
    .word 0x0000, 0x4000
    xor ax, ax
    mov ds, ax
    /* Commit only AFTER the original renderer normalizes PLAYER-1 at 001Bh.
     * Otherwise native redraw would immediately dirty that derived save byte.
     */
    mov byte ptr ds:0x05FC, 4
    mov byte ptr ds:0x05FD, 0
redraw:
    /* Original CALL 122F renders cursor + LEVEL/PLAYER/JUMP/SHOT values.
     * Its F3AA call is hooked once, before OAM state is reset.
     */
    .byte 0xEA
    .word 0x1227, 0x4000

/* Native glyph entries in D000:DB3E, each 8x8.
 * Two lines in the vacant upper panel (y36/46), not below EXIT.
 * No new tiles, no normal-menu OAM, no replacement of any original labels.
 */
render_options_ui:
    pushf
    pusha
    push ds
    push es
    xor ax, ax
    mov ds, ax
    cmp byte ptr ds:0x05FC, 4
    jne render_select
    .byte 0x9A
main_commit_off:
    .word 0x0000, 0x4000
    xor ax, ax
    mov ds, ax
    mov byte ptr ds:0x05FC, 2
    mov byte ptr ds:0x05FE, 60
render_select:
    cmp byte ptr ds:0x05FC, 1
    je render_confirm
    cmp byte ptr ds:0x05FC, 2
    je render_done
    jmp render_return
render_confirm:
    mov si, offset prompt
    call draw_text
    mov si, offset buttons
    call draw_text
    jmp render_return
render_done:
    mov si, offset done_text
    call draw_text
render_return:
    pop es
    pop ds
    popa
    popf
    retf

/* CS:SI list of (glyph index,x,y), terminated by FFh.
 * Native renderer may clobber DS but preserves CPU general registers.
 * Total modal budget 9+7=16 sprites + native OPTIONS list, no overlap.
 */
draw_text:
    mov bp, si
    mov ax, 0xD000
    mov es, ax
next_glyph:
    mov al, byte ptr cs:[bp]
    cmp al, 0xFF
    je text_done
    xor ah, ah
    mov dx, ax
    mov ch, byte ptr cs:[bp+1]
    mov cl, byte ptr cs:[bp+2]
    mov si, 0xDB3E
    .byte 0x9A
main_draw_glyph_off:
    .word 0x0000, 0x4000
    add bp, 3
    jmp next_glyph
text_done:
    ret
prompt:
    /* ERASE SAVE */
    .byte 0x0E,72,36, 0x1B,80,36, 0x0A,88,36, 0x1C,96,36, 0x0E,104,36
    .byte 0x1C,120,36, 0x0A,128,36, 0x1F,136,36, 0x0E,144,36, 0xFF
buttons:
    /* A YES   B NO */
    .byte 0x0A,64,46, 0x22,80,46, 0x0E,88,46, 0x1C,96,46
    .byte 0x0B,120,46, 0x17,136,46, 0x18,144,46, 0xFF
done_text:
    /* DONE */
    .byte 0x0D,96,40, 0x18,104,40, 0x17,112,40, 0x0E,120,40, 0xFF
aux_end:
