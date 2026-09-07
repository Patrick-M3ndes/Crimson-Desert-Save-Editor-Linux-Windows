#!/usr/bin/env python3
from __future__ import annotations
import os
import sys
import glob
from datetime import datetime
from dataclasses import dataclass
from typing import Optional, List, Dict

from src.crypto import load_save_file, save_save_file, SaveFile
from src.scanner import (
    scan_items,
    search_items,
    set_item_stack,
    set_item_enchant,
    set_item_endurance,
    set_item_sharpness,
    repair_item,
    swap_item_key,
    load_item_database,
    search_database_items,
    Item,
)
from src.backup import create_backup, list_backups, restore_backup
from src.locales import t, set_language, get_available_languages


@dataclass
class SlotInfo:
    slot_id: str
    save_path: str
    mtime: float
    mtime_str: str
    size_bytes: int


STEAM_DEFAULT_SAVE_DIR = os.path.expanduser(
    "~/.local/share/Steam/steamapps/compatdata/3321460/pfx/drive_c/users/steamuser/AppData/Local/Pearl Abyss/CD/save"
)

CURRENCY_KEYS = {
    1: "Copper (Dinheiro)",
    11: "Camp Funds (Fundos do Acampamento)",
    12: "Camp Food (Comida do Acampamento)",
    13: "Camp Timber (Madeira do Acampamento)",
    14: "Camp Stone (Pedra do Acampamento)",
    15: "Camp Weapons (Armas do Acampamento)",
}


@dataclass
class SlotInfo:
    slot_id: str
    save_path: str
    mtime: float
    mtime_str: str
    size_bytes: int


# ==============================================================================
# CORREÇÃO: Variáveis globais necessárias que estavam ausentes
# ==============================================================================
STEAM_DEFAULT_SAVE_DIR = os.path.expanduser(
    "~/.local/share/Steam/steamapps/compatdata/3321460/pfx/drive_c/users/steamuser/AppData/Local/Pearl Abyss/CD/save"
)

CURRENCY_KEYS = {
    1: "Copper (Dinheiro)",
    11: "Camp Funds (Fundos do Acampamento)",
    12: "Camp Food (Comida do Acampamento)",
    13: "Camp Timber (Madeira do Acampamento)",
    14: "Camp Stone (Pedra do Acampamento)",
    15: "Camp Weapons (Armas do Acampamento)",
}
# ==============================================================================


def get_candidate_save_dirs() -> List[str]:
    """Retorna uma lista de possíveis diretórios de save para Linux e Windows."""
    dirs: List[str] = []

    # Windows: %LOCALAPPDATA%\Pearl Abyss\CD\save
    local_appdata = os.environ.get("LOCALAPPDATA")
    if local_appdata:
        win_base = os.path.join(local_appdata, "Pearl Abyss", "CD", "save")
        if os.path.exists(win_base):
            for entry in os.listdir(win_base):
                sub = os.path.join(win_base, entry)
                if os.path.isdir(sub):
                    dirs.append(sub)

    # Linux (Steam/Proton): ~/.local/share/Steam/steamapps/compatdata/3321460/pfx/drive_c/users/steamuser/AppData/Local/Pearl Abyss/CD/save
    linux_proton_base = os.path.expanduser(
        "~/.local/share/Steam/steamapps/compatdata/3321460/pfx/drive_c/users/steamuser/AppData/Local/Pearl Abyss/CD/save"
    )
    if os.path.exists(linux_proton_base):
        for entry in os.listdir(linux_proton_base):
            sub = os.path.join(linux_proton_base, entry)
            if os.path.isdir(sub):
                dirs.append(sub)

    # Pasta atual do projeto (fallback para testes locais)
    dirs.append(os.getcwd())

    # Retorna lista sem duplicatas preservando a ordem
    seen = set()
    res = []
    for d in dirs:
        if d not in seen:
            seen.add(d)
            res.append(d)
    return res


def get_slot_label(slot_id: str) -> str:
    """Retorna um nome amigável para o slot."""
    slot_map = {
        "slot0": "Slot 1 (Principal/Manual)",
        "slot1": "Slot 2 (Manual)",
        "slot2": "Slot 3 (Manual)",
        "slot100": "Save Rápido / Auto (Slot 100)",
        "slot101": "Slot 101",
        "slot102": "Slot 102",
    }
    return slot_map.get(slot_id, f"Slot {slot_id}")


