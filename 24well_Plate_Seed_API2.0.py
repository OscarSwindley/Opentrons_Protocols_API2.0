#Readme:
#Protocol: 24Well plate seeding (630ul)
#Author: Oscar Swindley <oswindley1@sheffield.ac.uk>
#Please confirm 'labware' matches labwere section below
#Proceed with caution if any modifications are made (dilutions, volumes, not full plate)
#Date: 05Feb2020
#Enjoy!!!

#README:
# trough  CD-CHO to columns 9 to 12 (18ml) for 4 plates
# Can seed 4 plates at a time
#TIPRACKS SETUP, Only include ODD rows of tips (A,C,E,G)

# imports
from opentrons import protocol_api
from itertools import product

# metadata
metadata = {
    'apiLevel': '2.0',
    'protocolName': '24 _well_plate_seed',
    'author': 'Oscar Swindley <oswindley1@sheffield.co.uk>',
    'description': '24Well plate seeding'}

def run(protocol: protocol_api.ProtocolContext):
    # labware
    trough = protocol.load_labware('axygen_12_reservior_22ml', '8')
    tip300_1 = protocol.load_labware('opentrons_96_tiprack_300ul', '7')
    tip300_2 = protocol.load_labware('opentrons_96_tiprack_300ul', '10')

    plate24_1A = protocol.load_labware('nunc_24_plate', '1')
    plate24_2A = protocol.load_labware('nunc_24_plate', '2')
    plate24_3A = protocol.load_labware('nunc_24_plate', '4')
    plate24_4A = protocol.load_labware('nunc_24_plate', '5')

    # pipettes
    p300m = protocol.load_instrument('p300_multi', mount='right', tip_racks=[tip300_1, tip300_2])
    p300m.flow_rate.aspirate = 200
    p300m.well_bottom_clearance.aspirate = 2
    p300m.well_bottom_clearance.dispense = 2
    
    #Step 1: Create list of trough wells and plate names:
    list_plate1 = [(11, plate24_1A), (10, plate24_2A), (9, plate24_3A), (8, plate24_4A)] # Defines plates to be seeded
    # Creates function to seed plates. Variables: x = seed volume, col = start trough column for set of 4 plates, 24platelist = set of plates to use. 
    for (col, plate24_1), j in product(list_plate1, range(6)):
        p300m.pick_up_tip()
        for i in range(3):
            p300m.aspirate(20, trough.wells()[col].top())
            p300m.aspirate(210, trough.wells()[col])
            p300m.move_to(trough.wells()[col].top(-20))
            protocol.delay(seconds=1.0)
            p300m.dispense(220, plate24_1.wells()[4*j].top())
            protocol.delay(seconds=1.0)
            p300m.blow_out(plate24_1.wells()[4*j].top())
        p300m.drop_tip()
    # End Script