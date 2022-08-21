#!/usr/bin/env python3

import argparse
import asyncio
from datetime import datetime, date, timedelta
import logging
import os
import signal

import joycontrol.debug as debug
from joycontrol import logging_default as log, utils
from joycontrol.command_line_interface import ControllerCLI
from joycontrol.controller import Controller
from joycontrol.controller_state import ControllerState, button_push, button_press, button_release
from joycontrol.memory import FlashMemory
from joycontrol.protocol import controller_protocol_factory
from joycontrol.server import create_hid_server
from joycontrol.nfc_tag import NFCTag

logger = logging.getLogger(__name__)

async def _start_talisman(controller_state):
    await controller_state.connect()
    for _ in range(10):
        await button_push(controller_state, 'a')
        await asyncio.sleep(0.3)
        await button_push(controller_state, 'a')
        await asyncio.sleep(0.3)
        await button_push(controller_state, 'right')
        await asyncio.sleep(0.3)
        await button_push(controller_state, 'a')
        await asyncio.sleep(0.3)
        await button_push(controller_state, 'up')
        await asyncio.sleep(0.3)
        await button_push(controller_state, 'a')
        await asyncio.sleep(0.3)
        await button_push(controller_state, 'left')
        await asyncio.sleep(0.3)
        await button_push(controller_state, 'a')
        await asyncio.sleep(0.3)
    await button_push(controller_state, 'up')
    await asyncio.sleep(0.3)
    await button_push(controller_state, 'a')
    await asyncio.sleep(0.3)

    
async def _main(args):
    controller = Controller.from_arg(args.controller)
    spi_flash = FlashMemory()

    with utils.get_output(path=args.log, default=None) as capture_file:
        ctl_psm, itr_psm = 17, 19

        factory = controller_protocol_factory(controller, spi_flash=spi_flash, reconnect=args.reconnect_bt_addr)
        transport, protocol = await create_hid_server(factory, reconnect_bt_addr=args.reconnect_bt_addr,
                                                      ctl_psm=ctl_psm,
                                                      itr_psm=itr_psm, capture_file=capture_file,
                                                      device_id=args.device_id,
                                                      interactive=True)
        controller_state = protocol.get_controller_state()

        try:
            await _start_talisman(controller_state)
        finally:
            logger.info('Stopping communication...')
            await transport.close()


def signal_handler(sig, frame):
    global exiting
    exiting = True


if __name__ == '__main__':
    # check if root
    if not os.geteuid() == 0:
        raise PermissionError('Script must be run as root!')

    # setup logging
    # log.configure(console_level=logging.ERROR)
    log.configure()

    parser = argparse.ArgumentParser()
    parser.add_argument('controller', help='JOYCON_R, JOYCON_L or PRO_CONTROLLER')
    parser.add_argument('-l', '--log', help='BT-communication logfile output')
    parser.add_argument('-d', '--device_id', help='not fully working yet, the BT-adapter to use')
    parser.add_argument('--spi_flash', help='controller SPI-memory dump to use')
    parser.add_argument('-r', '--reconnect_bt_addr', type=str, default=None,
                        help='The Switch console Bluetooth address (or "auto" for automatic detection), '
                             'for reconnecting as an already paired controller.')
    parser.add_argument('--amiibo', type=str, help='The path of amiibo bin dir')
    parser.add_argument('-n', '--days', type=int, help='The days of loop')
    main_args = parser.parse_args()

    exiting = False
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(
        _main(main_args)
    )
