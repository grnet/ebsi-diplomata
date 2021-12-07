from bullet import Bullet, Check, YesNo, Input, Password, Numbers, \
    VerticalPrompt, SlidePrompt, ScrollBar, styles

_base_style = {
    'indent': 0,
    'align': 3,
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

class MenuHandler(object):

    def _adjust_prompt(self, prompt):
        return prompt + (' ' if not prompt.endswith(' ') \
            else '')

    def _mk_yes_no(self, prompt):
        return YesNo(_adjust_prompt(prompt))

    def _mk_input(self, prompt):
        return Input(_adjust_prompt(prompt))

    def _mk_number(self, prompt):
        return Numbers(_adjust_prompt(prompt),
            **_style['number'],)

    def _mk_single_choice(self, prompt, choices):
        return Bullet(prompt=prompt, choices=choices,
            **_style['bullet'],)

    def _mk_multiple_choices(self, prompt, choices):
        return Check(prompt=prompt, choices=choices,
            **_style['check'],)

    def launch_yes_no(self, prompt):
        return _mk_yes_no(prompt).launch()

    def launch_input(self, prompt):
        return _mk_input(prompt).launch()

    def launch_number(self, prompt):
        return _mk_number(prompt).launch()

    def launch_single_choice(self, prompt, choices):
        menu = self._mk_single_choice(prompt, choices)
        res = menu.launch()
        out = res[0]
        return out

    def launch_multiple_choices(self, prompt, choices):
        menu = self._mk_multiple_choices(prompt, choices)
        res = menu.launch()
        out = res[0]
        return out

    def launch_prompt(self, config):
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
        res = SlidePrompt(steps).launch()
        out = []
        for cur, key in zip(res, config.keys()):
            match key:
                case 'yes_no':
                    out += [cur[1]]
                case 'input':
                    out += [cur[1]]
                case 'number':
                    out += [cur[1]]
                case 'single':
                    out += [cur[1][0]]
                case 'multiple':
                    out += [cur[1][0]]
        return out         
