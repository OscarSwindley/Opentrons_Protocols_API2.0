#ReadME:
#Protocol: OS 24SWP Harvest Protocol. Iprasense load(100um 1in2) and supernatant collection
#Author: Oscar Swindley <oswindley1@sheffield.ac.uk>
#Proceed with caution if any modifications are made (dilutions, volumes, not full plate)
#Date: 05Feb20
#Enjoy!!!

#README:
#trough requires CD-CHO in col-1 for Iprasense intermediate plate dilution.
#tip300_1 rack (slot 7) requires only odd rows of tips (A. C, E, G), tip300_2 (slot 10) requires even rows (B, D, F, H). tip200_1 is full (slot 11)
#nunc24swp-pseudoA/B is physicaly the same plate type as nunc24swp. Intentional offcalibration allows compiling of 24-well-plates into 96-well-plates
#96-flat and 96-U plates have differnt depths. These are interchanged as 96flat is lower than 96U so the robot does not clash.
#Robot will pause for all interventions. Read onscreen instructions carefully 

# imports
from opentrons import protocol_api
from itertools import product
from opentrons import types

# metadata
metadata = {
    'apiLevel': '2.0',
    'protocolName': '24SWP harvest_with_IprasenseSampling_and_Titre_Sampling',
    'author': 'Oscar Swindley <oswindley1@sheffield.co.uk>',
    'description': 'Harvest 4 24_shallow_well_plate cultures for measurements on the iprasense. Includes 1in2 dilution step. This require tricking the OT2 to use multichannels on 24 well plate. Also includes collecting supernatant samples for titre assays'}

def run(protocol: protocol_api.ProtocolContext): 
    # labware
    plate_pel = protocol.load_labware('corning_96_wellplate_360ul_flat', '9')
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
        p50m.aspirate(35, trough.wells()[0])
        p50m.dispense(30, plate_dil.wells()[8*i])
        protocol.delay(seconds=0.5)
        p50m.blow_out(trough.wells()[0])
    p50m.return_tip()
    p50m.reset_tipracks()

    #Step 2: Mix and transfer 300ul 24wp_culture 1 into supernatant plate, transfer 30ul into dilution plate
    List_plate = [(plate24_1A, tip300_1, 0), (plate24_2B, tip300_2, 0),  (plate24_3A, tip300_1, 6), (plate24_4B, tip300_2, 6)]
                    #In list arguments 1-4 are: 24SWP number, 24SWP name, tiprack, column offset adjuster
    p300m.well_bottom_clearance.aspirate = 1.0
    p300m.well_bottom_clearance.dispense = 2.5  
    for (plate24, tip, j), i in product(List_plate, range(6)):  #'produt' multiplies two variables into a matrix, same as doubble loop.   
        isource = plate24.wells()[4*(i)]                            #isource/idest defines well location for simplifying the code below.
        idest_intermediate = plate_dil.wells()[8*(i+j)]
        idest_supernatant = plate_pel.wells()[8*(i+j)]

        well_edge_x1 = isource.bottom().move(types.Point(x=5.5, y=0, z=1.5))   # define 4 edges of the well for mixing
        well_edge_x2 = isource.bottom().move(types.Point(x=-5.5, y=0, z=1.5))
        well_edge_y1 = isource.bottom().move(types.Point(x=0, y=3.75, z=1.5))
        well_edge_y2 = isource.bottom().move(types.Point(x=0, y=-3.75, z=1.5))

        p300m.pick_up_tip(tip['A' + str(i+j+1)])       #Chooses tip to pick up, as cant slect only rack
        p300m.mix(1, 300, isource, rate=2.0)
        for r in range(2):                               # 2 loops of mixing each well edge
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
        p300m.transfer(300, isource, idest_supernatant, new_tip='never')
        protocol.delay(seconds=1)
        p300m.blow_out(idest_supernatant.top())
        p300m.drop_tip()
    p300m.well_bottom_clearance.aspirate = 1.0
    p300m.well_bottom_clearance.dispense = 1.0 

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
    
    #Step 3: Load into IP_slide 1 - odd numbers
    protocol.home()
    protocol.pause()
    protocol.comment("ATTENTION: Insert IP_slide 1 into position 3 (odd columns)")
    IP_slide_load(0)
    protocol.home()
    protocol.pause()
    protocol.comment("ATTENTION: Remove IP_slide 1 to read and replace with IP_slide 2 (even columns). Remove supernatant plate and pellet cells") 
    IP_slide_load(1)

    #Step 5: Transfer supernatant into new plate
    protocol.home()
    protocol.pause()
    protocol.comment("1: Remove IP_slide 2 to read. 2: Replace IP dilution plate with fresh nunc-96U for supernatant transfer. 3: Replace tip300_1 in 'slot 7' with a full rack")
    p300m.reset_tipracks() # Reset tipracks
    p300m.flow_rate.aspirate = 50
    p300m.well_bottom_clearance.aspirate = 2.5
    p300m.well_bottom_clearance.dispense = 1
    for i in range(12):
        p300m.pick_up_tip()
        p300m.transfer(190, plate_pel.wells()[8*i], plate_dil.wells()[8*i], new_tip='never')
        protocol.delay(seconds=1)
        p300m.blow_out(plate_dil.wells()[8*i].top())
        p300m.drop_tip()
    #End Protocol!!!
