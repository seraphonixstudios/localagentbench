"""Simple bank account. Task for the agent: WRITE the tests (see task YAML)."""
from __future__ import annotations


class BankAccount:
    def __init__(self, balance: float = 0.0, overdraft_limit: float = 0.0):
        if balance < 0:
            raise ValueError("initial balance must be >= 0")
        self.balance = float(balance)
        self.overdraft_limit = float(overdraft_limit)

    def deposit(self, amount: float) -> float:
        if amount <= 0:
            raise ValueError("deposit must be > 0")
        self.balance += amount
        return self.balance

    def withdraw(self, amount: float) -> float:
        if amount <= 0:
            raise ValueError("withdraw must be > 0")
        if self.balance - amount < -self.overdraft_limit:
            raise ValueError("insufficient funds (overdraft limit exceeded)")
        self.balance -= amount
        return self.balance
