# withdrawal_checker.py: Logic for managing automated withdrawal proposals.
# Part of LeoBook Core — System
#
# Functions: calculate_proposed_amount(), get_latest_win(), check_triggers(), propose_withdrawal(), check_withdrawal_approval(), execute_withdrawal()

import asyncio
from datetime import datetime as dt, timedelta
from pathlib import Path
from Core.System.lifecycle import state, log_audit_state, log_state
from Data.Access.db_helpers import log_audit_event
from Core.Intelligence.aigo_suite import AIGOSuite
from Core.Utils.constants import DEFAULT_STAKE, CURRENCY_SYMBOL, now_ng

# Scalable Thresholds (relative to DEFAULT_STAKE)
MIN_BALANCE_RESERVE = DEFAULT_STAKE * 5000 # Keep 5,000 units by default
WITHDRAWAL_TRIGGER_BALANCE = DEFAULT_STAKE * 10000
MIN_WIN_TRIGGER = DEFAULT_STAKE * 5000

# Local state for withdrawals
pending_withdrawal = {
    "active": False,
    "amount": 0.0,
    "proposed_at": None,
    "expiry": None,
    "approved": False
}

def calculate_proposed_amount(balance: float, latest_win: float) -> float:
    """Calculation: Min(30% balance, 50% latest win)."""
    val = min(balance * 0.30, latest_win * 0.50)
    # Ensure floor remains in account
    if balance - val < MIN_BALANCE_RESERVE:
        val = balance - MIN_BALANCE_RESERVE
    
    return max(0.0, float(int(val))) # Round to whole number

def get_latest_win() -> float:
    """Retrieves the latest win amount from audit logs or state."""
    return state.get("last_win_amount", MIN_WIN_TRIGGER)

async def check_triggers(page=None) -> bool:
    """v2.7 Triggers."""
    balance = state.get("current_balance", 0.0)
    if balance >= WITHDRAWAL_TRIGGER_BALANCE and get_latest_win() >= MIN_WIN_TRIGGER:
        return True
    return False

async def propose_withdrawal(amount: float):
    global pending_withdrawal
    if pending_withdrawal["active"]:
        return

    pending_withdrawal.update({
        "active": True,
        "amount": amount,
        "proposed_at": now_ng(),
        "expiry": now_ng() + timedelta(hours=2),
        "approved": False
    })

    print(f"   [Withdrawal] Proposal active: {CURRENCY_SYMBOL}{amount:.2f} (Awaiting LeoBook Web/App approval)")
    # Persist proposal to Supabase via audit log for Web/App approval UI
    log_audit_event(
        "WITHDRAWAL_PROPOSAL",
        f"Proposed: {CURRENCY_SYMBOL}{amount:.2f} | Balance: {CURRENCY_SYMBOL}{state.get('current_balance', 0):.2f}",
        status="pending"
    )

async def check_withdrawal_approval() -> bool:
    """
    Check if a pending withdrawal has been approved via LeoBook Web/App.
    Reads approval status from Supabase audit_log (flagged by Web/App).
    """
    if not pending_withdrawal["active"]:
        return False

    # Check expiration
    if pending_withdrawal["expiry"] and now_ng() > pending_withdrawal["expiry"]:
        print("   [Withdrawal] Proposal expired (Time-to-Live exceeded). Resetting.")
        log_audit_event("WITHDRAWAL_EXPIRED", f"Expired proposal: ₦{pending_withdrawal['amount']}", status="reset")
        pending_withdrawal.update({"active": False, "amount": 0.0, "expiry": None})
        return False
    
    try:
        from Data.Access.sync_manager import get_supabase_client
        sb = get_supabase_client()
        if sb:
            result = sb.table("audit_log").select("status").eq(
                "event_type", "WITHDRAWAL_APPROVAL"
            ).order("created_at", desc=True).limit(1).execute()
            
            if result.data and result.data[0].get("status") == "approved":
                pending_withdrawal["approved"] = True
                print("   [Withdrawal] ✅ Approval received from LeoBook Web/App.")
                return True
    except Exception as e:
        print(f"   [Withdrawal] Approval check failed: {e}")
    
    return False

@AIGOSuite.aigo_retry(max_retries=2, delay=5.0)
async def execute_withdrawal(amount: float, user_id: str = None):
    """Executes the withdrawal using an isolated, per-user browser context (v2.9)."""
    print(f"   [Execute] Starting approved withdrawal for {CURRENCY_SYMBOL}{amount:.2f}...")
    from playwright.async_api import async_playwright
    from Modules.FootballCom.fb_session import (
        get_user_session_dir, load_user_fingerprint, launch_browser_with_retry,
    )

    async with async_playwright() as p:
        user_data_dir = get_user_session_dir(user_id).absolute()
        user_data_dir.mkdir(parents=True, exist_ok=True)
        fingerprint = load_user_fingerprint(user_id) if user_id else None
        try:
            context = await launch_browser_with_retry(p, user_data_dir, fingerprint=fingerprint)
            page = await context.new_page()
            
            from Modules.FootballCom.booker.withdrawal import check_and_perform_withdrawal
            success = await check_and_perform_withdrawal(page, state["current_balance"], last_win_amount=amount*2)
            
            if success:
                log_state("Withdrawal", f"Executed {CURRENCY_SYMBOL}{amount:,.2f}", "Web/App Approval")
                log_audit_event("WITHDRAWAL_EXECUTED", f"Executed: {CURRENCY_SYMBOL}{amount}", state["current_balance"], state["current_balance"]-amount, amount)
                state["last_withdrawal_time"] = now_ng()
                # Reset pending state
                pending_withdrawal.update({"active": False, "amount": 0.0, "proposed_at": None, "expiry": None, "approved": False})
            else:
                print("   [Execute Error] Withdrawal process failed.")
                
            await context.close()
        except Exception as e:
            print(f"   [Execute Error] Failed to launch context for withdrawal: {e}")
