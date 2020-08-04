#! /bin/bash


##############################################
##
## Richard J. Sears
## richardjsears@gmail.com
##
## system_backup.sh
##
## V1.0.0
## July 31th, 2020
##
##
## GardenPi System Backup and Restore Script
##
## This backup scripts makes a complete backup
## of all critical GardenPi system files including
## everything needed to restore a clean, freshly
## imaged Raspbian Pi back to running GardenPi.
##
##############################################

## Are we running a MightyHat?
mightyhat=True

## Where is our utility directory? This houses our backup scripts
## and critical file and directory lists.
utility_dir="/etc/gardenpi/utilities"
critical_files_list="/etc/gardenpi/gardenpi_critical_files.txt"
critical_directory_list="/etc/gardenpi/gardenpi_critical_directories.txt"

## Are we going to save our images locally or remotely?
## Enter "remote", "local", or "usb". You can use "usb" for
## any USB externally connected device. You will have an option
## at runtime to override this setting.
operation=""

## What server are we going to save to and get images from?
## This should be a FQDN or if it is not, then you should have a host
## entry. A normal IP address is fine as well.
##
## IMPORTANT!!
## We do a **basic** rcp test to the NFS server to make sure we can talk
## NFS to it. Set your NFS version here!
nfs_server="backup_server"
nfs_version="3"

## What is the directory (local or remote) that we will be using for this script?
## Keep in mind that this could also be a USB drive installed locally. If this **IS**
## a USB drive, then this directory should be the mountpoint of your USB device.

## IMPORTANT ##
## Leave this blank backup_directory="" to select at runtime.
backup_directory="/mount/backup_server/backups"

## If we are using NFS what is the export where we will store our backups?
nfs_export="/mnt/vol1/backup_server/gardenpi/backups"

## What are the passwords we want to use for root and neptune access to our databases?
DATABASE_PASS='password!'
NEPTUNE_DB_PASS='password'


## How were we called?
how_called=$1

# Define some colors
red='\033[0;31m'
yellow='\033[0;33m'
green='\033[0;32m'
white='\033[0;37m'
blue='\033[0;34m'
nc='\033[0m'

# ASCII Warning Banner
warning_banner() {
  echo
  echo -e "${red}
 **       **           **           *******         ****     **       **       ****     **         ******** 
/**      /**          ****         /**////**       /**/**   /**      /**      /**/**   /**        **//////**
/**   *  /**         **//**        /**   /**       /**//**  /**      /**      /**//**  /**       **      // 
/**  *** /**        **  //**       /*******        /** //** /**      /**      /** //** /**      /**         
/** **/**/**       **********      /**///**        /**  //**/**      /**      /**  //**/**      /**    *****
/**** //****      /**//////**      /**  //**       /**   //****      /**      /**   //****      //**  ////**
/**/   ///**      /**     /**      /**   //**      /**    //***      /**      /**    //***       //******** 
//       //       //      //       //     //       //      ///       //       //      ///         ////////  
${nc}"
}

