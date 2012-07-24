

; Argument constraints.
(O (name ac_1) (^ (mario-nn x1) (say-vb e1 x1 e2 u1) (peach-nn x2) (cute-adj e2 x2) (say-vb e3 x1 e4 u2) (luigi-nn x3) (hate-vb e4 x1 x3 u3) ) )
(O (name ac_2) (^ (mario-nn x1) (say-vb e1 x1 e2 u1) (peach-nn x2) (cute-adj e2 x2) (say-vb e3 x1 e4 u2) (luigi-nn x3) (cute-adj e4 x2) ) )

(B (=> (cute-adj e x) (sweet-adj e x) ) )
(O (name ac_3) (^ (mario-nn x1) (say-vb e1 x1 e2 u1) (peach-nn x2) (cute-adj e2 x2) (say-vb e3 x1 e4 u2) (luigi-nn x3) (sweet-adj e4 x2) ) )

; Explicit non-identity.
(O (name enid_single) (^ (guy-nn x1) (guy-nn x2) (unlike-in e1 x1 x2) ) )
(O (name enid_multi)  (^ (guy-nn x1) (guy-nn x2) (separate-adj e1 x1) (from-in e2 e1 x2) ) )
