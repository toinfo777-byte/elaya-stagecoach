from __future__ import annotations
from aiogram import Router

router = Router(name="common")
# intentionally empty — универсальные ловушки отключены,
# чтобы все входы в меню шли через help.show_main_menu()
