#! /bin/bash
source /opt/ros/kinetic/setup.bash
gnome-terminal -x bash -c "git clone https://github.com/silvery5d/Joycontrol_amiibo_MHRS ~/Joycontrol_amiibo_MHRS"
gnome-terminal -x bash -c "cp ~/Joycontrol_amiibo_MHRS/run_* ~/joycontrol/"
gnome-terminal -x bash -c "cp ~/Joycontrol_amiibo_MHRS/run_* ~/JoyControl/"
gnome-terminal -x bash -c "cp ~/Joycontrol_amiibo_MHRS/\[Desktop\]/* ~/Desktop/"
gnome-terminal -x bash -c "cp ~/Joycontrol_amiibo_MHRS/\[Desktop\]/* ~/桌面/"
