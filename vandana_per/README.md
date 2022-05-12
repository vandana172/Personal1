# rucu_pts1

Project - RUCKUS
Product - RUCU_ZBDU
server ip - 172.17.194.11

# Installation
1. Basic socket client setup
## Image_Flash_Stage
1. create a directory /client/rucu_image/
2. copy "bootloader-uart-xmodem_perforce-combined.s37" and "zigbee.gbl" files inside "/client/rucu_image/"
3. ### Commander Setup 
- This setup is required at Image Flash Stage.
    1. Copy "SimplicityCommander_linux" in Download Folder
    2. run below command 
        > sudo nano ~/.bashrc 
    3. paste below command in .bashrc file to export its path
        > export PATH="$PATH:/home/vvdn/Downloads/SimplicityCommander-Linux/Commander_linux_x86_64_1v10p0b810/commander
    4. save and exit from .bashrc file by pressing "ctrl+x,y,Enter" and run below command to source it.
        source ~/.bashrc
    5. reboot
    6. run "commander -v" to verify commander setup.

## Image_Verification_Stage
1. install minicom
2. add vvdn in dialout group
3. make hardware flow no in minicom setup
4. reboot
