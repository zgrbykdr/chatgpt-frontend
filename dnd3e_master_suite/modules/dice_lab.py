import random
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, QTextEdit, QLabel, QSpinBox

from modules.shared.utils import parse_dice_expression
from modules.shared.dnd_rules_helpers import d20_outcome_text


class DiceLabPanel(QWidget):
    def __init__(self, data_manager, campaign) -> None:
        super().__init__()
        self.data = data_manager
        self.campaign = campaign
        self.expr = QLineEdit("1d20+0")
        self.history = QTextEdit(); self.history.setReadOnly(True)
        self.target = QSpinBox(); self.target.setRange(1, 100)
        self.target.setValue(15)
        self._build()

    def _build(self) -> None:
        layout = QVBoxLayout(self)
        row = QHBoxLayout()
        for die in [4, 6, 8, 10, 12, 20, 100]:
            b = QPushButton(f"d{die}")
            b.clicked.connect(lambda _, s=die: self.quick_roll(f"1d{s}"))
            row.addWidget(b)
        layout.addLayout(row)

        expr_row = QHBoxLayout()
        roll_btn = QPushButton("Roll Expression")
        roll_btn.clicked.connect(lambda: self.quick_roll(self.expr.text()))
        expr_row.addWidget(self.expr); expr_row.addWidget(roll_btn)
        layout.addLayout(expr_row)

        stats_btn = QPushButton("Simulate 1000 Rolls")
        stats_btn.clicked.connect(self.simulate)
        layout.addWidget(QLabel("Target Number")); layout.addWidget(self.target); layout.addWidget(stats_btn)
        layout.addWidget(self.history, 1)

    def quick_roll(self, expression: str) -> None:
        try:
            parsed = parse_dice_expression(expression)
            rolls = [random.randint(1, parsed["sides"]) for _ in range(parsed["count"])]
            total = sum(rolls) + parsed["mod"]
            tag = d20_outcome_text(rolls[0]) if parsed["sides"] == 20 and parsed["count"] == 1 else ""
            self.history.append(f"{expression} => rolls {rolls} mod {parsed['mod']} total {total} {tag}")
        except Exception as exc:
            self.history.append(f"Invalid expression '{expression}': {exc}")

    def simulate(self) -> None:
        expression = self.expr.text()
        try:
            parsed = parse_dice_expression(expression)
            totals = []
            target = self.target.value()
            success = 0
            for _ in range(1000):
                total = sum(random.randint(1, parsed["sides"]) for _ in range(parsed["count"])) + parsed["mod"]
                totals.append(total)
                if total >= target:
                    success += 1
            self.history.append(
                f"Sim {expression}: avg={sum(totals)/len(totals):.2f}, min={min(totals)}, max={max(totals)}, P(>={target})={success/10:.1f}%"
            )
        except Exception as exc:
            self.history.append(f"Simulation error: {exc}")
