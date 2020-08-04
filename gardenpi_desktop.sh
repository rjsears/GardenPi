#! /bin/bash

## Super simple script to switch between a normal X desktop and the
## GardenPi Kiosk mode menu interface.

# Define some colors
red='\033[0;31m'
yellow='\033[0;33m'
green='\033[0;32m'
white='\033[0;37m'
blue='\033[0;34m'
nc='\033[0m'


gardenpi_logo() {
  echo
  echo -e "${red}   ********            **           *******         *******         ********       ****     **             *******        **
  **//////**          ****         /**////**       /**////**       /**/////       /**/**   /**            /**////**      // ${white}
 **      //          **//**        /**   /**       /**    /**      /**            /**//**  /**            /**   /**       **
/**                 **  //**       /*******        /**    /**      /*******       /** //** /**            /*******       /**
/**    *****       **********      /**///**        /**    /**      /**////        /**  //**/**            /**////        /**
//**  ////**      /**//////**      /**  //**       /**    **       /**            /**   //****            /**            /** ${blue}
 //********       /**     /**      /**   //**      /*******        /********      /**    //***            /**            /**
  ////////        //      //       //     //       ///////         ////////       //      ///             //             //
${nc}"
}

do_desktop_normal() {
    mv ~pi/.config/lxsession/LXDE-pi/autostart ~pi/.config/lxsession/LXDE-pi/autostart.old
    systemctl restart display-manager
    echo -e "Normal Desktop ${green}Activated${nc}"
    echo -e "${blue}Verify${nc} correct MySQL Settings."
    exit 0
}

do_desktop_gardenpi(){
    mv ~pi/.config/lxsession/LXDE-pi/autostart.old ~pi/.config/lxsession/LXDE-pi/autostart
    systemctl restart display-manager
    echo -e "GardenPi Menu Kiosk ${green}Activated${nc}"
    echo -e "${blue}Verify${nc} correct MySQL Settings."
    exit 0
}


help(){
  clear
  gardenpi_logo
  echo
  echo
  echo -e "Welcome to the ${green}GardenPi${nc} Desktop Switching Appication."
  echo
  echo -e "This is a very simple application to switch between a normal Xwindows"
  echo -e "desktop interface and the ${green}GardenPi${nc} Kiosk mode menu deskstop."
  echo
  echo -e "Usage is very simple. If you want a normal desktop simply run:"
  echo -e "${blue} ./gardenpi_desktop.sh desktop${nc}"
  echo
  echo
  echo -e "When you are ready to switch back to the ${green}GardenPi${nc} interface, simply type:"
  echo -e "${blue} ./gardenpi_desktop.sh gardenpi"
  echo
  echo -e "E${red}n${yellow}j${green}o${white}y${nc}!"
  echo
}

case "$1" in
desktop) do_desktop_normal ;;
gardenpi) do_desktop_gardenpi ;;
help) help ;;
*)
  echo "usage: $0 [desktop | gardenpi | help ]" >&2
  exit 1
  ;;
esac
