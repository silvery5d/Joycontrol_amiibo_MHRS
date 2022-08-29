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


async def _change_date(controller_state, date_now): #根据当前月份数完成时间修改
    await controller_state.connect()    
    # 进入时间日期设置
    await button_push(controller_state, 'down', sec=1)
    await asyncio.sleep(0.3)
    await button_push(controller_state, 'a')
    await asyncio.sleep(0.3)

    if date_now.month == 12:
        #12月，年+1，月-1
        await button_push(controller_state, 'up')
        await asyncio.sleep(0.3)
        await button_push(controller_state, 'right')
        await asyncio.sleep(0.3)
        await button_push(controller_state, 'down')        
    else:
        #1~11月，年-1，月+1
        await button_push(controller_state, 'down')
        await asyncio.sleep(0.3)
        await button_push(controller_state, 'right')
        await asyncio.sleep(0.3)
        await button_push(controller_state, 'up')  

    # 结束向右按ok
    await asyncio.sleep(0.3)
    await button_push(controller_state, 'right', sec=1)
    await asyncio.sleep(0.3)
    await button_push(controller_state, 'a')
    await asyncio.sleep(0.3)

    # return home screen
    await button_push(controller_state, 'home')
    await asyncio.sleep(1)


async def _draw(controller_state, amiibo_dir): # 从Home界面回游戏抽完所有Amiibo
    await controller_state.connect()
    # return to game
    await button_push(controller_state, 'home')
    await asyncio.sleep(1)

    for amiibo_bin in os.listdir(amiibo_dir):
        print('READING ' + amiibo_bin)
        if not amiibo_bin.endswith('.bin'):
            continue
        # goto read amiibo screen
        for _ in range(3):
            await button_push(controller_state, 'a')
            await asyncio.sleep(0.2)
        controller_state.set_nfc(NFCTag.load_amiibo(os.path.join(amiibo_dir, amiibo_bin)))
        await asyncio.sleep(2)
        controller_state.set_nfc(None)
        for _ in range(10):
            await button_push(controller_state, 'a')
            await asyncio.sleep(0.1)
        # 下确定领完奖品
        await button_push(controller_state, 'down')
        await asyncio.sleep(0.3)
        await button_push(controller_state, 'a')
        await asyncio.sleep(1)
    await button_push(controller_state, 'home')
    await asyncio.sleep(1)
    print('----------------')

async def _reset_day(controller_state): # 按两下A
    await controller_state.connect()
    # sync time to internet
    await button_push(controller_state, 'a')
    await asyncio.sleep(1)
    # disable sync again
    await button_push(controller_state, 'a')
    await asyncio.sleep(0.3)
    # return home screen
    await button_push(controller_state, 'home')
    await asyncio.sleep(1)


async def _go_datetime_setting(controller_state): # 从Home屏幕去到 日期与时间 界面
    await controller_state.connect()
    # goto settings
    await button_push(controller_state, 'down', sec=0.5)
    await asyncio.sleep(0.3)
    await button_push(controller_state, 'right', sec=1)
    await asyncio.sleep(0.3)
    await button_push(controller_state, 'left')
    await asyncio.sleep(0.3)
    await button_push(controller_state, 'a')
    await asyncio.sleep(0.3)

    # go all the way down
    await button_push(controller_state, 'down', sec=3)
    await asyncio.sleep(0.3)

    # goto "Console" menu
    await button_push(controller_state, 'right')
    await asyncio.sleep(0.3)

    # goto "Date and Time" setting
    for _ in range(datetime_menu_loop):
        await button_push(controller_state, 'down', sec=0.1)
        await asyncio.sleep(0.1)
    await button_push(controller_state, 'a')
    await asyncio.sleep(0.3)


async def _run_amiibo(controller_state, args):
    if not args.amiibo or args.amiibo == '':
        print('amiibo dir cannot be empty')
        return
    date_now = datetime.now()

    await _go_datetime_setting(controller_state)
    await _change_date(controller_state, date_now)
    await _draw(controller_state, amiibo_dir=args.amiibo)

    await _go_datetime_setting(controller_state)
    await _reset_day(controller_state)
    await _draw(controller_state, amiibo_dir=args.amiibo)



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
            for _ in range(5000):
                await _run_amiibo(controller_state, args)
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
    parser.add_argument('-l', '--log', help='BT-communication logfile output')
    parser.add_argument('-d', '--device_id', help='not fully working yet, the BT-adapter to use')
    parser.add_argument('--spi_flash', help='controller SPI-memory dump to use')
    parser.add_argument('-r', '--reconnect_bt_addr', type=str, default=None,
                        help='The Switch console Bluetooth address (or "auto" for automatic detection), '
                             'for reconnecting as an already paired controller.')
    parser.add_argument('--amiibo', type=str, help='The path of amiibo bin dir')
    parser.add_argument('-n', '--days', type=int, help='The days of loop')
    # 当主机是switch lite时，使用--lite参数。
    parser.add_argument('--lite', type=bool, help='If console is switch lite')
    main_args = parser.parse_args()
    main_args.controller = 'PRO_CONTROLLER'

    datetime_menu_loop = 10
    if main_args.lite:
        # 在设置-主机界面，lite要按几下才能到达日期设置？我没有lite，有lite的同学自己调整这里的数字吧
        datetime_menu_loop = 5
    exiting = False
    loop = asyncio.get_event_loop()
    loop.run_until_complete(
        _main(main_args)
    )
