#Readme:
#Protocol: 24SWP sampling for Iprasense 100um (1in2), supernatants
#Author: Oscar Swindley <oswindley1@sheffield.ac.uk>
#Proceed with caution if any modifications are made (dilutions, volumes, not full plate)
#Version 1.0
#Date: 05Feb2020
#Enjoy!!!

#README:
#trough requires CD-CHO in A1, feed will be added to A3 at intervention, RNA later and PBS to A5 and A6.
#tip300_1 rack (slot 7) requires only odd rows of tips (A. C, E, G), tip300_2 (slot 10) requires even rows (B, D, F, H). tip200_1 is full (slot 11)
#nunc24swp-pseudoA/B is physicaly the same plate type as nunc24swp. Intentional offcalibration allows compiling of 24-well-plates into 96-well-plates
#96-flat and 96-U plates have differnt depths so arent interchangable without ammending labware in the script
#Remember to load second ip-slide after 1st is complete, robot will not pause however there is a 15min time window
#FOLLOW TIPRACK RESET INSTRUCTIONS CAREFULLY

# imports
from opentrons import protocol_api
from itertools import product
from opentrons import types

# metadata
metadata = {
    'apiLevel': '2.0',
    'protocolName': 'IprasenseSampling_24swp',
    'author': 'Oscar Swindley <oswindley1@sheffield.co.uk>',
    'description': 'Sampling 24_shallow_well_plate cultures for measurements on the iprasense. Includes dilution step. This require tricking the OT2 to use multichannels on 24 well plate',}

