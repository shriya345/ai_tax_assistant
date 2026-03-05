"""
Indian Income Tax Calculator — AY 2024-25
Implements both Old and New Tax Regimes per Income Tax Act
"""

class TaxCalculator:
    """
    Calculates Indian income tax under Old and New regimes.
    Rules based on Finance Act 2023 / AY 2024-25.
    """
    
    # ── New Regime Slabs (Finance Act 2023) ──────────────────────────────────
    NEW_SLABS = [
        (300_000,  0.00),
        (600_000,  0.05),
        (900_000,  0.10),
        (1_200_000, 0.15),
        (1_500_000, 0.20),
        (float('inf'), 0.30),
    ]
    
    # ── Old Regime Slabs ─────────────────────────────────────────────────────
    OLD_SLABS_BELOW_60 = [
        (250_000,  0.00),
        (500_000,  0.05),
        (1_000_000, 0.20),
        (float('inf'), 0.30),
    ]
    OLD_SLABS_SENIOR = [   # 60–80 years
        (300_000,  0.00),
        (500_000,  0.05),
        (1_000_000, 0.20),
        (float('inf'), 0.30),
    ]
    OLD_SLABS_SUPER_SENIOR = [  # 80+ years
        (500_000,  0.00),
        (1_000_000, 0.20),
        (float('inf'), 0.30),
    ]
    
    CESS_RATE = 0.04  # Health & Education Cess
    MAX_80C   = 150_000
    MAX_80D   = 25_000   # Base; seniors get more
    MAX_80D_PARENTS_NORMAL = 25_000
    MAX_80D_PARENTS_SENIOR = 50_000
    MAX_HOME_LOAN = 200_000
    STANDARD_DEDUCTION_SALARY = 50_000
    
    def calculate(self, inputs: dict) -> dict:
        """Main entry: runs both regimes and returns comparison."""
        old = self._calc_old(inputs)
        new = self._calc_new(inputs)
        
        savings = abs(old["total_tax"] - new["total_tax"])
        if old["total_tax"] < new["total_tax"]:
            better = "old"
        elif new["total_tax"] < old["total_tax"]:
            better = "new"
        else:
            better = "equal"
        
        return {
            "old_regime": old,
            "new_regime": new,
            "better_regime": better,
            "savings": savings,
        }
    
    # ── Old Regime ────────────────────────────────────────────────────────────
    def _calc_old(self, inp: dict) -> dict:
        gross = inp["gross_salary"] + inp.get("other_income", 0)
        
        # Standard deduction
        std_ded = self.STANDARD_DEDUCTION_SALARY
        
        # HRA exemption (least of three conditions)
        hra_exemption = self._calc_hra(
            inp.get("hra_received", 0),
            inp.get("rent_paid", 0),
            inp["gross_salary"],
            inp.get("is_metro", False)
        )
        
        # 80C (max ₹1.5L)
        ded_80c = min(inp.get("sec_80c", 0), self.MAX_80C)
        
        # 80D
        ded_80d = min(inp.get("sec_80d", 0), self.MAX_80D)
        
        # Home loan interest (max ₹2L)
        ded_home = min(inp.get("home_loan_interest", 0), self.MAX_HOME_LOAN)
        
        # Other deductions (80E, 80G, NPS 80CCD1B etc.)
        other_ded = inp.get("other_deductions", 0)
        
        total_deductions = std_ded + hra_exemption + ded_80c + ded_80d + ded_home + other_ded
        taxable = max(0, gross - total_deductions)
        
        age = inp.get("age", 0)
        slabs = (self.OLD_SLABS_SUPER_SENIOR if age >= 80
                 else self.OLD_SLABS_SENIOR if age >= 60
                 else self.OLD_SLABS_BELOW_60)
        
        tax, breakdown = self._apply_slabs(taxable, slabs)
        
        # Rebate u/s 87A: full rebate if taxable income ≤ ₹5L
        rebate = tax if taxable <= 500_000 else 0
        tax_after_rebate = max(0, tax - rebate)
        
        # Surcharge
        surcharge = self._calc_surcharge_old(tax_after_rebate, taxable)
        
        # Cess
        cess = round((tax_after_rebate + surcharge) * self.CESS_RATE)
        total = tax_after_rebate + surcharge + cess
        
        eff_rate = (total / gross * 100) if gross > 0 else 0
        
        return {
            "gross_income": gross,
            "standard_deduction": std_ded,
            "hra_exemption": hra_exemption,
            "deduction_80c": ded_80c,
            "deduction_80d": ded_80d,
            "home_loan_interest": ded_home,
            "other_deductions": other_ded,
            "total_deductions": total_deductions,
            "taxable_income": taxable,
            "tax_before_cess": tax_after_rebate,
            "rebate_87a": rebate,
            "surcharge": surcharge,
            "cess": cess,
            "total_tax": total,
            "effective_rate": eff_rate,
            "slab_breakdown": breakdown,
        }
    
    # ── New Regime ────────────────────────────────────────────────────────────
    def _calc_new(self, inp: dict) -> dict:
        gross = inp["gross_salary"] + inp.get("other_income", 0)
        
        # Only standard deduction allowed in new regime (from AY 2024-25)
        std_ded = self.STANDARD_DEDUCTION_SALARY
        taxable = max(0, gross - std_ded)
        
        tax, breakdown = self._apply_slabs(taxable, self.NEW_SLABS)
        
        # Rebate u/s 87A: if taxable ≤ ₹7L, full rebate in new regime
        rebate = tax if taxable <= 700_000 else 0
        tax_after_rebate = max(0, tax - rebate)
        
        # Marginal relief: if income just above ₹7L
        if taxable > 700_000:
            excess = taxable - 700_000
            if tax_after_rebate > excess:
                tax_after_rebate = excess
        
        surcharge = self._calc_surcharge_new(tax_after_rebate, taxable)
        cess = round((tax_after_rebate + surcharge) * self.CESS_RATE)
        total = tax_after_rebate + surcharge + cess
        
        eff_rate = (total / gross * 100) if gross > 0 else 0
        
        return {
            "gross_income": gross,
            "standard_deduction": std_ded,
            "taxable_income": taxable,
            "tax_before_cess": tax_after_rebate,
            "rebate_87a": rebate,
            "surcharge": surcharge,
            "cess": cess,
            "total_tax": total,
            "effective_rate": eff_rate,
            "slab_breakdown": breakdown,
        }
    
    # ── Helpers ───────────────────────────────────────────────────────────────
    def _apply_slabs(self, income: float, slabs: list) -> tuple:
        """Apply progressive tax slabs and return (total_tax, breakdown_list)."""
        tax = 0
        prev = 0
        breakdown = []
        
        for limit, rate in slabs:
            if income <= prev:
                break
            
            taxable_in_slab = min(income, limit) - prev
            tax_in_slab = round(taxable_in_slab * rate)
            
            if rate > 0 or taxable_in_slab > 0:
                breakdown.append({
                    "range": f"₹{prev:,} – {'₹'+str(int(limit)):} " if limit != float('inf') else f"Above ₹{prev:,}",
                    "rate": int(rate * 100),
                    "amount": taxable_in_slab,
                    "tax": tax_in_slab,
                })
            
            tax += tax_in_slab
            prev = limit
        
        return tax, breakdown
    
    def _calc_hra(self, hra_received, rent_paid, salary, is_metro) -> int:
        """Calculate HRA exemption — minimum of three conditions."""
        if hra_received == 0 or rent_paid == 0:
            return 0
        
        basic_salary = salary * 0.4  # Approximation: 40% of gross as basic
        
        cond1 = hra_received
        cond2 = rent_paid - (0.1 * basic_salary)
        cond3 = basic_salary * (0.5 if is_metro else 0.4)
        
        exemption = max(0, min(cond1, cond2, cond3))
        return int(exemption)
    
    def _calc_surcharge_old(self, tax, income) -> int:
        """Surcharge for old regime."""
        if income > 5_00_00_000:
            return round(tax * 0.37)
        elif income > 2_00_00_000:
            return round(tax * 0.25)
        elif income > 1_00_00_000:
            return round(tax * 0.15)
        elif income > 50_00_000:
            return round(tax * 0.10)
        return 0
    
    def _calc_surcharge_new(self, tax, income) -> int:
        """Surcharge for new regime (max 25% from FY2023-24)."""
        if income > 5_00_00_000:
            return round(tax * 0.25)
        elif income > 2_00_00_000:
            return round(tax * 0.25)
        elif income > 1_00_00_000:
            return round(tax * 0.15)
        elif income > 50_00_000:
            return round(tax * 0.10)
        return 0

