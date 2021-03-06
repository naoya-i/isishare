(O (name e1) (label (^
      (inst_smarket_shopping ?s :10)
      (go_step ?s GO1 :10)
      (find_step ?s FIND1 :10)
      (buy_step ?s ?b :10)
      (pay_step ?b PAY1 :10)
      (shopper ?s JACK1 :10)
      (store ?s SM1 :10)
      (thing_shopped_for ?s MILK1 :10)
      (name JACK1 JACK :10)
      (inst_milk MILK1 :10)
      (on MILK1 SHF1 :10)
      (inst_shelf SHF1 :10)
      (precede GO1 FIND1 :10)
      (precede FIND1 PAY1 :10)
      (! (inst_liqst_shopping *))
      (! (inst_shopping *))
      (! (inst_robbing *))
      (! (inst_going_by_plane *))
      (! (inst_going_by_bus *))
      (! (inst_rest_dining *))
      (! (inst_drinking *))
      (! (inst_going_by_taxi *))
      (! (inst_paying *))
      (! (inst_jogging *))
      (! (inst_partying *))
     ) ) (^ 
      (inst_going GO1 :10)
      (goer GO1 JACK1 :10)
      (name JACK1 JACK :10)
      (dest_go GO1 SM1 :10)
      (inst_smarket SM1 :10)
      (precede GO1 FIND1 :10)
      (inst_finding FIND1 :10)
      (finder FIND1 JACK1 :10)
      (thing_found FIND1 MILK1 :10)
      (inst_milk MILK1 :10)
      (on MILK1 SHF1 :10)
      (inst_shelf SHF1 :10)
      (precede FIND1 PAY1 :10)
      (inst_paying PAY1 :10)
      (payer PAY1 JACK1 :10)
      (thing_paid PAY1 MILK1 :10)
     ) )

(O (name e2) (label (^
      (inst_smarket_shopping ?s :10)
      (go_step ?s GO2 :10)
      (buy_step ?s ?b :10)
      (pay_step ?b PAY2 :10)
      (shopper ?s BILL2 :10)
      (store ?s SM2 :10)
      (thing_shopped_for ?s MILK2 :10)
      (name BILL2 BILL :10)
      (inst_milk MILK2 :10)
      (precede GO2 PAY2 :10)
      (! (inst_liqst_shopping *))
      (! (inst_shopping *))
      (! (inst_robbing *))
      (! (inst_going_by_plane *))
      (! (inst_going_by_bus *))
      (! (inst_rest_dining *))
      (! (inst_drinking *))
      (! (inst_going_by_taxi *))
      (! (inst_paying *))
      (! (inst_jogging *))
      (! (inst_partying *))
     ) ) (^ 
      (inst_going GO2 :10)
      (goer GO2 BILL2 :10)
      (name BILL2 BILL :10)
      (dest_go GO2 SM2 :10)
      (inst_smarket SM2 :10)
      (precede GO2 PAY2 :10)
      (inst_paying PAY2 :10)
      (payer PAY2 BILL2 :10)
      (thing_paid PAY2 MILK2 :10)
      (inst_milk MILK2 :10)
     ) )

(O (name e3) (label (^
      (inst_smarket_shopping ?s :10)
      (inst_going_by_bus ?b :10)
      (go_step ?s ?b :10)
      (give_token_step ?b GIVE3 :10)
      (get_off_step ?b GETOFF3 :10)
      (shopper ?s JACK3 :10)
      (store ?s SM3 :10)
      (bus_driver ?b BD3 :10)
      (token ?b TK3 :10)
      (name JACK3 JACK :10)
      (precede GIVE3 GETOFF3 :10)
      (! (inst_liqst_shopping *))
      (! (inst_shopping *))
      (! (inst_robbing *))
      (! (inst_going_by_plane *))
      (! (inst_rest_dining *))
      (! (inst_drinking *))
      (! (inst_going_by_taxi *))
      (! (inst_paying *))
      (! (inst_jogging *))
      (! (inst_partying *))
     ) ) (^ 
      (inst_giving GIVE3 :10)
      (giver GIVE3 JACK3 :10)
      (name JACK3 JACK :10)
      (recipient GIVE3 BD3 :10)
      (occupation BD3 BUSDRIVER :10)
      (thing_given GIVE3 TK3 :10)
      (inst_token TK3 :10)
      (precede GIVE3 GETOFF3 :10)
      (inst_getting_off GETOFF3 :10)
      (agent_get_off GETOFF3 JACK3 :10)
      (place_get_off GETOFF3 SM3 :10)
      (inst_smarket SM3 :10)
     ) )

