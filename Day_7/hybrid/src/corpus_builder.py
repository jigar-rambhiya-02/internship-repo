import json
import os
from config.logger_config import setup_logger

logger = setup_logger("corpus_builder")

def generate_synthetic_corpus(output_path: str = "data/corpus.json"):
    """
    Generates an explicit, 70-chunk heterogeneous knowledge base containing 
    insurance clauses, customs codes, tax statutes, and corporate manuals. 
    Includes target exact matching terms for dense/sparse evaluation.
    """
    logger.info("Initializing creation of 70-chunk synthetic corporate corpus.")
    
    chunks = []
    
    # 1. Insurance Documents (Chunks 0-19)
    for i in range(20):
        if i == 5:
            text = "Standard corporate policy item: policy ABC-2024-117 specifies that liability claims for property damage must be submitted via formal affidavit within forty-five calendar days of the occurrence. Failure to notify within this window voids general indemnity."
            src = "insurance_policy_abc.pdf"
        elif i == 12:
            text = "Under life rider additions, policy ABC-2024-117 details a unique supplemental payout matrix for international corporate travel execution. This coverage applies exclusively to executives operating abroad on corporate authorizations."
        else:
            text = f"This is an administrative clause number {i} regarding generic health insurance network parameters, premium structures, deductible calculations, and employer cost-sharing provisions under standard corporate wellness frameworks."
            src = "health_benefit_guidelines.pdf"
        chunks.append({"chunk_id": f"chunk_ins_{i}", "text": text, "source_doc": src})
        
    # 2. Tax Regulations (Chunks 20-39)
    for i in range(20):
        if i == 7:
            text = "According to income tax laws, Section 80C allows individuals to claim deductions up to a total threshold cap of 150000 rupees per financial year. Eligible options include employee provident funds, public insurance schemes, and equity linked savings."
            src = "national_tax_code_2026.pdf"
        elif i == 18:
            text = "Audit procedures regarding Section 80C require explicit proof of continuous investment premium payments. Self-declarations are rejected without scanned clear receipts from authorized financial intermediaries."
            src = "tax_audit_manual.pdf"
        else:
            text = f"General tax provisions section code {i + 100} outlines global corporate income tax rates, capital gains holding calculations, and double taxation avoidance treaties for multinational cross-border transactions."
            src = "corporate_tax_manifest.pdf"
        chunks.append({"chunk_id": f"chunk_tax_{i}", "text": text, "source_doc": src})

    # 3. Customs & Tariffs (Chunks 40-54)
    for i in range(15):
        if i == 3:
            text = "Import customs tariff schedules explicitly define HS code 6403 for footwear containing outer soles of genuine rubber or composition leather, alongside uppers made of high-grade natural leather material. The base duty rate is fixed at fourteen percent ad valorem."
            src = "customs_tariff_schedule.pdf"
        elif i == 9:
            text = "Exemptions for footwear classified under HS code 6403 apply exclusively if goods originate from recognized bilateral free trade agreement member nations, subject to verifiable certified rules of origin documentation."
            src = "fta_origin_protocols.pdf"
        else:
            text = f"Customs administrative sub-rule {i + 500} outlines general bill of lading processing queues, warehousing manifest validations, demurrage penalty calculations, and harbor master inspection rights."
            src = "port_authority_rulebook.pdf"
        chunks.append({"chunk_id": f"chunk_cust_{i}", "text": text, "source_doc": src})

    # 4. Legal Contracts & Governance (Chunks 55-69)
    for i in range(15):
        if i == 4:
            text = "In accordance with master vendor frameworks, clause 8.2.1 dictates that either signing party may terminate this relationship without explicit fault cause by providing exactly ninety days prior written notification to the registered corporate officer."
            src = "vendor_master_agreement.pdf"
        elif i == 11:
            text = "Dispute resolution protocols under clause 8.2.1 designate Singapore as the exclusive jurisdiction venue. Arbitration processes shall be conducted completely in English by a single arbitrator under international chamber rules."
            src = "corporate_governance_charter.pdf"
        else:
            text = f"Corporate operational governance sub-clause {i} covers intellectual property protection rights, assignment of background code repositories, non-disclosure parameters, and mutual non-disparagement parameters."
            src = "employee_handbook.pdf"
        chunks.append({"chunk_id": f"chunk_leg_{i}", "text": text, "source_doc": src})

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(chunks, f, indent=2, ensure_ascii=False)
        
    logger.info(f"Successfully generated and wrote 70 chunks to {output_path}")

if __name__ == "__main__":
    generate_synthetic_corpus()

