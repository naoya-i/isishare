
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

 ; Relational feature in hidden variables.
 ;; (:sfRelUnify (^ (synset%p %4 %1) (synset%p %5 %2) (causes _ %2 _) (= %1 %2) (= %4 %5) ) )
 ;; (:sfRelUnify (^ (synset%p %4 %1) (synset%p %5 %2) (entails _ %2 _) (= %1 %2) (= %4 %5) ) )
 (:sfFnUnify (^ (FN%p _ %1 *) (FN%p _ %2 *) (= %1 %2) ) )
 (:sfFnUnify (^ (FN%p _ _ %1 *) (FN%p _ _ %2 *) (= %1 %2) ) )
 (:sfFnUnify (^ (FN%p _ _ _ %1 *) (FN%p _ _ _ %2 *) (= %1 %2) ) )
 (:sfFnUnify (^ (FN%p _ _ _ _ %1 *) (FN%p _ _ _ _ %2 *) (= %1 %2) ) )
 (:sfFnUnify (^ (FN%p _ _ _ _ _ %1 *) (FN%p _ _ _ _ _ %2 *) (= %1 %2) ) )
 (:sfFnUnify (^ (FN%p _ _ _ _ _ _ %1 *) (FN%p _ _ _ _ _ _ %2 *) (= %1 %2) ) )
 (:sfFnUnify (^ (FN%p _ _ _ _ _ _ _ %1 *) (FN%p _ _ _ _ _ _ _ %2 *) (= %1 %2) ) )
 (:sfFnUnify (^ (FN%p _ _ _ _ _ _ _ _ %1 *) (FN%p _ _ _ _ _ _ _ _ %2 *) (= %1 %2) ) )
 (:sfFnUnify (^ (FN%p _ _ _ _ _ _ _ _ _ %1 *) (FN%p _ _ _ _ _ _ _ _ _ %2 *) (= %1 %2) ) )

 ;; ;(:sfSynsetCoref (^ (synset%p _ %1) (synset%q _ %2) (= %1 %2) ) )
 (:sfSynsetCoref (^ (synset%p _ %1) (synset%p _ %2) (= %1 %2) ) )

 ; FrameNet Selectional Restruction
 ;; (:sfFnSelRestr (^ (synset%p _ %1) (FN%q _ %2 *) (= %1 %2) ) )
 ;; (:sfFnSelRestr (^ (synset%p _ %1) (FN%q _ _ %2 *) (= %1 %2) ) )
 ;; (:sfFnSelRestr (^ (synset%p _ %1) (FN%q _ _ _ %2 *) (= %1 %2) ) )
 ;; (:sfFnSelRestr (^ (synset%p _ %1) (FN%q _ _ _ _ %2 *) (= %1 %2) ) )
 ;; (:sfFnSelRestr (^ (synset%p _ %1) (FN%q _ _ _ _ _ %2 *) (= %1 %2) ) )
 ;; (:sfFnSelRestr (^ (synset%p _ %1) (FN%q _ _ _ _ _ _ %2 *) (= %1 %2) ) )
 ;; (:sfFnSelRestr (^ (synset%p _ %1) (FN%q _ _ _ _ _ _ _ %2 *) (= %1 %2) ) )
 ;; (:sfFnSelRestr (^ (synset%p _ %1) (FN%q _ _ _ _ _ _ _ _ %2 *) (= %1 %2) ) )
 
 ; NP-NP pairs.
 (:sfBaseCoref (^ (%p-nn _ %1) (%q-nn _ %2) (= %1 %2) ) )
 (:sfBaseCoref (^ (%p-nn _ %1) (~%q _ %2) (= %1 %2) ) )
 (:sfBaseCoref (^ (~%p _ %1) (~%q _ %2) (= %1 %2) ) )
 (:sfBaseCorefProp (^ (@%p _ %1) (@%q _ %2) (= %1 %2) ) )

 ;; ; Narrative chain score.
 ;; (:sfSlots (^ (%p-vb _ %1 _ _) (%q-vb _ %2 _ _) (%r-nn _ %1) (%s-nn _ %2) (= %1 %2) ) )
 ;; (:sfSlots (^ (%p-vb _ _ %1 _) (%q-vb _ _ %2 _) (%r-nn _ %1) (%s-nn _ %2) (= %1 %2) ) )
 ;; (:sfSlots (^ (%p-vb _ _ _ %1) (%q-vb _ _ _ %2) (%r-nn _ %1) (%s-nn _ %2) (= %1 %2) ) )

 ;; (:sfSlots (^ (%p-vb _ %1 _ _) (%q-vb _ _ %2 _) (%r-nn _ %1) (%s-nn _ %2) (= %1 %2) ) )
 ;; (:sfSlots (^ (%p-vb _ %1 _ _) (%q-vb _ _ _ %2) (%r-nn _ %1) (%s-nn _ %2) (= %1 %2) ) )
 
 ; Modality constraints (John might ran. A man ran.)
 ; (:sfModConstr (^ (%p-M _ %1) (%q-M _ %2) (= %1 %2) ) )
 
 ; Argument constraints (John says that she is brabra. A man says that he is brabra.)
 ;(:sfArgConstr (^ (%p-vb %1 _ %3 _) (%q-vb %2 _ %4 _) (%r-vb %3 _ _ _) (%s-vb %4 _ _ _) (= %1 %2) (!= %3 %4) ) )
  
 )