(O (name e4) (label (^
      (inst_robbing ?r :10)
      (inst_going_by_bus ?b :10)
      (go_step ?r ?b :10)
      (get_off_step ?b GETOFF4 :10)
      (point_weapon_step ?r POINT4 :10)
      (vehicle ?b BUS4 :10)
      (robber ?r JACK4 :10)
      (weapon_rob ?r GUN4 :10)
      (victim_rob ?r O4 :10)
      (place_rob ?r LS4 :10)
      (name JACK4 JACK :10)
      (inst_liquor_store LS4 :10)
      (inst_gun GUN4 :10)
      (own O4 LS4 :10)
      (precede GETOFF4 POINT4 :10)
      (! (inst_smarket_shopping *))
      (! (inst_liqst_shopping *))
      (! (inst_shopping *))
      (! (inst_going_by_plane *))
      (! (inst_rest_dining *))
      (! (inst_drinking *))
      (! (inst_going_by_taxi *))
      (! (inst_paying *))
      (! (inst_jogging *))
      (! (inst_partying *))
     ) ) (^ 
      (inst_getting_off GETOFF4 :10)
      (agent_get_off GETOFF4 JACK4 :10)
      (name JACK4 JACK :10)
      (patient_get_off GETOFF4 BUS4 :10)
      (inst_bus BUS4 :10)
      (place_get_off GETOFF4 LS4 :10)
      (inst_liquor_store LS4 :10)
      (precede GETOFF4 POINT4 :10)
      (inst_pointing POINT4 :10)
      (agent_point POINT4 JACK4 :10)
      (instr_point POINT4 GUN4 :10)
      (inst_gun GUN4 :10)
      (patient_point POINT4 O4 :10)
      (own O4 LS4 :10)
     ) )

(O (name e5) (label (^
      (inst_liqst_shopping ?s :10)
      (go_step ?s GO5 :10)
      (find_step ?s FIND5 :10)
      (shopper ?s JACK5 :10)
      (store ?s LS5 :10)
      (thing_shopped_for ?s BOURBON5 :10)
      (name JACK5 JACK :10)
      (inst_bourbon BOURBON5 :10)
      (on BOURBON5 SHF5 :10)
      (inst_shelf SHF5 :10)
      (precede GO5 FIND5 :10)
      (! (inst_smarket_shopping *))
      (! (inst_shopping *))
      (! (inst_robbing *))
      (! (inst_going_by_plane *))
      (! (inst_going_by_bus *))
      (! (inst_rest_dining *))
      (! (inst_drinking *))
      (! (inst_going_by_taxi *))
      (! (inst_paying *))
      (! (inst_jogging *))
      (! (inst_partying *))
     ) ) (^ 
      (inst_going GO5 :10)
      (goer GO5 JACK5 :10)
      (name JACK5 JACK :10)
      (dest_go GO5 LS5 :10)
      (inst_liquor_store LS5 :10)
      (precede GO5 FIND5 :10)
      (inst_finding FIND5 :10)
      (finder FIND5 JACK5 :10)
      (thing_found FIND5 BOURBON5 :10)
      (inst_bourbon BOURBON5 :10)
      (on BOURBON5 SHF5 :10)
      (inst_shelf SHF5 :10)
     ) )

(O (name e6) (label (^
      (inst_robbing ?r :10)
      (go_step ?r GO6 :10)
      (point_weapon_step ?r POINT6 :10)
      (robber ?r BILL6 :10)
      (place_rob ?r LS6 :10)
      (weapon_rob ?r GUN6 :10)
      (victim_rob ?r O6 :10)
      (name BILL6 BILL :10)
      (inst_liquor_store LS6 :10)
      (inst_gun GUN6 :10)
      (own O6 LS6 :10)
      (precede GO6 POINT6 :10)
      (! (inst_smarket_shopping *))
      (! (inst_liqst_shopping *))
      (! (inst_shopping *))
      (! (inst_going_by_plane *))
      (! (inst_going_by_bus *))
      (! (inst_rest_dining *))
      (! (inst_drinking *))
      (! (inst_going_by_taxi *))
      (! (inst_paying *))
      (! (inst_jogging *))
      (! (inst_partying *))
     ) ) (^ 
      (inst_going GO6 :10)
      (goer GO6 BILL6 :10)
      (name BILL6 BILL :10)
      (dest_go GO6 LS6 :10)
      (inst_liquor_store LS6 :10)
      (precede GO6 POINT6 :10)
      (inst_pointing POINT6 :10)
      (agent_point POINT6 BILL6 :10)
      (instr_point POINT6 GUN6 :10)
      (inst_gun GUN6 :10)
      (patient_point POINT6 O6 :10)
      (own O6 LS6 :10)
     ) )