def run(protocol: protocol_api.ProtocolContext):
    # labware
    plate_pel = protocol.load_labware('nunc_96_ubottom', '9') 
    plate_dil = protocol.load_labware('nunc_96_ubottom', '6')
    plate_ip = protocol.load_labware('iprasense_48_slide', '3')
    trough = protocol.load_labware('axygen_12_reservior_22ml', '8')
    tip300_1 = protocol.load_labware('opentrons_96_tiprack_300ul', '7')
    tip300_2 = protocol.load_labware('opentrons_96_tiprack_300ul', '10')
    tip200_1 = protocol.load_labware('opentrons_96_filtertiprack_200ul', '11')

    plate24_1A = protocol.load_labware('nunc_24_pseudo_a', '1')
    plate24_2B = protocol.load_labware('nunc_24_pseudo_b', '2')
    plate24_3A = protocol.load_labware('nunc_24_pseudo_a', '4')
    plate24_4B = protocol.load_labware('nunc_24_pseudo_b', '5')
    
    # pipettes (& settings if different to defaults)
    p300m = protocol.load_instrument('p300_multi', mount='right', tip_racks=[tip300_1, tip300_2])
    p50m = protocol.load_instrument('p50_multi', mount='left', tip_racks=[tip200_1])


    #Protocol Start!!!:
    #Step 1: Fill Dilution plate with 30ul media per well
    p50m.pick_up_tip()
    for i in range(12):
        p50m.aspirate(35, trough.wells('A1'))
        p50m.dispense(30, plate_dil.columns()[i])
        protocol.delay(seconds=0.5)
        p50m.blow_out(trough.wells('A1'))
    p50m.return_tip()
    p50m.reset_tipracks()

    #Step 2: Mix and transfer 300ul 24wp_culture 1 into supernatant plate, transfer 30ul into dilution plate
    List_plate = [(0, plate24_1A, tip300_1, 0, 0), (3, plate24_1A, tip300_1, 1, 0), (0, plate24_2B, tip300_2, 0, 0), (3, plate24_2B, tip300_2, 1, 0), (0, plate24_3A, tip300_1, 2, 6), (3, plate24_3A, tip300_1, 3, 6), (0, plate24_4B, tip300_2, 2, 6), (3, plate24_4B, tip300_2, 3, 6)]
                    #In list arguments 1-4 are: 24SWP number, 24SWP name, tiprack, column offset adjuster
    p300m.well_bottom_clearance.aspirate = 1.0
    p300m.well_bottom_clearance.dispense = 2.5  
    for (j, plate24, tip, k, l), i in product(List_plate, range(3)):    #'produt' multiplies two variables into a matrix, same as doubble loop.   
        isource = plate24.wells()[4*(i+j)]                            #isource and isource 2 are the same location, defined by wells or columns
        idest_intermediate = plate_dil.wells()[8*(i+j+l)]                      # save the source and destinations to variables based on 'i', 'j' 'k', 'l'
        idest_wb = plate_pel.wells()[8*k]

        well_edge_x1 = isource.bottom().move(types.Point(x=5.5, y=0, z=1.5))   # define 4 edges of the well for mixing
        well_edge_x2 = isource.bottom().move(types.Point(x=-5.5, y=0, z=1.5))
        well_edge_y1 = isource.bottom().move(types.Point(x=0, y=3.75, z=1.5))
        well_edge_y2 = isource.bottom().move(types.Point(x=0, y=-3.75, z=1.5))

        
        p300m.pick_up_tip(tip['A' + str(i+k*3+1)]) #Chooses tip to pick up, as cant slect only rack
        p300m.mix(1, 300, isource, rate=2.0)
        for r in range(2):                      # 2 loops of mixing each well edge
            p300m.aspirate(290, well_edge_x1, rate=2.0)
            p300m.dispense(300, well_edge_x2, rate=3.0)
            p300m.aspirate(290, well_edge_y1, rate=2.0)
            p300m.dispense(300, well_edge_y2, rate=3.0)            
            p300m.aspirate(290, well_edge_x2, rate=2.0)
            p300m.dispense(300, well_edge_x1, rate=3.0)            
            p300m.aspirate(290, well_edge_y2, rate=2.0)
            p300m.dispense(300, well_edge_y1, rate=3.0)
        p300m.mix(1, 300, isource, rate=2.0)
        protocol.delay(seconds=1.0)
        p300m.blow_out(isource.top())   
        p300m.transfer(30, isource, idest_intermediate, mix_after=(2, 45), new_tip='never')
        protocol.delay(seconds=1)
        p300m.blow_out(idest_intermediate.top())
        p300m.mix(1, 300, isource, rate=2.0)
        protocol.delay(seconds=1.0)
        p300m.blow_out(isource.top())
        p300m.transfer(75, isource, idest_wb, new_tip='never')
        protocol.delay(seconds=1)
        p300m.blow_out(idest_wb.top())
        p300m.drop_tip()
    p300m.well_bottom_clearance.aspirate = 1.0
    p300m.well_bottom_clearance.dispense = 1.0 

    #Intervention 1:
    protocol.home()
    protocol.pause("ATTENTION: Replace 'tiprack-300-1' in 'slot 7' as follows: Cols 1+2 odd rows, 3+4 even rows, rest of rack full. Replace 'tiprack-300-2' in slot 2 with a full rack. Insert IP slide into slot 3 for odd wells. Add feed to trough.A3")
    p300m.reset_tipracks()
    
     #Step 4: Feed Plates
    def Feed_Plate(plate_name):
        p300m.pick_up_tip()
        for i in range(6):
            p300m.aspirate(10, trough.wells()[2].top())
            p300m.aspirate(140, trough.wells()[2], rate=0.7)
            p300m.move_to(trough.wells()[2].top(-20))
            protocol.delay(seconds=1.0)
            p300m.dispense(150, plate_name.wells()[4*i])
            protocol.delay(seconds=1.0)
            p300m.blow_out(plate_name.wells()[4*i].top())
        p300m.drop_tip()

    p300m.well_bottom_clearance.aspirate = 1.0
    p300m.well_bottom_clearance.dispense = 15.0  
    Feed_Plate(plate24_1A)
    Feed_Plate(plate24_3A)
    Feed_Plate(plate24_2B)
    Feed_Plate(plate24_4B)

    p300m.well_bottom_clearance.aspirate = 1.0
    p300m.well_bottom_clearance.dispense = 1.0 
    protocol.home()
    
    #Function_create: Load into IP_slide, x indicates column miltipier on 96well plate, value = 0 or 1
    def IP_slide_load(x):
        for i in range(6):
            p50m.pick_up_tip()
            p50m.mix(8, 50, plate_dil.wells()[8*(2*i+x)], rate=4.0)
            protocol.delay(seconds=1) 
            p50m.blow_out(plate_dil.wells()[8*(2*i+x)].top())
            p50m.aspirate(10, plate_dil.wells()[8*(2*i+x)].top())
            p50m.flow_rate.aspirate = 25
            p50m.flow_rate.dispense = 2.5
            p50m.aspirate(9.0, plate_dil.wells()[8*(2*i+x)])
            p50m.dispense(30, plate_ip.wells()[8*(2*i+x)])
            protocol.delay(seconds=1.0)
            p50m.flow_rate.aspirate = 50
            p50m.flow_rate.dispense = 100
            p50m.drop_tip()

    #Step 3: Load into IP_slide 1, swaps slides, load IP_slide 2
    IP_slide_load(0)
    protocol.pause()
    protocol.comment("ATTENTION: Replace loaded iprasense slide with empty slide. Once complete click resume. Once protocol resumes, run IP_slide one on Iprasense")
    IP_slide_load(1)
    protocol.home()
    protocol.pause()
    protocol.comment("ATTENTION: Replace dilution plate with empty nunc_96U to take samples for qPCR")
    
    #Step 4: Seperate 60ul from WB samples for qPCR
    for i in range(4):
        p300m.pick_up_tip()
        p300m.mix(4, 200, plate_pel.wells()[8*i])
        protocol.delay(seconds=1.0)
        p300m.blow_out(plate_pel.wells()[8*i].top())
        p300m.transfer(60, plate_pel.wells()[8*i], plate_dil.wells()[8*i], new_tip='never')
        protocol.delay(seconds=1)
        p300m.blow_out(plate_dil.wells()[8*i].top())
        p300m.drop_tip()

    protocol.home()
    protocol.pause()
    protocol.comment("ATTENTION: Remove western blot at qPCR plates, pellet cells and return. Add 8ml RNA_Later to trough A5. Add 8ml ice cold PBS to trough A6")
   
    #Step 5: Add PBC to western blot samples and mix, Add RNA later to qPCR samples
    p300m.well_bottom_clearance.aspirate = 1.0
    p300m.well_bottom_clearance.dispense = 9.0 
    p300m.flow_rate.aspirate = 150
    p300m.flow_rate.dispense = 50
    
    p300m.pick_up_tip()
    for i in range(4):
        p300m.transfer(100, trough.wells('A6'), plate_pel.wells()[8*i], new_tip='never')
        protocol.delay(seconds=1)
        p300m.blow_out(plate_pel.wells()[8*i].top())
    p300m.drop_tip()
    
    p300m.pick_up_tip()
    for i in range(4):
        p300m.transfer(100, trough.wells('A5'), plate_dil.wells()[8*i], new_tip='never')
        protocol.delay(seconds=1)
        p300m.blow_out(plate_dil.wells()[8*i].top())
    p300m.drop_tip()


    #END SCRIPT!!!