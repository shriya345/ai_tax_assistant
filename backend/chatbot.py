"""
AI Tax Chatbot — Indian Tax Domain
Uses a curated knowledge base with keyword-based retrieval
and optionally integrates with Claude API for advanced responses.
"""

import re
import os
from typing import Optional

# ─── Curated Indian Tax Knowledge Base ───────────────────────────────────────
# This knowledge base is built from official Income Tax Department sources,
# the Income Tax Act 1961, Finance Acts, and CBDT circulars.
KNOWLEDGE_BASE = {
    # ── Sections ─────────────────────────────────────────────────────────────
    "80c": {
        "keywords": ["80c", "section 80c", "ppf", "elss", "lic", "nsc", "sukanya", "epf", "investment deduction", "tax saving investment"],
        "answer": """**Section 80C — Maximum Deduction: ₹1,50,000**

Section 80C is the most popular tax-saving section under the Income Tax Act, 1961. It allows a deduction of up to **₹1,50,000** per year from your taxable income.

**Eligible Investments:**
• **EPF** (Employee Provident Fund) — contribution from salary
• **PPF** (Public Provident Fund) — 15-year lock-in, tax-free returns
• **ELSS** (Equity Linked Saving Scheme) — 3-year lock-in, market-linked
• **NSC** (National Savings Certificate) — 5-year lock-in
• **Tax-saving FD** — 5-year lock-in with banks
• **LIC Premium** — life insurance premium paid
• **Home Loan Principal** repayment
• **Sukanya Samriddhi Yojana** (for girl child)
• **Senior Citizens Savings Scheme (SCSS)**
• **Tuition fees** (children's school/college — max 2 children)
• **NPS (Employee contribution)** — u/s 80CCD(1), part of 80C

⚠️ **Note:** Section 80C deductions are **NOT available** under the New Tax Regime."""
    },
    "80d": {
        "keywords": ["80d", "section 80d", "health insurance", "medical insurance", "mediclaim"],
        "answer": """**Section 80D — Health Insurance Deduction**

Deduction for health insurance premiums paid for self, family, and parents.

**Limits for AY 2024-25:**
| Category | Deduction Limit |
|---|---|
| Self + Spouse + Children (below 60) | ₹25,000 |
| Self + Spouse + Children (60+) | ₹50,000 |
| Parents (below 60) | + ₹25,000 |
| Parents (60 or above) | + ₹50,000 |
| **Maximum (all senior citizens)** | **₹1,00,000** |

**Also includes:**
• Preventive health check-up: ₹5,000 (within overall limit)
• Medical expenditure for very senior citizens (80+) where no insurance is available

⚠️ Payment must be through **non-cash modes** (cheque, digital) except for preventive check-ups."""
    },
    "hra": {
        "keywords": ["hra", "house rent allowance", "rent exemption", "rent deduction"],
        "answer": """**HRA (House Rent Allowance) Exemption — Section 10(13A)**

HRA exemption is the **least of these three conditions:**

1. **Actual HRA received** from employer
2. **Actual rent paid** minus 10% of Basic Salary
3. **50% of Basic Salary** (Metro cities: Delhi, Mumbai, Kolkata, Chennai)
   **40% of Basic Salary** (Non-metro cities)

**Example:**
- Basic Salary: ₹6,00,000/year
- HRA Received: ₹2,00,000/year
- Rent Paid: ₹1,80,000/year
- City: Non-metro

Condition 1: ₹2,00,000
Condition 2: ₹1,80,000 − ₹60,000 = ₹1,20,000
Condition 3: ₹6,00,000 × 40% = ₹2,40,000

**HRA Exemption = ₹1,20,000 (minimum)**

📌 Rent > ₹1,00,000/year? Landlord's PAN is mandatory.
📌 HRA is NOT available in **New Tax Regime**."""
    },
    "new_vs_old": {
        "keywords": ["new regime", "old regime", "which regime", "regime comparison", "better regime", "tax regime"],
        "answer": """**Old vs New Tax Regime — Which is Better?**

**New Regime Slabs (Default from FY 2023-24):**
| Income | Rate |
|---|---|
| Up to ₹3,00,000 | Nil |
| ₹3L–₹6L | 5% |
| ₹6L–₹9L | 10% |
| ₹9L–₹12L | 15% |
| ₹12L–₹15L | 20% |
| Above ₹15L | 30% |
Rebate u/s 87A: **Zero tax if income ≤ ₹7 Lakh**

**Old Regime Slabs:**
| Income | Rate |
|---|---|
| Up to ₹2,50,000 | Nil |
| ₹2.5L–₹5L | 5% |
| ₹5L–₹10L | 20% |
| Above ₹10L | 30% |
Rebate: Zero tax if income ≤ ₹5 Lakh

**When Old Regime is Better:**
✅ You have large 80C investments (₹1.5L)
✅ You pay house rent and claim HRA
✅ You have home loan interest deduction
✅ Total deductions > ₹3.75 Lakh (typically)

**When New Regime is Better:**
✅ You have few/no deductions
✅ Income ≤ ₹7 Lakh (zero tax!)
✅ Want simplicity without tracking investments

💡 Use our **Tax Calculator** to compare both regimes for your exact situation!"""
    },
    "itr_forms": {
        "keywords": ["itr form", "which itr", "income tax return form", "itr-1", "itr-2", "itr-3", "itr-4", "sahaj", "sugam"],
        "answer": """**Which ITR Form Should You File?**

| ITR Form | Who Should File |
|---|---|
| **ITR-1 (Sahaj)** | Salary/Pension + 1 House Property + Other income ≤ ₹50L. NOT if foreign assets. |
| **ITR-2** | Capital gains, foreign income, multiple properties, directorship |
| **ITR-3** | Business/professional income (non-presumptive) |
| **ITR-4 (Sugam)** | Presumptive income: business ≤ ₹2Cr (44AD) or profession ≤ ₹50L (44ADA) |
| **ITR-5** | Partnership firms, LLPs |
| **ITR-6** | Companies |
| **ITR-7** | Trusts, political parties |

**Most salaried individuals file ITR-1 or ITR-2.**

Filing deadline (non-audit): **July 31** of the assessment year."""
    },
    "nps": {
        "keywords": ["nps", "national pension system", "national pension scheme", "80ccd", "pension deduction"],
        "answer": """**NPS (National Pension System) Tax Benefits**

NPS offers triple tax benefits:

**1. Section 80CCD(1)** — Part of 80C limit:
- Employee contribution: Up to 10% of salary (Basic + DA)
- Self-employed: Up to 20% of gross income
- Maximum: ₹1,50,000 (within overall 80C limit)

**2. Section 80CCD(1B)** — Additional ₹50,000:
- Over and above the ₹1.5L 80C limit
- Exclusive to NPS contributions
- **Total 80C + 80CCD(1B) = ₹2,00,000**

**3. Section 80CCD(2)** — Employer's contribution:
- Up to 10% of salary (Basic + DA) — no upper limit
- Available in **BOTH old and new regimes!**

**At Maturity:**
- 60% can be withdrawn tax-free
- 40% must be used to buy annuity (pension)

📌 NPS is one of the few deductions available in the **New Tax Regime** via 80CCD(2)."""
    },
    "filing_deadline": {
        "keywords": ["deadline", "last date", "due date", "when to file", "filing date", "itr deadline", "july 31"],
        "answer": """**ITR Filing Deadlines — AY 2024-25 (FY 2023-24)**

| Category | Due Date |
|---|---|
| Individuals, HUF (non-audit) | **July 31, 2024** |
| Businesses requiring audit | October 31, 2024 |
| TP Audit cases | November 30, 2024 |
| Belated/Revised ITR | December 31, 2024 |

**Late Filing Fees (Section 234F):**
- Income > ₹5 Lakh: **₹5,000**
- Income ≤ ₹5 Lakh: **₹1,000**
- Income below exemption limit: **Nil** (but filing still recommended)

**Advance Tax Dates:**
- June 15: 15% | Sep 15: 45% | Dec 15: 75% | Mar 15: 100%

⚠️ Interest u/s 234A is charged at 1% per month for delay in filing."""
    },
    "capital_gains": {
        "keywords": ["capital gains", "stcg", "ltcg", "shares", "mutual fund", "property sale", "capital asset"],
        "answer": """**Capital Gains Tax in India**

**Equity Shares & Equity Mutual Funds:**
- STCG (held < 1 year): **15%** u/s 111A
- LTCG (held > 1 year): **10%** on gains above ₹1,00,000 u/s 112A (no indexation)

**Debt Mutual Funds (from April 2023):**
- Now taxed as per income tax slab (like FD interest)
- No LTCG benefit for debt funds invested after April 1, 2023

**Real Estate / Property:**
- STCG (held < 2 years): Added to income, taxed at slab rate
- LTCG (held > 2 years): **20% with indexation** u/s 112
- Exemption u/s 54: Reinvest in residential property
- Exemption u/s 54EC: Invest in NHAI/REC bonds (max ₹50L)

**Gold:**
- STCG (< 3 years): Slab rate
- LTCG (> 3 years): 20% with indexation

📌 Report capital gains in **ITR-2 or ITR-3**, not ITR-1."""
    },
    "tds": {
        "keywords": ["tds", "tax deducted at source", "form 16", "form 26as", "tds refund", "tds credit"],
        "answer": """**TDS (Tax Deducted at Source)**

TDS is tax deducted by the payer before making payments to you.

**Common TDS Rates:**
| Payment Type | Section | Rate |
|---|---|---|
| Salary | 192 | As per slab |
| Bank Interest (FD) | 194A | 10% (if PAN given) |
| Rent > ₹50,000/month | 194IB | 5% |
| Professional fees | 194J | 10% |
| Commission/Brokerage | 194H | 5% |
| Dividends | 194 | 10% |

**Key Points:**
- Submit **Form 15G/15H** to avoid TDS if income is below taxable limit
- Check your TDS credits in **Form 26AS** and **AIS** on the IT portal
- TDS reflects in your return and adjusts your final tax liability
- **Excess TDS = Refund** (claim while filing ITR)

📌 Form 16 (from employer) and Form 16A (from others) are TDS certificates."""
    },
    "standard_deduction": {
        "keywords": ["standard deduction", "50000", "salaried deduction"],
        "answer": """**Standard Deduction for Salaried Individuals**

A flat deduction of **₹50,000** is available to all salaried individuals and pensioners.

- No bills or proofs required
- Automatically applied while calculating tax
- Available in **BOTH Old and New Tax Regimes** (New regime got it from FY 2023-24)
- Replaces the earlier transport allowance and medical reimbursement provisions

**For Pensioners:**
Family pension is also eligible for standard deduction of ₹15,000 or 1/3rd of pension, whichever is lower."""
    },
    "do_i_file": {
        "keywords": ["mandatory", "compulsory filing", "do i need to file", "should i file", "filing mandatory", "who should file"],
        "answer": """**Is ITR Filing Mandatory for You?**

**Mandatory if ANY of these apply:**
✅ Gross income > Basic exemption limit (₹2.5L / ₹3L / ₹5L based on age)
✅ Deposited > ₹1 Crore in bank accounts
✅ Electricity bill > ₹1 Lakh in a year
✅ Foreign travel expense > ₹2 Lakh in a year
✅ TDS/TCS > ₹25,000 (₹50,000 for seniors)
✅ Own foreign assets or foreign income
✅ Signing authority in a foreign account
✅ Business turnover > ₹60 Lakh / Profession receipts > ₹10 Lakh

**Recommended even if not mandatory:**
- To claim TDS refund
- For loan/visa applications (banks ask for 2-3 years ITR)
- To carry forward capital losses"""
    },
    "home_loan": {
        "keywords": ["home loan", "housing loan", "section 24", "80ee", "80eea", "interest deduction", "principal deduction"],
        "answer": """**Home Loan Tax Benefits**

**Section 24(b) — Interest Deduction:**
- Self-occupied property: Up to **₹2,00,000** per year
- Let-out property: **No limit** on interest deduction
- Under construction: Interest allowed from year of completion (5 equal installments)

**Section 80C — Principal Repayment:**
- Up to **₹1,50,000** per year (within overall 80C limit)
- Includes stamp duty and registration charges in year of payment

**Section 80EEA — Additional Interest (First-time buyers):**
- Additional **₹1,50,000** on interest
- Property stamp duty value ≤ ₹45 Lakh
- Loan sanctioned between April 1, 2019 – March 31, 2022

**Joint Home Loan Benefits:**
- Each co-borrower can claim **separate** benefits u/s 24(b) and 80C

⚠️ Section 24 interest deduction is **NOT available** under New Tax Regime for self-occupied property."""
    },
    "form26as": {
        "keywords": ["form 26as", "ais", "annual information statement", "tax statement"],
        "answer": """**Form 26AS & AIS — Your Tax Summary**

**Form 26AS** (Annual Tax Statement) shows:
- All TDS deducted by employers, banks, others
- Advance tax and self-assessment tax paid
- Tax refunds received
- High-value transactions (property, bank deposits)

**AIS (Annual Information Statement)** — More comprehensive:
- Salary details
- Interest income (savings, FD, bonds)
- Dividends received
- Securities transactions (shares, MF)
- Foreign remittances
- GST turnover (for businesses)

**How to Access:**
1. Login at **incometax.gov.in**
2. Go to e-File → Income Tax Returns → View AIS
3. Form 26AS: Under My Account or Quick Links

📌 **Always cross-check your ITR with AIS/26AS** to avoid notices from the IT department. Discrepancies trigger automated scrutiny."""
    },
}