error_banner() {
  echo
  echo -e "${red}
 ********       *******         *******           *******         *******
/**/////       /**////**       /**////**         **/////**       /**////**
/**            /**   /**       /**   /**        **     //**      /**   /**
/*******       /*******        /*******        /**      /**      /*******
/**////        /**///**        /**///**        /**      /**      /**///**
/**            /**  //**       /**  //**       //**     **       /**  //**
/********      /**   //**      /**   //**       //*******        /**   //**
////////       //     //       //     //         ///////         //     //
${nc}"
}

# The awesome GardenPi Logo....

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

## Due to the nature of this script, it must be run as root or via sudo/su.
must_run_as_root(){
    if [[ $(id -u) -ne 0 ]]; then
        echo "Must run as root!"
        echo "sudo system_backup.sh option"
        echo "or su - first."
        exit 1
    fi
}

## Here we determine if we are running X and if we have Zenity installed.
## If we do, then zenity becomes our default display, if not then we check
## to see if dialog is installed and use it, otherwise fall back to text
## output.

## Dialog is the "preferred" interface for this script. We try to detect
## if it is not installed and install it if necessary. If this fails then
## we will fall back to text mode.
check_dialog(){
  if [[ -x "$(command -v dialog)" ]]; then
      return
  else
     sudo apt install dialog -y
  fi
}

# change zzenity to zenity below to use zenity if installed
determine_display() {
    if [[ -x "$(command -v zenity)" ]] && [[ $DISPLAY ]]; then
        display="zenity"
    elif [[ -x "$(command -v dialog)" ]]; then
        display="dialog"
    else
        display=""
    fi
}

welcome(){
    if [[ "$display" == "dialog" ]]; then
        dialog --colors \
                  --clear \
                  --backtitle "Welcome to GardenPi" \
                  --title "\Z1*** GardenPi - Create or Restore a Backup ***\Zn" \
                  --ok-label "Create Backup"\
                  --extra-button --extra-label "Restore Backup"\
                  --yesno "\nWelcome to the GardenPi Backup and Restore script. \
                            \n\nHere you can choose to \Z4CREATE\Zn or \Z4RESTORE\Zn a GardenPi system\
                            backup. This backup will allow you to create a fully operational copy of your GardenPi system in minutes.\
                            \n\nYou will have the option to backup/restore to a USB device,\
                            a local directory (\Z1not recommended\Zn), or to an NFS mount. \
                             \n\nWe will walk you through the various options as best \
                             we can but please verify all entries before making \
                             your backup/restore. This is \Z4MOST\Zn important if you choose \
                             to make a local backup into a directory on your running \
                             Pi.\n\nDid we mention that local mode is \Z1NOT RECOMMENDED?\Zn" 22 65 2>/dev/null
        selected_option=$?
        if [[ $selected_option == 0 ]]; then
            create_backup
        elif [[ $selected_option == 3 ]]; then
            restore_backup
        else
            exit 1
        fi
    elif [[ "$display" == "zenity" ]]; then
        selected_option=$(zenity --no-wrap --info --title "*** GardenPi - Create or Restore a Backup ***" \
      --text "Welcome to the GardenPi Backup and Restore script. \
                            \n\nHere you can choose to <b>CREATE</b> or <b>RESTORE</b> a GardenPi system\n\
backup. This backup will allow you to create a fully operational\n\
copy of your GardenPi system in minutes.\
                            \n\nYou will have the option to backup/restore to a USB device,\n\
a local directory (<b>not recommended</b>), or to an NFS mount. \
                             \n\nWe will walk you through the various options as best \n\
we can but please verify all entries before making\n \
your backup/restore. This is <b>MOST</b> important if you choose \n\
to make a local backup into a directory on your running \
Pi.\n\nDid we mention that local mode is <b>NOT RECOMMENDED?</b>" --ok-label="Create Backup" --extra-button "Restore Backup" --extra-button "Cancel")
    exit_code=$?
    if [[ $exit_code == 0 ]]; then
        create_backup
    elif [[ $exit_code == 1 ]] && [[ $selected_option == "Cancel" ]]; then
            exit 1
    else
        restore_backup
    fi

    else
        clear
    echo -e "    *** Welcome to the ${red}G${yellow}a${green}r${white}d${blue}e${red}n${yellow}P${green}i${nc} Backup and Restore Script ***"
    echo -e
    echo -e "Here you can choose to ${blue}CREATE${nc} or ${blue}RESTORE${nc} a ${red}G${yellow}a${green}r${white}d${blue}e${red}n${yellow}P${green}i${nc} system backup."
    echo -e "This backup will allow you to create a fully operational copy of"
    echo -e "your ${red}G${yellow}a${green}r${white}d${blue}e${red}n${yellow}P${green}i${nc} system in minutes."
    echo -e
    echo -e "You will have the option to backup or restore to a USB device, a"
    echo -e "local directory (${red}not recommended${nc}), or to an NFS mount."
    echo -e
    echo -e "We will walk you through the various options as best we can, but"
    echo -e "please verify all entries before making or restoring your backup."
    echo -e
    echo -e "This is ${blue}MOST${nc} important if you choose to make a local backup into "
    echo -e "a directory on you running Pi."
    echo -e
    echo -e "Did we mention that local mode is ${red}NOT RECOMMENDED?${nc}"
    echo -e

            PS3="Select Mode: "
            select selected_option in Create Restore Exit; do
              case $selected_option in
              Create)  operation="create_backup" ;;
              Restore) operation="restore_backup" ;;
              Exit) exit 1 ;;
              esac
              echo -e -e -n "You entered [${blue}$selected_option${nc}], is this correct? "
              read -n 1 -r
              echo -e
              if [[ $REPLY =~ ^[Yy]$ ]]; then
                  clear
                  $operation
                  exit 1
              else
                  selected_option=""
                  welcome
              fi
done
  fi
}

## Are we running on a Raspberry Pi? If not, exit script
running_on_rpi() {
    if [[ $(cat /proc/device-tree/model | grep -c Raspberry) != 1 ]]; then
        if [[ "$display" == "dialog" ]]; then
            dialog --colors \
              --clear \
              --backtitle "PLATFORM ERROR!" \
              --title "\Z1*** Raspberry Pi Not Detected! ***\Zn" \
              --ok-label "EXIT" \
              --msgbox "\nGardenPi requires a Raspberry Pi to work properly. \
                              \n\nIf you are not on a Raspberry Pi, this will not work!" \
              10 60
              exit 1
        elif [[ "$display" == "zenity" ]]; then
            zenity --no-wrap --warning --text="<span size=\"xx-large\">   PLATFORM ERROR!</span>\n\nYou MUST be running on a Raspberry Pi\nin order to run <b>GardenPi</b>!"\
            --title="PLATFORM ERROR" --ok-label="QUIT" 2>/dev/null
            exit 1
        else
          error_banner
          echo
          echo -e "${red}ERROR${nc} - Is does not appear that this is a Rapsberry Pi!" >&2
          echo "Please install GardenPi on a Raspberry Pi"
          echo
          echo -e "${yellow}ABORTING!${nc}"
          exit 1
        fi
    fi
}

## First if we have hard coded the operation type let the user know and ask them
## if they would like to override the hard coded setting:
select_operation_mode() {
    if [[ "$operation" == "usb" ]] || [[ "$operation" == "local" ]] || [[ "$operation" == "remote" ]]; then
        if [[ "$display" == "dialog" ]]; then
            dialog --colors --clear --backtitle "Verify Operating Mode" --title "Verify Operating Mode" \
              --yesno "Operating Mode set to [ \Z4$operation\Zn ] -  OVERRIDE?" 5 60
            if [ $? = 0 ]; then
                operation=""
                select_operation_mode
            else
                if [[ "$operation" == "usb" ]]; then
                    backup_directory="/mount/usb"
                fi
                return
            fi
        elif [[ "$display" == "zenity" ]]; then
            zenity --question --no-wrap --title="Verify Operating Mode" --text="Operating Mode set to [ <b>$operation</b> ] - OVERRIDE?" 2>/dev/null
                if [[ $? = 0 ]]; then
                  operation=""
                  select_operation_mode
                else
                    if [[ "$operation" == "usb" ]]; then
                    backup_directory="/mount/usb"
                    fi
                    return
                fi
        else
            clear
            echo
            echo -e -n "Operating Mode set to [ ${yellow}$operation${nc} ] - OVERRIDE? "
            read -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                operation=""
                select_operation_mode
            else
                if [[ "$operation" == "usb" ]]; then
                    backup_directory="/mount/usb"
                fi
                return
            fi
        fi
    ## Since the operation type id not hard coded, ask the end use how they want to run:
    else
        if [[ "$display" == "dialog" ]]; then
            INPUT=/dev/shm/menu.sh.$$
            trap "rm $INPUT; exit" SIGHUP SIGINT SIGTERM
            dialog --no-cancel --clear --backtitle "GardenPi Backup & Restore" \
              --title "[ GardenPi Backup & Restore ]" \
              --menu "Please choose where you plan to store or retrieve your backup files. \
                USB is any USB block device, Local is the locally mounted filesystem, and \
                Remote is a remotely mounted NFS export." 16 60 40 \
              USB "Local USB Device" \
              Remote "Remote NFS Mount" \
              Local "Local Filesystem (Not Recommended)" \
              Exit "Exit" 2>"${INPUT}"

            menuitem=$(<"${INPUT}")
            # make decision
            case $menuitem in
            USB) operation="usb" ;;
            Local) operation="local" ;;
            Remote) operation="remote" ;;
            Exit) exit 1 ;;
            esac
            # if temp files found, delete them
            [[ -f $INPUT ]] && rm $INPUT

          ## As long as operation does not come back blank (ie they just hit enter)
          ## let's verify the entry:
            if [[ -n $operation ]]; then
                dialog --colors --clear --backtitle "Verify Entry" --title "Verify Entry" \
                --yesno "You entered [ \Z4$operation\Zn ], is this correct?" 5 80
                if [[ $? = 0 ]]; then
                    if [[ "$operation" == "usb" ]]; then
                    backup_directory="/mount/usb"
                    fi
                    return
                else
                    operation=""
                    select_operation_mode
                fi
            else
               select_operation_mode
            fi
        elif [[ "$display" == "zenity" ]]; then
            operation=$(zenity --list --text="Select Operating Mode" --column Selection --column Mode \
            FALSE usb FALSE remote FALSE local --radiolist --width=300 --height=250 2>/dev/null)
            if [[ $? = 0 ]]; then
                if [[ -z "$operation" ]]; then
                    select_operation_mode
                fi
            else
                exit 1
            fi
            zenity --question --no-wrap --title="Verify Entry" --text="You entered [ <b>$operation</b> ], is this correct?" 2>/dev/null
            if [[ $? = 0 ]]; then
                    if [[ "$operation" == "usb" ]]; then
                        backup_directory="/mount/usb"
                    fi
                    return
            else
                operation=""
                select_operation_mode
                fi
        else
            echo "Where are we putting our backup?"
            PS3="Select Operation Mode: "
            select operation_mode in USB Remote Local Exit; do
              case $operation_mode in
              USB) operation="usb" ;;
              Local) operation="local" ;;
              Remote) operation="remote" ;;
              Exit) exit 1 ;;
              esac
              echo -e -n "You entered [${blue}$operation${nc}], is this correct? "
              read -n 1 -r
              echo
              if [[ $REPLY =~ ^[Yy]$ ]]; then
                #  operation=$operation
                  if [[ "$operation" == "usb" ]]; then
                  backup_directory="/mount/usb"
                  fi
                  return
              else
                  operation=""
                  select_operation_mode
              fi
            done
        fi
    fi
}

## This is where we verify the directory to store or retrieve the backups from.
## If there is a hard coded directory we ask if they want to override it:
get_backup_directory() {
    if [[ -n "$backup_directory" ]]; then
        if [[ "$display" == "dialog" ]]; then
            dialog --colors --clear --default-button "No" --backtitle "Verify Backup Directory" --title "Verify Backup Directory" \
              --yesno "Backup directory set to [ \Z4$backup_directory\Zn ] by default in script. OVERRIDE?" 5 90
            if [[ $? = 0 ]]; then
                backup_directory=""
                get_backup_directory
            else
                return
            fi
        elif [[ "$display" == "zenity" ]]; then
            zenity --question --no-wrap --title="Verify Backup Directory" --text="Backup directory set to [ <b>$backup_directory</b> ] by default in script. OVERRIDE?" 2>/dev/null
            if [[ $? = 0 ]]; then
                backup_directory=""
                get_backup_directory
            else
                return
            fi
        else
            echo
            echo -e -n "Backup directory set to [ ${yellow}$backup_directory${nc} ] by default in script. OVERRIDE? "
            read -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                backup_directory=""
                get_backup_directory
            else
                return
            fi
        fi
    else
        if [[ "$display" == "zenity" ]]; then
            backup_directory=$(zenity --title="Backup Directory" --entry --text "What is the mount point for your backup Directory?\nThis is the directory where we will mount our USB drive or NFS export.\nFor example: /mount/usb or /mount/phxnas/backups" 2>/dev/null)
            if [[ $? = 0 ]]; then
                if [[ -z "$backup_directory" ]]; then
                    get_backup_directory
                fi
            else
                exit 1
            fi

            zenity --question --no-wrap --title="Verify Backup Directory" --text="You entered [ <b>$backup_directory</b> ], is this correct?" 2>/dev/null
            if [[ $? = 0 ]]; then
                return
            else
                backup_directory=""
                get_backup_directory
            fi
        elif [[ "$display" == "dialog" ]]; then
            exec 3>&1
            backup_directory=$(dialog --clear \
              --backtitle "Backup Directory" \
              --title "Backup Directory" \
              --inputbox "\nWhat is the mount point for the backup directory?\nThis is the directory where we will mount our USB drive or NFS export.\nFor example: /mount/usb or /mount/phxnas/backups" \
              15 75 "/mount/phxnas/backups" 2>&1 1>&3)

            if [[ $? = 0 ]]; then
                if [[ -z "$backup_directory" ]]; then
                  get_backup_directory
                fi
            else
                exit 1
            fi

            dialog --colors --clear --backtitle "Verify Backup Directory" --title "Verify Backup Directory" \
              --yesno "You entered [ \Z4$backup_directory\Zn ], is this correct?" 5 90
            if [ $? = 0 ]; then
                return
            else
                backup_directory=""
                get_backup_directory
            fi
        else
            echo
            echo
            echo -e -n "What is the mount point for your backup Directory?\nThis is the directory where we will mount our USB drive or NFS export.\nFor example: /mount/usb or /mount/phxnas/backups: "
            read backup_directory
            echo
            echo -e -n "You entered [${blue}$backup_directory${nc}], is this correct? "
            read -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                return
            else
                backup_directory=""
                get_backup_directory
            fi
        fi
    fi
}

## This is where we verify the directory to store or retrieve the backups from.
## If there is a hard coded directory we ask if they want to override it:
get_usb_backup_directory() {
    if [[ -n "$backup_directory" ]]; then
        if [[ "$display" == "dialog" ]]; then
            dialog --colors --clear --default-button "No" --backtitle "Verify Backup Directory" --title "Verify Backup Directory" \
              --yesno "Backup directory set to [ \Z4$backup_directory\Zn ] by default in script. OVERRIDE?" 5 90
            if [[ $? = 0 ]]; then
                backup_directory=""
                get_backup_directory
            else
                return
            fi
        elif [[ "$display" == "zenity" ]]; then
            zenity --question --no-wrap --title="Verify Backup Directory" --text="Backup directory set to [ <b>$backup_directory</b> ] by default in script. OVERRIDE?" 2>/dev/null
            if [[ $? = 0 ]]; then
                backup_directory=""
                get_backup_directory
            else
                return
            fi
        else
            echo
            echo -e -n "Backup directory set to [ ${yellow}$backup_directory${nc} ] by default in script. OVERRIDE? "
            read -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                backup_directory=""
                get_usb_backup_directory
            else
                return
            fi
        fi
    else
        if [[ "$display" == "zenity" ]]; then
            backup_directory=$(zenity --title="Backup Directory" --entry --text "What is the mount point for your backup Directory?\nThis is the directory where we will mount our USB drive or NFS export.\nFor example: /mount/usb or /mount/phxnas/backups" 2>/dev/null)
            if [[ $? = 0 ]]; then
                if [[ -z "$backup_directory" ]]; then
                    get_backup_directory
                fi
            else
                exit 1
            fi

            zenity --question --no-wrap --title="Verify Backup Directory" --text="You entered [ <b>$backup_directory</b> ], is this correct?" 2>/dev/null
            if [[ $? = 0 ]]; then
                return
            else
                backup_directory=""
                get_backup_directory
            fi
        elif [[ "$display" == "dialog" ]]; then
            exec 3>&1
            backup_directory=$(dialog --clear \
              --backtitle "Backup Directory" \
              --title "Select Directory where your backups are stored!" \
              --dselect "/media/pi/" 10 70 2>&1 1>&3)

            if [[ $? = 0 ]]; then
                if [[ -z "$backup_directory" ]]; then
                  get_usb_backup_directory
                fi
            else
                exit 1
            fi

            dialog --colors --clear --backtitle "Verify Backup Directory" --title "Verify Backup Directory" \
              --yesno "You entered [ \Z4$backup_directory\Zn ], is this correct?" 5 90
            if [ $? = 0 ]; then
                return
            else
                backup_directory=""
                get_backup_directory
            fi
        else
            echo
            echo
            echo -e -n "What is the mount point for your backup Directory?\nThis is the directory where we will mount our USB drive or NFS export.\nFor example: /mount/usb or /mount/phxnas/backups: "
            read backup_directory
            echo
            echo -e -n "You entered [${blue}$backup_directory${nc}], is this correct? "
            read -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                return
            else
                backup_directory=""
                get_backup_directory
            fi
        fi
    fi
}

get_current_restore_backup_directory(){
  SOURCE="${BASH_SOURCE[0]}"
while [ -h "$SOURCE" ]; do # resolve $SOURCE until the file is no longer a symlink
  DIR="$( cd -P "$( dirname "$SOURCE" )" >/dev/null 2>&1 && pwd )"
  SOURCE="$(readlink "$SOURCE")"
  [[ $SOURCE != /* ]] && SOURCE="$DIR/$SOURCE" # if $SOURCE was a relative symlink, we need to resolve it relative to the path where the symlink file was located
done
backup_directory="$( cd -P "$( dirname "$SOURCE" )" >/dev/null 2>&1 && pwd )"
}


## This is where we verify the directory to store or retrieve the backups from.
## If there is a hard coded directory we ask if they want to override it:
get_nfs_export() {
    if [[ -n "$nfs_export" ]]; then
        if [[ "$display" == "dialog" ]]; then
            dialog --colors --clear --default-button "No" --backtitle "Verify NFS Export" --title "Verify NFS Export" \
              --yesno "NFS Export is set to [ \Z4$nfs_export\Zn ] by default in script. OVERRIDE?" 7 100
            if [[ $? = 0 ]]; then
                nfs_export=""
                get_nfs_export
            else
                return
            fi
        elif [[ "$display" == "zenity" ]]; then
            zenity --question --no-wrap --title="Verify NFS Export" --text="NFS Export is set to [ <b>$nfs_export</b> ] by default in script. OVERRIDE?" 2>/dev/null
            if [[ $? = 0 ]]; then
                nfs_export=""
                get_nfs_export
            else
                return
            fi
        else
            clear
            echo
            echo -e -n "NFS Export is set to [ ${yellow}$nfs_export${nc} ] by default in script. OVERRIDE? "
            read -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                nfs_export=""
                get_nfs_export
            else
                return
            fi
        fi
    else
        if [[ "$display" == "zenity" ]]; then
            nfs_export=$(zenity --title="NFS Export" --entry --text "What is the NFS Export you are going to use?\nThis is the export FROM your NFS Server.\nFor example: /mnt/vol1/pool_control_backups/gardenpi/backups" 2>/dev/null)
            if [[ $? = 0 ]]; then
                if [[ -z "$nfs_export" ]]; then
                    get_nfs_export
                fi
            else
                exit 1
            fi

            zenity --question --no-wrap --title="Verify NFS Export" --text="You entered [ <b>$nfs_export</b> ], is this correct?" 2>/dev/null
            if [[ $? = 0 ]]; then
                return
            else
                nfs_export=""
                get_nfs_export
            fi
        elif [[ "$display" == "dialog" ]]; then
            exec 3>&1
            nfs_export=$(dialog --clear \
              --backtitle "NFS Export" \
              --title "Backup Directory" \
              --inputbox "\nWhat is the NFS Export you are going to use?\nThis is the export FROM your NFS Server.\nFor example: /mnt/vol1/pool_control_backups/gardenpi/backups" \
              15 75 "/mnt/vol1/pool_control_backups/gardenpi/backups" 2>&1 1>&3)

            if [[ $? = 0 ]]; then
                if [[ -z "$nfs_export" ]]; then
                  get_nfs_export
                fi
            else
                exit 1
            fi

            dialog --colors --clear --backtitle "Verify NFS Export" --title "Verify NFS Export" \
              --yesno "You entered [ \Z4$nfs_export\Zn ], is this correct?" 5 90
            if [ $? = 0 ]; then
                return
            else
                nfs_export=""
                get_nfs_export
            fi
        else
            echo
            echo
            echo -e -n "What is the NFS Export you are going to use?\nThis is the export FROM your NFS Server.\nFor example: /mnt/vol1/pool_control_backups/gardenpi/backups: "
            read nfs_export
            echo
            echo -e -n "You entered [${blue}$nfs_export${nc}], is this correct? "
            read -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                return
            else
                nfs_export=""
                get_nfs_export
            fi
        fi
    fi
}

## Does our selected backup directory exist?
does_directory_exist() {
  if [[ ! -d $backup_directory ]]; then
    if [[ "$display" == "dialog" ]]; then
      dialog --colors --clear --yes-label "CREATE DIRECTORY" --no-label "CANCEL & QUIT" --backtitle "DIRECTORY ERROR!" \
        --title "\Z1*** DIRECTORY ERROR ***\Zn" --yesno "\nYour selected backup directory [ \Z4$backup_directory\Zn ] is MISSING!\n\nThis script requires that the directory [ \Z4$backup_directory\Zn ] already be created.\n\nWould you like us to attempt to create the directory for you?" 10 100 2>/dev/null

      if [[ $? = 0 ]]; then
        mkdir -p $backup_directory
        if [[ ! -d $backup_directory ]]; then
          echo "Directory Creation Failed, please create $backup_directory manually and rerun script"
          exit 1
        fi
      else
        exit 1
      fi

    else
      if [[ "$display" == "zenity" ]]; then
        zenity --no-wrap --question --text="<span size=\"xx-large\"> \
$backup_directory does not exist!</span>\n\n\n\
This script requires that the [ <b>$backup_directory</b> ] directory already be created.\
\n\nWould you like us to attempt to create the directory for you?" \
          --title="Directory Error !!" --cancel-label="CANCEL & QUIT" --ok-label="CREATE DIRECTORY" 2>/dev/null

        if [[ $? = 0 ]]; then
          mkdir -p $backup_directory
          if [[ ! -d $backup_directory ]]; then
            echo "Directory Creation Failed, please create $backup_directory manually and rerun script"
            exit 1
          fi
        else
          exit 1
        fi
      else
        error_banner
        echo
        echo -e "${red}DIRECTORY ERROR${nc} - $backup_directory does not appear to exist!." >&2
        echo
        echo -e "This script requires that the directory [ ${blue}$backup_directory${nc} ] exist."
        echo
        echo -e -n "Would you like us to attempt to create the directory for you? "
        read -n 1 -r
        if [[ $REPLY =~ ^[Yy]$ ]]; then
          mkdir -p $backup_directory
          if [[ ! -d $backup_directory ]]; then
            echo -e "Directory Creation Failed, please create ${blue}$backup_directory${nc} manually and rerun script"
            exit 1
          fi
        else
          clear
          echo -e "${yellow}ABORTING!!${nc}"
          exit 1
        fi
      fi
    fi
  fi
}

## Is the backup directory mounted at the correct location? In order for this script
## to operate in the way I designed it, backups are done to a remote system or USB device,
## **NOT** the local filesystem. If you attempt to backup to the local filesystem you could
##  run out of space. This just verifies if $backup_directory is **actually** a "mounted"
## filesystem as opposed to just a directory. To save locally, set operation="local"
## and it will skip this check.

is_remote_directory() {
  if ! [[ $(findmnt -M "$backup_directory") ]]; then
    if [[ "$display" == "dialog" ]]; then
      dialog --colors --clear --yes-label "ATTEMPT MOUNT" --no-label "CANCEL & QUIT" --backtitle "MOUNT ERROR!" \
        --title "\Z1*** REMOTE OPERATION MOUNT ERROR ***\Zn" --yesno "\nYou chose REMOTE operation!\n\n
Remote Operation requires that your selected backup directory:\n\n      [ \Z4$backup_directory\Zn ]\n\
\nalready be created and that it be mounted to:\n\n
      [ \Z4$nfs_server:$nfs_export\Zn ] \n\n\n
Would you like us to attempt to mount the correct export for you?" 20 100 2>/dev/null

      if [[ $? = 0 ]]; then
        /bin/umount $backup_directory 2>/dev/null
        /bin/mount -t nfs $nfs_server:$nfs_export $backup_directory
        if [ $? != 0 ]; then
          echo "Mount Failed, please mount manually and rerun script"
          exit 1
        fi
      else
        exit 1
      fi

    else
      if [[ "$display" == "zenity" ]]; then
        zenity --no-wrap --question --text="<span size=\"xx-large\"> \
$backup_directory is not mounted properly!</span>\n\n\n\
Remote Operation requires that the [ <b>$backup_directory</b> ] directory already be created
and that it be mounted to:\n\n<b> $nfs_server:$nfs_export</b>.\n\n\
Would you like us to attempt to mount the correct export for you?" \
          --title="Mount Error !!" --cancel-label="CANCEL & QUIT" --ok-label="ATTEMPT MOUNT" 2>/dev/null

        if [[ $? = 0 ]]; then
          /bin/umount $backup_directory 2>/dev/null
          /bin/mount -t nfs $nfs_server:$nfs_export $backup_directory
          if [[ $? != 0 ]]; then
            echo "Mount Failed, please mount manually and rerun script"
            exit 1
          fi
        else
          exit 1
        fi
      else
        error_banner
        echo
        echo -e "${red}REMOTE OPERATION MOUNT ERROR${nc} - $backup_directory does not appear to be mounted correctly!" >&2
        echo
        echo -e "Remote Operation requires that [ ${blue}$backup_directory${nc} ] be mounted to: [ ${blue}$nfs_server:$nfs_export${nc} ] "
        echo
        echo -e -n "Would you like us to attempt to mount the correct export for you? "
        read -n 1 -r
        if [[ $REPLY =~ ^[Yy]$ ]]; then
          /bin/umount $backup_directory 2>/dev/null
          /bin/mount -t nfs $nfs_server:$nfs_export $backup_directory
          if [[ $? != 0 ]]; then
            echo "Mount Failed, please mount manually and rerun script"
            echo -e "${white}mount -t nfs $nfs_server:$nfs_export $backup_directory${nc}"
            exit 1
          fi
        else
          clear
          echo -e "${yellow}ABORTING!!${nc}"
          exit 1
        fi
      fi
    fi
  fi
}

## This function ***tries*** to mount the USB device if it is not already mounted:
mount_usb_device() {
  if ! [[ $(findmnt -M "$backup_directory") ]]; then
    if [[ "$display" == "dialog" ]]; then
      dialog --colors --clear --yes-label "ATTEMPT MOUNT" --no-label "CANCEL & QUIT" --backtitle "MOUNT ERROR!" \
        --title "\Z1*** USB DEVICE NOT MOUNTED ***\Zn" --yesno "\nUSB Operation requires that your selected backup directory:\n\n      [ \Z4$backup_directory\Zn ]\n\
\nalready be created and that it be mounted to your USB Device:\n\n
      [ \Z4/dev/$userDEV\Zn ] \n\n\n
Would you like us to attempt to mount the USB drive for you?\n\nWe will be running the following command:\n\n     \Z4/bin/mount /dev/$userDEV $backup_directory\Zn" 20 100 2>/dev/null

      if [[ $? = 0 ]]; then
        /bin/umount $backup_directory 2>/dev/null
        /bin/mount /dev/$userDEV $backup_directory
        if [[ $? != 0 ]]; then
          echo "Mount Failed, please mount manually and rerun script"
          exit 1
        fi
      else
        exit 1
      fi

    else
      if [[ "$display" == "zenity" ]]; then
        zenity --no-wrap --question --text="<span size=\"xx-large\"> \
$backup_directory is not mounted properly!</span>\n\n\n\
USB Operation requires that the [ <b>$backup_directory<b> ] directory already be created
and that it be mounted to:\n\n<b> /dev/$userDEV</b>\n\n\
Would you like us to attempt to mount the USB drive for you?" \
          --title="Mount Error !!" --cancel-label="CANCEL & QUIT" --ok-label="ATTEMPT MOUNT" 2>/dev/null

        if [[ $? = 0 ]]; then
          /bin/umount $backup_directory 2>/dev/null
          /bin/mount /dev/$userDEV $backup_directory
          if [[ $? != 0 ]]; then
            zenity --warning --no-wrap --text="Mount Failed! Please mount manually and rerun the script!"
            exit 1
          fi
        else
          exit 1
        fi
      else
        error_banner
        echo
        echo -e "${red}USB OPERATION MOUNT ERROR${nc} - $backup_directory does not appear to be mounted correctly!" >&2
        echo
        echo -e "USB Operation requires that ${blue}$backup_directory${nc} be mounted to: /dev/$userDEV"
        echo
        echo -e -n "Would you like us to attempt to mount the USB drive for you?"
        read -n 1 -r
        if [[ $REPLY =~ ^[Yy]$ ]]; then
          /bin/umount $backup_directory 2>/dev/null
          /bin/mount /dev/$userDEV $backup_directory
          if [ $? != 0 ]; then
            echo "Mount Failed, please mount manually and rerun script"
            echo -e "${white}/bin/mount /dev/$userDEV $backup_directory${nc}"
            exit 1
          fi
        else
          clear
          echo -e "${yellow}ABORTING!!${nc}"
          exit 1
        fi
      fi
    fi
  fi
}

## We need nfs.common installed in order to mount the nfs export where we store our images.
## If nfs.common is not installed, error and quit. I separate this out from our software check
## since we only need this for remote operations.
is_nfs_installed() {
   if  [[ ! -x "$(command -v mount.nfs)" ]]; then
      if [[ "$display" == "dialog" ]]; then
          dialog --clear \
          --backtitle "NFS ERROR" \
          --title "Is NFS installed...?" \
          --ok-label "EXIT" \
          --msgbox "\nNFS Common is required for this script to run. \
                        \n\nPlease install nfs-common and rerun this script! \
                        \n\nYou might try: apt install nfs-common" \
          13 70
          exit 1
       elif [[ "$display" == "zenity" ]]; then
              zenity --no-wrap --warning --text="<span size=\"xx-large\"> \
NFS Installation Error!</span>\n\n\
Please install nfs-common and run this script again.\n\n\n\
You might try: \n\n<b>apt install nfs-common</b>." \
          --title="NFS Error" --ok-label="QUIT" 2>/dev/null
              exit 1
       else
           clear
           error_banner
           echo
           echo -e "${red}ERROR${nc} - NFS does not appear to be installed!." >&2
           echo "Please install nfs-common and rerun script."
           echo
           echo -e "You might try: ${yellow}apt install nfs-common${nc}"
           echo
           echo -e "${yellow}ABORTING!${nc}"
           echo
           echo
           exit 1
      fi
   fi
}

## Once a device is entered into the script we do a **little** error checking. Here
## we are checking to see if the device actually exists on the system as seen via
## dmesg. Chances are, if dmesg does not see it, it is not the correct device.
check_device_available() {
    if [[ $(lsblk | grep -c $userDEV) = 0 ]]; then
        if [[ "$display" == "dialog" ]]; then
            dialog --clear \
            --colors \
            --backtitle "DEVICE ERROR!" \
            --title "\Z1** DEVICE ERROR **\Zn" \
            --ok-label "EXIT" \
            --msgbox "\n/dev/$userDEV does not appear to be valid or available on this system! \
                        \n\nOnce this script exits, please rerun \Zb\Z1 dmesg \Zn from the command line and check your device selection!" \
        10 60
        exit 1
        elif [[ "$display" == "zenity" ]]; then
            zenity --no-wrap --warning --text="<span size=\"xx-large\"> \
/dev/$userDEV is not valid!</span>\n\n\n\
/dev/$userDEV does not appear to be valid or available on this system!\n\n
Once this script exits, run <b>dmesg</b> from the command line\nand check your device selection." \
          --title="Device Error !!" --ok-label="QUIT" 2>/dev/null
            exit 1
        else
            clear
            echo
            echo
            error_banner
            echo
            echo -e "             *** ${red}DEVICE UNAVAILABLE ERROR${nc} ***"
            echo -e "${blue}/dev/$userDEV${nc} does not appear to be valid or available on this system."
            echo -e "Please rerun ${red}dmesg${nc} from the command line and check your device selection."
            echo
            exit 1
        fi
    fi
}

## Is the necessary software installed? If not, let them know
## we need it and exit the script.
is_software_installed() {
  if [[ ! -x "$(command -v mysqldump)" ]] || [[ ! -x "$(command -v pip3)" ]] ||
     [[ ! -x "$(command -v wget)" ]] || [[ ! -x "$(command -v chpasswd)" ]]; then
      if [[ "$display" == "dialog" ]]; then
          dialog --colors --clear \
          --backtitle "SOFTWARE INSTALLATION ERROR" \
          --title "\Z1Is all required software installed...?\Zn" \
          --ok-label "EXIT" \
          --msgbox "\nSpecific software is required for this script to run. \
                        \n\nPlease check the requirements and rerun this script! \
                        \n\n\n\nYou might want to try the following:\n\napt install pip3 wget mariadb-client-10.0 -y" \
          15 80
      elif [[ "$display" == "zenity" ]]; then
          zenity --no-wrap --warning --text="<span size=\"xx-large\"> \
Software Installation Error!</span>\n\n\
Please check software requirements and run this script again.\n\n\n\
You might want to try the following: \n\n<b>apt install pip3 wget mariadb-client-10.0 -y</b>." \
          --title="Software Error" --ok-label="QUIT" 2>/dev/null
          exit 1
      else
          clear
          error_banner
          echo
          echo -e "${red}ERROR${nc} - All required software does not appear to be installed!." >&2
          echo "Please install mariadb-client-10.0, wget & pip3 and rerun script."
          echo
          echo -e "You might want to try: ${red}apt install pip3 wget mariadb-client-10.0 -y${nc}"
          echo
          echo -e "${yellow}ABORTING!${nc}"
          echo
          echo
          exit 1
      fi
    fi
}

## Ask the user for the device we will be using for the cloning or restore operation.
get_device() {
    if [[ "$display" == "zenity" ]]; then
        userDEV=$(zenity --title="Device Entry" --entry --text "Please input your USB device partition to use for backup. \nFor example: sda1 sdb2 sdc1:  " 2>/dev/null)
        if [[ $? = 0 ]]; then
            if [[ -z "$userDEV" ]]; then
                get_device
            fi
         else
             exit 1
        fi
        zenity --question --no-wrap --title="Verify Device Entry" --text="You entered [ $userDEV ], is this correct?" 2>/dev/null
        if [[ $? = 0 ]]; then
            check_device_available
            check_device_ifbootdevice
        else
            get_device
        fi

    elif [[ "$display" == "dialog" ]]; then
        exec 3>&1
        userDEV=$(dialog --clear \
        --backtitle "Enter Device Name" \
        --title "Enter Device Name" \
        --inputbox "\nPlease input the USB or External HDD device to use.\nFor example: sda1  sdb1  sdc1:  " \
        10 50 2>&1 1>&3)

        if [[ $? = 0 ]]; then
            if [ -z "$userDEV" ]; then
                get_device
            fi
        else
            exit 1
        fi
        dialog --colors --clear --backtitle "Verify Device Entry" --title "Verify Device Entry" \
        --yesno "You entered [ \Z4$userDEV\Zn ], is this correct?" 5 50
        if [[ $? = 0 ]]; then
            check_device_available
            check_device_ifbootdevice
        else
            get_device
        fi

    else
      clear
      echo -e "${blue}Enter USB Device Partition: ${nc}"
      echo
      echo -e "Please input the SDD or HDD device to use."
      echo -e -n "For example: sda1 sdb1 sdc1:  "
      read userDEV
      echo
      echo -e -n "You entered [${blue}$userDEV${nc}], is this correct? "
      read -n 1 -r
      echo
      if [[ $REPLY =~ ^[Yy]$ ]]; then
        check_device_available
        check_device_ifbootdevice
      else
        get_device
      fi
    fi
}

get_nfs_server() {
    if [[ -n "$nfs_server" ]] ; then
        if [[ "$display" == "dialog" ]]; then
            dialog --colors --clear --default-button "No" --backtitle "Verify NFS Server" --title "Verify NFS Server" \
        --yesno "NFS Server set to [ \Z4$nfs_server\Zn ] -  OVERRIDE?" 5 60
            if [[ $? = 0 ]]; then
                nfs_server=""
                get_nfs_server
            else
                return
            fi
        elif [[ "$display" == "zenity" ]]; then
                zenity --question --no-wrap --title="Verify NFS Server" --text="NFS Server set to [ <b>$nfs_server</b> ] - OVERRIDE?" 2>/dev/null
                if [[ $? = 0 ]]; then
                    nfs_server=""
                    get_nfs_server
                else
                    return
                fi
        else
            clear
            echo
            echo -e -n "NFS Server set to [ ${yellow}$nfs_server${nc} ] - OVERRIDE? "
            read -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                nfs_server=""
                get_nfs_server
            else
                return
            fi
        fi
  ## Since the operation type id not hard coded, ask the end use about their NFS server:
    else
        if [[ "$display" == "dialog" ]]; then
            exec 3>&1
            nfs_server=$(dialog --clear \
            --backtitle "Enter NFS Server Name or IP" \
            --title "Enter NFS Server Name or IP" \
            --inputbox "\nPlease enter the hostname or IP address of your NFS server: " \
            10 50 2>&1 1>&3)

            if [[ $? = 0 ]]; then
                if [ -z "$nfs_server" ]; then
                    get_nfs_server
                fi
            else
                exit 1
            fi
      ## As long as nfs_server does not come back blank (ie they just hit enter)
      ## let's verify the entry:
            if [[ -n $nfs_server ]]; then
                dialog --colors --clear --backtitle "Verify Entry" --title "Verify Entry" \
                --yesno "You entered [ \Z4$nfs_server\Zn ], is this correct?" 5 80
                if [[ $? = 0 ]]; then
                    return
                else
                    nfs_server=""
                    get_nfs_server
                fi
            else
                get_nfs_server
            fi
        elif [[ "$display" == "zenity" ]]; then
            nfs_server=$(zenity --title="Enter NFS Server Name or IP" --entry --text "Please enter the hostname or IP address of your NFS server: " 2>/dev/null)
            if [[ $? = 0 ]]; then
                if [[ -z "$nfs_server" ]]; then
                    get_nfs_server
                fi
            else
                exit 1
            fi
            zenity --question --no-wrap --title="Verify Entry" --text="You entered [ $nfs_server ], is this correct?" 2>/dev/null
            if [[ $? = 0 ]]; then
                return
            else
                nfs_server=""
                get_nfs_server
            fi
        else
            clear
            echo
            echo
            echo -e -n "Please enter the hostname or IP address of your NFS server: "
            read nfs_server
            echo
            echo -e -n "You entered [${blue}$nfs_server${nc}], is this correct? "
            read -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
              return
            else
              nfs_server=""
              get_nfs_server
            fi
        fi

    fi
}

## Here we do a basic rpctest. Out server is using v3, change this to v4 or disable
## entirely below if you do not need/want the test.
test_nfs_server(){
   reachable=$(rpcinfo -t $nfs_server nfs $nfs_version | grep -c "ready and waiting" 2>/dev/null)
   if [[ ! $reachable = 1 ]]; then
       if [[ "$display" == "dialog" ]]; then
            dialog --clear \
            --colors \
            --backtitle "NFS Server Error" \
            --title "\Z1** NFS Server Error **\Zn" \
            --ok-label "Go Back & Try Again" \
            --msgbox "\n\Z4$nfs_server\Zn does not appear to be a valid NFS server! \
                        \n\nWe were unable to make an NFS connection to your server.\nPlease check your NFS server and try again." \
        10 60
        get_nfs_server
        elif [[ "$display" == "zenity" ]]; then
            zenity --no-wrap --warning --text="<span size=\"xx-large\"> \
$nfs_server is not valid!</span>\n\n\n\
$nfs_server does not appear to be a valid NFS server!\n\n
We were unable to make an NFS connection to your server.\nPlease check your NFS server and try again." \
          --title="NFS Server Error" --ok-label="Go Back & Try Again" 2>/dev/null
            get_nfs_server
        else
            clear
            echo
            echo
            error_banner
            echo
            echo -e "          *** ${red}NFS SERVER ERROR${nc} ***"
            echo -e "${blue}$nfs_server${nc} does not appear to be a valid NFS server!"
            echo -e "We were ${red}unable${nc} to make an NFS connection to your server."
            echo -e "Please check your NFS server and try again."
            echo
            read -n 1 -s -r -p "Press any key to go back and try again....... "
            get_nfs_server
        fi
  fi
}

## Here we are doing a basic check to see if the device entered is actually / or /boot.
## If it is, we throw and error and exit.
check_device_ifbootdevice() {
    if [[ $(mount | grep $userDEV | grep -c boot) != 0 ]] || [[ $(mount | grep $userDEV | egrep -c '\s/\s') != 0 ]]; then
        if [[ "$display" == "zenity" ]]; then
            zenity --warning --no-wrap --text="The device that you have selected appears to be your BOOT device!\n\n \
Please <b>VERIFY</b> your device and try again!" 2>/dev/null
            exit 1
        elif [ "$display" == "dialog" ]; then
            dialog --colors --backtitle "WARNING" --title "\Z1*** WARNING - Possible Boot Device ***\Zn" \
            --msgbox "\nThe device that you have selected appears to be your BOOT device!\n\n\
Please VERIFY your device and try again!" 10 60
            exit 1
        else
            clear
            warning_banner
            echo
            echo
            echo -e "${red}WARNING${yellow} * * * ${red}WARNING${yellow} * * * ${red}WARNING${nc}"
            echo
            echo
            echo -e "The device you have selected [${yellow}/dev/$userDEV${nc}] appears to be your BOOT device!"
            echo -e "Please ${white}VERIFY${nc} your device and try again!"
            echo
            exit 1
        fi
    fi
}

## Check to make sure we have a list of files and directories
## that we need to backup. These reside it /etc/gardenpi
## by default but can be charged above. Die if we cannot get
## to these files/directories.
check_critical_files_and_directories() {
    if [[ ! -d $utility_dir ]]; then
        if [[ "$display" == "dialog" ]]; then
            dialog --colors --title "\Z1**** Utility Directory Unavailable ***\Zn" --msgbox "Your Utility directory [ \Z4$utility_dir\Zn ] is Unavailable.\
                \n\nWe are \Z1UNABLE\Zn to Continue." 7 80
            exit 1
        elif [[ "$display" == "zenity" ]]; then
            zenity --warning --no-wrap --text="Your Utility directory [ $utility_dir ] is Unavailable!\n\n \
                     We are <b>UNABLE</b> to continue!" 2>/dev/null
            exit 1
        else
            echo
            clear
            warning_banner
            echo
            echo -e "${red}WARNING${yellow} * * * ${red}WARNING${yellow} * * * ${red}WARNING${nc}"
            echo
            echo
            echo -e "Your Utility Directory [${yellow}$utility_dir${nc}] is unavailable!"
            echo -e "We are ${white}UNABLE${nc} to continue!"
            echo
            exit 1
        fi

    elif [[ ! -f $critical_files_list ]]; then
        if [[ "$display" == "dialog" ]]; then
            dialog --colors --title "\Z1**** Critical File List Unavailable ***\Zn" --msgbox "Your Critical File List [ \Z4$critical_files_list\Zn ] is Unavailable.\
               \n\nWe are \Z1UNABLE\Zn to Continue." 10 110
            exit 1
        elif [[ "$display" == "zenity" ]]; then
            zenity --warning --no-wrap --text="Your Critical File List [ $critical_files_list ] is Unavailable!\n\n \
                     We are <b>UNABLE</b> to continue!" 2>/dev/null
            exit 1
        else
            echo
            clear
            warning_banner
            echo
            echo -e "${red}WARNING${yellow} * * * ${red}WARNING${yellow} * * * ${red}WARNING${nc}"
            echo
            echo
            echo -e "Your Critical File List [${yellow}$critical_files_list${nc}] is unavailable!"
            echo -e "We are ${white}UNABLE${nc} to continue!"
            echo
            exit 1
        fi
    elif [[ ! -f $critical_directory_list ]]; then
        if [[ "$display" == "dialog" ]]; then
            dialog --colors --title "\Z1**** Critical Directory List Unavailable ***\Zn" --msgbox "Your Critical Directory List [ \Z4$critical_directory_list\Zn ] is Unavailable.\
                        \n\nWe are \Z1UNABLE\Zn to Continue." 10 110
            exit 1
        elif [[ "$display" == "zenity" ]]; then
            zenity --warning --no-wrap --text="Your Critical Directory List [ $critical_directory_list ] is Unavailable!\n\n \
                     We are <b>UNABLE</b> to continue!" 2>/dev/null
            exit 1
        else
            echo
            clear
            warning_banner
            echo
            echo -e "${red}WARNING${yellow} * * * ${red}WARNING${yellow} * * * ${red}WARNING${nc}"
            echo
            echo
            echo -e "Your Critical File Directory [${yellow}$critical_directory_list${nc}] is unavailable!"
            echo -e "We are ${white}UNABLE${nc} to continue!"
            echo
            exit 1
        fi
    else
        if [[ "$display" == "dialog" ]]; then
            dialog --colors --title "**** Directory & Files Good ****" --msgbox "Your Utility directory [ \Z4$utility_dir\Zn ] is Available.\
        \nYour Critical File List [ \Z4$critical_files_list\Zn ] is Available. \
        \nYour Critical Directory List [ \Z4$critical_directory_list\Zn ] is Available." 8 120

        elif [[ "$display" == "zenity" ]]; then
            zenity --info --no-wrap --text="\nYour Utility directory [ $utility_dir ] is Available.\nYour Critical File List [ $critical_files_list ] is Available.\nYour Critical Directory List [ $critical_directory_list ] is Available." 2>/dev/null
        else
            clear
            echo
            echo
            echo -e "Your Utility directory [${yellow}$utility_dir${nc}] is Available!"
            echo -e "Your Critical File List [${yellow}$critical_files_list${nc}] is Available!"
            echo -e "Your Critical Directory List [${yellow}$critical_directory_list${nc}] is Available!"
            echo
            read -n 1 -s -r -p "Press any key to begin your backup..... "
        fi
    fi
}

do_backup() {
    ## First, let's use today's date and time to create
    ## a subdirectory to store our backup in:
    day=$(date +%Y%B%d_%H%M%S)
    mkdir $backup_directory/backup_$day
    destination_dir=$backup_directory/backup_$day

    ## Now let's backup all the files in our critical
    ## files file:
    while IFS= read -r file; do
    cp --verbose $file $destination_dir
    done <$critical_files_list

    ## Now we do the same thing for the directories:
    while IFS= read -r dirs; do
    cp -R --verbose $dirs $destination_dir
    done <$critical_directory_list

    ## Now we need to backup our MySQL database.
    ## This requires the credentials of the database
    ## to be placed in the /user/.my.cnf file where user
    ## is the user executing the backup, otherwise this
    ## will fail.
    mysqldump -h localhost -u neptune neptune > $destination_dir/neptune.sql
    mysqldump -h localhost -u neptune phpmyadmin > $destination_dir/phpmyadmin.sql

    ## Now we need to get rid of the uwsgi.sock file so
    ## we do not accidentally restore it to the new Pi
    ## and cause our app to fail:
    rm $destination_dir/gardenpi_control/uwsgi.sock

    ## Now let's put a copy of our backup and restore script
    ## in our backup directory root just to make sure we have it.
    cp $destination_dir/system_backup.sh $backup_directory
    sleep 3
    ## See how large the backup was:
    current_backup_size=$(du -sh "$destination_dir")
    current_backup_directory_size=$(du -sh "$backup_directory")
    clear #clear the screen
    if [[ $display == "dialog" ]]; then
        dialog --colors --title "*** Backup Complete ***" --msgbox "Your backup completed successfully.\
        \nThe size of your latest backup was: $current_backup_size.
        \nThe overall size of your backup directory is: $current_backup_directory_size" 8 100
    elif [[ $display == "zenity" ]]; then
        zenity --info --no-wrap --text="\nYour backup was successful.\
        \nThe size of your latest backup is: $current_backup_size.\
        \nThe overall size of your backup directory is: $current_backup_directory_size" 2>/dev/null
    else
      clear
      echo -e "    *** Your ${red}G${yellow}a${green}r${white}d${blue}e${red}n${yellow}P${green}i${nc} Backup Completed Successfully! ***"
      echo
      echo -e "Current size of ${blue}backup_$day${nc} file is: ${yellow}$current_backup_size${nc}."
      echo -e "Current overall size of ${blue}$backup_directory${nc} file is: ${yellow}$current_backup_directory_size${nc}."
      echo
      echo
      exit 1
    fi
}


## Here is where we start the restore process....

## Here is where we look in the critical files and critical
## directory files and parse out all of the directories that
## we need to make in order to put everything in its proper
## place during the restore process.
check_directories_exist(){
    while IFS= read -r f;do
    file_directory=($(printf '%s\n' "${f%/*}/"))
       if [ ! -d ${file_directory[0]} ]; then
          mkdir -p ${file_directory[0]}
       fi
    done < $critical_files_list

    while IFS= read -r critical_directory;do
    critical_directory=($(printf '%s\n' "${critical_directory%/*}"))
       if [ ! -d ${critical_directory[0]} ]; then
          mkdir -p ${critical_directory[0]}
       fi
    done < $critical_directory_list
}

## Here is where we go into our backup directory and create
## a list of all backups so we can choose one of them to
## restore.
get_list_of_existing_backups(){
   [ ! -e /dev/shm/.tempfile ] || rm /dev/shm/.tempfile
   cp /dev/null /dev/shm/.backup_images_list
   shopt -s dotglob
   find $backup_directory/* -prune -type d | while IFS= read -r d; do
   dirs=($(printf "%s" "$d"|cut -d'/' --output-delimiter=' ' -f1-))
   echo ${dirs[-1]} >> /dev/shm/.backup_images_list
   done
}

select_backup_image(){
    if [[ "$display" == "dialog" ]]; then
        counter=1
        imagelist=""
        while read i; do
        imagelist="$imagelist $i $i off"
        let counter+=1
        done < /dev/shm/.backup_images_list

        dialog --no-tags --backtitle "Available Backups" \
        --radiolist "Select Backup to Restore" 0 0 $counter \
        $imagelist 2> /dev/shm/.tempfile

        if [[ $? = 0 ]]; then
            image_selected=`cat /dev/shm/.tempfile`
            if [[ ! "$image_selected" == "" ]]; then
                echo "You chose $image_selected"
                rm /dev/shm/.tempfile
                rm /dev/shm/.backup_images_list
            else
                select_backup_image
            fi
        else
            exit 1
        fi

    elif [[ "$display" == "zenity" ]]; then
        image_selected=$(zenity --file-selection --directory --title="Choose Backup" --filename=$backup_directory)
        zenity --question --no-wrap --title="Verify Entry" --text="You entered [ $image_selected ], is this correct?" 2>/dev/null
        if [[ $? = 0 ]]; then
                return
            else
                select_backup_image
            fi
    else
        PS3=""
        echo
        echo -e "Select Backup to ${blue}Restore${nc}:"
        echo
        select d in */; do test -n "$d" && break; echo ">>> Invalid Selection"; done

        image_selected=$d
        echo
        echo -e -e -n "You entered [${blue}$image_selected${nc}], is this correct? "
        read -n 1 -r
        echo -e
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            return
        else
            select_backup_image
        fi
    fi
}