(O (name e7) (label (^
      (inst_going_by_bus ?b :10)
      (give_token_step ?b GIVE7 :10)
      (goer ?b BILL7 :10)
      (bus_driver ?b BD7 :10)
      (token ?b TK7 :10)
      (name BILL7 BILL :10)
      (! (inst_smarket_shopping *))
      (! (inst_liqst_shopping *))
      (! (inst_shopping *))
      (! (inst_robbing *))
      (! (inst_going_by_plane *))
      (! (inst_rest_dining *))
      (! (inst_drinking *))
      (! (inst_going_by_taxi *))
      (! (inst_paying *))
      (! (inst_jogging *))
      (! (inst_partying *))
     ) ) (^ 
      (inst_giving GIVE7 :10)
      (giver GIVE7 BILL7 :10)
      (name BILL7 BILL :10)
      (recipient GIVE7 BD7 :10)
      (occupation BD7 BUSDRIVER :10)
      (thing_given GIVE7 TK7 :10)
      (inst_token TK7 :10)
     ) )

(O (name e8) (label (^
      (inst_robbing ROB8 :10)
      (point_weapon_step ROB8 POINT8 :10)
      (robber ROB8 FRED8 :10)
      (weapon_rob ROB8 GUN8 :10)
      (victim_rob ROB8 O8 :10)
      (place_rob ROB8 LS8 :10)
      (name FRED8 FRED :10)
      (inst_liquor_store LS8 :10)
      (inst_gun GUN8 :10)
      (own O8 LS8 :10)
      (! (inst_smarket_shopping *))
      (! (inst_liqst_shopping *))
      (! (inst_shopping *))
      (! (inst_going_by_plane *))
      (! (inst_going_by_bus *))
      (! (inst_rest_dining *))
      (! (inst_drinking *))
      (! (inst_going_by_taxi *))
      (! (inst_paying *))
      (! (inst_jogging *))
      (! (inst_partying *))
     ) ) (^ 
      (inst_robbing ROB8 :10)
      (robber ROB8 FRED8 :10)
      (name FRED8 FRED :10)
      (place_rob ROB8 LS8 :10)
      (inst_liquor_store LS8 :10)
      (inst_pointing POINT8 :10)
      (agent_point POINT8 FRED8 :10)
      (instr_point POINT8 GUN8 :10)
      (inst_gun GUN8 :10)
      (patient_point POINT8 O8 :10)
      (own O8 LS8 :10)
     ) )

(O (name e9) (label (^
      (inst_robbing ?r :10)
      (get_weapon_step ?r GET9 :10)
      (go_step ?r GO9 :10)
      (robber ?r BILL9 :10)
      (weapon_rob ?r GUN9 :10)
      (place_rob ?r SM9 :10)
      (name BILL9 BILL :10)
      (inst_gun GUN9 :10)
      (inst_smarket SM9 :10)
      (precede GET9 GO9 :10)
      (! (inst_smarket_shopping *))
      (! (inst_liqst_shopping *))
      (! (inst_shopping *))
      (! (inst_going_by_plane *))
      (! (inst_going_by_bus *))
      (! (inst_rest_dining *))
      (! (inst_drinking *))
      (! (inst_going_by_taxi *))
      (! (inst_paying *))
      (! (inst_jogging *))
      (! (inst_partying *))
     ) ) (^ 
      (inst_getting GET9 :10)
      (agent_get GET9 BILL9 :10)
      (name BILL9 BILL :10)
      (patient_get GET9 GUN9 :10)
      (inst_gun GUN9 :10)
      (precede GET9 GO9 :10)
      (inst_going GO9 :10)
      (goer GO9 BILL9 :10)
      (dest_go GO9 SM9 :10)
      (inst_smarket SM9 :10)
     ) )

(O (name e10) (label (^
      (inst_robbing ?r :10)
      (go_step ?r GO10 :10)
      (point_weapon_step ?r POINT10 :10)
      (robber ?r FRED10 :10)
      (place_rob ?r SM10 :10)
      (weapon_rob ?r GUN10 :10)
      (victim_rob ?r O10 :10)
      (inst_going_by_plane ?p :10)
      (pack_step ?p PACK10 :10)
      (go_step ?p GO10B :10)
      (goer ?p FRED10 :10)
      (plane_luggage ?p BAG10 :10)
      (source_go ?p AIRPORT10 :10)
      (name FRED10 FRED :10)
      (inst_smarket SM10 :10)
      (inst_gun GUN10 :10)
      (own O10 SM10 :10)
      (precede GO10 POINT10 :10)
      (precede POINT10 PACK10 :10)
      (precede PACK10 GO10B :10)
      (! (inst_smarket_shopping *))
      (! (inst_liqst_shopping *))
      (! (inst_shopping *))
      (! (inst_going_by_bus *))
      (! (inst_rest_dining *))
      (! (inst_drinking *))
      (! (inst_going_by_taxi *))
      (! (inst_paying *))
      (! (inst_jogging *))
      (! (inst_partying *))
     ) ) (^ 
      (inst_going GO10 :10)
      (goer GO10 FRED10 :10)
      (name FRED10 FRED :10)
      (dest_go GO10 SM10 :10)
      (inst_smarket SM10 :10)
      (precede GO10 POINT10 :10)
      (inst_pointing POINT10 :10)
      (agent_point POINT10 FRED10 :10)
      (instr_point POINT10 GUN10 :10)
      (inst_gun GUN10 :10)
      (patient_point POINT10 O10 :10)
      (own O10 SM10 :10)
      (precede POINT10 PACK10 :10)
      (inst_packing PACK10 :10)
      (agent_pack PACK10 FRED10 :10)
      (patient_pack PACK10 BAG10 :10)
      (inst_bag BAG10 :10)
      (precede PACK10 GO10B :10)
      (inst_going GO10B :10)
      (goer GO10B FRED10 :10)
      (dest_go GO10B AIRPORT10 :10)
      (inst_airport AIRPORT10 :10)
     ) )

