# Startup guide for OpenSourceRIS



## Required materials

- **1x Programmer** (NUCLEO-F446RE)
_Note: The given programmer is tested. Other compatible programmers may also work._
- **6x Jumper wires** (FF or FM, depending on the programmer board)
- **1x USB-B Mini Kabel**
- **1x Power connection to RIS, choose one:**
    - 1x USB-B Mini Kabel
    - 1x Power supply 9V-24V DC with coaxial power connector (2.1 x 5.5 mm), positiv on inner pin
- **1x PC with install Software**  
    - STM32CubeIDE **version 1.12.1** _Warning: other versions may not work properly_
    - FT Prog **version 3.12.70.678**
---

## Step-by-step guide to programming the microcontroller.

### 1. Preparation
- Ensure that all pin header connections between the RIS PCB and the RIS controller PCB are secure.
- Install the development environment (IDE).
_Note: The standart settings are fine. No additional setup required_

### 2. Wiring
- Connect the jumper wires between the programmer ST-LINK connectoer and the RIS controller board.
- PIN description from top to bottom (PIN 1-6):
    - VDD from application
    - SWD clock
    - ground
    - SWD data input/output
    - RESET of target STM32
    - Reseved

<figure>
  <img src="wiring_1.png" alt="center">
  <figcaption>Possible wiring with external power supply and NUCLEO-F446RE</figcaption>
</figure>

- The cabling must be adjusted later for programming the USM-UART chip witch FT Prog.

### 3. Software Setup
- Start the STM32CubeIDE and verify the installed version.
- Import the given *.c, *.h and *.ioc files from the repository.


### 4. Programming microcontroller
- Compile the firmware in the development environment.
- Run the programm to flasch the microcontroller.
- Check if the upload was successful (watch for the blue LED to switch on).<br>
_Note: The RIS is not yet operational, the USB-UART chip has not yet been programmed._

---

## Step-by-step guide to programming the USB-UART chip.

### 1. Preparation
- Install the FT-Prog software.
_Note: The standart settings are fine. No additional setup required_

### 2. Wiring
- disconnect all wires from the RIS controller board.
- connect the RIS controller board via USB-B mini directly to the PC

### 3. Software Setup
- Start the FT-Prog software
- Update the Devicetree by selceting `Scan and Parse` from the `DEVICES` menu or press `F5`
- The connected USB-UART chip schould now be displayed in the Device Tree.
- Import the given `FT231XS-Template.xml` file from the repository by selecting `Open Template` from the `FILE` menu or press `Strg+O`.
- The File should now be displayed in the Device Tree.

### 4. Programming USB-UART chip
- Programm the chip by select `Prgramm` in the `DEVICES` menu or press `Strg+P`
- The `Program Devices` GUI should open
- select the connected device and click Program

---

## Testing RIS functionality
- Reconnect the RIS to the PC to ensure proper initialization.
- Run one of the control software programs provided:
    - [MATLAB test code](../Control%20Software/MATLAB%20Code%20Examples/example_USB.m)
    - [Java GUI](../Control%20Software/Graphical%20JAVA%20Tools/RIS-Terminal.jar)

---

> Note: additional information can be found here:
> - [NUCLEO-F446RE user manuel](https://www.st.com/resource/en/user_manual/um1724-stm32-nucleo64-boards-mb1136-stmicroelectronics.pdf)
> - [FT-Prog User Guide](https://www.ftdichip.com/Support/Documents/AppNotes/AN_124_User_Guide_For_FT_PROG.pdf)
> <br>
> _The above links lead to external websites that are not under my control. I am not responsible for the content or availability of these external sites. Please use them at your own discretion._
---