## This is the actual restore function. This parses each of the
## files listed, takes the name of the file (or directory in the
## case of copying the entire directory) and then executes the
## copy command necessary to get the job done.
## Since this script is executed within the directory of the
## chosen backup image, we hard code the file names here.
restore_files() {
    cd $backup_directory/$image_selected || exit
    while IFS= read -r f;do
        directory=($(printf '%s\n' "${f%/*}"))
        fields=($(printf "%s" "$f"|cut -d'/' --output-delimiter=' ' -f1-))
        cp -v ${fields[-1]} ${directory[0]}
    done < $backup_directory/$image_selected/gardenpi/gardenpi_critical_files.txt

    while IFS= read -r critical_directory;do
           critical_directories=($(printf '%s\n' "${critical_directory%/*}"))
           fields=($(printf "%s" "$critical_directory"|cut -d'/' --output-delimiter=' ' -f1-))
           cp -Rv ${fields[-1]} ${critical_directories[0]}
    done < $backup_directory/$image_selected/gardenpi/gardenpi_critical_directories.txt
}

after_restore_operations(){
    chown -R www-data:www-data /var/www/gardenpi_control
    pip3 install -r /var/www/gardenpi_control/gardenpi/requirements.txt
    apt autoremove -y
    cat /etc/fstab.gardenpi >> /etc/fstab
    mount -a
    systemctl disable hciuart
    systemctl daemon-reload
    systemctl enable nginx emperor.uwsgi network-wait-online postfix
    mightyhat_setup
    echo 'pi:gardenpi' | sudo chpasswd
    systemctl enable ssh
    systemctl start ssh
    create_symbolic_links
    dpkg -i /etc/wiringpi/wiringpi-latest.deb #Required but depreciated which is why we keep a copy on the system
}