(O (name e11) (label (^
      (inst_going_by_plane ?p :10)
      (inst_going_by_bus GO11 :10)
      (go_step ?p GO11 :10)
      (buy_ticket_step ?p BUY11 :10)
      (vehicle GO11 BUS11 :10)
      (goer ?p JACK11 :10)
      (source_go ?p AIRPORT11 :10)
      (plane_ticket ?p TK11 :10)
      (name JACK11 JACK :10)
      (precede GO11 BUY11 :10)
      (! (inst_smarket_shopping *))
      (! (inst_liqst_shopping *))
      (! (inst_shopping *))
      (! (inst_robbing *))
      (! (inst_rest_dining *))
      (! (inst_drinking *))
      (! (inst_going_by_taxi *))
      (! (inst_paying *))
      (! (inst_jogging *))
      (! (inst_partying *))
     ) ) (^ 
      (inst_going GO11 :10)
      (goer GO11 JACK11 :10)
      (name JACK11 JACK :10)
      (vehicle GO11 BUS11 :10)
      (inst_bus BUS11 :10)
      (dest_go GO11 AIRPORT11 :10)
      (inst_airport AIRPORT11 :10)
      (precede GO11 BUY11 :10)
      (inst_buying BUY11 :10)
      (buyer BUY11 JACK11 :10)
      (thing_bought BUY11 TK11 :10)
      (inst_ticket TK11 :10)
     ) )

(O (name e12) (label (^
      (inst_going_by_plane ?p :10)
      (pack_step ?p PACK12 :10)
      (go_step ?p GO12 :10)
      (goer ?p BILL12 :10)
      (plane_luggage ?p SC12 :10)
      (source_go ?p AIRPORT12 :10)
      (name BILL12 BILL :10)
      (inst_suitcase SC12 :10)
      (precede PACK12 GO12 :10)
      (! (inst_smarket_shopping *))
      (! (inst_liqst_shopping *))
      (! (inst_shopping *))
      (! (inst_robbing *))
      (! (inst_going_by_bus *))
      (! (inst_rest_dining *))
      (! (inst_drinking *))
      (! (inst_going_by_taxi *))
      (! (inst_paying *))
      (! (inst_jogging *))
      (! (inst_partying *))
     ) ) (^ 
      (inst_packing PACK12 :10)
      (agent_pack PACK12 BILL12 :10)
      (name BILL12 BILL :10)
      (patient_pack PACK12 SC12 :10)
      (inst_suitcase SC12 :10)
      (precede PACK12 GO12 :10)
      (inst_going GO12 :10)
      (goer GO12 BILL12 :10)
      (dest_go GO12 AIRPORT12 :10)
      (inst_airport AIRPORT12 :10)
     ) )

(O (name e13) (label (^
      (inst_going_by_bus ?b :10)
      (get_on_step ?b GETON13 :10)
      (get_off_step ?b GETOFF13 :10)
      (vehicle ?b BUS13 :10)
      (inst_going_by_vehicle GO13 :10)
      (go_step GO13 ?b :10)
      (source_go GO13 PARK13 :10)
      (inst_smarket_shopping ?s :10)
      (go_step ?s GO13 :10)
      (shopper ?s JACK13 :10)
      (store ?s SM13 :10)
      (name JACK13 JACK :10)
      (inst_park PARK13 :10)
      (precede GETON13 GETOFF13 :10)
      (precede GETOFF13 GO13 :10)
      (! (inst_liqst_shopping *))
      (! (inst_shopping *))
      (! (inst_robbing *))
      (! (inst_going_by_plane *))
      (! (inst_rest_dining *))
      (! (inst_drinking *))
      (! (inst_going_by_taxi *))
      (! (inst_paying *))
      (! (inst_jogging *))
      (! (inst_partying *))
     ) ) (^ 
      (inst_getting_on GETON13 :10)
      (agent_get_on GETON13 JACK13 :10)
      (name JACK13 JACK :10)
      (patient_get_on GETON13 BUS13 :10)
      (inst_bus BUS13 :10)
      (precede GETON13 GETOFF13 :10)
      (inst_getting_off GETOFF13 :10)
      (agent_get_off GETOFF13 JACK13 :10)
      (place_get_off GETOFF13 PARK13 :10)
      (inst_park PARK13 :10)
      (precede GETOFF13 GO13 :10)
      (inst_going GO13 :10)
      (goer GO13 JACK13 :10)
      (dest_go GO13 SM13 :10)
      (inst_smarket SM13 :10)
     ) )

