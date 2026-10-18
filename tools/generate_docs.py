#!/usr/bin/env python3
"""Render method cards and catalog from the versioned registry; never uses network."""
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    ops = json.loads((ROOT / "src/edits_api/operations.json").read_text())
    detailed = [o for o in ops if "variables" in o]
    outputs = {}
    lines = ["# Методы Edits и аналитики Reels", "",
             "Каталог описывает конкретную сборку APK 448.0.0.53.84. "
             "Тип query/mutation у записей без контракта может быть определён по имени.", "",
             "[Уровни доказательств](verification.md). "
             "Наличие operation ID не гарантирует доступность на сервере.", "",
             "## Подробно разобранные методы", "",
             "| Метод | Уровень | Назначение |", "|---|---|---|"]
    for o in detailed:
        name = o["operation_name"]
        lines.append(f"| [{name}](methods/{name}.md) | `{o['evidence_level']}` | {o['description']} |")
        text = [f"# {name}", "", o["description"], "",
                f"- **client_doc_id:** `{o['client_doc_id']}`",
                f"- **schema:** `{o['schema']}`",
                f"- **kind:** `{o['kind']}`",
                f"- **evidence:** `{o['evidence_level']}`", ""]
        if o['evidence_level'] != 'live-verified':
            text += ["**На сервере не проверено.** Параметры восстановлены из APK; "
                     "ниже нет гарантии актуальной доступности этому аккаунту.", ""]
        else:
            text += ["Проверено запросом SDK 18 октября 2026 на одном аккаунте. "
                     "[Область проверки](../verification.md).", "",
                     "**Наблюдение:** " + o['live_observation'], ""]
        text += ["## Variables", "", "| Поле | Восстановленный контракт |", "|---|---|"]
        for key, value in o["variables"].items():
            escaped = str(value).replace("|", "\\|")
            text.append(f"| `{key}` | {escaped} |")
        text += ["", "## Ответ", "", o["returns"], ""]
        if name == "BaselReelDetailsQuery":
            text += ["Логические имена отличаются от фактических canonical-имён: "
                     "`1$xig_fetch_media(id:$media_id)` и `1fvalue`. "
                     "[Рабочий пример](../../examples/retention.py), [разбор](../retention.md).", ""]
        if o["kind"] == "mutation":
            text += ["## Изменение состояния", "",
                     "Операция не входит в автоматический сбор статистики. "
                     "`execute()` блокирует её без `allow_mutation=True`. "
                     "Для частично восстановленных input нет готового payload: "
                     "поля нельзя угадывать по названию метода.", ""]
        else:
            text += ["## Вызов из вашей системы", "", "```python",
                     "response = client.execute(", f'    "{name}",',
                     "    variables,  # dict с полями из таблицы; неизвестные enum сначала проверить",
                     ")", "payload = response.payload", "```", ""]
        text += ["## Источники статического разбора", "",
                 "Пути ниже относятся к исходному исследовательскому набору. "
                 "Декомпилированные исходники в этот репозиторий не включены.", ""]
        text += [f"- `{reference}`" for reference in o.get("source_references", [])]
        outputs[Path("docs/methods") / (name + ".md")] = "\n".join(text) + "\n"
    lines += ["", "## Остальные операции с именами Basel / Eddy", "",
              "У этих записей может отсутствовать контракт. Не подставляйте "
              "параметры по предположению. Полный машинный реестр: "
              "[operations.json](../src/edits_api/operations.json).", "",
              "| Operation | Kind | client_doc_id | Evidence |", "|---|---|---|---|"]
    for o in ops:
        if o["edits_related"]:
            lines.append(f"| `{o['operation_name']}` | {o['kind']} | `{o['client_doc_id']}` | {o['evidence_level']} |")
    outputs[Path("docs/methods.md")] = "\n".join(lines) + "\n"
    stale = []
    for rel, content in outputs.items():
        path = ROOT / rel
        if args.check:
            if not path.exists() or path.read_text() != content:
                stale.append(str(rel))
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content)
    if stale:
        raise SystemExit("Regenerate docs: " + ", ".join(stale))
    print(f"{'Checked' if args.check else 'Wrote'} {len(outputs)} documentation files")


if __name__ == "__main__":
    main()