mightyhat_setup(){
    if [[ $mightyhat ]]; then
        wget https://raw.githubusercontent.com/LowPowerLab/ATX-Raspi/master/shutdownchecksetup.sh
        bash shutdownchecksetup.sh
        rm shutdownchecksetup.sh
    else
        return
    fi
}

## Here is where we create symbolic links to some of the utilities
## that we use. Notably system_backup.sh (this script), and our
## kiosk switching script
create_symbolic_links() {
    ln -s /etc/gardenpi/utilities/gardenpi_desktop.sh /usr/bin/gardenpi_desktop.sh
    ln -s /etc/gardenpi/utilities/system_backup.sh /usr/bin/system_backup.sh
}

## Here is where we do all of the software updating that we need to do to run GardenPi
update_rpi_software_and_system(){
  apt update && apt upgrade -y  # Let's do the basic update of the Rpi software before we do anything else
  apt install locate unclutter vim wget gawk python3 uwsgi uwsgi-emperor uwsgi-plugin-python3 nginx-full mariadb-client-10.0 libsasl2-modules postfix mailutils -y
  systemctl stop uwsgi-emperor
  systemctl disable uwsgi-emperor #Out with the old uwsgi script, we have replaced it with our own...
  mkdir /var/log/gardenpi
  mkdir -p /mount/phxnas/backups
  mkdir -p /mount/phxnas/utilities
  chown -R www-data:www-data /var/log/gardenpi
  adduser www-data gpio
  adduser www-data i2c
  adduser www-data sudo
  adduser www-data dialout
  usermod -a -G www-data pi
}