(O (name e14) (label (^
      (inst_going_by_bus ?b :10)
      (give_token_step ?b GIVE14 :10)
      (get_off_step ?b GETOFF14 :10)
      (bus_driver ?b BD14 :10)
      (token ?b TK14 :10)
      (inst_going_by_vehicle GO14 :10)
      (go_step GO14 ?b :10)
      (source_go GO14 PARK14 :10)
      (inst_going_by_plane ?p :10)
      (go_step ?p GO14 :10)
      (get_on_step ?p GETON14 :10)
      (goer ?p JACK14 :10)
      (source_go ?p AIRPORT14 :10)
      (vehicle ?p PLANE14 :10)
      (name JACK14 JACK :10)
      (inst_park PARK14 :10)
      (precede GIVE14 GETOFF14 :10)
      (precede GETOFF14 GO14 :10)
      (precede GO14 GETON14 :10)
      (! (inst_smarket_shopping *))
      (! (inst_liqst_shopping *))
      (! (inst_shopping *))
      (! (inst_robbing *))
      (! (inst_rest_dining *))
      (! (inst_drinking *))
      (! (inst_going_by_taxi *))
      (! (inst_paying *))
      (! (inst_jogging *))
      (! (inst_partying *))
     ) ) (^ 
      (inst_giving GIVE14 :10)
      (giver GIVE14 JACK14 :10)
      (name JACK14 JACK :10)
      (recipient GIVE14 BD14 :10)
      (occupation BD14 BUSDRIVER :10)
      (thing_given GIVE14 TK14 :10)
      (inst_token TK14 :10)
      (precede GIVE14 GETOFF14 :10)
      (inst_getting_off GETOFF14 :10)
      (agent_get_off GETOFF14 JACK14 :10)
      (place_get_off GETOFF14 PARK14 :10)
      (inst_park PARK14 :10)
      (precede GETOFF14 GO14 :10)
      (inst_going GO14 :10)
      (goer GO14 JACK14 :10)
      (dest_go GO14 AIRPORT14 :10)
      (inst_airport AIRPORT14 :10)
      (precede GO14 GETON14 :10)
      (inst_getting_on GETON14 :10)
      (agent_get_on GETON14 JACK14 :10)
      (patient_get_on GETON14 PLANE14 :10)
      (inst_plane PLANE14 :10)
     ) )

(O (name e15) (label (^
      (inst_smarket_shopping ?s :10)
      (go_step ?s GO15 :10)
      (shopper ?s FRED15 :10)
      (store ?s SM15 :10)
      (inst_going_by_bus GO15 :10)
      (sit_step GO15 SIT15 :10)
      (vehicle_seat GO15 SEAT15 :10)
      (vehicle GO15 BUS15 :10)
      (name FRED15 FRED :10)
      (precede SIT15 GO15 :10)
      (! (inst_liqst_shopping *))
      (! (inst_shopping *))
      (! (inst_robbing *))
      (! (inst_going_by_plane *))
      (! (inst_rest_dining *))
      (! (inst_drinking *))
      (! (inst_going_by_taxi *))
      (! (inst_paying *))
      (! (inst_jogging *))
      (! (inst_partying *))
     ) ) (^ 
      (inst_sitting SIT15 :10)
      (agent_sit SIT15 FRED15 :10)
      (name FRED15 FRED :10)
      (patient_sit SIT15 SEAT15 :10)
      (inst_seat SEAT15 :10)
      (in SEAT15 BUS15 :10)
      (inst_bus BUS15 :10)
      (precede SIT15 GO15 :10)
      (inst_going GO15 :10)
      (goer GO15 FRED15 :10)
      (dest_go GO15 SM15 :10)
      (inst_smarket SM15 :10)
     ) )

(O (name e16) (label (^
      (inst_rest_dining ?d :10)
      (go_step ?d GO16 :10)
      (diner ?d JACK16 :10)
      (restaurant ?d REST16 :10)
      (order_step ?d ORDER16 :10)
      (rest_thing_ordered ?d MS16 :10)
      (name JACK16 JACK :10)
      (inst_milkshake MS16 :10)
      (precede GO16 ORDER16 :10)
      (! (inst_smarket_shopping *))
      (! (inst_liqst_shopping *))
      (! (inst_shopping *))
      (! (inst_robbing *))
      (! (inst_going_by_plane *))
      (! (inst_going_by_bus *))
      (! (inst_drinking *))
      (! (inst_going_by_taxi *))
      (! (inst_paying *))
      (! (inst_jogging *))
      (! (inst_partying *))
     ) ) (^ 
      (inst_going GO16 :10)
      (goer GO16 JACK16 :10)
      (name JACK16 JACK :10)
      (dest_go GO16 REST16 :10)
      (inst_restaurant REST16 :10)
      (precede GO16 ORDER16 :10)
      (inst_ordering ORDER16 :10)
      (agent_order ORDER16 JACK16 :10)
      (patient_order ORDER16 MS16 :10)
      (inst_milkshake MS16 :10)
     ) )

