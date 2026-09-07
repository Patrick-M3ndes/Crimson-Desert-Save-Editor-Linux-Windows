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

    def print_banner(self):
        print("=" * 70)
        print("     ⚔️  CRIMSON DESERT - ITEM SAVE EDITOR (Enhanced Edition) ⚔️")
        print("=" * 70)

    def load_save(self, path: str, slot_name: str = "", mtime_str: str = "") -> bool:
        """Carrega e descriptografa um arquivo de save."""
        path = os.path.expanduser(path.strip().strip("'\""))
        if not os.path.exists(path):
            print(f"❌ Erro: O arquivo não foi encontrado: {path}")
            return False

        try:
            print(f"\n⏳ Descriptografando e lendo save ({os.path.basename(path)})...")
            self.save_file = load_save_file(path)
            print(f"🔍 Escaneando itens do inventário...")
            self.items = scan_items(self.save_file.blob, self.item_db)
            self.modified = False
            self.current_slot_id = slot_name if slot_name else os.path.basename(os.path.dirname(path))

            if not mtime_str:
                mtime = os.path.getmtime(path)
                mtime_str = datetime.fromtimestamp(mtime).strftime("%d/%m/%Y às %H:%M:%S")
            self.current_mtime_str = mtime_str

            hmac_status = "✅ Válido" if self.save_file.hmac_valid else "⚠️ Inconsistente (modificado previamente)"
            print(f"✅ Save carregado com sucesso!")
            print(f"   • Slot: {get_slot_label(self.current_slot_id)}")
            print(f"   • Data/Horário do Save: {self.current_mtime_str}")
            print(f"   • Integridade HMAC: {hmac_status}")
            print(f"   • Total de itens no inventário: {len(self.items)}")
            return True
        except Exception as e:
            print(f"❌ Falha ao carregar o save: {e}")
            self.save_file = None
            self.items = []
            return False

    def select_save_dialog(self):
        """Lista os slots detectados com data e hora exata."""
        slots = detect_save_slots()
        print("\n📂 Slots de Save Encontrados no seu Jogo:")
        print("-" * 70)
        if slots:
            for idx, s in enumerate(slots, 1):
                rec = " ⭐ [Mais Recente]" if idx == 1 else ""
                label = get_slot_label(s.slot_id)
                print(f"  [{idx}] {label:<28} | Horário: {s.mtime_str}{rec}")
            print(f"  [D] Digitar outro caminho manualmente")
            print(f"  [0] Cancelar / Voltar")
            print("-" * 70)

            choice = input(f"\nEscolha o slot desejado (1 a {len(slots)}): ").strip().lower()
            if choice == "0":
                return
            if choice.isdigit() and 1 <= int(choice) <= len(slots):
                selected = slots[int(choice) - 1]
                self.load_save(selected.save_path, selected.slot_id, selected.mtime_str)
                return

        path = input("Cole ou digite o caminho completo do arquivo save.save: ").strip()
        if path:
            self.load_save(path)

    def edit_money_and_camp_funds(self):
        """Menu rápido e direto para visualizar e alterar Dinheiro e Fundos do Acampamento."""
        if not self.save_file:
            print("⚠️ Nenhum save carregado. Selecione um slot primeiro.")
            return

        currencies = [it for it in self.items if it.item_key in CURRENCY_KEYS]
        if not currencies:
            print("⚠️ Nenhum registro de moeda/dinheiro encontrado neste save.")
            return

        print("\n💰 DINHEIRO E RECURSOS DO ACAMPAMENTO:")
        print("-" * 70)
        for idx, it in enumerate(currencies, 1):
            custom_name = CURRENCY_KEYS.get(it.item_key, it.name)
            print(f"  [{idx}] {custom_name:<38} | Atual: {it.stack_count:,}")
        print("-" * 70)

        choice = input(f"\nEscolha qual deseja alterar (1 a {len(currencies)} ou 0 para voltar): ").strip()
        if not choice.isdigit() or int(choice) == 0:
            return

        idx = int(choice)
        if not (1 <= idx <= len(currencies)):
            print("❌ Opção inválida.")
            return

        target_item = currencies[idx - 1]
        custom_name = CURRENCY_KEYS.get(target_item.item_key, target_item.name)
        print(f"\nAlterando: {custom_name}")
        print(f"Quantidade Atual: {target_item.stack_count:,}")

        new_val_str = input("Digite o novo valor desejado (ex: 50000000 para 50 milhões): ").strip()
        if not new_val_str.isdigit() or int(new_val_str) < 1:
            print("❌ Valor inválido.")
            return

        new_val = int(new_val_str)
        old_val = set_item_stack(self.save_file.blob, target_item, new_val)
        self.modified = True
        print(f"✅ {custom_name} alterado de {old_val:,} para {new_val:,}!")

    def list_inventory_interactive(self):
        """Lista o inventário completo e permite selecionar qualquer item para editar."""
        if not self.save_file:
            print("⚠️ Nenhum save carregado. Selecione um slot primeiro.")
            return

        if not self.items:
            print("Nenhum item encontrado no inventário.")
            return

        page_size = 25
        current_page = 0
        total_pages = (len(self.items) + page_size - 1) // page_size

        while True:
            start_idx = current_page * page_size
            end_idx = min(start_idx + page_size, len(self.items))
            page_items = self.items[start_idx:end_idx]

            print(f"\n📦 Inventário Completo (Página {current_page + 1}/{total_pages} - Itens {start_idx + 1} a {end_idx}):")
            print("-" * 70)
            for i, it in enumerate(page_items, start=start_idx + 1):
                print(f"  [{i:3}] {it}")
            print("-" * 70)
            print("Comandos: [N] Próxima pág | [P] Pág anterior | [Número do Item] Editar | [0] Voltar")

            cmd = input("\nDigite a opção desejada: ").strip().lower()
            if cmd == "0":
                break
            elif cmd == "n":
                if current_page < total_pages - 1:
                    current_page += 1
                else:
                    print("⚠️ Já está na última página.")
            elif cmd == "p":
                if current_page > 0:
                    current_page -= 1
                else:
                    print("⚠️ Já está na primeira página.")
            elif cmd.isdigit() and 1 <= int(cmd) <= len(self.items):
                selected_item = self.items[int(cmd) - 1]
                self.item_action_menu(selected_item)
            else:
                print("❌ Opção inválida.")

    def search_inventory_menu(self):
        """Pesquisa itens no inventário carregado."""
        if not self.save_file:
            print("⚠️ Nenhum save carregado. Selecione um slot primeiro.")
            return

        query = input("\n🔎 Digite o nome ou ID do item no inventário (ex: 'Abyss Artifact'): ").strip()
        if not query:
            return

        results = search_items(self.items, query)
        if not results:
            print(f"❌ Nenhum item encontrado com o termo '{query}'.")
            return

        print(f"\n📦 Resultados no Inventário ({len(results)} encontrados):")
        print("-" * 70)
        for idx, it in enumerate(results, 1):
            print(f"  [{idx:2}] {it}")
        print("-" * 70)

        choice = input("\nDigite o número do item que deseja editar (ou 0 para cancelar): ").strip()
        if not choice.isdigit() or int(choice) == 0:
            return

        idx = int(choice)
        if not (1 <= idx <= len(results)):
            print("❌ Opção inválida.")
            return

        selected_item = results[idx - 1]
        self.item_action_menu(selected_item)

    def item_action_menu(self, item: Item):
        """Menu de ações para um item específico."""
        while True:
            enchant_str = f" (+{item.enchant_level})" if item.enchant_level > 0 else " (+0)"
            print("\n" + "=" * 60)
            print(f"  🎯 EDITANDO ITEM: {item.name}")
            print(f"     • Categoria: {item.category}")
            print(f"     • Slot no Inventário: {item.slot_no}")
            print(f"     • Quantidade Atual: {item.stack_count:,}")
            print(f"     • Preço Médio / Dinheiro (Average Price): {item.average_price:,}")
            print(f"     • Nível de Encanto: {enchant_str}")
            print(f"     • Durabilidade (Endurance): {item.endurance}")
            print(f"     • Afiação (Sharpness): {item.sharpness}")
            print(f"     • ID Interno (Key): {item.item_key}")
            print("=" * 60)
            print("  1. Alterar Quantidade (Stack Count)")
            print("  2. Definir Nível de Encantamento (+0 até +20)")
            print("  3. 🛠️ Reparar Equipamento (Durabilidade e Afiação Máximas)")
            print("  4. Substituir / Trocar por outro Item do Banco de Dados")
            print("  0. Concluir / Voltar")

            sub_choice = input("\nEscolha uma opção: ").strip()

            if sub_choice == "1":
                if item.max_stack == 1:
                    print("\n⚠️ AVISO: Este item é um equipamento (Stack padrão = 1).")
                    print("   Colocar quantidade > 1 pode causar sobreposição visual no jogo.")

                new_val_str = input(f"Digite a nova quantidade (atual: {item.stack_count:,}): ").strip()
                if not new_val_str.isdigit() or int(new_val_str) < 1:
                    print("❌ Quantidade inválida.")
                    continue

                new_val = int(new_val_str)
                if item.max_stack == 1 and new_val > 1:
                    conf = input("Deseja realmente definir quantidade > 1 para este equipamento? (s/N): ").strip().lower()
                    if conf != "s":
                        continue

                old_val = set_item_stack(self.save_file.blob, item, new_val)
                self.modified = True
                print(f"✅ Quantidade alterada de {old_val:,} para {new_val:,}!")

            elif sub_choice == "2":
                new_enc_str = input(f"Digite o nível de encanto (ex: 0 para normal, 10 para +10, 20 para +20): ").strip()
                if not new_enc_str.isdigit():
                    print("❌ Valor inválido.")
                    continue
                new_enc = int(new_enc_str)
                old_enc = set_item_enchant(self.save_file.blob, item, new_enc)
                self.modified = True
                print(f"✅ Encantamento alterado de +{old_enc} para +{new_enc}!")

            elif sub_choice == "3":
                repair_item(self.save_file.blob, item)
                self.modified = True
                print(f"🛠️ Equipamento reparado com sucesso! Durabilidade: {item.endurance}, Afiação: {item.sharpness}")

            elif sub_choice == "4":
                self.swap_item_workflow(item)

            elif sub_choice == "0":
                break
            else:
                print("❌ Opção inválida.")

    def swap_item_workflow(self, item: Item):
        """Fluxo de busca no banco global de itens e substituição."""
        query = input("\n🔎 Digite o nome do novo item para buscar no banco global (6.200+ itens): ").strip()
        if not query:
            return

        matches = search_database_items(query, self.item_db, limit=20)
        if not matches:
            print(f"❌ Nenhum item encontrado no banco com o termo '{query}'.")
            return

        print(f"\n📚 Itens Encontrados no Banco Global ({len(matches)}):")
        print("-" * 70)
        for idx, m in enumerate(matches, 1):
            cat = m.get("category", "Geral")
            print(f"  [{idx:2}] {m.get('name')} (ID: {m.get('itemKey')}) [{cat}] - Stack Máx: {m.get('maxStack')}")
        print("-" * 70)

        sel = input("\nDigite o número do item desejado para substituir o atual (ou 0 para cancelar): ").strip()
        if not sel.isdigit() or int(sel) == 0:
            return

        sel_idx = int(sel)
        if not (1 <= sel_idx <= len(matches)):
            print("❌ Opção inválida.")
            return

        new_meta = matches[sel_idx - 1]
        confirm = input(f"Confirma trocar '{item.name}' por '{new_meta.get('name')}'? (S/n): ").strip().lower()
        if confirm == "" or confirm == "s":
            old_name = item.name
            swap_item_key(self.save_file.blob, item, new_meta.get("itemKey"), new_meta)
            self.modified = True
            print(f"✅ Item '{old_name}' substituído com sucesso por '{item.name}'!")

    def global_database_search(self):
        """Consulta rápida ao banco de dados global de itens do jogo."""
        query = input("\n🔎 Pesquisar no Banco de Dados Global de Itens (ex: 'Sword', 'Plate', 'Artifact'): ").strip()
        if not query:
            return

        matches = search_database_items(query, self.item_db, limit=30)
        if not matches:
            print(f"❌ Nenhum item encontrado com o termo '{query}'.")
            return

        print(f"\n📚 Resultados da Busca Global ({len(matches)} itens):")
        print("-" * 70)
        for idx, m in enumerate(matches, 1):
            cat = m.get("category", "Geral")
            internal = m.get("internalName", "")
            print(f"  [{idx:2}] {m.get('name')} (ID: {m.get('itemKey')}) [{cat}] | Interno: {internal}")
        print("-" * 70)
        input("Pressione Enter para voltar ao menu...")

    def save_changes(self):
        """Salva as modificações no arquivo, cria backup e remove steam_autocloud.vdf."""
        if not self.save_file:
            print("⚠️ Nenhum save carregado.")
            return

        if not self.modified:
            print("ℹ️ Nenhuma alteração foi feita neste save.")
            confirm = input("Deseja regravar mesmo assim? (s/N): ").strip().lower()
            if confirm != "s":
                return

        try:
            print("\n💾 1. Criando cópia de segurança automática (.bak)...")
            backup_path = create_backup(self.save_file.file_path)
            print(f"   🛡️ Backup salvo em: {backup_path}")

            print("⏳ 2. Recompactando em LZ4 e recriptografando ChaCha20...")
            save_save_file(
                self.save_file.file_path,
                self.save_file.blob,
                self.save_file.raw_header,
                self.save_file.version,
            )
            print("   ✅ Save gravado com integridade HMAC 100% válida!")

            print("🧹 3. Verificando 'steam_autocloud.vdf'...")
            if cleanup_steam_autocloud(self.save_file.file_path):
                print("   ✨ 'steam_autocloud.vdf' removido com sucesso! O jogo iniciará sem travar no menu.")
            else:
                print("   ℹ️ 'steam_autocloud.vdf' já não estava presente.")

            self.modified = False
            # Atualiza o timestamp exibido
            mtime = os.path.getmtime(self.save_file.file_path)
            self.current_mtime_str = datetime.fromtimestamp(mtime).strftime("%d/%m/%Y às %H:%M:%S")
            print("\n🎉 Todas as alterações foram salvas com sucesso! Pronto para jogar.")
        except Exception as e:
            print(f"❌ Erro ao salvar arquivo: {e}")

    def restore_backup_dialog(self):
        """Lista os backups disponíveis para o slot atual e permite restaurar com 1 clique."""
        if not self.save_file:
            print("⚠️ Nenhum save carregado. Selecione um slot primeiro.")
            return

        save_path = self.save_file.file_path
        backups = list_backups(save_path)
        if not backups:
            print(f"❌ Nenhum backup encontrado na pasta 'backups' deste slot.")
            return

        print("\n🛡️ BACKUPS DISPONÍVEIS PARA RESTAURAÇÃO:")
        print("-" * 70)
        for idx, b in enumerate(backups, 1):
            rec = " ⭐ [Mais Recente]" if idx == 1 else ""
            size_kb = b["size_bytes"] / 1024
            print(f"  [{idx:2}] {b['mtime_str']} ({size_kb:.1f} KB){rec}")
            print(f"       Arquivo: {b['filename']}")
        print("-" * 70)

        choice = input(f"\nEscolha o backup para restaurar (1 a {len(backups)} ou 0 para cancelar): ").strip()
        if not choice.isdigit() or int(choice) == 0:
            return

        idx = int(choice)
        if not (1 <= idx <= len(backups)):
            print("❌ Opção inválida.")
            return

        selected_backup = backups[idx - 1]
        confirm = input(f"⚠️ ATENÇÃO: Confirma restaurar o backup de '{selected_backup['mtime_str']}'? O save atual será substituído. (s/N): ").strip().lower()
        if confirm != "s":
            print("Restauração cancelada.")
            return

        try:
            restore_backup(selected_backup["path"], save_path)
            print(f"✅ Backup de {selected_backup['mtime_str']} restaurado com sucesso!")
            print("⏳ Recarregando save na memória...")
            self.load_save(save_path, self.current_slot_id)
        except Exception as e:
            print(f"❌ Erro ao restaurar backup: {e}")

    def run(self):
        """Loop principal do editor."""
        self.print_banner()

        # Detecção automática na inicialização com Data e Hora
        slots = detect_save_slots()
        if slots:
            most_recent = slots[0]
            label = get_slot_label(most_recent.slot_id)
            print(f"\n💡 Slot mais recente detectado automaticamente:")
            print(f"   👉 {label} (Gravado em: {most_recent.mtime_str})")
            auto_load = input("\nDeseja carregar este slot agora? (S/n/outros): ").strip().lower()
            if auto_load == "" or auto_load == "s":
                self.load_save(most_recent.save_path, most_recent.slot_id, most_recent.mtime_str)
            elif auto_load == "outros" or auto_load == "o":
                self.select_save_dialog()

        while True:
            print("\n" + "=" * 55)
            if self.save_file:
                status_mod = " ⚠️ [ALTERAÇÕES NÃO SALVAS]" if self.modified else ""
                print(f"📂 Slot Ativo: {get_slot_label(self.current_slot_id)}{status_mod}")
                print(f"⏰ Horário do Save: {self.current_mtime_str}")
            else:
                print("📂 Slot Ativo: Nenhum save carregado")
            print("=" * 55)

            print("1. Escolher / Trocar Slot de Save (com Data e Horário)")
            print("2. 💰 Alterar Dinheiro & Recursos do Acampamento")
            print("3. Ver Inventário Completo (Paginação e Edição)")
            print("4. Buscar Item no Inventário Atual (ex: Abyss Artifact)")
            print("5. Pesquisar Banco de Dados Global (6.200+ itens)")
            print("6. Salvar alterações no save (com backup e anti-crash)")
            print("7. 🛡️ Restaurar Backup / Recuperar Save")
            print("8. Limpar manualmente 'steam_autocloud.vdf'")
            print("0. Sair")

            choice = input("\nEscolha uma opção: ").strip()

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
                    print("✨ 'steam_autocloud.vdf' removido com sucesso!")
                else:
                    print("ℹ️ 'steam_autocloud.vdf' não encontrado (o diretório já está limpo).")
            elif choice == "0":
                if self.modified:
                    exit_conf = input("⚠️ Existem alterações não salvas. Deseja sair mesmo assim? (s/N): ").strip().lower()
                    if exit_conf != "s":
                        continue
                print("\nAté logo e bom jogo em Crimson Desert! ⚔️\n")
                break
            else:
                print("❌ Opção inválida. Tente novamente.")

if __name__ == "__main__":
    app = SaveEditorCLI()
    app.run()