install_setup_mysql_phpmyadmin(){
  apt install mariadb-server php-fpm -y
  mysqladmin -u root password "$DATABASE_PASS"
  mysql -u root -p"$DATABASE_PASS" -e "UPDATE mysql.user SET Password=PASSWORD('$DATABASE_PASS') WHERE User='root'"
  mysql -u root -p"$DATABASE_PASS" -e "DELETE FROM mysql.user WHERE User='root' AND Host NOT IN ('localhost', '127.0.0.1', '::1')"
  mysql -u root -p"$DATABASE_PASS" -e "DELETE FROM mysql.user WHERE User=''"
  mysql -u root -p"$DATABASE_PASS" -e "DELETE FROM mysql.db WHERE Db='test' OR Db='test\_%'"
  mysql -u root -p"$DATABASE_PASS" -e "FLUSH PRIVILEGES"
  mysql -u root -p"$DATABASE_PASS" -e "CREATE DATABASE neptune /*\!40100 DEFAULT CHARACTER SET utf8 */;"
  mysql -u root -p"$DATABASE_PASS" -e "CREATE USER neptune@localhost IDENTIFIED BY '$NEPTUNE_DB_PASS';"
  mysql -u root -p"$DATABASE_PASS" -e "GRANT ALL PRIVILEGES ON neptune.* TO 'neptune'@'localhost';"
  mysql -u root -p"$DATABASE_PASS" -e "FLUSH PRIVILEGES;"
  mysql -u root -p"$DATABASE_PASS" neptune < $backup_directory/$image_selected/neptune.sql
  ln -s /etc/php/7.1/mods-available/mcrypt.ini /etc/php/7.3/mods-available/
  phpenmod mcrypt
  systemctl restart php7.3-fpm
  apt install phpmyadmin -y
  ln -s /usr/share/phpmyadmin /var/www/gardenpi_control/phpmyadmin
  mysql -u root -p"$DATABASE_PASS" < /usr/share/doc/phpmyadmin/examples/create_tables.sql
  mysql -u root -p"$DATABASE_PASS" -e "CREATE USER phpmyadmin@localhost IDENTIFIED BY '$DATABASE_PASS';"
  mysql -u root -p"$DATABASE_PASS" -e "GRANT SELECT, INSERT, UPDATE, DELETE ON phpmyadmin.* TO 'phpmyadmin'@'localhost'  IDENTIFIED BY '$DATABASE_PASS';"
  mysql -u root -p"$DATABASE_PASS" -e "GRANT SELECT, INSERT, UPDATE, LOCK TABLES, DELETE ON phpmyadmin.* TO 'neptune'@'localhost'  IDENTIFIED BY '$NEPTUNE_DB_PASS';"
  mysql -u root -p"$DATABASE_PASS" -e "FLUSH PRIVILEGES;"
}

