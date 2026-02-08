from dataclasses import dataclass
from typing import Type, Callable

from aiogram import Bot
from aiogram.types import Message
from aiogram.fsm.context import FSMContext


@dataclass
class FormAdapter:
    states: Type
    question_factory: Callable

    message: Message
    bot: Bot
    fsm: FSMContext

    def question(self):
        return self.question_factory(
            message=self.message,
            bot=self.bot,
            state=self.fsm
        )

    def state(self, name: str):
        try:
            return getattr(self.states, name)
        except AttributeError:
            raise ValueError(f"State '{name}' not found in {self.states.__name__}")
