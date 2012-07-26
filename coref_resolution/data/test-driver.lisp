
;
; UNIFICATION.
(O (name simple_unify) (^ (guy-nn x1) (guy-nn x2) ) )

; 
; ARGUMENT CONSTRAINTS.

; Mario says that Peach is cute. Mario says that he hates Luigi. (e2 and e4 should NOT be unified)
(O (name ac_1) (^ (mario-nn x1) (say-vb e1 x1 e2 u1) (peach-nn x2) (cute-adj e2 x2) (say-vb e3 x1 e4 u2) (luigi-nn x3) (hate-vb e4 x1 x3 u3) ) )

; Mario says that Peach is cute. Mario says that Peach is cute. (e2 and e4 should be unified)
(O (name ac_2) (^ (mario-nn x1) (say-vb e1 x1 e2 u1) (peach-nn x2) (cute-adj e2 x2) (say-vb e3 x1 e4 u2) (cute-adj e4 x2) ) )

; Mario says that Peach is cute. Mario says that Peach is sweet. (e2 and e4 should be unified)
(B (=> (cute-adj e x) (sweet-adj e x) ) )
(O (name ac_3) (^ (mario-nn x1) (say-vb e1 x1 e2 u1) (peach-nn x2) (cute-adj e2 x2) (say-vb e3 x1 e4 u2) (sweet-adj e4 x2) ) )

;
; EXPLICIT NON-IDENTITY. (x1 and x2 in the examples below should not be unified)

; A guy is unlike another guy.
(O (name enid_single) (^ (guy-nn x1) (guy-nn x2) (unlike-in e1 x1 x2) ) )

; A guy is separate from another guy (?).
(O (name enid_multi)  (^ (guy-nn x1) (guy-nn x2) (separate-adj e1 x1) (from-in e2 e1 x2) ) )

;
; DISJOINTNESS.
(O (name wndisj_1) (^ (cat-nn x1) (dog-nn x2) (cute-adj x1) (cute-adj x2) ) )
(O (name wndisj_2) (^ (puppy-nn x1) (dog-nn x2) (cute-adj x1) (cute-adj x2) ) )

;
; NAMED ENTITIES.

; Mario jumped. Luigi also jumped. (x1 and x2 should NOT be unified)
(O (name ne_unify_1) (^ (mario-nn x1) (luigi-nn x2) (jump-vb e1 x1 u1 u2) (jump-vb e2 x2 u3 u4) (per e3 x1) (per e4 x2) ) )

; Lennon jumped. John Lennon jumped. (x1 and x2 should be unified)
(O (name ne_unify_2) (^ (lennon-nn x1) (john-lennon-nn x2) (jump-vb e1 x1 u1 u2) (jump-vb e2 x2 u3 u4) (per e3 x1) (per e4 x2) ) )

;
; FUNCTIONAL RELATIONS.

; Place 1 is the capital of German. Place 2 is the capital of Japan. (x1 and x2 should NOT be unified)
(O (name funcrel_unify) (^ (place-nn x1) (place-nn x2) (capital-nn e1 x3) (of-in e2 x3 x4) (german-nn x4) (capital-nn e3 x5) (of-in e4 x5 x6) (japan-nn x6) ) )