verify_restore_start(){
    if [[ "$display" == "dialog" ]]; then
        dialog --colors --clear --default-button "No" --yes-label "START RESTORE" --no-label "CANCEL & QUIT" --backtitle "SYSTEM RESTORE" \
        --title "\Z1*** System Restore Script ***\Zn" --yesno "\nThis restore operation \Z1WILL\Zn overwrite your current\n
Raspberry Pi. You should be running this on brand new\nPi image.\n\nShould we Continue? " 10 60 2>/dev/null
        if [[ ! $? = 0 ]]; then
            dialog --colors --clear --backtitle "System Restore Cancelled!" --title "\Z1 System Restore Cancelled!\Zn" --msgbox "\n\nSystem Restore Cancelled!" 10 35
            exit 1
        else
           return
        fi
    elif [[ "$display" == "zenity" ]]; then
        zenity --question --no-wrap --title="SYSTEM RESTORE" --ok-label="START RESTORE" --text="This restore operation <b>WILL</b> overwrite your current\nRaspberry Pi. You should be running this on a brand new\nPi image.\n\nShould we Continue?" 2>/dev/null
        if [[ ! $? = 0 ]]; then
            zenity --warning --no-wrap --text="System Restore Cancelled"
            exit 1
        else
            return
        fi
    else
        clear
        echo
        echo -e "    *** Welcome to the ${red}G${yellow}a${green}r${white}d${blue}e${red}n${yellow}P${green}i${nc} Backup and Restore Script ***"
        echo
        echo -e "        ${red}***${nc} ${blue}SYSTEM RESTORE SCRIPT${nc} ${red}***${nc}"
        echo
        echo -e "This restore operation ${red}WILL${nc} overwrite your current"
        echo -e "Raspberry Pi. You should be running this script on"
        echo -e "a brand new Pi image!"
        echo
        echo
        echo -e -n "Should we ${blue}Continue${nc}?  "
        read -n 1 -r
        if [[  $REPLY =~ ^[Yy]$ ]]; then
            echo
            return
        else
           echo
           echo -e "${yellow}ABORTING!${nc}"
           echo
           exit 1
       fi
fi
}


