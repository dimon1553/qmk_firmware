"""Used by the make system to generate LUFA Keyboard.h from info.json
"""
from dotty_dict import dotty
from milc import cli

from qmk.decorators import automagic_keyboard
from qmk.info import info_json, get_keyboard_overrides
from qmk.path import is_keyboard, normpath
from qmk.keyboard import keyboard_completer


@cli.argument('-o', '--output', arg_only=True, type=normpath, help='File to write to')
@cli.argument('-q', '--quiet', arg_only=True, action='store_true', help="Quiet mode, only output error messages")
@cli.argument('-kb', '--keyboard', completer=keyboard_completer, help='Keyboard to generate LUFA Keyboard.h for.')
@cli.argument('-km', '--keymap', arg_only=True, help='Keyboard to generate LUFA Keyboard.h for.')
@cli.subcommand('Used by the make system to generate LUFA Keyboard.h from info.json', hidden=True)
@automagic_keyboard
def generate_dfu_header(cli):
    """Generates the Keyboard.h file.
    """
    # Determine our keyboard(s)
    if not cli.config.generate_dfu_header.keyboard:
        cli.log.error('Missing parameter: --keyboard')
        cli.subcommands['info'].print_help()
        return False

    if not is_keyboard(cli.config.generate_dfu_header.keyboard):
        cli.log.error('Invalid keyboard: "%s"', cli.config.generate_dfu_header.keyboard)
        return False

    # Build the Keyboard.h file.
    kb_info_json = dotty(info_json(cli.config.generate_dfu_header.keyboard, overrides=get_keyboard_overrides(cli.args.keyboard, cli.args.keymap)))

    keyboard_h_lines = ['/* This file was generated by `qmk generate-dfu-header`. Do not edit or copy.' ' */', '', '#pragma once']
    keyboard_h_lines.append(f'#define MANUFACTURER {kb_info_json["manufacturer"]}')
    keyboard_h_lines.append(f'#define PRODUCT {cli.config.generate_dfu_header.keyboard} Bootloader')

    # Optional
    if 'qmk_lufa_bootloader.esc_output' in kb_info_json:
        keyboard_h_lines.append(f'#define QMK_ESC_OUTPUT {kb_info_json["qmk_lufa_bootloader.esc_output"]}')
    if 'qmk_lufa_bootloader.esc_input' in kb_info_json:
        keyboard_h_lines.append(f'#define QMK_ESC_INPUT {kb_info_json["qmk_lufa_bootloader.esc_input"]}')
    if 'qmk_lufa_bootloader.led' in kb_info_json:
        keyboard_h_lines.append(f'#define QMK_LED {kb_info_json["qmk_lufa_bootloader.led"]}')
    if 'qmk_lufa_bootloader.speaker' in kb_info_json:
        keyboard_h_lines.append(f'#define QMK_SPEAKER {kb_info_json["qmk_lufa_bootloader.speaker"]}')

    # Show the results
    keyboard_h = '\n'.join(keyboard_h_lines)

    if cli.args.output:
        cli.args.output.parent.mkdir(parents=True, exist_ok=True)
        if cli.args.output.exists():
            cli.args.output.replace(cli.args.output.parent / (cli.args.output.name + '.bak'))
        cli.args.output.write_text(keyboard_h)

        if not cli.args.quiet:
            cli.log.info('Wrote Keyboard.h to %s.', cli.args.output)

    else:
        print(keyboard_h)
