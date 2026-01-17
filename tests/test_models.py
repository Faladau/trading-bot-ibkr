"""
Teste pentru models
"""

import pytest
from datetime import datetime, timedelta
from src.models.market_data import Bar, Quote, Tick
from src.models.signal import Signal, SignalAction, Indicator
from src.models.trade import Trade, Position, Order, OrderType, OrderSide, OrderStatus, PositionStatus


class TestBar:
    """Teste pentru Bar"""
    
    def test_create_valid_bar(self):
        """Test creare bar valid"""
        bar = Bar(
            timestamp=datetime.now(),
            open=100.0,
            high=105.0,
            low=99.0,
            close=103.0,
            volume=1000
        )
        
        assert bar.open == 100.0
        assert bar.high == 105.0
        assert bar.low == 99.0
        assert bar.close == 103.0
        assert bar.volume == 1000
    
    def test_bar_validation_high_low(self):
        """Test validare high >= low"""
        with pytest.raises(ValueError, match="High cannot be less than Low"):
            Bar(
                timestamp=datetime.now(),
                open=100.0,
                high=99.0,
                low=100.0,
                close=100.0,
                volume=1000
            )
    
    def test_bar_price_change(self):
        """Test calcul price change"""
        bar = Bar(
            timestamp=datetime.now(),
            open=100.0,
            high=105.0,
            low=99.0,
            close=103.0,
            volume=1000
        )
        
        assert bar.price_change == 3.0
        assert bar.price_change_pct == 0.03
        assert bar.range == 6.0
    
    def test_bar_to_dict(self):
        """Test conversie la dict"""
        bar = Bar(
            timestamp=datetime(2024, 1, 15, 10, 0, 0),
            open=100.0,
            high=105.0,
            low=99.0,
            close=103.0,
            volume=1000
        )
        
        data = bar.to_dict()
        assert data["open"] == 100.0
        assert data["close"] == 103.0
        assert "timestamp" in data


class TestQuote:
    """Teste pentru Quote"""
    
    def test_create_valid_quote(self):
        """Test creare quote valid"""
        quote = Quote(
            timestamp=datetime.now(),
            symbol="AAPL",
            bid=150.0,
            ask=150.5,
            bid_size=100,
            ask_size=100
        )
        
        assert quote.bid == 150.0
        assert quote.ask == 150.5
        assert quote.spread == 0.5
        assert quote.mid_price == 150.25
    
    def test_quote_validation_bid_ask(self):
        """Test validare bid <= ask"""
        with pytest.raises(ValueError, match="Bid cannot be greater than Ask"):
            Quote(
                timestamp=datetime.now(),
                symbol="AAPL",
                bid=151.0,
                ask=150.5,
                bid_size=100,
                ask_size=100
            )


class TestSignal:
    """Teste pentru Signal"""
    
    def test_create_buy_signal(self):
        """Test creare semnal BUY"""
        signal = Signal(
            action=SignalAction.BUY,
            symbol="AAPL",
            timestamp=datetime.now(),
            entry_price=150.0,
            take_profit=153.0,
            stop_loss=149.0,
            confidence=0.8
        )
        
        assert signal.action == SignalAction.BUY
        assert signal.entry_price == 150.0
        assert signal.has_targets is True
    
    def test_signal_validation_take_profit_buy(self):
        """Test validare take profit pentru BUY"""
        with pytest.raises(ValueError, match="Take profit must be greater"):
            Signal(
                action=SignalAction.BUY,
                symbol="AAPL",
                timestamp=datetime.now(),
                entry_price=150.0,
                take_profit=149.0,  # Mai mic decât entry
                stop_loss=149.0,
                confidence=0.8
            )
    
    def test_signal_risk_reward_ratio(self):
        """Test calcul risk/reward ratio"""
        signal = Signal(
            action=SignalAction.BUY,
            symbol="AAPL",
            timestamp=datetime.now(),
            entry_price=150.0,
            take_profit=153.0,  # +3%
            stop_loss=149.0,     # -1%
            confidence=0.8
        )
        
        ratio = signal.risk_reward_ratio
        assert ratio is not None
        assert ratio == 3.0  # 3% reward / 1% risk = 3:1


class TestOrder:
    """Teste pentru Order"""
    
    def test_create_market_order(self):
        """Test creare ordin market"""
        order = Order(
            symbol="AAPL",
            side=OrderSide.BUY,
            order_type=OrderType.MARKET,
            quantity=10
        )
        
        assert order.symbol == "AAPL"
        assert order.side == OrderSide.BUY
        assert order.order_type == OrderType.MARKET
        assert order.quantity == 10
        assert order.status == OrderStatus.PENDING
    
    def test_create_limit_order(self):
        """Test creare ordin limit"""
        order = Order(
            symbol="AAPL",
            side=OrderSide.BUY,
            order_type=OrderType.LIMIT,
            quantity=10,
            limit_price=150.0
        )
        
        assert order.limit_price == 150.0
    
    def test_order_validation_limit_price(self):
        """Test validare limit price pentru LIMIT order"""
        with pytest.raises(ValueError, match="Limit price required"):
            Order(
                symbol="AAPL",
                side=OrderSide.BUY,
                order_type=OrderType.LIMIT,
                quantity=10
                # limit_price lipsă
            )
    
    def test_order_fill_properties(self):
        """Test proprietăți de fill"""
        order = Order(
            symbol="AAPL",
            side=OrderSide.BUY,
            order_type=OrderType.MARKET,
            quantity=10
        )
        
        assert order.remaining_quantity == 10
        assert order.fill_percentage == 0.0
        
        order.filled_quantity = 5
        order.status = OrderStatus.PARTIALLY_FILLED
        
        assert order.remaining_quantity == 5
        assert order.fill_percentage == 50.0
        assert order.is_partially_filled is True