after_restore_message(){
    clear
    echo
    echo -e "*** ${red}G${yellow}a${green}r${white}d${blue}e${red}n${yellow}P${green}i${nc} Restore Completed ***"
    echo
    echo -e "The default system user ${blue}pi${nc} password has been updated to: gardenpi"
    echo
    echo "You should REBOOT now...."
    echo
    exit 1
}

## Initial function called with the script. Process starts here to create or restore a backup.
create_backup() {
  is_software_installed
  select_operation_mode
  if [[ "$operation" == "remote" ]]; then
    is_nfs_installed
    get_nfs_server
    test_nfs_server
    get_nfs_export
    get_backup_directory
    does_directory_exist
    is_remote_directory
  else
    if [[ "$operation" == "usb" ]]; then
      get_device
      get_backup_directory
      does_directory_exist
      mount_usb_device
    else
      get_backup_directory
      does_directory_exist
      userDEV=$backup_directory
      check_device_ifbootdevice
    fi
  fi
  check_critical_files_and_directories
  do_backup
}

## Initial function called with the script. Process starts here to restore an image.
restore_backup() {
  verify_restore_start
  select_operation_mode
  if [[ "$operation" == "remote" ]]; then
    is_nfs_installed
    get_nfs_server
    test_nfs_server
    get_nfs_export
    get_backup_directory
    does_directory_exist
    is_remote_directory
  else
    if [[ "$operation" == "usb" ]]; then
      echo""
    fi
  fi
  get_current_restore_backup_directory # where was this script called from? Allow us to cd into directory for copy operations.
  get_list_of_existing_backups
  select_backup_image
  check_directories_exist
  update_rpi_software_and_system
  install_setup_mysql_phpmyadmin
  restore_files
  after_restore_operations
  after_restore_message
}