(O (name e17) (label (^
      (inst_drinking DRINK17 :10)
      (drinker DRINK17 BILL17 :10)
      (name BILL17 BILL :10)
      (patient_drink DRINK17 MS17 :10)
      (inst_milkshake MS17 :10)
      (instr_drink DRINK17 STR17 :10)
      (! (inst_smarket_shopping *))
      (! (inst_liqst_shopping *))
      (! (inst_shopping *))
      (! (inst_robbing *))
      (! (inst_going_by_plane *))
      (! (inst_going_by_bus *))
      (! (inst_rest_dining *))
      (! (inst_going_by_taxi *))
      (! (inst_paying *))
      (! (inst_jogging *))
      (! (inst_partying *))
     ) ) (^ 
      (inst_drinking DRINK17 :10)
      (drinker DRINK17 BILL17 :10)
      (name BILL17 BILL :10)
      (patient_drink DRINK17 MS17 :10)
      (inst_milkshake MS17 :10)
      (instr_drink DRINK17 STR17 :10)
      (inst_straw STR17 :10)
     ) )

(O (name e18) (label (^
      (inst_rest_dining ?d :10)
      (go_step ?d ?b :10)
      (order_step ?d ORDER18 :10)
      (inst_going_by_bus ?b :10)
      (get_off_step ?b GETOFF18 :10)
      (vehicle ?b BUS18 :10)
      (diner ?d FRED18 :10)
      (restaurant ?d REST18 :10)
      (rest_thing_ordered ?d MS18 :10)
      (name FRED18 FRED :10)
      (inst_milkshake MS18 :10)
      (precede GETOFF18 ORDER18 :10)
      (! (inst_smarket_shopping *))
      (! (inst_liqst_shopping *))
      (! (inst_shopping *))
      (! (inst_robbing *))
      (! (inst_going_by_plane *))
      (! (inst_drinking *))
      (! (inst_going_by_taxi *))
      (! (inst_paying *))
      (! (inst_jogging *))
      (! (inst_partying *))
     ) ) (^ 
      (inst_getting_off GETOFF18 :10)
      (agent_get_off GETOFF18 FRED18 :10)
      (name FRED18 FRED :10)
      (patient_get_off GETOFF18 BUS18 :10)
      (inst_bus BUS18 :10)
      (place_get_off GETOFF18 REST18 :10)
      (inst_restaurant REST18 :10)
      (precede GETOFF18 ORDER18 :10)
      (inst_ordering ORDER18 :10)
      (agent_order ORDER18 FRED18 :10)
      (patient_order ORDER18 MS18 :10)
      (inst_milkshake MS18 :10)
     ) )

(O (name e19) (label (^
      (inst_drinking ?d :10)
      (put_straw_step ?d PUT19 :10)
      (drinker ?d JANET19 :10)
      (instr_drink ?d STR19 :10)
      (patient_drink ?d MS19 :10)
      (name JANET19 JANET :10)
      (inst_milkshake MS19 :10)
      (! (inst_smarket_shopping *))
      (! (inst_liqst_shopping *))
      (! (inst_shopping *))
      (! (inst_robbing *))
      (! (inst_going_by_plane *))
      (! (inst_going_by_bus *))
      (! (inst_rest_dining *))
      (! (inst_going_by_taxi *))
      (! (inst_paying *))
      (! (inst_jogging *))
      (! (inst_partying *))
     ) ) (^ 
      (inst_putting PUT19 :10)
      (agent_put PUT19 JANET19 :10)
      (name JANET19 JANET :10)
      (patient_put PUT19 STR19 :10)
      (inst_straw STR19 :10)
      (place_put PUT19 MS19 :10)
      (inst_milkshake MS19 :10)
     ) )

