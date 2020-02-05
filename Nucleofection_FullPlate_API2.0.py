#Readme:
#Protocol: 96well nucleofection with seeding into 24 SWP's (70ul)
#Author: Oscar Swindley <oswindley1@sheffield.ac.uk>
#Please confirm 'labware' matches labwere section below
#Proceed with caution if any modifications are made (dilutions, volumes, not full plate)
#Date: 05Feb2020
#Enjoy!!!

#README:
#First run prerequisite protocol 24well_Plate_Seed for as many plates as needed (multiples of 4)
#Trough requires 'Nucleofection Solution' in 'A1' at start, 'resuspended cells' in 'A2' (add when prompted), and pre-gassed media to 'A3' (add when prompted)
#DURING TIPRACK RESET (prior to seeding)tip200_1 rack (slot 7) requires only odd rows of tips (A. C, E, G), tip300_2 (slot 10) requires even rows (B, D, F, H). This allows transfer from 96-well-plate to 24-well-plates
#96-flat and 96-U plates have differnt depths so arent interchangable without ammending labware in the script

# imports
from opentrons import protocol_api
from itertools import product
# metadata
metadata = {
    'apiLevel': '2.0',
    'protocolName': '96well_nucleofection_into24swps',
    'author': 'Oscar Swindley <oswindley1@sheffield.co.uk>',
    'description': 'Lonza Nucelofection protocol with 1.5fold excess and seeding into 24-shallow-well-plates'}

