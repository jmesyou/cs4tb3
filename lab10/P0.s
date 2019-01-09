'''
names: James You, Zicheng Jiang
'''


# advance (OFFSET) :
#   moves PC ahead by the OFFSET

        .data   
j_:     .space 4
i_:     .space 4
a_:     .space 4
        .text
        .globl p   
        .ent p

p:      
                            # offset(u) = 20
                            # offset(v) = 16
                            # offset(w) = 12
                            # offset(x) = 8
                            # offset(y) = 4
                            # offset(z) = 0
        sw $fp, -28($sp)    # M[$sp - parametersize - 4] = $fp
        sw $ra, -32($sp)    # M[parametersize + 8] = 32
        sub $fp, $sp, 24    # $fp := $sp - parametersize
        sub $sp, $fp, 8     # $sp := $fp - 8
        lw $t0, 20($fp)     # $t0 := M[$fp + offset(u)]
        addi $t5, $0, 1     # $t5 := 1
        sw $t5, 0($t0)      # [M[adr(u) = ] M[$t0] := $t5
        lw $t2, 20($fp)     # $t2 := M[$fp + offset(u)]
        lw $t6, 0($t2)      # $t6 := M[$t2]
        beq $t6, $0, L1     # if $t6 == $0: advance (L1 << 2) else: advance (4)

L2:
        lw $t8, 16($fp)     # $t8 := M[$fp + offset(v)]
        beq $t8, $0, L3     # if $t8 == $0: advance (L3 << 2) else: advance (4)

L4:
        addi $t4, $0, 1     # $t4 := 1
        b, L5               # advance (L5 << 2)

L3:
L1:
        addi $t4, $0, 1     # $t4 := 1

L5:
        sw $t4, 16($fp)     # M[$fp + offset(v)] = $t4
        lw $t1, 8($fp)      # M[$fp + offset(x)] = $t1
        lw $t7, 12($fp)     # M[$fp + offset(w)] = $t7
        add $t7, $t7, 3     # $t7 := $t7 + 3
        sw $t7, 0($t1)      # M[$t1] = $t7
        addi $t3, $0, 5     # $t3 := 5
        sw $t3, 12($fp)     # M[$fp + offset(w)] = $t3
        lw $t5, 4($fp)      # $t5 := M[$fp + offset(y)]
        addi $t2, $0, 7     # $t2 := 7
        lw $t6, 0($fp)      # $t6 := M[$fp + offset(z)]
        sub $t2, $t2, $t6   # $t2 := $t2 - $t6
        add $sp, $fp, 24    # $sp := $fp + parametersize
        lw $ra, -8($fp)     # $ra := M[$fp - 8]
        lw $fp, -4($fp)     # $fp := M[$fp - 4]
        jr $ra              # PC := nPC; nPC = $ra
        .text
        .globl main
        .ent main

main:
        la $t8, a_          # $t8 := adr(a)
        sw $t8, -4($sp)     # M[$sp - 4] = $t8
        addi $t4, $0, 1     # $t4 := 1
        sw $t4, -8($sp)     # M[$sp - 8] = $t4
        addi $t7, $0, 7     # $t7 := 7
        sw $t7, -12($sp)    # M[$sp - 12] = $t7
        la $t3, i_          # $t3 := adr(i)
        sw $t3, -16($sp)    # M[$sp - 16] = $t3
        la $t2, j_          # $t2 := adr(j)
        sw $t2, -20($sp)    # M[$sp - 16] = $t2
        addi $t6, $0, 9     # $t6 := 9
        sw $t6, -24($sp)    # M[$sp - 24] = $t6
        jal, p              # $ra := PC + 8 (or nPC + 4); PC := nPC; nPC := (PC & 0xf0000000) | (p << 2);
        lw $t8, a_          # $t8 = adr(a)
        beq $t8, $0, L6     # if $t8 == $0: advance (L6 << 2) else: advance (4) 

L7:
        lw $a0, j_          # $a0 := M[adr(j)]
        li $v0, 1           # $v0 := 1
        syscall

L6:
        li $v0, 10          # $v0 := 10
        syscall
        .end main