def detect_save_slots(base_dir: Optional[str] = None) -> List[SlotInfo]:
    """Detecta todos os slots de save e ordena pelo mais recente."""
    slots: List[SlotInfo] = []
    candidate_dirs = [base_dir] if base_dir else get_candidate_save_dirs()

    for target_dir in candidate_dirs:
        if not target_dir or not os.path.exists(target_dir):
            continue

        for entry in os.listdir(target_dir):
            slot_dir = os.path.join(target_dir, entry)
            if os.path.isdir(slot_dir):
                save_path = os.path.join(slot_dir, "save.save")
                if os.path.exists(save_path):
                    mtime = os.path.getmtime(save_path)
                    mtime_str = datetime.fromtimestamp(mtime).strftime("%d/%m/%Y às %H:%M:%S")
                    size = os.path.getsize(save_path)
                    slots.append(
                        SlotInfo(
                            slot_id=entry,
                            save_path=save_path,
                            mtime=mtime,
                            mtime_str=mtime_str,
                            size_bytes=size,
                        )
                    )

    # Ordena pelo arquivo mais recente primeiro
    slots.sort(key=lambda s: s.mtime, reverse=True)
    return slots


def cleanup_steam_autocloud(save_path: str) -> bool:
    """Remove o arquivo steam_autocloud.vdf para evitar travamento da Steam."""
    cleaned = False
    if not save_path:
        return False

    parent = os.path.dirname(save_path)
    grandparent = os.path.dirname(parent)

    possible_paths = [
        os.path.join(parent, "steam_autocloud.vdf"),
        os.path.join(grandparent, "steam_autocloud.vdf"),
    ]

    for vdf_path in set(possible_paths):
        if os.path.exists(vdf_path):
            try:
                os.remove(vdf_path)
                cleaned = True
            except Exception as e:
                print(f"⚠️ Não foi possível remover '{vdf_path}': {e}")

    return cleaned


