
;
; SCORE FUNCTION TEMPLATE
(score-function
 
 ((%p -1) (^ (* *) ) )
 ;(1 @EXPL-OR)

 ;(1 (^ (= x1 y1) (_parse x1 v1) (_parse y1 v1) ) )
 ;(sfSim (^ (= x1 y1) (<p> x1) (<p> y1) ) )

 ; Similarity (including disjointness) score
 ;(sfBaseCoref (^ (= x1 y1) ) )
 ;(:sfBaseUnify (^ (%p %1 %2) (%p %3 %4) (= %1 %3) (= %2 %4) ) )

 (:sfRelUnify (^ (synset%p %4 %1) (synset%p %5 %2) (causes _ %2 _) (= %1 %2) (= %4 %5) ) )
 (:sfRelUnify (^ (synset%p %4 %1) (synset%p %5 %2) (entails _ %2 _) (= %1 %2) (= %4 %5) ) )
 (:sfFnUnify (^ (FN%p _ %1 *) (FN%p _ %2 *) (= %1 %2) ) )
 (:sfFnUnify (^ (FN%p _ _ %1 *) (FN%p _ _ %2 *) (= %1 %2) ) )
 (:sfFnUnify (^ (FN%p _ _ _ %1 *) (FN%p _ _ _ %2 *) (= %1 %2) ) )
 (:sfFnUnify (^ (FN%p _ _ _ _ %1 *) (FN%p _ _ _ _ %2 *) (= %1 %2) ) )
 (:sfFnUnify (^ (FN%p _ _ _ _ _ %1 *) (FN%p _ _ _ _ _ %2 *) (= %1 %2) ) )
 (:sfFnUnify (^ (FN%p _ _ _ _ _ _ %1 *) (FN%p _ _ _ _ _ _ %2 *) (= %1 %2) ) )
 (:sfFnUnify (^ (FN%p _ _ _ _ _ _ _ %1 *) (FN%p _ _ _ _ _ _ _ %2 *) (= %1 %2) ) )
 (:sfFnUnify (^ (FN%p _ _ _ _ _ _ _ _ %1 *) (FN%p _ _ _ _ _ _ _ _ %2 *) (= %1 %2) ) )
 (:sfFnUnify (^ (FN%p _ _ _ _ _ _ _ _ _ %1) (FN%p _ _ _ _ _ _ _ _ _ %2) (= %1 %2) ) )
 
 (:sfBaseCoref (^ (%p-nn _ %1) (%q-nn _ %2) (= %1 %2) ) )
 (:sfBaseCoref (^ (%p-nn _ %1) (~%q _ %2) (= %1 %2) ) )
 (:sfBaseCorefProp (^ (%p-nn _ %1) (%q-nn _ %2) (@%p _ %1) (@%q _ %2) (= %1 %2) ) )
 
 ;; (:sfBaseCoref (^ (%p-vb _ %1 _ _) (%q-vb _ %2 _ _) (= %1 %2) ) )
 ;; (:sfBaseCoref (^ (%p-vb _ _ %1 _) (%q-vb _ _ %2 _) (= %1 %2) ) )
 ;; (:sfBaseCoref (^ (%p-vb _ _ _ %1) (%q-vb _ _ _ %2) (= %1 %2) ) )
 
 ; Selectional preference score
 ;; (pref (^ (= x1 y1) (<p1>-nn . x1) (<p2>-vb . y1 y2 y3) ) )
 ;; (pref (^ (= x1 y2) (<p1>-nn . x1) (<p2>-vb . y1 y2 y3) ) )
 ;; (pref (^ (= x1 y3) (<p1>-nn . x1) (<p2>-vb . y1 y2 y3) ) )
 
 
 )
