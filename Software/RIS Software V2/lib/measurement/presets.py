
presets =[
        {
            "name": "full sweep",
            "description": "This preset measures all given patterns for frequencies between 5.15 GHz and 5.875 GHz, with rotations ranging from 0° to 180°.",
            "fname": "RIS_Projekt_FK.znx",
            "single_freq": False,
            "freq_start_Hz": 5.15e9,
            "freq_stop_Hz": 5.875e9,
            "if_bw_Hz": 100,
            "points": 401,
            "single_rot": False,
            "rot_start_deg": 0,
            "rot_stop_deg": 180,
            "rot_step_deg": 1.0,
            "port_tx": 2,
            "port_rx": 1,
            "power_tx_dBm": -20
        },
        {
            "name": "single point",
            "description": "This preset measures only at 5.5125 GHz and the RIS rotated to 90°.",
            "fname": "RIS_Projekt_FK_2.znx",
            "single_freq": True,
            "freq_Hz": 5.5125e9,
            "single_rot": True,
            "rot_deg": 90,
            "port_tx": 2,
            "port_rx": 1,
            "power_tx_dBm": -20
        }
    ]