class TestPosition:
    """Teste pentru Position"""
    
    def test_create_buy_position(self):
        """Test creare poziție BUY"""
        position = Position(
            symbol="AAPL",
            side=OrderSide.BUY,
            quantity=10,
            entry_price=150.0,
            current_price=152.0,
            take_profit=153.0,
            stop_loss=149.0
        )
        
        assert position.symbol == "AAPL"
        assert position.unrealized_pnl == 20.0  # (152 - 150) * 10
        assert position.is_profitable is True
    
    def test_position_unrealized_pnl_buy(self):
        """Test calcul PnL pentru poziție BUY"""
        position = Position(
            symbol="AAPL",
            side=OrderSide.BUY,
            quantity=10,
            entry_price=150.0,
            current_price=148.0
        )
        
        assert position.unrealized_pnl == -20.0  # (148 - 150) * 10
        assert position.is_profitable is False
    
    def test_position_unrealized_pnl_sell(self):
        """Test calcul PnL pentru poziție SELL"""
        position = Position(
            symbol="AAPL",
            side=OrderSide.SELL,
            quantity=10,
            entry_price=150.0,
            current_price=148.0
        )
        
        assert position.unrealized_pnl == 20.0  # (150 - 148) * 10
        assert position.is_profitable is True
    
    def test_position_at_take_profit(self):
        """Test verificare atingere take profit"""
        position = Position(
            symbol="AAPL",
            side=OrderSide.BUY,
            quantity=10,
            entry_price=150.0,
            current_price=153.0,
            take_profit=153.0
        )
        
        assert position.is_at_take_profit is True
    
    def test_position_at_stop_loss(self):
        """Test verificare atingere stop loss"""
        position = Position(
            symbol="AAPL",
            side=OrderSide.BUY,
            quantity=10,
            entry_price=150.0,
            current_price=149.0,
            stop_loss=149.0
        )
        
        assert position.is_at_stop_loss is True
    
    def test_position_update_price(self):
        """Test actualizare preț"""
        position = Position(
            symbol="AAPL",
            side=OrderSide.BUY,
            quantity=10,
            entry_price=150.0,
            current_price=150.0
        )
        
        position.update_price(152.0)
        assert position.current_price == 152.0
        assert position.unrealized_pnl == 20.0


class TestTrade:
    """Teste pentru Trade"""
    
    def test_create_profitable_trade(self):
        """Test creare trade profitabil"""
        entry_time = datetime.now()
        exit_time = entry_time + timedelta(hours=2)
        
        trade = Trade(
            symbol="AAPL",
            side=OrderSide.BUY,
            quantity=10,
            entry_price=150.0,
            exit_price=153.0,
            entry_timestamp=entry_time,
            exit_timestamp=exit_time,
            commission=1.0
        )
        
        assert trade.gross_pnl == 30.0  # (153 - 150) * 10
        assert trade.net_pnl == 29.0    # 30 - 1
        assert trade.pnl_pct == 2.0    # (153 - 150) / 150 * 100
        assert trade.is_profitable is True
    
    def test_create_losing_trade(self):
        """Test creare trade cu pierdere"""
        entry_time = datetime.now()
        exit_time = entry_time + timedelta(hours=1)
        
        trade = Trade(
            symbol="AAPL",
            side=OrderSide.BUY,
            quantity=10,
            entry_price=150.0,
            exit_price=148.0,
            entry_timestamp=entry_time,
            exit_timestamp=exit_time,
            commission=1.0
        )
        
        assert trade.gross_pnl == -20.0  # (148 - 150) * 10
        assert trade.net_pnl == -21.0    # -20 - 1
        assert trade.is_profitable is False
    
    def test_trade_duration(self):
        """Test calcul durată trade"""
        entry_time = datetime(2024, 1, 15, 10, 0, 0)
        exit_time = datetime(2024, 1, 15, 12, 0, 0)
        
        trade = Trade(
            symbol="AAPL",
            side=OrderSide.BUY,
            quantity=10,
            entry_price=150.0,
            exit_price=153.0,
            entry_timestamp=entry_time,
            exit_timestamp=exit_time
        )
        
        assert trade.duration_seconds == 7200.0  # 2 ore
    
    def test_trade_to_dict(self):
        """Test conversie la dict"""
        entry_time = datetime.now()
        exit_time = entry_time + timedelta(hours=1)
        
        trade = Trade(
            symbol="AAPL",
            side=OrderSide.BUY,
            quantity=10,
            entry_price=150.0,
            exit_price=153.0,
            entry_timestamp=entry_time,
            exit_timestamp=exit_time
        )
        
        data = trade.to_dict()
        assert data["symbol"] == "AAPL"
        assert data["gross_pnl"] == 30.0
        assert "entry_timestamp" in data