def run(protocol: protocol_api.ProtocolContext):
    # labware
    plate_stock = protocol.load_labware('cornering_96_wellplate_500ul', '9')
    plate_dna = protocol.load_labware('nunc_96_ubottom', '6')
    plate_nuc = protocol.load_labware('lonza_96_electroporation', '3')
    trough = protocol.load_labware('axygen_12_reservior_22ml', '8')
    tip200_1 = protocol.load_labware('opentrons_96_filtertiprack_200ul', '7')
    tip200_2 = protocol.load_labware('opentrons_96_filtertiprack_200ul', '10')
    tip200_3 = protocol.load_labware('opentrons_96_filtertiprack_200ul', '11')

    plate24_1A = protocol.load_labware('nunc_24_pseudo_a', '1')
    plate24_2B = protocol.load_labware('nunc_24_pseudo_b', '2')
    plate24_3A = protocol.load_labware('nunc_24_pseudo_a', '4')
    plate24_4B = protocol.load_labware('nunc_24_pseudo_b', '5')

    # pipettes (& settings if different to defaults)
    p300m = protocol.load_instrument('p300_multi', mount='right', tip_racks=[tip200_1, tip200_2])
    p300m.flow_rate.aspirate = 100
    p300m.flow_rate.dispense = 200
    p300m.maximum_volume = 200
    p300m.minimum_volume = 15
    
    p50m = protocol.load_instrument('p50_multi', mount='left', tip_racks=[tip200_1, tip200_3])

	#Step 1: Distrubute Nuc Solution to DNA plate
    p50m.pick_up_tip()
    for i in range(4):
        p50m.aspirate(45, trough.wells()[0])
        p50m.dispense(38, plate_dna.wells()[8*i])
        protocol.delay(seconds=1)
        p50m.blow_out(trough.wells()[0].top())
    p50m.drop_tip()

    #Step 2: Distrubute DNA/RNA mix to DNA Plate
    for i in range(4):
        p50m.pick_up_tip()
        p50m.mix(3, 50, plate_stock.wells()[8*i])
        protocol.delay(seconds=1)
        p50m.blow_out(plate_stock.wells()[8*i].top())
        p50m.transfer(7, plate_stock.columns()[i], plate_dna.columns()[i], mix_after=(1, 40), new_tip='never')
        protocol.delay(seconds=1)
        p50m.blow_out(plate_dna.wells()[8*i].top())
        p50m.drop_tip()
 
    # Intervention 1: Insert pause to comfirm cells ready in trough column 2
    protocol.pause()
    protocol.comment('ATTENTION: Ensure below criteris are met prior to resuming protocol. Resuspended cells added to trough, position 8, column 2. Once complete click resume') 
    
	#Step 3: Mix cells + transfer to DNA plate
    p300m.pick_up_tip()
    p300m.well_bottom_clearance.aspirate = 2
    p300m.well_bottom_clearance.dispense = 10  
    for j in range(15):
	    p300m.aspirate(190, trough.wells_by_name()['A2'], rate=3.0) 
	    p300m.dispense(190, trough.wells_by_name()['A2'], rate=3.0) 
    protocol.delay(seconds=1) 
    p300m.blow_out(trough.wells_by_name()['A2'].top())
    p300m.touch_tip()   
    p300m.drop_tip()
    p300m.flow_rate.aspirate = 150
    p300m.flow_rate.dispense = 200
    p300m.well_bottom_clearance.aspirate = 1
    p300m.well_bottom_clearance.dispense = 1

    for i in range(4):
        p50m.pick_up_tip()
        p50m.well_bottom_clearance.aspirate = 2
        p50m.well_bottom_clearance.dispense = 10
        for j in range(5):
        	p50m.aspirate(50, trough.wells_by_name()['A2'], rate=5.0)
        	p50m.dispense(50, trough.wells_by_name()['A2'], rate=5.0)
        p50m.well_bottom_clearance.aspirate = 1
        p50m.well_bottom_clearance.dispense = 1
        protocol.delay(seconds=1) 
        p50m.blow_out(trough.wells_by_name()['A2'].top())
        p50m.transfer(45, trough.wells('A2'), plate_dna.wells()[8*i], new_tip='never', mix_after=(2, 50), touch_tip=True)
        protocol.delay(seconds=1)
        p50m.blow_out(plate_dna.wells()[8*i])
        p50m.drop_tip()

    #Step 4: Distribute cells to nucleofection plate
    for i in range(4): # loop for 4 columns on DNA setup plate
        p50m.pick_up_tip()
        p50m.mix(10, 50, plate_dna.wells()[8*i], rate=5.0)
        protocol.delay(seconds=1) 
        p50m.blow_out(plate_dna.wells()[8*i].top())
        for j in range(3): # Subloop for 3 replicates
            p50m.mix(4, (50-10*j), plate_dna.wells()[8*i], rate=5.0)
            p50m.blow_out(plate_dna.wells()[8*i].top())
            protocol.delay(seconds=1.0)
            p50m.well_bottom_clearance.dispense = 2.5
            p50m.aspirate(25, plate_dna.wells()[8*i])
            p50m.dispense(20, plate_nuc.wells()[8*(3*i+j)])
            protocol.delay(seconds=1.5)
            p50m.well_bottom_clearance.dispense = 1
            p50m.blow_out(plate_dna.wells()[8*i].top()) 
        p50m.drop_tip()

    #Intervention 3: Insert pause for electroporation
    protocol.pause()
    protocol.comment('ATTENTION: Ensure below criteris are met prior to resuming protocol. Perform electroporation and return nucleofection plate to position 3. During electroporation, add pregassed media to trough, position 8, col 3. Once complete click resume.')

    #Step 5: Add 80ul media to all wells
    p300m.well_bottom_clearance.dispense = 12
    p300m.pick_up_tip()
    for i in range(12):
        p300m.aspirate(80, trough.wells()[2])
        p300m.dispense(80, plate_nuc.wells()[8*i])
        protocol.delay(seconds=1)
        p300m.blow_out(plate_nuc.wells()[8*i].top())
    p300m.drop_tip()
    p300m.well_bottom_clearance.dispense = 1
    protocol.home()

    #Intervention 4: Reset tipracks for seeding
    protocol.pause()
    protocol.comment('ATTENTION: Ensure below criteria are met prior to resuming protocol. Please reset tipracks as detailed below ready for seeding of cells. tip200_1 (slot 7) Only odd rows or tips. tip200_2 (slot 10) requires only even rows of tips. Extended details in ReadME section of script. Once complete click resume.')
    p300m.reset_tipracks() # Reset tipracks
   
    #Step 8: Seed into 24SWPs
    List_plate = [(0, plate24_1A, tip200_1),(0, plate24_2B, tip200_2), (6, plate24_3A, tip200_1), (6, plate24_4B, tip200_2)]
                #In list arguments 1-4 are: 24SWP number, 24SWP name, tiprack, column offset adjuster
    
    for (j, plate24, tip), i in product(List_plate, range(6)):    #'produt' multiplies two variables into a matrix, same as doubble loop.
        isource = plate24.wells()[4*(i)]                            #isource and isource 2 are the same location, defined by wells or columns
        idest_nuc = plate_nuc.wells()[8*(i+j)]

        p300m.well_bottom_clearance.aspirate = 2.5
        p300m.well_bottom_clearance.dispense = 2.5
        p300m.pick_up_tip(tip['A' + str(i+j+1)])
        for m in range(10):
            p300m.aspirate(70, idest_nuc, rate=2.0)
            p300m.dispense(70, idest_nuc, rate=2.0)
        protocol.delay(seconds=1.0)
        p300m.blow_out(plate_nuc.wells()[8*(j+i)].top())
        protocol.delay(seconds=1.0)
        p300m.aspirate(70, idest_nuc, rate=0.5)
        p300m.well_bottom_clearance.aspirate = 1.0
        p300m.well_bottom_clearance.dispense = 1.0
        p300m.dispense(70, isource)
        p300m.mix(2, 190, isource)
        protocol.delay(seconds=1.0)
        p300m.blow_out(isource.top())
        p300m.drop_tip()
    #END SCRIPT!!!