from bullet import Bullet, Check, YesNo, Input, Password, Numbers, \
    VerticalPrompt, SlidePrompt, ScrollBar, styles

_formatting = {
    'indent': 1,
    'shift': 0,
    'align': 4,
    'margin': 0,
    'pad_right': 5,
    'return_index': True,
}

_style = {
    'yn': {},
    'input': {},
    'number': {
        'type': int
    },
    'bullet': {
        **_formatting,
        'bullet': '',
    },
    'check': {
        **_formatting,
        # TODO
    },
}


class MenuHandler(object):

    def _normalize_prompt(self, prompt):
        return prompt + (' ' if not prompt.endswith(' ')
                         else '')

    def _mk_yn(self, prompt):
        prompt = self._normalize_prompt(prompt)
        return YesNo(prompt)

    def _mk_input(self, prompt):
        prompt = self._normalize_prompt(prompt)
        return Input(prompt)

    def _mk_number(self, prompt):
        prompt = self._normalize_prompt(prompt)
        return Numbers(prompt, **_style['number'],)

    def _mk_choice(self, prompt, choices):
        prompt = self._normalize_prompt(prompt)
        return Bullet(prompt=prompt, choices=choices,
                      **_style['bullet'],)

    def _mk_selection(self, prompt, choices):
        prompt = self._normalize_prompt(prompt)
        return Check(prompt=prompt, choices=choices,
                     **_style['check'],)

    def launch_yn(self, prompt):
        return self._mk_yn(prompt).launch()

    def launch_input(self, prompt):
        return self._mk_input(prompt).launch()

    def launch_number(self, prompt):
        return self._mk_number(prompt).launch()

    def launch_choice(self, prompt, choices):
        menu = self._mk_choice(prompt, choices)
        res = menu.launch()
        out = res[0]
        return out

    def launch_selection(self, prompt, choices):
        menu = self._mk_selection(prompt, choices)
        res = menu.launch()
        out = res[0]
        return out

    def launch_prompt(self, config):
        steps = []
        for key, params in config.items():
            match key:
                case 'yn':
                    steps += [self._mk_yn(params), ]
                case 'input':
                    steps += [self._mk_input(params), ]
                case 'number':
                    steps += [self._mk_number(params), ]
                case 'single':
                    steps += [self._mk_choice(**params), ]
                case 'selection':
                    steps += [self._mk_selection(**params), ]
        res = SlidePrompt(steps).launch()
        out = []
        for cur, key in zip(res, config.keys()):
            match key:
                case 'yn':
                    out += [cur[1]]
                case 'input':
                    out += [cur[1]]
                case 'number':
                    out += [cur[1]]
                case 'single':
                    out += [cur[1][0]]
                case 'selection':
                    out += [cur[1][0]]
        return out