(O (name e20) (label (^
      (inst_rest_dining ?d :10)
      (go_step ?d ?b :10)
      (inst_going_by_bus ?b :10)
      (get_on_step ?b GETON20 :10)
      (vehicle ?b BUS20 :10)
      (get_off_step ?b GETOFF20 :10)
      (diner ?d BILL20 :10)
      (restaurant ?d REST20 :10)
      (drink_step ?d DRINK20 :10)
      (rest_thing_drunk ?d MS20 :10)
      (rest_drink_straw ?d STR20 :10)
      (name BILL20 BILL :10)
      (inst_milkshake MS20 :10)
      (precede GETON20 GETOFF20 :10)
      (precede GETOFF20 DRINK20 :10)
      (! (inst_smarket_shopping *))
      (! (inst_liqst_shopping *))
      (! (inst_shopping *))
      (! (inst_robbing *))
      (! (inst_going_by_plane *))
      (! (inst_drinking *))
      (! (inst_going_by_taxi *))
      (! (inst_paying *))
      (! (inst_jogging *))
      (! (inst_partying *))
     ) ) (^ 
      (inst_getting_on GETON20 :10)
      (agent_get_on GETON20 BILL20 :10)
      (name BILL20 BILL :10)
      (patient_get_on GETON20 BUS20 :10)
      (inst_bus BUS20 :10)
      (precede GETON20 GETOFF20 :10)
      (inst_getting_off GETOFF20 :10)
      (agent_get_off GETOFF20 BILL20 :10)
      (place_get_off GETOFF20 REST20 :10)
      (inst_restaurant REST20 :10)
      (precede GETOFF20 DRINK20 :10)
      (inst_drinking DRINK20 :10)
      (drinker DRINK20 BILL20 :10)
      (patient_drink DRINK20 MS20 :10)
      (inst_milkshake MS20 :10)
      (instr_drink DRINK20 STR20 :10)
      (inst_straw STR20 :10)
     ) )

(O (name e21) (label (^
      (inst_rest_dining ?d :10)
      (go_step ?d GO21 :10)
      (diner ?d BILL21 :10)
      (inst_going_by_bus GO21 :10)
      (restaurant ?d REST21 :10)
      (drink_step ?d DRINK21 :10)
      (rest_thing_drunk ?d MS21 :10)
      (inst_robbing ?r :10)
      (go_step ?r GO21 :10)
      (place_rob ?r REST21 :10)
      (point_weapon_step ?r POINT21 :10)
      (robber ?r BILL21 :10)
      (weapon_rob ?r GUN21 :10)
      (victim_rob ?r O21 :10)
      (get_valuable_step ?r GET21 :10)
      (thing_robbed ?r MONEY21 :10)
      (name BILL21 BILL :10)
      (vehicle GO21 BUS21 :10)
      (inst_milkshake MS21 :10)
      (inst_gun GUN21 :10)
      (own O21 REST21 :10)
      (inst_money MONEY21 :10)
      (precede GO21 DRINK21 :10)
      (precede DRINK21 POINT21 :10)
      (precede POINT21 GET21 :10)
      (! (inst_smarket_shopping *))
      (! (inst_liqst_shopping *))
      (! (inst_shopping *))
      (! (inst_going_by_plane *))
      (! (inst_drinking *))
      (! (inst_going_by_taxi *))
      (! (inst_paying *))
      (! (inst_jogging *))
      (! (inst_partying *))
     ) ) (^ 
      (inst_going GO21 :10)
      (goer GO21 BILL21 :10)
      (name BILL21 BILL :10)
      (vehicle GO21 BUS21 :10)
      (inst_bus BUS21 :10)
      (dest_go GO21 REST21 :10)
      (inst_restaurant REST21 :10)
      (precede GO21 DRINK21 :10)
      (inst_drinking DRINK21 :10)
      (drinker DRINK21 BILL21 :10)
      (patient_drink DRINK21 MS21 :10)
      (inst_milkshake MS21 :10)
      (precede DRINK21 POINT21 :10)
      (inst_pointing POINT21 :10)
      (agent_point POINT21 BILL21 :10)
      (instr_point POINT21 GUN21 :10)
      (inst_gun GUN21 :10)
      (patient_point POINT21 O21 :10)
      (own O21 REST21 :10)
      (precede POINT21 GET21 :10)
      (inst_getting GET21 :10)
      (agent_get GET21 BILL21 :10)
      (patient_get GET21 MONEY21 :10)
      (inst_money MONEY21 :10)
      (from_get GET21 O21 :10)
     ) )

