from bullet import Bullet, Check, YesNo, Input, Password, Numbers, \
    VerticalPrompt, SlidePrompt, ScrollBar

_base_style = {
    'indent': 0,
    'align': 5,
    'margin': 2,
    'shift': 0,
    'pad_right': 5,
    'return_index': True,
}

_style = {
    'yes_no': {},
    'input': {},
    'number': {
        'type': int
    },
    'bullet': {
        **_base_style,
        'bullet': '',
    },
    'check': {
        **_base_style,
        # TODO
    },
}

def _adjust_prompt(prompt):
    return prompt + (' ' if not prompt.endswith(' ') else '')

def _mk_yes_no(prompt):
    return YesNo(_adjust_prompt(prompt))

def _mk_input(prompt):
    return Input(_adjust_prompt(prompt))

def _mk_number(prompt):
    return Numbers(_adjust_prompt(prompt),
        **_style['number'],)

def _mk_single_choice(prompt, choices):
    return Bullet(prompt=prompt, choices=choices,
        **_style['bullet'],)

def _mk_multiple_choices(prompt, choices):
    return Check(prompt=prompt, choices=choices,
        **_style['check'],)

def launch_yes_no(prompt):
    return _mk_yes_no(prompt).launch()

def launch_input(prompt):
    return _mk_input(prompt).launch()

def launch_number(prompt):
    return _mk_number(prompt).launch()

def launch_single_choice(prompt, choices):
    menu = _mk_single_choice(prompt, choices)
    out = menu.launch()
    return out

def launch_multiple_choices(prompt, choices):
    menu = _mk_multiple_choices(prompt, choices)
    res = menu.launch()
    out = list(zip(res[0], res[1]))
    return out

def launch_prompt(config):
    steps = []
    for key, params in config.items():
        match key:
            case 'yes_no':
                steps += [_mk_yes_no(params),]
            case 'input':
                steps += [_mk_input(params),]
            case 'number':
                steps += [_mk_number(params),]
            case 'single':
                steps += [_mk_single_choice(**params),]
            case 'multiple':
                steps += [_mk_multiple_choices(**params),]
    _prompt = SlidePrompt(steps)
    return _prompt.launch()