class SaveEditorCLI:
    def __init__(self):
        self.save_file: Optional[SaveFile] = None
        self.items: List[Item] = []
        self.modified: bool = False
        self.current_slot_id: str = ""
        self.current_mtime_str: str = ""
        self.item_db = load_item_database()

    def choose_language(self):
        """Exibe menu de seleção de idioma."""
        print("=" * 70)
        print(t("CHOOSE_LANGUAGE"))
        print("=" * 70)
        print(f"  [1] {t('LANG_PT')}")
        print(f"  [2] {t('LANG_EN')}")
        print("-" * 70)
        
        choice = input("\n> ").strip()
        if choice == "1":
            set_language("pt")
        elif choice == "2":
            set_language("en")
        else:
            print(t("INVALID_LANG"))
            set_language("pt")

    def print_banner(self):
        print("=" * 70)
        print(f"     {t('APP_TITLE')}")
        print("=" * 70)

    def load_save(self, path: str, slot_name: str = "", mtime_str: str = "") -> bool:
        """Carrega e descriptografa um arquivo de save."""
        path = os.path.expanduser(path.strip().strip("'\""))
        if not os.path.exists(path):
            print(f"{t('ERR_FILE_NOT_FOUND').format(path=path)}")
            return False

        try:
            print(f"\n{t('DECRYPTING').format(file=os.path.basename(path))}")
            self.save_file = load_save_file(path)
            print(f"{t('SCANNING')}")
            self.items = scan_items(self.save_file.blob, self.item_db)
            self.modified = False
            self.current_slot_id = slot_name if slot_name else os.path.basename(os.path.dirname(path))

            if not mtime_str:
                mtime = os.path.getmtime(path)
                mtime_str = datetime.fromtimestamp(mtime).strftime("%d/%m/%Y às %H:%M:%S")
            self.current_mtime_str = mtime_str

            hmac_status = t("HMAC_VALID") if self.save_file.hmac_valid else t("HMAC_INVALID")
            print(f"{t('SAVE_LOADED')}")
            print(f"{t('SAVE_SLOT').format(slot=get_slot_label(self.current_slot_id))}")
            print(f"{t('SAVE_TIME').format(time=self.current_mtime_str)}")
            print(f"{hmac_status}")
            print(f"{t('ITEMS_COUNT').format(count=len(self.items))}")
            return True
        except Exception as e:
            print(f"{t('ERR_LOAD_FAILED').format(error=e)}")
            self.save_file = None
            self.items = []
            return False

    def select_save_dialog(self):
        """Lista os slots detectados com data e hora exata."""
        slots = detect_save_slots()
        print(f"\n{t('SLOTS_FOUND')}")
        print("-" * 70)
        if slots:
            for idx, s in enumerate(slots, 1):
                rec = t("SLOT_RECENT") if idx == 1 else ""
                label = get_slot_label(s.slot_id)
                print(f"{t('SLOT_FORMAT').format(idx=idx, label=label, time=s.mtime_str, recent=rec)}")
            print(f"{t('OPT_MANUAL')}")
            print(f"{t('OPT_CANCEL')}")
            print("-" * 70)

            choice = input(f"\n{t('CHOOSE_SLOT').format(count=len(slots))}").strip().lower()
            if choice == "0":
                return
            if choice.isdigit() and 1 <= int(choice) <= len(slots):
                selected = slots[int(choice) - 1]
                self.load_save(selected.save_path, selected.slot_id, selected.mtime_str)
                return

        path = input(f"{t('ENTER_PATH')}").strip()
        if path:
            self.load_save(path)

    def edit_money_and_camp_funds(self):
        """Menu rápido e direto para visualizar e alterar Dinheiro e Fundos do Acampamento."""
        if not self.save_file:
            print(t("NO_SAVE_LOADED"))
            return

        currencies = [it for it in self.items if it.item_key in CURRENCY_KEYS]
        if not currencies:
            print(t("NO_CURRENCIES"))
            return

        print(f"\n{t('MONEY_HEADER')}")
        print("-" * 70)
        for idx, it in enumerate(currencies, 1):
            custom_name = CURRENCY_KEYS.get(it.item_key, it.name)
            print(f"{t('MONEY_FORMAT').format(idx=idx, name=custom_name, count=it.stack_count)}")
        print("-" * 70)

        choice = input(f"\n{t('CHOOSE_CURRENCY').format(count=len(currencies))}").strip()
        if not choice.isdigit() or int(choice) == 0:
            return

        idx = int(choice)
        if not (1 <= idx <= len(currencies)):
            print(t("ERR_INVALID_OPTION"))
            return

        target_item = currencies[idx - 1]
        custom_name = CURRENCY_KEYS.get(target_item.item_key, target_item.name)
        print(f"\n{t('ALTERING').format(name=custom_name)}")
        print(f"{t('CURRENT_AMOUNT').format(count=target_item.stack_count)}")

        new_val_str = input(f"{t('ENTER_NEW_VALUE')}").strip()
        if not new_val_str.isdigit() or int(new_val_str) < 1:
            print(t("ERR_INVALID_VALUE"))
            return

        new_val = int(new_val_str)
        old_val = set_item_stack(self.save_file.blob, target_item, new_val)
        self.modified = True
        print(f"{t('SUCCESS_CHANGE').format(name=custom_name, old=old_val, new=new_val)}")

    def list_inventory_interactive(self):
        """Lista o inventário completo e permite selecionar qualquer item para editar."""
        if not self.save_file:
            print(t("NO_SAVE_LOADED"))
            return

        if not self.items:
            print(t("NO_ITEMS"))
            return

        page_size = 25
        current_page = 0
        total_pages = (len(self.items) + page_size - 1) // page_size

        while True:
            start_idx = current_page * page_size
            end_idx = min(start_idx + page_size, len(self.items))
            page_items = self.items[start_idx:end_idx]

            print(f"\n{t('INVENTORY_HEADER').format(page=current_page + 1, total=total_pages, start=start_idx + 1, end=end_idx)}")
            print("-" * 70)
            for i, it in enumerate(page_items, start=start_idx + 1):
                print(f"{t('ITEM_FORMAT').format(idx=i, item=it)}")
            print("-" * 70)
            print(f"{t('NAV_COMMANDS')}")

            cmd = input(f"\n{t('ENTER_OPTION')}").strip().lower()
            if cmd == "0":
                break
            elif cmd == "n":
                if current_page < total_pages - 1:
                    current_page += 1
                else:
                    print(t("LAST_PAGE"))
            elif cmd == "p":
                if current_page > 0:
                    current_page -= 1
                else:
                    print(t("FIRST_PAGE"))
            elif cmd.isdigit() and 1 <= int(cmd) <= len(self.items):
                selected_item = self.items[int(cmd) - 1]
                self.item_action_menu(selected_item)
            else:
                print(t("ERR_INVALID_OPTION"))

    def search_inventory_menu(self):
        """Pesquisa itens no inventário carregado."""
        if not self.save_file:
            print(t("NO_SAVE_LOADED"))
            return

        query = input(f"\n{t('SEARCH_INVENTORY')}").strip()
        if not query:
            return

        results = search_items(self.items, query)
        if not results:
            print(f"{t('NO_RESULTS').format(query=query)}")
            return

        print(f"\n{t('SEARCH_RESULTS').format(count=len(results))}")
        print("-" * 70)
        for idx, it in enumerate(results, 1):
            print(f"  [{idx:2}] {it}")
        print("-" * 70)

        choice = input(f"\n{t('CHOOSE_ITEM')}").strip()
        if not choice.isdigit() or int(choice) == 0:
            return

        idx = int(choice)
        if not (1 <= idx <= len(results)):
            print(t("ERR_INVALID_OPTION"))
            return

        selected_item = results[idx - 1]
        self.item_action_menu(selected_item)

    def item_action_menu(self, item: Item):
        """Menu de ações para um item específico."""
        while True:
            enchant_str = f" (+{item.enchant_level})" if item.enchant_level > 0 else " (+0)"
            print("\n" + "=" * 60)
            print(f"{t('EDITING_ITEM').format(name=item.name)}")
            print(f"{t('ITEM_CATEGORY').format(category=item.category)}")
            print(f"{t('ITEM_SLOT').format(slot=item.slot_no)}")
            print(f"{t('ITEM_STACK').format(count=item.stack_count)}")
            print(f"{t('ITEM_PRICE').format(price=item.average_price)}")
            print(f"{t('ITEM_ENCHANT').format(enchant=enchant_str)}")
            print(f"{t('ITEM_DURABILITY').format(durability=item.endurance)}")
            print(f"{t('ITEM_SHARPNESS').format(sharpness=item.sharpness)}")
            print(f"{t('ITEM_KEY').format(key=item.item_key)}")
            print("=" * 60)
            print(f"{t('ACTION_1')}")
            print(f"{t('ACTION_2')}")
            print(f"{t('ACTION_3')}")
            print(f"{t('ACTION_4')}")
            print(f"{t('ACTION_0')}")

            sub_choice = input(f"\n{t('CHOOSE_ACTION')}").strip()

            if sub_choice == "1":
                if item.max_stack == 1:
                    print(f"\n{t('STACK_WARNING')}")
                    print(f"{t('STACK_OVERLAP')}")

                new_val_str = input(f"{t('ENTER_NEW_STACK').format(count=item.stack_count)}").strip()
                if not new_val_str.isdigit() or int(new_val_str) < 1:
                    print(t("ERR_INVALID_STACK"))
                    continue

                new_val = int(new_val_str)
                if item.max_stack == 1 and new_val > 1:
                    conf = input(f"{t('CONFIRM_STACK')}").strip().lower()
                    if conf != "s" and conf != "y":
                        continue

                old_val = set_item_stack(self.save_file.blob, item, new_val)
                self.modified = True
                print(f"{t('SUCCESS_STACK').format(old=old_val, new=new_val)}")

            elif sub_choice == "2":
                new_enc_str = input(f"{t('ENTER_ENCHANT')}").strip()
                if not new_enc_str.isdigit():
                    print(t("ERR_INVALID_ENCHANT"))
                    continue
                new_enc = int(new_enc_str)
                old_enc = set_item_enchant(self.save_file.blob, item, new_enc)
                self.modified = True
                print(f"{t('SUCCESS_ENCHANT').format(old=old_enc, new=new_enc)}")

            elif sub_choice == "3":
                repair_item(self.save_file.blob, item)
                self.modified = True
                print(f"{t('SUCCESS_REPAIR').format(durability=item.endurance, sharpness=item.sharpness)}")

            elif sub_choice == "4":
                self.swap_item_workflow(item)

            elif sub_choice == "0":
                break
            else:
                print(t("ERR_INVALID_OPTION"))

    def swap_item_workflow(self, item: Item):
        """Fluxo de busca no banco global de itens e substituição."""
        query = input(f"\n{t('SEARCH_NEW_ITEM')}").strip()
        if not query:
            return

        matches = search_database_items(query, self.item_db, limit=20)
        if not matches:
            print(f"{t('NO_DB_RESULTS').format(query=query)}")
            return

        print(f"\n{t('DB_RESULTS').format(count=len(matches))}")
        print("-" * 70)
        for idx, m in enumerate(matches, 1):
            cat = m.get("category", "Geral")
            print(f"{t('DB_ITEM_FORMAT').format(idx=idx, name=m.get('name'), key=m.get('itemKey'), cat=cat, max=m.get('maxStack'))}")
        print("-" * 70)

        sel = input(f"\n{t('CHOOSE_NEW_ITEM')}").strip()
        if not sel.isdigit() or int(sel) == 0:
            return

        sel_idx = int(sel)
        if not (1 <= sel_idx <= len(matches)):
            print(t("ERR_INVALID_OPTION"))
            return

        new_meta = matches[sel_idx - 1]
        confirm = input(f"{t('CONFIRM_SWAP').format(old=item.name, new=new_meta.get('name'))}").strip().lower()
        if confirm == "" or confirm == "s" or confirm == "y":
            old_name = item.name
            swap_item_key(self.save_file.blob, item, new_meta.get("itemKey"), new_meta)
            self.modified = True
            print(f"{t('SUCCESS_SWAP').format(old=old_name, new=item.name)}")

    def global_database_search(self):
        """Consulta rápida ao banco de dados global de itens do jogo."""
        query = input(f"\n{t('GLOBAL_SEARCH')}").strip()
        if not query:
            return

        matches = search_database_items(query, self.item_db, limit=30)
        if not matches:
            print(f"{t('NO_RESULTS').format(query=query)}")
            return

        print(f"\n{t('GLOBAL_RESULTS').format(count=len(matches))}")
        print("-" * 70)
        for idx, m in enumerate(matches, 1):
            cat = m.get("category", "Geral")
            internal = m.get("internalName", "")
            print(f"{t('GLOBAL_ITEM_FORMAT').format(idx=idx, name=m.get('name'), key=m.get('itemKey'), cat=cat, internal=internal)}")
        print("-" * 70)
        input(f"{t('PRESS_ENTER')}")

    def save_changes(self):
        """Salva as modificações no arquivo, cria backup e remove steam_autocloud.vdf."""
        if not self.save_file:
            print(t("NO_SAVE_LOADED"))
            return

        if not self.modified:
            print(t("NO_CHANGES"))
            confirm = input(f"{t('CONFIRM_SAVE')}").strip().lower()
            if confirm != "s" and confirm != "y":
                return

        try:
            print(f"\n{t('CREATING_BACKUP')}")
            backup_path = create_backup(self.save_file.file_path)
            print(f"{t('BACKUP_SAVED').format(path=backup_path)}")

            print(f"{t('RECOMPACTING')}")
            save_save_file(
                self.save_file.file_path,
                self.save_file.blob,
                self.save_file.raw_header,
                self.save_file.version,
            )
            print(f"{t('SAVE_SUCCESS')}")

            print(f"{t('CHECKING_AUTOCLOUD')}")
            if cleanup_steam_autocloud(self.save_file.file_path):
                print(f"{t('AUTOCLOUD_REMOVED')}")
            else:
                print(f"{t('AUTOCLOUD_NOT_FOUND')}")

            self.modified = False
            # Atualiza o timestamp exibido
            mtime = os.path.getmtime(self.save_file.file_path)
            self.current_mtime_str = datetime.fromtimestamp(mtime).strftime("%d/%m/%Y às %H:%M:%S")
            print(f"{t('ALL_SAVED')}")
        except Exception as e:
            print(f"{t('ERR_SAVE_FAILED').format(error=e)}")

    def restore_backup_dialog(self):
        """Lista os backups disponíveis para o slot atual e permite restaurar com 1 clique."""
        if not self.save_file:
            print(t("NO_SAVE_LOADED"))
            return

        save_path = self.save_file.file_path
        backups = list_backups(save_path)
        if not backups:
            print(t("NO_BACKUPS"))
            return

        print(f"\n{t('BACKUP_HEADER')}")
        print("-" * 70)
        for idx, b in enumerate(backups, 1):
            rec = t("BACKUP_RECENT") if idx == 1 else ""
            size_kb = b["size_bytes"] / 1024
            print(f"{t('BACKUP_FORMAT').format(idx=idx, time=b['mtime_str'], size=size_kb, recent=rec)}")
            print(f"{t('BACKUP_FILE').format(filename=b['filename'])}")
        print("-" * 70)

        choice = input(f"\n{t('CHOOSE_BACKUP').format(count=len(backups))}").strip()
        if not choice.isdigit() or int(choice) == 0:
            return

        idx = int(choice)
        if not (1 <= idx <= len(backups)):
            print(t("ERR_INVALID_OPTION"))
            return

        selected_backup = backups[idx - 1]
        confirm = input(f"{t('CONFIRM_RESTORE').format(time=selected_backup['mtime_str'])}").strip().lower()
        if confirm != "s" and confirm != "y":
            print(t("RESTORE_CANCELLED"))
            return

        try:
            restore_backup(selected_backup["path"], save_path)
            print(f"{t('RESTORE_SUCCESS').format(time=selected_backup['mtime_str'])}")
            print(f"{t('RELOADING')}")
            self.load_save(save_path, self.current_slot_id)
        except Exception as e:
            print(f"{t('ERR_RESTORE_FAILED').format(error=e)}")

    def run(self):
        """Loop principal do editor."""
        # Seleção de idioma ANTES de tudo
        self.choose_language()
        
        self.print_banner()

        # Detecção automática na inicialização com Data e Hora
        slots = detect_save_slots()
        if slots:
            most_recent = slots[0]
            label = get_slot_label(most_recent.slot_id)
            print(f"\n{t('SLOT_DETECTED')}")
            print(f"{t('SLOT_INFO').format(label=label, time=most_recent.mtime_str)}")
            auto_load = input(f"\n{t('LOAD_SLOT_NOW')}").strip().lower()
            if auto_load == "" or auto_load == "s" or auto_load == "y":
                self.load_save(most_recent.save_path, most_recent.slot_id, most_recent.mtime_str)
            elif auto_load == "outros" or auto_load == "o":
                self.select_save_dialog()

        while True:
            print("\n" + "=" * 55)
            if self.save_file:
                status_mod = t("MENU_UNSAVED") if self.modified else ""
                print(f"{t('MENU_HEADER').format(slot=get_slot_label(self.current_slot_id), status=status_mod)}")
                print(f"{t('MENU_SAVE_TIME').format(time=self.current_mtime_str)}")
            else:
                print(f"{t('MENU_NO_SAVE')}")
            print("=" * 55)

            print(f"{t('OPT_1')}")
            print(f"{t('OPT_2')}")
            print(f"{t('OPT_3')}")
            print(f"{t('OPT_4')}")
            print(f"{t('OPT_5')}")
            print(f"{t('OPT_6')}")
            print(f"{t('OPT_7')}")
            print(f"{t('OPT_8')}")
            print(f"{t('OPT_0')}")

            choice = input(f"\n{t('CHOOSE_OPTION')}").strip()

            if choice == "1":
                self.select_save_dialog()
            elif choice == "2":
                self.edit_money_and_camp_funds()
            elif choice == "3":
                self.list_inventory_interactive()
            elif choice == "4":
                self.search_inventory_menu()
            elif choice == "5":
                self.global_database_search()
            elif choice == "6":
                self.save_changes()
            elif choice == "7":
                self.restore_backup_dialog()
            elif choice == "8":
                save_path = self.save_file.file_path if self.save_file else STEAM_DEFAULT_SAVE_DIR
                if cleanup_steam_autocloud(save_path):
                    print(f"{t('AUTOCLOUD_MANUAL_SUCCESS')}")
                else:
                    print(f"{t('AUTOCLOUD_MANUAL_NOT_FOUND')}")
            elif choice == "0":
                if self.modified:
                    exit_conf = input(f"{t('UNSAVED_CHANGES')}").strip().lower()
                    if exit_conf != "s" and exit_conf != "y":
                        continue
                print(f"{t('GOODBYE')}")
                break
            else:
                print(t("ERR_INVALID_OPTION"))

if __name__ == "__main__":
    app = SaveEditorCLI()
    app.run()
