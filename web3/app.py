from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

class VulnerableBank:
    def __init__(self):
        self.userFunds = {
            "John Doe": 10, 
            "Jack Doe": 20, 
            "Mathilda Doe": 15, 
            "Attacker": 0
        }
        self.total_balance = sum(self.userFunds.values())
        self.is_reentrant = False

    def deposit(self, user, amount):
        if amount < 1:
            return "Deposit amount must be at least 1 ether."
        self.userFunds[user] += amount
        self.total_balance += amount
        return f"{amount} ETH deposited to {user}'s account."

    def withdraw(self, user, amount):
        if self.is_reentrant:
            return "Withdrawal blocked"

        if self.userFunds[user] < amount:
            return "Insufficient funds"

        self.is_reentrant = True

        try:
            self.userFunds[user] -= amount
            self.total_balance -= amount
        finally:
            self.is_reentrant = False

        return f"Withdrawal of {amount} successful for {user}"

    def attack(self, attacker):
        if self.is_reentrant:
            return "Reentrancy attack blocked"

        stolen = 0
        self.is_reentrant = True

        def recursive_steal():
            nonlocal stolen
            for victim in list(self.userFunds.keys()):
                if victim != attacker and self.userFunds[victim] > 0:
                    stolen_amount = min(10, self.userFunds[victim])
                    self.userFunds[attacker] += stolen_amount
                    self.userFunds[victim] -= stolen_amount
                    self.total_balance -= stolen_amount
                    stolen += stolen_amount
                    print(f"Reentrancy: Stole {stolen_amount} from {victim}. Attacker's total: {self.userFunds[attacker]} ETH.")
                    recursive_steal()  # Recursive çağrı
                    break

        try:
            recursive_steal()
        finally:
            self.is_reentrant = False

        return f"Attacker successfully stole {stolen} ETH!"

    def get_balances(self):
        return {
            "individual": self.userFunds,
            "total": self.total_balance
        }

bank = VulnerableBank()

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/deposit", methods=["POST"])
def deposit():
    data = request.json
    user = data["user"]
    amount = float(data["amount"])
    result = bank.deposit(user, amount)
    return jsonify({"message": result, "balances": bank.get_balances()})

@app.route("/withdraw", methods=["POST"])
def withdraw():
    data = request.json
    user = data["user"]
    amount = float(data["amount"])
    result = bank.withdraw(user, amount)
    return jsonify({"message": result, "balances": bank.get_balances()})

@app.route("/attack", methods=["POST"])
def attack():
    attacker = "Attacker"
    result = bank.attack(attacker)
    return jsonify({"message": result, "balances": bank.get_balances()})

@app.route("/balances", methods=["GET"])
def balances():
    return jsonify(bank.get_balances())

if __name__ == "__main__":
    app.run(debug=True)