## Help Information

help() {
  clear
  echo
  echo -e "    *** Welcome to the ${red}G${yellow}a${green}r${white}d${blue}e${red}n${yellow}P${green}i${nc} Backup and Restore Script ***"
  echo
  echo -e "This script is designed to make a backup of a running ${red}G${yellow}a${green}r${white}d${blue}e${red}n${yellow}P${green}i${nc} system,"
  echo -e "or to restore a backup to a ${blue}newly imaged Rpi Raspbian installation${nc}."
  echo
  echo -e "This script ${red}IS NOT${nc} a full system backup. It only backs up and restores"
  echo -e "those files necessary to run ${red}G${yellow}a${green}r${white}d${blue}e${red}n${yellow}P${green}i${nc}."
  echo
  echo "There are several other prerequisites to using this script:"
  echo -e "     1) Some version of mysqldump ${yellow}must${nc} be installed on your local system."
  echo -e "     2) You ${yellow}must${nc} have nfs.common installed for NFS operations (We will check for you)."
  echo -e "     3) You ${yellow}must${nc} know the name of the backup you want restored if restoring from backup."
  echo -e "     4) There ${yellow}must${nc} be a host entry for your NFS server in /etc/hosts or other name resolution."
  echo -e "     5) YOUR system ${yellow}must${nc} be on an IP address allowed to nfs mount your export."
  echo
  echo "If any of these prerequisites are not met, this script will not work for you."
  echo
  echo "Some of these things we can attempt to correct for you, like mounting the correct directory,"
  echo "but you need to verify all the necessary software has been installed before the script will run."
  echo
  echo "During a restore we will attempt to mount the necessary nfs mounts and install all the"
  echo "necessary software as well."
  echo
  echo "USB DEVICE"
  echo "If you do not know what your USB device is, remove it and put it back in to the Pi. Then run dmesg at"
  echo "the command prompt and look for the last entries. They should look something like this:"
  echo
  echo -e ${yellow}
  echo "[17689.034012] usb 2-1: new SuperSpeed Gen 1 USB device number 4 using xhci_hcd"
  echo "[17689.065591] usb 2-1: New USB device found, idVendor=13fe, idProduct=5500, bcdDevice= 1.10"
  echo "[17689.065608] usb 2-1: New USB device strings: Mfr=1, Product=2, SerialNumber=3"
  echo "[17689.065620] usb 2-1: Product: Patriot Memory"
  echo "[17689.065632] usb 2-1: Manufacturer:"
  echo "[17689.065645] usb 2-1: SerialNumber: 070B6A4DB5E62084"
  echo -e "[17689.068692] usb-storage 2-1:1.0: ${white}USB Mass Storage device detected${yellow}"
  echo "[17689.070010] scsi host0: usb-storage 2-1:1.0"
  echo -e "[17690.124620] scsi 0:0:0:0: Direct-Access              ${white}Patriot Memory${yellow}   PMAP PQ: 0 ANSI: 6"
  echo "[17690.125469] sd 0:0:0:0: Attached scsi generic sg0 type 0"
  echo -e "[17690.126053] sd 0:0:0:0: [sda] 60555264 512-byte logical blocks: ${white}(31.0 GB/28.9 GiB)${yellow}"
  echo "[17690.133089] sd 0:0:0:0: [sda] Write Protect is off"
  echo "[17690.133107] sd 0:0:0:0: [sda] Mode Sense: 45 00 00 00"
  echo "[17690.134176] sd 0:0:0:0: [sda] Write cache: disabled, read cache: enabled, doesn't support DPO or FUA"
  echo -e "17690.274234]  sda: ${white}sda1${yellow}"
  echo "17690.275911] sd 0:0:0:0: [sda] Attached SCSI removable disk"
  echo -e ${nc}
  echo
  echo -e "Notice the ${white}manufacturer${nc} and the ${white}size${nc} of the device. This can help to make sure you have"
  echo -e "the correct device. ${red}WARNING${nc} - Failure to use the correct device can overwrite your main"
  echo "hard drive, so please be very careful."
  echo
  echo "In this case, the USB drive we want to use is /dev/sda1"
  echo
  echo "If you have any doubts about using this script - STOP and get HELP!"
  echo
  echo -e "We will ${yellow}ATTEMPT${nc} to check to make sure everything should run correctly, but we will not"
  echo "know the actual device you are using, so be careful!"
  echo
  echo

}

while getopts ":h" option; do
   case $option in
      h) # display Help
         help
         exit;;
     \?) # incorrect option
         echo "Error: Invalid option"
         exit;;
   esac
done

running_on_rpi
must_run_as_root
check_dialog
determine_display #just in case above fails or we are in X
welcome #start the process or backup or restore

