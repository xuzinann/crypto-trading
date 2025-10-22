from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from src.database.connection import get_db
from src.database.models.trade import Trade
from src.database.models.position import Position
from src.database.models.daily_stats import DailyStats
from pydantic import BaseModel
from datetime import datetime, timedelta

router = APIRouter()


class PositionResponse(BaseModel):
    id: int
    symbol: str
    entry_price: float
    current_price: float
    amount: float
    unrealized_pnl: float
    status: str
    entry_time: datetime

    class Config:
        from_attributes = True


class TradeResponse(BaseModel):
    id: int
    symbol: str
    type: str
    amount: float
    entry_price: float
    exit_price: float
    profit_loss: float
    timestamp: datetime
    reasoning: str

    class Config:
        from_attributes = True


@router.get("/positions", response_model=List[PositionResponse])
async def get_positions(db: Session = Depends(get_db)):
    """Get all open positions"""
    positions = db.query(Position).filter(Position.status == "OPEN").all()
    return positions


@router.get("/trades", response_model=List[TradeResponse])
async def get_trades(
    limit: int = 100,
    days: int = 30,
    db: Session = Depends(get_db)
):
    """Get trade history"""
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    trades = db.query(Trade).filter(
        Trade.timestamp >= cutoff_date
    ).order_by(Trade.timestamp.desc()).limit(limit).all()
    return trades


@router.get("/stats/daily")
async def get_daily_stats(db: Session = Depends(get_db)):
    """Get today's trading statistics"""
    from datetime import date
    today = date.today()
    stats = db.query(DailyStats).filter(DailyStats.date == today).first()

    if not stats:
        return {
            "date": today,
            "total_trades": 0,
            "winning_trades": 0,
            "losing_trades": 0,
            "total_pnl": 0.0
        }

    return stats


@router.get("/system/status")
async def get_system_status():
    """Get system status"""
    # In real implementation, get actual status from trading engine
    return {
        "status": "running",
        "paper_trading": True,
        "last_signal": "HOLD",
        "account_balance": 10000.0,
        "daily_pnl": 0.0,
        "total_pnl": 0.0
    }


@router.post("/system/pause")
async def pause_trading():
    """Pause trading"""
    # In real implementation, pause the trading engine
    return {"status": "paused"}


@router.post("/system/resume")
async def resume_trading():
    """Resume trading"""
    # In real implementation, resume the trading engine
    return {"status": "running"}


@router.post("/positions/close-all")
async def close_all_positions():
    """Emergency close all positions"""
    # In real implementation, trigger emergency close
    return {"status": "all positions closed"}