(O (name e22) (label (^
      (inst_going_by_bus ?b :10)
      (give_token_step ?b GIVE22 :10)
      (bus_driver ?b BD22 :10)
      (token ?b TK22 :10)
      (get_off_step ?b GETOFF22 :10)
      (vehicle ?b BUS22 :10)
      (inst_going_by_vehicle GO22 :10)
      (go_step GO22 ?b :10)
      (source_go GO22 PARK22 :10)
      (inst_robbing ?r :10)
      (go_step ?r GO22 :10)
      (robber ?r FRED22 :10)
      (place_rob ?r REST22 :10)
      (get_valuable_step ?r GET22 :10)
      (thing_robbed ?r MONEY22 :10)
      (victim_rob ?r O22 :10)
      (name FRED22 FRED :10)
      (inst_park PARK22 :10)
      (inst_restaurant REST22 :10)
      (inst_money MONEY22 :10)
      (own O22 REST22 :10)
      (precede GIVE22 GETOFF22 :10)
      (precede GETOFF22 GO22 :10)
      (precede GO22 GET22 :10)
      (! (inst_smarket_shopping *))
      (! (inst_liqst_shopping *))
      (! (inst_shopping *))
      (! (inst_going_by_plane *))
      (! (inst_rest_dining *))
      (! (inst_drinking *))
      (! (inst_going_by_taxi *))
      (! (inst_paying *))
      (! (inst_jogging *))
      (! (inst_partying *))
     ) ) (^ 
      (inst_giving GIVE22 :10)
      (giver GIVE22 FRED22 :10)
      (name FRED22 FRED :10)
      (recipient GIVE22 BD22 :10)
      (occupation BD22 BUSDRIVER :10)
      (thing_given GIVE22 TK22 :10)
      (inst_token TK22 :10)
      (precede GIVE22 GETOFF22 :10)
      (inst_getting_off GETOFF22 :10)
      (agent_get_off GETOFF22 FRED22 :10)
      (patient_get_off GETOFF22 BUS22 :10)
      (inst_bus BUS22 :10)
      (place_get_off GETOFF22 PARK22 :10)
      (inst_park PARK22 :10)
      (precede GETOFF22 GO22 :10)
      (inst_going GO22 :10)
      (goer GO22 FRED22 :10)
      (dest_go GO22 REST22 :10)
      (inst_restaurant REST22 :10)
      (precede GO22 GET22 :10)
      (inst_getting GET22 :10)
      (agent_get GET22 FRED22 :10)
      (patient_get GET22 MONEY22 :10)
      (inst_money MONEY22 :10)
      (from_get GET22 O22 :10)
      (own O22 REST22 :10)
     ) )

(O (name e23) (label (^
      (inst_going_by_taxi GO23 :10)
      (goer GO23 JACK23 :10)
      (name JACK23 JACK :10)
      (vehicle GO23 TAXI23 :10)
      (dest_go GO23 PARK23 :10)
      (inst_park PARK23 :10)
      (! (inst_smarket_shopping *))
      (! (inst_liqst_shopping *))
      (! (inst_shopping *))
      (! (inst_robbing *))
      (! (inst_going_by_plane *))
      (! (inst_going_by_bus *))
      (! (inst_rest_dining *))
      (! (inst_drinking *))
      (! (inst_paying *))
      (! (inst_jogging *))
      (! (inst_partying *))
     ) ) (^ 
      (inst_going GO23 :10)
      (goer GO23 JACK23 :10)
      (name JACK23 JACK :10)
      (vehicle GO23 TAXI23 :10)
      (inst_taxi TAXI23 :10)
      (dest_go GO23 PARK23 :10)
      (inst_park PARK23 :10)
     ) )

(O (name e24) (label (^
      (inst_going_by_taxi GO24 :10)
      (goer GO24 BILL24 :10)
      (name BILL24 BILL :10)
      (vehicle GO24 TAXI24 :10)
      (! (inst_smarket_shopping *))
      (! (inst_liqst_shopping *))
      (! (inst_shopping *))
      (! (inst_robbing *))
      (! (inst_going_by_plane *))
      (! (inst_going_by_bus *))
      (! (inst_rest_dining *))
      (! (inst_drinking *))
      (! (inst_paying *))
      (! (inst_jogging *))
      (! (inst_partying *))
     ) ) (^ 
      (inst_going GO24 :10)
      (goer GO24 BILL24 :10)
      (name BILL24 BILL :10)
      (vehicle GO24 TAXI24 :10)
      (inst_taxi TAXI24 :10)
     ) )

(O (name e25) (label (^
      (inst_going_by_bus ?b :10)
      (go_step ?b GO25 :10)
      (inst_going_by_taxi GO25 :10)
      (goer ?b FRED25 :10)
      (source_go ?b BUS_STATION25 :10)
      (get_on_step ?b GETON25 :10)
      (vehicle ?b BUS25 :10)
      (name FRED25 FRED :10)
      (vehicle GO25 TAXI25 :10)
      (precede GO25 GETON25 :10)
      (! (inst_smarket_shopping *))
      (! (inst_liqst_shopping *))
      (! (inst_shopping *))
      (! (inst_robbing *))
      (! (inst_going_by_plane *))
      (! (inst_rest_dining *))
      (! (inst_drinking *))
      (! (inst_paying *))
      (! (inst_jogging *))
      (! (inst_partying *))
     ) ) (^ 
      (inst_going GO25 :10)
      (goer GO25 FRED25 :10)
      (name FRED25 FRED :10)
      (vehicle GO25 TAXI25 :10)
      (inst_taxi TAXI25 :10)
      (dest_go GO25 BUS_STATION25 :10)
      (inst_bus_station BUS_STATION25 :10)
      (precede GO25 GETON25 :10)
      (inst_getting_on GETON25 :10)
      (agent_get_on GETON25 FRED25 :10)
      (patient_get_on GETON25 BUS25 :10)
      (inst_bus BUS25 :10)
     ) )