# ─── Chatbot Class ────────────────────────────────────────────────────────────
class TaxChatbot:
    """
    AI Tax Chatbot using:
    1. Keyword-based retrieval from curated knowledge base
    2. Falls back to Claude API for complex queries (if API key available)
    """
    
    def __init__(self):
        self.kb = KNOWLEDGE_BASE
        self.api_key = os.environ.get("ANTHROPIC_API_KEY", "")
        self._conversation_history = []
    
    def get_response(self, user_query: str) -> str:
        """Get response for user query."""
        query_lower = user_query.lower().strip()
        
        # 1. Try knowledge base first
        kb_response = self._search_knowledge_base(query_lower)
        if kb_response:
            return kb_response
        
        # 2. Try Claude API if available
        if self.api_key:
            return self._query_claude_api(user_query)
        
        # 3. Fallback
        return self._fallback_response(query_lower)
    
    def _search_knowledge_base(self, query: str) -> Optional[str]:
        """Search knowledge base using keyword matching with scoring."""
        best_match = None
        best_score = 0
        
        for topic, data in self.kb.items():
            score = 0
            for keyword in data["keywords"]:
                if keyword in query:
                    # Longer keyword matches score higher
                    score += len(keyword.split())
            
            if score > best_score:
                best_score = score
                best_match = data["answer"]
        
        # Return if we have a meaningful match
        if best_score >= 1:
            return best_match
        
        return None
    
    def _query_claude_api(self, query: str) -> str:
        """Use Claude API for complex queries with domain restriction."""
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=self.api_key)
            
            system_prompt = """You are TaxSaathi, an expert AI assistant specializing EXCLUSIVELY in Indian Income Tax. 
            
Your knowledge covers:
- Income Tax Act 1961 and amendments
- CBDT circulars and notifications  
- Finance Acts and Union Budget announcements
- ITR filing procedures and forms
- Tax deductions (80C, 80D, HRA, etc.)
- Old vs New Tax Regime comparison
- Capital gains, TDS, advance tax

Rules:
1. ONLY answer questions related to Indian income tax
2. For non-tax questions, politely redirect: "I specialize only in Indian income tax. Please ask me a tax-related question!"
3. Always mention if rules changed recently
4. Add disclaimer for complex situations: "Please consult a CA for your specific case"
5. Use ₹ symbol for amounts, cite relevant sections

Current tax year context: AY 2024-25 (FY 2023-24)"""
            
            response = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=600,
                system=system_prompt,
                messages=[{"role": "user", "content": query}]
            )
            return response.content[0].text
        
        except Exception as e:
            return self._fallback_response(query)
    
    def _fallback_response(self, query: str) -> str:
        """Provide helpful fallback when no specific answer found."""
        # Check if it's off-topic
        tax_keywords = ["tax", "income", "deduction", "return", "itr", "refund", "salary", 
                        "investment", "filing", "form", "regime", "80c", "section"]
        
        is_tax_related = any(kw in query for kw in tax_keywords)
        
        if not is_tax_related:
            return ("I specialize exclusively in **Indian Income Tax** topics. "
                    "Please ask me about:\n"
                    "• Income tax calculations\n"
                    "• Deductions (80C, 80D, HRA, etc.)\n"
                    "• Old vs New Tax Regime\n"
                    "• ITR forms and filing\n"
                    "• TDS, capital gains, advance tax")
        
        return (f"I couldn't find a specific answer for *'{query}'* in my knowledge base. "
                "Here are topics I can help with:\n\n"
                "**Popular Questions:**\n"
                "• What is Section 80C?\n"
                "• New vs Old Tax Regime comparison?\n"  
                "• Which ITR form should I file?\n"
                "• How is HRA exemption calculated?\n"
                "• What is Section 80D?\n"
                "• NPS tax benefits?\n"
                "• Capital gains tax rules?\n\n"
                "💡 *Try asking one of the Quick Questions on the right panel!*")

