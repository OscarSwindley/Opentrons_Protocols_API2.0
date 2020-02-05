#Readme:
#Protocol: Valitatiter Assay, full plate standard curve for ValitaCell Opentrons Assessment
#Author: Oscar Swindley <oswindley1@sheffield.ac.uk>
#Proceed with caution if any modifications are made (dilutions, volumes, not full plate)
# Version 4.0
# Date: 30Jan20
#Enjoy!!!

#Notes:
#Please confirm 'labware' matches labwere section below, including correct tip box types and tip sizes
#For trough (Volumes in 25% excess): 
    #CD-CHO = Cols 2-4. Min volume 18.0ml
    #IgG Standard at final concentration = Col 1. Min volume 7.5ml
#Current protocol for nunc 96 well plates, check dimensions if using different plates

# imports
from opentrons import protocol_api

# metadata
metadata = {
    'apiLevel': '2.0',
    'protocolName': 'ValitaTiterAssay_1in20',
    'author': 'Oscar Swindley <oswindley1@sheffield.co.uk>',
    'description': 'First python protocol, ValitaTiterAssay, 1in15 sample dilution',
}
def run(protocol: protocol_api.ProtocolContext):

    # labware: Labware used in the protocol is loaded, format: variable = labware.load('labware name', 'Position on deck')
    plate_dil_1 = protocol.load_labware('nunc_96_ubottom', '4')
    plate_vt_1 = protocol.load_labware('valitacell_96_wellplate_150ul', '1')
    plate_dil_2 = protocol.load_labware('nunc_96_ubottom', '5')
    plate_vt_2 = protocol.load_labware('valitacell_96_wellplate_150ul', '2')
    plate_dil_3 = protocol.load_labware('nunc_96_ubottom', '6')
    plate_vt_3 = protocol.load_labware('valitacell_96_wellplate_150ul', '3')
    tip200_1 = protocol.load_labware('opentrons_96_filtertiprack_200ul', '7')
    tip200_2 = protocol.load_labware('opentrons_96_filtertiprack_200ul', '10')
    tip200_3 = protocol.load_labware('opentrons_96_filtertiprack_200ul', '11')
    tip200_4 = protocol.load_labware('opentrons_96_filtertiprack_200ul', '9')
    trough = protocol.load_labware('axygen_12_reservior_22ml', '8')

    # pipettes and settings
    p300m = protocol.load_instrument('p300_multi', mount='right', tip_racks=[tip200_1, tip200_2, tip200_3, tip200_4])
    p300m.flow_rate.aspirate = 100
    p300m.flow_rate.dispense = 200
    p300m.maximum_volume = 200
    p300m.minimum_volume = 15

    
    def VT_SC_Plate(trough_well, plate_dil, plate_vt): #FDefines running of VT_SC_Plate as a function
        #Step1: Fill Dilution media to cols 2-12
        p300m.pick_up_tip()
        for i in range(11):
            p300m.aspirate(100, trough.wells()[trough_well])
            p300m.move_to(trough.wells()[trough_well].top(-20))
            protocol.delay(seconds=1)
            p300m.dispense(100, plate_dil.wells()[8*(i+1)])
            protocol.delay(seconds=1)
            p300m.blow_out()
        p300m.drop_tip()

        #Step2: Add 222ul Standard to dil_plate Col-1
        p300m.pick_up_tip()
        p300m.mix(10, 190, trough.wells()[0])
        protocol.delay(seconds=1)
        p300m.blow_out(trough.wells()[0].top())
        p300m.transfer(100, trough.wells()[0], plate_dil.wells()[0], new_tip='never')
        protocol.delay(seconds=1)
        p300m.blow_out()
        p300m.transfer(122, trough.wells()[0], plate_dil.wells()[0], new_tip='never')
        protocol.delay(seconds=1)
        p300m.blow_out()
        p300m.drop_tip()

        #Step3: Dilute at ration of 0.6 accross cols 1-11
        p300m.pick_up_tip()
        for i in range(10):
            p300m.transfer(122, plate_dil.wells()[8*i], plate_dil.wells()[8*(i+1)], mix_after=(6, 180), new_tip='never')
            protocol.delay(seconds=1)
            p300m.blow_out(plate_dil.wells()[8*(i+1)].top())
        p300m.drop_tip()
        protocol.home()

       #Step3: Add 60ul VT-Buff to VT plate
        p300m.well_bottom_clearance.dispense = 7
        p300m.pick_up_tip()
        for i in range(12):
            p300m.aspirate(60, trough.wells()[trough_well])
            p300m.move_to(trough.wells()[trough_well].top(-20))
            protocol.delay(seconds=1)
            p300m.dispense(60, plate_vt.wells()[8*i])
            protocol.delay(seconds=1)
            p300m.blow_out(plate_vt.wells()[8*i].top())
        p300m.drop_tip()
        p300m.well_bottom_clearance.dispense = 1
        protocol.home()

        #Step 4: Add 60ul Dil.Sample to VT plate + mix.
        for i in range(12):
            p300m.pick_up_tip()
            p300m.mix(5, 60, plate_dil.wells()[8*i])
            p300m.blow_out(plate_dil.wells()[8*i].top())
            p300m.transfer(60, plate_dil.wells()[8*i], plate_vt.wells()[8*i], mix_after=(6, 80), new_tip='never') 
            protocol.delay(seconds=1)
            p300m.blow_out(plate_vt.wells()[8*i].top())  
            p300m.drop_tip() 

    VT_SC_Plate(2, plate_dil_1, plate_vt_1) #Call function to runn VT_SC_Plate
    protocol.home()
    VT_SC_Plate(3, plate_dil_2, plate_vt_2)
    protocol.home()
    VT_SC_Plate(4, plate_dil_3, plate_vt_3)
    #End of Protocol