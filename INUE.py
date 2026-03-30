# DISCLAIMER OF LIABILITY:
# This software is provided "as is", without any warranty
# The author is not responsible for any damages resulting from its use
# LICENSE:
# This file is part of INUE - INteractive and Userfriendly Emergency tool for burnt areas v. 1.1 'άλφα, released under the GNU Affero General Public License v3.
# See the LICENSE file or https://www.gnu.org/licenses/agpl-3.0.html for more details.
# Copyright Costantino Pala © 2025
# This file was created in the framework of a PhD funded by CNR-IRPI-PG and DSCG-UNICA
# Written by me, with coding support and suggestions from ChatGPT.


import platform
import GUI #The INUE Guided User Interface
from assetios import parameters
import os


def prataforma():
    #checks the OS
    sys = platform.system()
    match sys:
        case 'Linux':
            syscode = 1
        case 'Windows':
            syscode = 2
        case 'Darwin':
            syscode = 3
    parameters['sistema'] = syscode

    
def aviadore():
    #Starts INUE GUI
    prataforma()
    GUI.GUI()

aviadore()
