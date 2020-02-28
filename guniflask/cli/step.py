# coding=utf-8

import os
import signal

from guniflask.utils.cli import readchar

__all__ = ['Step', 'StepChain', 'InputStep', 'ChoiceStep']


class Step:
    desc = None

    def __init__(self):
        self.value = None
        self.title = self.desc
        self.tooltip = None

    def process_arguments(self, settings):
        pass

    def process_user_input(self):
        while True:
            self.show_question()
            user_input = self.get_user_input()
            if self.check_user_input(user_input):
                self.show_decision()
                break
            else:
                self.show_invalid_tooltip()

    def show_question(self):
        raise NotImplementedError

    def get_user_input(self):
        raise NotImplementedError

    def show_decision(self):
        raise NotImplementedError

    def show_invalid_tooltip(self):
        raise NotImplementedError

    def check_user_input(self, user_input):
        return True

    def update_settings(self, settings):
        raise NotImplementedError

    def question(self):
        return '\033[32m?\033[0m {} \033[37m({})\033[0m'.format(self.title, self.tooltip)

    def decision(self):
        return '\033[32m?\033[0m {} \033[36m{}\033[0m'.format(self.title, self.value)

    def go_back_lines(self, n=1):
        return '\033[1A\r\033[K' * n

    def clean_line(self):
        return '\r\033[K'

    @property
    def next_step(self):
        return None


class StepChain:
    def __init__(self, step, length=0, next_steps=None):
        self.step = step
        self.length = length
        self.next_steps = next_steps

    def previous(self, father, siblings=None):
        max_depth = self.length
        next_steps = [self]
        if siblings:
            for s in siblings:
                max_depth = max(max_depth, s.length)
                next_steps.append(s)
        s = StepChain(father, length=max_depth + 1, next_steps=next_steps)
        return s

    def __iter__(self):
        return StepChainIter(self)


class StepChainIter:
    def __init__(self, step_chain):
        self.step_chain = step_chain
        self.total_steps = step_chain.length + 1

    def __next__(self):
        if not self.step_chain:
            raise StopIteration
        cur_step = self.total_steps - self.step_chain.length
        step = self.step_chain.step

        next_step = None
        if self.step_chain.next_steps:
            if len(self.step_chain.next_steps) == 1:
                next_step = self.step_chain.next_steps[0]
            else:
                next_step_cls = self.step_chain.step.next_step
                if next_step_cls:
                    for s in self.step_chain.next_steps:
                        if isinstance(s.step, next_step_cls):
                            next_step = s
                            break
                if next_step is None:
                    raise RuntimeError('No matching next step')
        self.step_chain = next_step

        return cur_step, self.total_steps, step


class InputStep(Step):
    def show_question(self):
        print(self.question() + ' ', end='', flush=True)

    def get_user_input(self):
        return input()

    def show_decision(self):
        print(self.clean_line(), end='', flush=True)
        print(self.go_back_lines(), end='', flush=True)
        print(self.decision(), flush=True)

    def show_invalid_tooltip(self):
        print(self.go_back_lines(), end='', flush=True)


class ChoiceStep(Step):
    def __init__(self):
        super().__init__()
        self.selected = 0
        self.choices = []
        self.values = []

    def show_question(self):
        print(self.question() + ' ', end='', flush=True)
        for i in range(len(self.choices)):
            print(flush=True)
            if i == self.selected:
                print('\033[36m>\033[0m \033[36m{}\033[0m'.format(self.choices[i]), end='', flush=True)
            else:
                print('  {}'.format(self.choices[i]), end='', flush=True)
        self.hide_cursor()

    def get_user_input(self):
        ch = readchar()
        if ch == '\x03':
            self.show_cursor()
            raise KeyboardInterrupt
        if ch == '\x1a':
            self.show_cursor()
            os.kill(os.getpid(), signal.SIGSTOP)
        return ch

    def check_user_input(self, user_input):
        if user_input == '\r' or user_input == '\n':
            self.value = self.choices[self.selected]
            self.show_cursor()
            return True
        if user_input == '\x1b':
            assert readchar() == '['
            ch = readchar()
            if ch == 'A':
                self.selected -= 1
                if self.selected < 0:
                    self.selected = len(self.choices) - 1
            elif ch == 'B':
                self.selected += 1
                if self.selected >= len(self.choices):
                    self.selected = 0
        return False

    def show_decision(self):
        print(self.clean_line(), end='', flush=True)
        print(self.go_back_lines(len(self.choices)), end='', flush=True)
        print(self.decision(), flush=True)

    def show_invalid_tooltip(self):
        print(self.clean_line(), end='', flush=True)
        print(self.go_back_lines(len(self.choices)), end='', flush=True)

    def add_choice(self, desc=None, value=None):
        self.choices.append(desc)
        self.values.append(value)

    @property
    def selected_value(self):
        return self.values[self.selected]

    def show_cursor(self):
        print('\033[?25h', end='', flush=True)

    def hide_cursor(self):
        print('\033[?25l', end='', flush=True)
